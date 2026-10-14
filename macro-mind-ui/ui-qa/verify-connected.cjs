// 连接模式验证：本地服务运行中（8787 + vite 5199）。
// 模型清单完全来自本地配置：没有占位模型，不可用的模型列出但禁用并说明原因。
// 前置：npm run server（8787）与 vite --port 5199 都在跑。结果与是否设置了密钥无关。
const path = require('path');
const os = require('os');
const { chromium } = require('playwright-core');

const EXEC = path.join(
  os.homedir(),
  'Library/Caches/ms-playwright/chromium-1155/chrome-mac/Chromium.app/Contents/MacOS/Chromium',
);
const results = [];
const check = (name, ok, extra = '') => {
  results.push(ok);
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}${extra ? ` — ${extra}` : ''}`);
};

(async () => {
  const browser = await chromium.launch({ executablePath: EXEC, headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://localhost:5199/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  const status = (await page.locator('header [role=status]').innerText()).trim();
  check('连接状态为已连接', status.includes('已连接'), status);

  const options = await page.locator('#model-select option').allInnerTexts();
  const values = await page.locator('#model-select option').evaluateAll((els) => els.map((o) => o.value));
  check('模型清单来自本地配置', values.length >= 1 && values.every((v) => v !== ''), values.join(','));
  check('不出现界面占位模型', !options.some((o) => o.includes('演示')), options.join(' / '));

  const selected = await page.locator('#model-select').inputValue();
  const selectedText = values.indexOf(selected) >= 0 ? options[values.indexOf(selected)] : '';
  check('选中项在清单内或未选择', selected === '' || values.includes(selected), selected || '(未选择)');

  const unavailableOpts = await page
    .locator('#model-select option')
    .evaluateAll((els) => els.filter((o) => o.textContent.includes('不可用')).map((o) => o.textContent));
  if (unavailableOpts.length > 0) {
    check('不可用模型说明原因', unavailableOpts.every((t) => t.includes('：')), unavailableOpts.join(' / '));
    check(
      '不可用模型被禁用',
      await page.locator('#model-select option', { hasText: '不可用' }).first().isDisabled(),
    );
    check('不会选中不可用模型', !unavailableOpts.includes(selectedText), selectedText || '(未选择)');
  } else {
    check('配置的模型都可用', true, options.join(' / '));
  }

  await browser.close();
  console.log(`\n${results.filter(Boolean).length}/${results.length} 项通过`);
  process.exit(results.every(Boolean) ? 0 : 1);
})().catch((e) => {
  console.error(e);
  process.exit(2);
});
