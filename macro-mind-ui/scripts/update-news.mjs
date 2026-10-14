// 更新时间线数据：抓取财联社电报 → 归类 → 写出事件与展示快照。
//
// 用法：
//   node scripts/update-news.mjs --rebuild        # 只用已抓取的 data/news.raw.json 重建
//   node scripts/update-news.mjs                  # 增量抓取（从最新事件往前翻到已覆盖的位置）
//   node scripts/update-news.mjs --days 30        # 首次补齐 30 天
//
// 进出文件：
//   data/news.raw.json       抓取到的原始电报（大文件，不进版本控制）
//   data/news.events.json    采纳的全部事件（含审计字段与正文），累积保存
//   public/news.snapshot.json 每日每类别限量后的展示快照（随前端构建发布，离线可用）
//
// 抓取速率：请求之间固定间隔 1.5 秒，单次运行最多 150 次请求，到达上限即停止并保留已抓部分。

import { createHash } from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildSnapshot, buildThreads, limitThreadEvents, toEvents } from '../server/news/pipeline.mjs';
import { CATEGORY_ORDER } from '../server/news/pipeline.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const DATA = path.join(ROOT, 'data');
const RAW = path.join(DATA, 'news.raw.json');
const EVENTS = path.join(DATA, 'news.events.json');
// 展示快照写到 public/，随前端构建一起发布：没有本地服务时也能看到真实数据
const SNAPSHOT = path.join(ROOT, 'public/news.snapshot.json');

const API = 'https://www.cls.cn/v1/roll/get_roll_list';
const REQUEST_INTERVAL_MS = 1500; // 抓取速率：每次请求间隔
const MAX_REQUESTS_PER_RUN = 150; // 单次运行请求上限
const PAGE_SIZE = 50;

const argv = process.argv.slice(2);
const flag = (name, fallback) => {
  const i = argv.indexOf(`--${name}`);
  return i === -1 ? fallback : argv[i + 1];
};
const days = Number(flag('days', 92));
const rebuild = argv.includes('--rebuild');

const readJson = (file, fallback) => {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch {
    return fallback;
  }
};
const writeJson = (file, obj) => {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, JSON.stringify(obj));
  console.log(`wrote ${path.relative(ROOT, file)} (${(JSON.stringify(obj).length / 1024).toFixed(0)} KB)`);
};

// ---------- 抓取 ----------

function sign(params) {
  const q = Object.keys(params).sort().map((k) => `${k}=${params[k]}`).join('&');
  return createHash('md5').update(createHash('sha1').update(q).digest('hex')).digest('hex');
}

async function fetchPage(lastTime) {
  const base = {
    app: 'CailianpressWeb', os: 'web', sv: '8.4.6',
    rn: String(PAGE_SIZE), refresh_type: '1', last_time: String(lastTime), category: '',
  };
  const url = `${API}?${new URLSearchParams({ ...base, sign: sign(base) })}`;
  const res = await fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0', Referer: 'https://www.cls.cn/telegraph' },
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  if (data.errno !== 0) throw new Error(`errno ${data.errno} ${data.msg}`);
  return data.data.roll_data ?? [];
}

async function fetchNewRaw(existingItems) {
  const newest = existingItems.reduce((max, i) => Math.max(max, i.ctime), 0);
  const cutoff = Math.floor(Date.now() / 1000) - days * 86400;
  const byId = new Map(existingItems.map((i) => [i.id, i]));
  let cursor = Math.floor(Date.now() / 1000);
  let requests = 0;

  for (;;) {
    if (requests >= MAX_REQUESTS_PER_RUN) {
      console.log(`达到单次请求上限 ${MAX_REQUESTS_PER_RUN}，本次停止（已抓部分已保存）`);
      break;
    }
    const items = await fetchPage(cursor);
    requests += 1;
    if (items.length === 0) break;

    let oldest = cursor;
    for (const it of items) {
      const known = byId.get(it.id);
      if (!known) byId.set(it.id, it);
      else if (known.modified_time !== it.modified_time) byId.set(it.id, it); // 更新过的电报取新版本
      if (it.ctime < oldest) oldest = it.ctime;
    }
    console.log(`请求 ${requests}：本页 ${items.length} 条，累计 ${byId.size} 条，最早 ${new Date(oldest * 1000).toISOString().slice(0, 16)}`);

    if (oldest <= Math.max(cutoff, newest)) break;
    cursor = oldest;
    await new Promise((r) => setTimeout(r, REQUEST_INTERVAL_MS));
  }
  return { items: [...byId.values()].sort((a, b) => a.ctime - b.ctime), requests };
}

