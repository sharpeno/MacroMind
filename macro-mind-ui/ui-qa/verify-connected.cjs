// 连接模式验证：本地服务运行中（无密钥 → 模型不可用，回退演示模型）
const path = require('path');
const os = require('os');
const { chromium } = require('playwright-core');
const EXEC = path.join(os.homedir(), 'Library/Caches/ms-playwright/chromium-1155/chrome-mac/Chromium.app/Contents/MacOS/Chromium');
const results = [];
const check = (name, ok, extra = '') => { results.push(ok); console.log(`${ok ? 'PASS' : 'FAIL'} ${name}${extra ? ` — ${extra}` : ''}`); };
(async () => {
  const browser = await chromium.launch({ executablePath: EXEC, headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto('http://localhost:5199/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  check('连接状态为已连接', (await page.locator('header [role=status]').innerText()).includes('已连接'),
    (await page.locator('header [role=status]').innerText()).trim());
  const options = await page.locator('#model-select option').allInnerTexts();
  check('本地模型出现在下拉中', options.some((o) => o.includes('g-deepseek-flash')), options.join(' / '));
  check('无密钥时本地模型标记不可用', options.some((o) => o.includes('不可用')));
  const disabled = await page.locator('#model-select option', { hasText: 'g-deepseek-flash' }).first().isDisabled();
  check('不可用模型被禁用', disabled);
  const selected = await page.locator('#model-select').inputValue();
  check('自动回退到演示模型', selected === 'demo-offline', selected);
  await browser.close();
  console.log(`\n${results.filter(Boolean).length}/${results.length} 项通过`);
  process.exit(results.every(Boolean) ? 0 : 1);
})().catch((e) => { console.error(e); process.exit(2); });
