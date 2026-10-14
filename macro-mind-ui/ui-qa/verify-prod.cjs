// 生产构建验证：本地服务同端口提供前端与 /api（打包后 Electron 加载的就是这个）
const path = require('path');
const os = require('os');
const { chromium } = require('playwright-core');
const EXEC = path.join(os.homedir(), 'Library/Caches/ms-playwright/chromium-1155/chrome-mac/Chromium.app/Contents/MacOS/Chromium');
(async () => {
  const browser = await chromium.launch({ executablePath: EXEC, headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await page.goto('http://127.0.0.1:8787/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  const status = (await page.locator('header [role=status]').innerText()).trim();
  const hasTimeline = await page.locator('section[aria-label=新闻时间线] >> text=货币政策').first().isVisible();
  // 发送一条演示消息
  await page.locator('textarea').fill('生产构建测试');
  await page.locator('textarea').press('Enter');
  await page.waitForTimeout(4000);
  const gotAnswer = (await page.locator('text=演示回答').count()) > 0;
  console.log('连接状态:', status);
  console.log('时间线渲染:', hasTimeline);
  console.log('演示聊天完成:', gotAnswer);
  console.log('JS错误:', errors.length === 0 ? '无' : errors.join('|'));
  await page.screenshot({ path: 'ui-qa/prod-desktop.png' });
  await browser.close();
  process.exit(status.includes('已连接') && hasTimeline && gotAnswer && errors.length === 0 ? 0 : 1);
})().catch((e) => { console.error(e); process.exit(2); });
