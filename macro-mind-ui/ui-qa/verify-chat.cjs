// 聊天链路验证：发送 / 流式 / 研究模式 / 停止 / 重试 / 记录模型。
//
// 完全隔离，不接触任何真实模型与密钥：
//   1) 本地 mock 上游（127.0.0.1，OpenAI 兼容 SSE）
//   2) 一个独立的本地服务实例（临时配置目录 + 端口 8790 + 关闭后台抓取）
//   3) 一个把 /api 指向该实例的 vite dev（端口 5200）
// 回环地址不需要密钥，因此本脚本无需任何环境变量即可运行。
const path = require('path');
const os = require('os');
const fs = require('fs');
const http = require('http');
const { spawn } = require('child_process');
const { chromium } = require('playwright-core');

const EXEC = path.join(
  os.homedir(),
  'Library/Caches/ms-playwright/chromium-1155/chrome-mac/Chromium.app/Contents/MacOS/Chromium',
);
const ROOT = path.resolve(__dirname, '..');
const SERVICE_PORT = 8790;
const VITE_PORT = 5200;
const URL = `http://localhost:${VITE_PORT}/`;
/** 回答里的固定标记：断言页面显示的确实是这个 mock 上游返回的内容 */
const MARKER = 'MOCK-UPSTREAM';

