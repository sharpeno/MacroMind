// 设置界面验证：模型配置对话框（模型清单、密钥只写不读、校验错误、测试连接、关闭与焦点）。
// 前置：vite dev 在 5199；本地服务在 8787 且以临时配置目录启动（避免改动仓库配置）。
const path = require('path');
const os = require('os');
const fs = require('fs');
const { chromium } = require('playwright-core');

const EXEC = path.join(os.homedir(), 'Library/Caches/ms-playwright/chromium-1155/chrome-mac/Chromium.app/Contents/MacOS/Chromium');
const CFG_DIR = process.env.MACROMIND_QA_CFG || '/tmp/mm-qa-cfg';

/** 每次运行前重置夹具：本地服务按请求读取这些文件，无需重启 */
function resetFixture() {
  // 只重置状态文件，别删目录本身——服务是拿这个路径启动的
  fs.mkdirSync(CFG_DIR, { recursive: true });
  for (const f of ['settings.local.json', 'secrets.local.json']) {
    const p = path.join(CFG_DIR, f);
    if (fs.existsSync(p)) fs.unlinkSync(p);
  }
  fs.writeFileSync(
    path.join(CFG_DIR, 'model.local.json'),
    `${JSON.stringify(
      {
        protocol: 'chat_completions',
        base_url: 'https://api.example.com/v1',
        model: 'g-deepseek-flash',
        api_key_env: 'MACROMIND_LOCAL_API_KEY',
        chat_token_parameter: 'max_tokens',
        timeout_seconds: 45,
        max_retries: 1,
        max_rounds: 8,
        max_output_tokens: 3000,
      },
      null,
      2,
    )}\n`,
  );
}

const results = [];
const check = (name, ok, extra = '') => {
  results.push(ok);
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}${extra ? ` — ${extra}` : ''}`);
};
const api = async (p) => (await fetch(`http://127.0.0.1:8787${p}`)).json();

