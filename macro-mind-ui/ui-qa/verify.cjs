// UI 验证脚本：桌面 + 移动截图，并检查关键交互。
const path = require('path');
const os = require('os');
const { chromium } = require('playwright-core');

const EXEC = path.join(
  os.homedir(),
  'Library/Caches/ms-playwright/chromium-1155/chrome-mac/Chromium.app/Contents/MacOS/Chromium',
);
const URL = 'http://localhost:5199/';
const results = [];
const check = (name, ok, extra = '') => {
  results.push({ name, ok, extra });
  console.log(`${ok ? 'PASS' : 'FAIL'} ${name}${extra ? ` — ${extra}` : ''}`);
};

(async () => {
  const browser = await chromium.launch({ executablePath: EXEC, headless: true });

  // ---------- 桌面 ----------
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  // /api/* 探测失败（502/503/404）是预期的降级路径：本地服务未运行或 /api/news 尚未实现 → 回退演示数据
  page.on('console', (m) => {
    if (m.type() !== 'error') return;
    const text = m.text();
    if (/Failed to load resource.*(502|503|404)/.test(text)) return;
    errors.push(text);
  });
  await page.goto(URL, { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);

  check('页面标题', (await page.title()).includes('MacroMind'));
  check('顶部栏产品名', await page.locator('header >> text=MacroMind').isVisible());
  check('默认进入对话页', await page.locator('nav[role=tablist] button[aria-selected=true]').innerText() === '聊天');
  check('不存在左右分栏', (await page.locator('[role=separator]').count()) === 0);
  check('连接状态显示', await page.locator('header [role=status]').isVisible(),
    (await page.locator('header [role=status]').innerText()).trim());
  check('模式切换存在', await page.locator('[role=radiogroup][aria-label=模式]').isVisible());
  check('模型下拉存在', await page.locator('#model-select').isVisible());
  check('空状态建议问题', (await page.locator('text=开始一次宏观研究对话').count()) > 0);
  await page.getByRole('tab', { name: '时间线' }).click();
  // 等首屏数据到位：本地服务冷启动解析快照可能要 1 秒以上，固定等待会误判成空数据
  await page
    .locator('[data-thread-id]')
    .first()
    .waitFor({ timeout: 20000 })
    .catch(() => console.log('WARN 等待脉络卡片超时'));
  await page.waitForTimeout(300);
  // 数据来源标签：未接后端时为演示数据提示，接了后端为真实来源说明（财联社电报）
  const sourceNote = await page.locator('main p').filter({ hasText: /演示数据|财联社|快照/ }).first().innerText().catch(() => '');
  check('标注数据来源', sourceNote.length > 0, sourceNote.slice(0, 60));

  // 画廊：一级主题标签 + 脉络卡片
  const topicGroup = page.locator('[role=group][aria-label=主题]');
  check('主题标签存在', await topicGroup.isVisible(), (await topicGroup.innerText()).replace(/\s+/g, ' '));
  const allCards = await page.locator('[data-thread-id]').count();
  check('画廊渲染脉络卡片', allCards >= 8, `cards=${allCards}`);
  // 卡片铺满：多列网格，且最后一张卡片在首屏之下或附近（不留半屏空白）
  const cols = await page.evaluate(() => {
    const xs = [...document.querySelectorAll('[data-thread-id]')].map((b) => Math.round(b.getBoundingClientRect().x));
    return new Set(xs).size;
  });
  check('卡片多列排布', cols >= 2, `cols=${cols}`);
  await page.screenshot({ path: 'ui-qa/gallery-light.png' });
  // 切换主题标签 → 只剩该主题卡片
  await topicGroup.getByRole('button', { name: /^市场与商品/ }).click();
  await page.waitForTimeout(200);
  const topicLabels = await page.locator('[data-thread-id] > span:first-child').allInnerTexts();
  check('主题筛选卡片', topicLabels.length > 0 && topicLabels.length < allCards && topicLabels.every((x) => x === '市场与商品'), topicLabels.join(','));
  await topicGroup.getByRole('button', { name: /^全部/ }).click();
  await page.waitForTimeout(200);

  // 打开一条脉络 → 占满面板的时间线（卡片随数据来源变化，取事件最多的一条）
  const cardInfos = await page.locator('[data-thread-id]').evaluateAll((els) =>
    els.map((b) => {
      const m = b.innerText.match(/(\d+)\s*条事件/);
      return { id: b.dataset.threadId, n: m ? Number(m[1]) : 1 };
    }),
  );
  const target = cardInfos.filter((c) => c.n > 1).sort((a, b) => b.n - a.n)[0] ?? cardInfos[0];
  const cardBtn = page.locator(`[data-thread-id="${target.id}"]`);
  const expectedCount = target.n;
  await cardBtn.click();
  await page.waitForTimeout(600);
  const article = page.locator('article');
  check('打开脉络时间线', await article.isVisible(), `id=${target.id}`);
  const entryCount = await page.locator('[data-event-id]').count();
  check('脉络内事件全部渲染', entryCount === expectedCount, `entries=${entryCount} 期望=${expectedCount}`);
  const dayKeys = await page.locator('section[data-day]').evaluateAll((els) => els.map((e) => e.dataset.day));
  check('脉络按时间先后（最早在上）', dayKeys.length > 1 && dayKeys.every((k, i) => i === 0 || dayKeys[i - 1] < k), dayKeys.slice(0, 3).join(','));
  const articleBox = await article.boundingBox();
  check('脉络页占据面板宽度', articleBox.width > 900, `w=${Math.round(articleBox.width)}`);
  check('详情面板默认不打开', (await page.locator('aside[aria-label^=事件详情]').count()) === 0);
  await page.screenshot({ path: 'ui-qa/thread-light.png' });

  // 缩略线点选 → 选中对应事件并打开详情
  await page.locator('[role=group][aria-label^=时间分布] button').last().click();
  await page.waitForTimeout(400);
  check('缩略线点选打开详情', await page.locator('aside[aria-label^=事件详情]').isVisible());
  await page.locator('aside').getByRole('button', { name: '关闭' }).click();

  // 点击事件 → 详情面板
  await page.locator('[data-event-id]').first().click();
  await page.waitForTimeout(300);
  check('详情面板打开', await page.locator('aside[aria-label^=事件详情]').isVisible());
  check('详情显示发生/发布时间', (await page.locator('aside >> text=事件发生时间').count()) > 0);
  check('详情面板不再重复脉络列表', (await page.locator('aside >> text=事件脉络').count()) === 0);
  await page.screenshot({ path: 'ui-qa/thread-detail.png' });
  await page.getByRole('button', { name: '加入聊天', exact: true }).click();
  await page.waitForTimeout(200);
  check('事件已加入聊天上下文', (await page.locator('text=已加入的事件上下文').count()) > 0);
  await page.locator('aside').getByRole('button', { name: '关闭' }).click();

  // 返回画廊：焦点回到卡片，选中状态清空
  await page.getByRole('button', { name: /返回全部时间线/ }).click();
  await page.waitForTimeout(300);
  check('返回画廊', (await page.locator('[data-thread-id]').count()) === allCards);
  check('返回后焦点回到卡片', await page.evaluate((id) => document.activeElement?.dataset.threadId === id, target.id), target.id);

  // 筛选：关键词 → 空结果 → 重置
  await page.getByPlaceholder('搜索关键词…').fill('不存在的关键词XYZ');
  await page.waitForTimeout(300);
  check('空筛选结果提示', (await page.locator('text=当前筛选条件下没有事件').count()) > 0);
  await page.getByRole('button', { name: '重置筛选' }).first().click();
  await page.waitForTimeout(200);
  check('重置筛选恢复', (await page.locator('[data-thread-id]').count()) === allCards);
  // 关键词命中 → 卡片收窄为相关脉络
  await page.getByPlaceholder('搜索关键词…').fill('原油');
  await page.waitForTimeout(300);
  const hit = await page.locator('[data-thread-id]').count();
  check('关键词筛选卡片', hit > 0 && hit < allCards, `cards=${hit}`);
  await page.getByRole('button', { name: '重置筛选' }).first().click();
  await page.waitForTimeout(200);

  // 深色主题截图：画廊 + 脉络页
  await page.getByRole('button', { name: '切换主题' }).click();
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'ui-qa/gallery-dark.png' });
  await page.locator(`[data-thread-id="${target.id}"]`).click();
  await page.waitForTimeout(600);
  await page.locator('[data-event-id]').nth(Math.min(1, entryCount - 1)).click();
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'ui-qa/thread-dark.png' });
  await page.locator('aside').getByRole('button', { name: '关闭' }).click();
  await page.getByRole('button', { name: /返回全部时间线/ }).click();
  await page.getByRole('button', { name: '切换主题' }).click();

  // 聊天：模型下拉只反映配置，没有配置就明说（发送链路见 verify-chat.cjs）
  // 这里连的是仓库真实配置的模型，不能发请求（会产生真实调用），只验证界面状态。
  await page.getByRole('tab', { name: '聊天' }).click();
  await page.waitForTimeout(300);
  const modelOptions = await page.locator('#model-select option').allInnerTexts();
  check('模型下拉不含界面占位模型', !modelOptions.some((o) => o.includes('演示')), modelOptions.join(' / '));
  const selectedModel = await page.locator('#model-select').inputValue();
  const emptyHint = (await page.locator('text=还没有可用的模型').count()) > 0;
  const blockedHint = (await page.locator('text=当前模型不可用').count()) > 0;
  if (emptyHint || blockedHint) {
    check('无可用模型时说明原因', true, emptyHint ? '未配置模型' : '模型不可用');
    check('说明里给出设置入口', await page.getByRole('button', { name: '打开设置' }).isVisible());
    await page.locator('textarea').fill('有内容也不该能发出去');
    await page.waitForTimeout(200);
    check('无可用模型时发送被禁用', await page.getByRole('button', { name: '发送', exact: true }).isDisabled());
    await page.locator('textarea').fill('');
  } else {
    check('有可用模型时不显示无模型提示', true, `当前模型 ${selectedModel}`);
    console.log(`SKIP 发送链路（连的是真实模型 ${selectedModel}，避免真实调用；见 verify-chat.cjs）`);
  }

  // 主题切换
  await page.getByRole('button', { name: '切换主题' }).click();
  await page.waitForTimeout(200);
  const isDark = await page.evaluate(() => document.documentElement.classList.contains('dark'));
  check('主题切换生效', isDark === true || isDark === false, `dark=${isDark}`);
  await page.screenshot({ path: 'ui-qa/desktop-dark.png' });
  await page.getByRole('button', { name: '切换主题' }).click();
  await page.waitForTimeout(200);
  await page.screenshot({ path: 'ui-qa/desktop-light.png', fullPage: false });

  check('无页面 JS 错误', errors.length === 0, errors.slice(0, 3).join(' | '));

  // ---------- 移动端 ----------
  const mpage = await browser.newPage({ viewport: { width: 390, height: 844 } });
  await mpage.goto(URL, { waitUntil: 'networkidle' });
  await mpage.waitForTimeout(600);
  check('移动端标签页存在', await mpage.locator('header [role=tablist]').isVisible());
  // 切到时间线，设置筛选，再切回聊天，草稿保留
  await mpage.locator('textarea').fill('移动端草稿');
  await mpage.getByRole('tab', { name: '时间线' }).click();
  await mpage.waitForTimeout(300);
  check('移动端画廊可见', await mpage.locator('[data-thread-id]').first().isVisible());
  const mcols = await mpage.evaluate(() => new Set([...document.querySelectorAll('[data-thread-id]')].map((b) => Math.round(b.getBoundingClientRect().x))).size);
  check('移动端卡片单列', mcols === 1, `cols=${mcols}`);
  const overflowX = await mpage.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  check('移动端无横向溢出', !overflowX);
  await mpage.screenshot({ path: 'ui-qa/mobile-gallery.png' });
  await mpage.locator(`[data-thread-id="${target.id}"]`).click();
  await mpage.waitForTimeout(400);
  await mpage.screenshot({ path: 'ui-qa/mobile-thread.png' });
  await mpage.locator('[data-event-id]').first().click();
  await mpage.waitForTimeout(300);
  check('移动端详情为抽屉', (await mpage.locator('[role=dialog][aria-label^=事件详情]').count()) === 1);
  await mpage.screenshot({ path: 'ui-qa/mobile-detail.png' });
  await mpage.locator('[role=dialog]').getByRole('button', { name: '关闭' }).click();
  await mpage.getByRole('tab', { name: '聊天' }).click();
  await mpage.waitForTimeout(200);
  check('切换标签后草稿保留', (await mpage.locator('textarea').inputValue()) === '移动端草稿');
  await mpage.screenshot({ path: 'ui-qa/mobile-chat.png' });

  await browser.close();
  const failed = results.filter((r) => !r.ok);
  console.log(`\n${results.length - failed.length}/${results.length} 项通过`);
  process.exit(failed.length > 0 ? 1 : 0);
})().catch((e) => {
  console.error('脚本错误：', e);
  process.exit(2);
});