const results = [];
const check = (name, ok, extra = '') => {
  results.push(ok);
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}${extra ? ` — ${extra}` : ''}`);
};

// ---------- 1) mock 上游 ----------
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function startUpstream() {
  const server = http.createServer((req, res) => {
    let body = '';
    req.on('data', (d) => (body += d));
    req.on('end', async () => {
      let parsed = {};
      try {
        parsed = JSON.parse(body);
      } catch {
        /* 保持空对象 */
      }
      const messages = Array.isArray(parsed.messages) ? parsed.messages : [];
      const answer = `${MARKER} 已收到 ${messages.length} 条消息。这是本地验证用的回答，不是任何真实模型输出。`;
      if (!parsed.stream) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ choices: [{ message: { role: 'assistant', content: answer } }] }));
        return;
      }
      // 分块 + 间隔输出：真实模型不是瞬间返回，留出观察流式状态的时间
      res.writeHead(200, { 'Content-Type': 'text/event-stream; charset=utf-8', 'Cache-Control': 'no-cache' });
      const step = Math.ceil(answer.length / 5);
      for (let i = 0; i < answer.length; i += step) {
        res.write(`data: ${JSON.stringify({ choices: [{ delta: { content: answer.slice(i, i + step) } }] })}\n\n`);
        await sleep(250);
      }
      res.write('data: [DONE]\n\n');
      res.end();
    });
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

/** 轮询等待某个 HTTP 地址就绪 */
async function waitFor(url, timeoutMs = 20000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const res = await fetch(url);
      if (res.ok) return true;
    } catch {
      /* 还没起来 */
    }
    await new Promise((r) => setTimeout(r, 300));
  }
  return false;
}

(async () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'mm-qa-chat-'));
  const upstream = await startUpstream();
  const upstreamPort = upstream.address().port;

  // 临时模型配置：回环地址 → 无需密钥；label 供界面显示
  fs.writeFileSync(
    path.join(tmpDir, 'model.local.json'),
    `${JSON.stringify(
      {
        protocol: 'chat_completions',
        base_url: `http://127.0.0.1:${upstreamPort}/v1`,
        model: 'mock-upstream-model',
        chat_token_parameter: 'max_tokens',
        timeout_seconds: 30,
        max_retries: 1,
        max_rounds: 8,
        max_output_tokens: 3000,
      },
      null,
      2,
    )}\n`,
  );

  const service = spawn(process.execPath, ['server/index.mjs'], {
    cwd: ROOT,
    env: {
      ...process.env,
      MACROMIND_UI_PORT: String(SERVICE_PORT),
      MACROMIND_MODEL_CONFIG: path.join(tmpDir, 'model.local.json'),
      MACROMIND_NO_BACKGROUND_FETCH: '1',
    },
    stdio: 'ignore',
  });
  const vite = spawn(path.join(ROOT, 'node_modules/.bin/vite'), ['--port', String(VITE_PORT), '--strictPort'], {
    cwd: ROOT,
    env: { ...process.env, MACROMIND_API_PORT: String(SERVICE_PORT) },
    stdio: 'ignore',
  });

  let upstreamClosed = false;
  const closeUpstream = () => {
    if (upstreamClosed) return;
    upstreamClosed = true;
    upstream.close();
  };
  const cleanup = () => {
    service.kill();
    vite.kill();
    closeUpstream();
    fs.rmSync(tmpDir, { recursive: true, force: true });
  };

  const browser = await chromium.launch({ executablePath: EXEC, headless: true });
  try {
    if (!(await waitFor(`http://127.0.0.1:${SERVICE_PORT}/api/health`))) throw new Error('本地服务实例未就绪');
    if (!(await waitFor(URL))) throw new Error('vite 实例未就绪');

    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    const errors = [];
    page.on('pageerror', (e) => errors.push(String(e)));
    page.on('console', (m) => {
      if (m.type() === 'error') errors.push(m.text());
    });
    await page.goto(URL, { waitUntil: 'networkidle' });
    await page.waitForTimeout(800);

    // ---------- 模型清单只来自配置 ----------
    const options = await page.locator('#model-select option').allInnerTexts();
    check('下拉里是配置的模型', options.length === 1 && options[0].includes('mock-upstream-model'), options.join(' / '));
    check('不再出现界面占位模型', !options.some((o) => o.includes('演示')), options.join(' / '));
    check('回环模型无需密钥即可用', !options[0].includes('不可用'));
    await page.screenshot({ path: 'ui-qa/chat-connected.png' });

    // ---------- 快速模式：发送 + 流式回答 ----------
    await page.locator('textarea').fill('测试问题：美联储政策路径？');
    await page.locator('textarea').press('Enter');
    await page.waitForTimeout(300);
    const streaming =
      (await page.locator('text=生成中').count()) > 0 ||
      (await page.locator('.stream-cursor').count()) > 0 ||
      (await page.locator('text=等待响应').count()) > 0;
    check('发送后进入生成状态', streaming);
    await page.waitForTimeout(2500);
    check('收到上游回答', (await page.locator(`text=${MARKER}`).count()) > 0);
    check('回答记录模型与模式', (await page.getByText(/mock-upstream-model.*· 快速/).count()) > 0);
    check('回答不标演示', (await page.locator('text=演示回答').count()) === 0);

    // ---------- 研究模式：流程状态 ----------
    await page.locator('[role=radio]', { hasText: '研究' }).click();
    await page.locator('textarea').fill('研究模式测试');
    await page.locator('textarea').press('Enter');
    await page.waitForTimeout(600);
    check('研究流程状态显示', (await page.locator('text=收集来源').count()) > 0);

    // ---------- 停止生成 ----------
    const stopBtn = page.getByRole('button', { name: '停止生成' });
    if (await stopBtn.isVisible()) {
      await stopBtn.click();
      await page.waitForTimeout(300);
      check('取消后显示已取消', (await page.locator('text=已取消').count()) > 0);
      check('取消后可重试', (await page.getByRole('button', { name: '重试' }).count()) > 0);
      await page.getByRole('button', { name: '重试' }).click();
      await page.waitForTimeout(3000);
      check(
        '重试后完成',
        (await page.locator(`text=${MARKER}`).count()) >= 2,
        `markers=${await page.locator(`text=${MARKER}`).count()}`,
      );
    }

    // ---------- 上游故障：错误有说明 ----------
    closeUpstream();
    await page.locator('[role=radio]', { hasText: '快速' }).click();
    await page.locator('textarea').fill('上游已停止');
    await page.locator('textarea').press('Enter');
    await page.waitForTimeout(1500);
    check('上游不可用时给出错误说明', (await page.locator('[role=alert]').count()) > 0,
      (await page.locator('[role=alert]').allInnerTexts()).join(' | ').slice(0, 120));

    check('无控制台错误', errors.length === 0, errors.slice(0, 2).join(' | '));
  } finally {
    await browser.close();
    cleanup();
  }

  console.log(`\n${results.filter(Boolean).length}/${results.length} 项通过`);
  process.exit(results.every(Boolean) ? 0 : 1);
})().catch((e) => {
  console.error(e);
  process.exit(2);
});
