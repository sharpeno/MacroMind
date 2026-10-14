// 真实数据（财联社电报）时间线的浏览器检查与截图。
// 前置：npm run build && npm run server（或 node server/index.mjs）。
const { chromium } = require('playwright-core');

const EXEC = process.env.CHROME_PATH;
const BASE = process.env.MACROMIND_UI_URL || 'http://127.0.0.1:8787/';

(async () => {
  const browser = await chromium.launch({ executablePath: EXEC });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));

  await page.goto(BASE, { waitUntil: 'networkidle' });
  await page.getByRole('tab', { name: '时间线' }).click();
  await page.waitForTimeout(2500);
  console.log('来源说明:', (await page.getByText('财联社电报').first().textContent())?.trim());
  console.log('脉络卡片:', await page.locator('[data-thread-id]').count());
  await page.screenshot({ path: 'ui-qa/final-gallery-dark.png' });

  await page.locator('[data-thread-id]').first().click();
  await page.waitForTimeout(1200);
  console.log('脉络页事件:', await page.locator('[data-event-id]').count());
  await page.screenshot({ path: 'ui-qa/final-thread-dark.png' });

  await page.locator('[data-event-id]').first().click();
  await page.waitForTimeout(800);
  console.log('详情标题:', (await page.locator('aside h2').first().textContent())?.trim());
  console.log('报道原文折叠块:', await page.getByText('报道原文').count());
  console.log('来源链接:', await page.locator('aside a[target=_blank]').count());
  await page.screenshot({ path: 'ui-qa/final-detail-dark.png' });

  // 关键词筛选
  await page.getByPlaceholder('搜索关键词…').fill('美联储');
  await page.waitForTimeout(800);
  console.log('筛选后事件:', await page.locator('[data-event-id]').count());
  console.log('控制台错误:', errors.slice(0, 5));

  await browser.close();
})();