// ---------- 主流程 ----------

let raw = readJson(RAW, { items: [] });
let requests = 0;

if (!rebuild) {
  const got = await fetchNewRaw(raw.items ?? []);
  raw = { fetched_at: new Date().toISOString(), source: 'https://www.cls.cn/telegraph', items: got.items };
  requests = got.requests;
  writeJson(RAW, raw);
}

const items = raw.items ?? [];
if (items.length === 0) {
  console.error('没有可用的原始电报（先运行不带 --rebuild 的抓取）');
  process.exit(1);
}

// 与已有事件合并：同 ID 取新版本（正文可能被修订），保留历史区间
const previous = readJson(EVENTS, { events: [] });
const previousById = new Map((previous.events ?? []).map((e) => [e.id, e]));
const events = toEvents(items);
const merged = new Map(previousById);
for (const e of events) merged.set(e.id, e);
const all = [...merged.values()].sort((a, b) => new Date(a.publishedAt) - new Date(b.publishedAt));

const threads = limitThreadEvents(all, buildThreads(all, items, { maxThreads: 24 }), { perDay: 5 });
const snapshot = buildSnapshot(all, threads, { perDayPerCategory: 8 });

// 快照里挂上脉络归属；事件文件里保留多脉络的完整关系
const threadOf = snapshot.eventThread;
const snapEvents = snapshot.events.map((e) => ({ ...e, threadId: threadOf[e.id] }));
const threadsWithCount = snapshot.threads.map((th) => ({
  id: th.id,
  topicId: th.topicId,
  title: th.title,
  summary: th.summary,
  isDemo: false,
  eventCount: th.eventIds.length,
  /** 该主题抓到的全部条数（卡片上显示，示意脉络的真实规模） */
  totalEvents: th.totalEvents ?? th.eventIds.length,
}));

const times = all.map((e) => new Date(e.publishedAt).getTime());
const coverage = {
  from: new Date(Math.min(...times)).toISOString(),
  to: new Date(Math.max(...times)).toISOString(),
};
const perCategory = Object.fromEntries(
  CATEGORY_ORDER.map((c) => [c, snapEvents.filter((e) => e.category === c).length]),
);

writeJson(EVENTS, {
  updatedAt: new Date().toISOString(),
  source: raw.source,
  isDemo: false,
  coverage,
  total: all.length,
  /** 财联社正文是媒体报道，未做独立核实（与 engine 同一口径） */
  epistemicStatus: 'MEDIA_REPORT_NOT_INDEPENDENTLY_VERIFIED',
  events: all,
});

writeJson(SNAPSHOT, {
  updatedAt: new Date().toISOString(),
  source: raw.source,
  isDemo: false,
  coverage,
  total: all.length,
  shown: snapEvents.length,
  perCategoryInSnapshot: perCategory,
  requestsThisRun: requests,
  events: snapEvents,
  threads: threadsWithCount,
});

console.log(`原始 ${items.length} 条 → 采纳事件 ${all.length} 条 → 展示快照 ${snapEvents.length} 条；脉络 ${threadsWithCount.length} 条`);
console.log(`时间范围 ${coverage.from} .. ${coverage.to}`);
console.log('各类别在快照中的条数', perCategory);