(async () => {
  resetFixture();
  const browser = await chromium.launch({ executablePath: EXEC, headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('console', (m) => {
    if (m.type() !== 'error') return;
    const text = m.text();
    // 本脚本会故意提交非法配置（400）、请求不存在的本机模型（连接失败），这些不算错误
    if (/Failed to load resource.*(400|404|502|503)/.test(text)) return;
    errors.push(text);
  });
  await page.goto('http://localhost:5199/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);

  // ---------- 打开设置 ----------
  const gear = page.getByTestId('open-settings');
  check('顶栏有设置入口', await gear.isVisible());
  await gear.click();
  await page.waitForTimeout(500);
  const dialog = page.locator('[role=dialog][aria-label=设置]');
  check('设置对话框打开', await dialog.isVisible());
  check('初始焦点在关闭按钮', await page.evaluate(() => document.activeElement?.getAttribute('aria-label') === '关闭设置'));
  check('显示设置文件路径', (await dialog.locator('text=settings.local.json').count()) > 0);
  check('demo 模型提示存在', (await dialog.locator('text=不含密钥').count()) === 0);

  // ---------- 既有模型被导入 ----------
  const cards = dialog.locator('li');
  check('导入既有 model.local.json', (await cards.count()) === 1, `cards=${await cards.count()}`);
  const modelInput = cards.first().getByLabel('模型 ID');
  const urlInput = cards.first().getByLabel('接口地址');
  check('模型 ID 已填充', (await modelInput.inputValue()) === 'g-deepseek-flash', await modelInput.inputValue());
  check('接口地址已填充', (await urlInput.inputValue()) === 'https://api.example.com/v1', await urlInput.inputValue());
  check('标记为当前用于对话', await cards.first().locator('input[type=radio]').isChecked());
  check('密钥显示未设置', (await cards.first().locator('text=未设置').count()) > 0);

  // ---------- 密钥只写不读 ----------
  check('密钥输入为密码框', (await cards.first().locator('input[type=password]').count()) === 1);
  await cards.first().locator('input[type=password]').fill('sk-qa-secret-value');
  await page.getByRole('button', { name: '保存密钥' }).click();
  await page.waitForTimeout(500);
  check('保存后显示已设置', (await cards.first().locator('text=已设置').count()) > 0);
  check('保存后清空输入框', (await cards.first().locator('input[type=password]').inputValue()) === '');
  const settingsBody = await api('/api/settings');
  check('接口不返回密钥', !JSON.stringify(settingsBody).includes('sk-qa-secret-value'));
  check('接口回报 hasKey', settingsBody.settings.models[0].hasKey === true);
  const modelsBody = await api('/api/models');
  check('加密钥后模型可用', modelsBody.models[0].available === true, JSON.stringify(modelsBody.models[0].unavailableReason ?? ''));
  const settingsFile = require('fs').readFileSync('/tmp/mm-qa-cfg/settings.local.json', 'utf8');
  check('设置文件不含密钥', !settingsFile.includes('sk-qa-secret-value'));
  const secretsMode = require('fs').statSync('/tmp/mm-qa-cfg/secrets.local.json').mode & 0o777;
  check('密钥文件权限 0600', secretsMode === 0o600, secretsMode.toString(8));

  // ---------- 校验错误逐项显示 ----------
  await urlInput.fill('https://api.example.com/v1?debug=1');
  await page.getByRole('button', { name: '保存', exact: true }).click();
  await page.waitForTimeout(400);
  check('校验错误显示在条目上', (await dialog.locator('text=不能包含账号密码').count()) > 0);
  check('未保存状态提示', (await dialog.locator('text=有未保存的修改').count()) > 0);
  await urlInput.fill('http://api.example.com/v1');
  await page.getByRole('button', { name: '保存', exact: true }).click();
  await page.waitForTimeout(400);
  check('http 非回环被拒', (await dialog.locator('text=必须使用 https').count()) > 0);
  await urlInput.fill('http://127.0.0.1:11434/v1');
  await page.getByRole('button', { name: '保存', exact: true }).click();
  await page.waitForTimeout(500);
  check('合法配置保存成功', (await dialog.locator('text=已保存').count()) > 0);
  check('错误提示已清除', (await dialog.locator('text=必须使用 https').count()) === 0);
  const projection = require('fs').readFileSync('/tmp/mm-qa-cfg/model.local.json', 'utf8');
  check('投影回 model.local.json', projection.includes('127.0.0.1:11434'), JSON.parse(projection).base_url);

  // ---------- 测试连接（本机地址无服务 → 失败但给出原因）----------
  await page.getByRole('button', { name: '测试连接' }).click();
  await page.waitForTimeout(2500);
  check('连接失败给出原因', (await dialog.locator('text=连接失败').count()) > 0,
    (await dialog.locator('[role=status]').allInnerTexts()).join(' | ').slice(0, 120));

  // ---------- 新增 / 删除模型 ----------
  await page.getByRole('button', { name: '添加模型' }).click();
  await page.waitForTimeout(600);
  check('新增后有两条模型', (await dialog.locator('li').count()) === 2, `cards=${await dialog.locator('li').count()}`);
  check('新条目聚焦在名称输入', await page.evaluate(() => document.activeElement?.tagName === 'INPUT'));
  await dialog.locator('li').nth(1).getByRole('button', { name: '删除此模型' }).click();
  await page.waitForTimeout(200);
  check('删除前就地确认', (await dialog.locator('text=删除这个模型？').count()) === 1);
  await dialog.getByRole('button', { name: '确认删除' }).click();
  await page.waitForTimeout(500);
  check('删除模型生效', (await dialog.locator('li').count()) === 1, `cards=${await dialog.locator('li').count()}`);
  check('剩下一个时禁用删除', await dialog.locator('li').first().getByRole('button', { name: '删除此模型' }).isDisabled());

  // ---------- Esc 关闭 + 焦点回到入口 ----------
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
  check('Esc 关闭设置', (await page.locator('[role=dialog][aria-label=设置]').count()) === 0);
  check('焦点回到设置入口', await page.evaluate(() => document.activeElement?.getAttribute('aria-label') === '设置'));

  // ---------- 保存后模型下拉刷新 ----------
  await page.getByTestId('open-settings').click();
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'ui-qa/settings-light.png' });
  // 模态框打开时不点击背景控件，先关闭再切主题后重新打开
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
  await page.getByRole('button', { name: '切换主题' }).click();
  await page.waitForTimeout(300);
  await page.getByTestId('open-settings').click();
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'ui-qa/settings-dark.png' });
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
  await page.getByRole('button', { name: '切换主题' }).click();
  await page.waitForTimeout(300);
  const options = await page.locator('#model-select option').allInnerTexts();
  check('模型下拉反映设置', options.some((o) => o.includes('已导入') || o.includes('g-deepseek')), options.join(' / '));

  // ---------- 窄屏：对话框不横向溢出 ----------
  const narrow = await browser.newPage({ viewport: { width: 390, height: 780 } });
  await narrow.goto('http://localhost:5199/', { waitUntil: 'networkidle' });
  await narrow.waitForTimeout(700);
  await narrow.getByTestId('open-settings').click();
  await narrow.waitForTimeout(500);
  check('窄屏设置可见', await narrow.locator('[role=dialog][aria-label=设置]').isVisible());
  const overflow = await narrow.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  check('窄屏无横向溢出', !overflow);
  await narrow.screenshot({ path: 'ui-qa/settings-mobile.png' });

  check('无控制台错误', errors.length === 0, errors.slice(0, 2).join(' | '));

  await browser.close();
  console.log(`\n${results.filter(Boolean).length}/${results.length} 项通过`);
  process.exit(results.every(Boolean) ? 0 : 1);
})().catch((e) => {
  console.error(e);
  process.exit(2);
});
