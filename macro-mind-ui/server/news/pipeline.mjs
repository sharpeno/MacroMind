// 财联社原始电报 → 时间线事件 / 事件脉络 / 每日快照（纯函数，不联网）。
//
// 输出两层：
// - data/news.events.json：每个被采纳的事件（含正文、来源链接、命中词），用于审计与检索。
// - data/news.snapshot.json：每日每类别限量后的展示快照，随前端一起发布，
//   因此不启动本地服务时时间线也是真实数据（不再回退演示数据）。

import {
  classify,
  cleanText,
  classifyImportance,
  classifyRegion,
  deriveSummary,
  deriveTitle,
  extractClaims,
  extractEntities,
  hasTitle,
  IMPORTANCE_RANK,
  isDroppable,
} from './rules.mjs';
import { CATEGORY_TERMS } from './rules.mjs';

export const SOURCE_NAME = '财联社电报';
export const CATEGORY_ORDER = Object.keys(CATEGORY_TERMS);

const ISO = (sec) => new Date(sec * 1000).toISOString();

/** 展示时区（Asia/Shanghai）自然日键 */
export function dayKeyOf(iso) {
  const ms = new Date(iso).getTime() + 8 * 3600 * 1000;
  return new Date(ms).toISOString().slice(0, 10);
}

/** 事件发生时间是否比发布时间早（发生时间未知时不设 occurredAt） */
function occurredAtOf(iso) {
  return { occurredAt: iso, occurredAtPrecision: 'unknown' };
}

/** 单条电报 → 事件；不采纳时返回 null */
export function toEvent(item, { dropIds } = {}) {
  if (!item || !item.content) return null;
  if (isDroppable(item)) return null;
  if (dropIds && dropIds.has(item.id)) return null;

  const title = deriveTitle(item);
  const bodyText = cleanText(item.content);
  // 归类与重要性都看标题 + 正文，避免只看正文漏掉标题里的类别词
  const haystack = `${title}\n${bodyText}`.toLowerCase();

  const cat = classify(haystack);
  if (cat === null) return null; // 8 个宏观类别都不命中：不进入时间线
  const region = classifyRegion(haystack);
  const { importance, reasons } = classifyImportance(item, haystack);
  const { occurredAt, occurredAtPrecision } = occurredAtOf(ISO(item.ctime));

  const url = `https://www.cls.cn/detail/${item.id}`;
  const claims = extractClaims(bodyText);

  return {
    id: `cls_${item.id}`,
    occurredAt,
    occurredAtPrecision,
    publishedAt: occurredAt,
    category: cat.category,
    region: region.region,
    title,
    summary: deriveSummary(item),
    /** 报道正文原文（保留，详情面板可展开对照） */
    body: bodyText,
    sources: [{ name: SOURCE_NAME, url }],
    importance,
    entities: extractEntities(item),
    isDemo: false,
    // 财联社正文是媒体报道：原文归入「明确归属的主张」，不写「Agent 的解释」，
    // 以免把生成的解读混入事实层。
    attributedClaims: claims.length > 0 ? claims : undefined,
    /** 审计字段：为什么被这样归类（界面上不展示） */
    _audit: {
      level: item.level,
      readingNum: item.reading_num,
      hasTitle: hasTitle(item),
      categoryHits: cat.hits,
      regionHits: region.hits,
      importanceReasons: reasons,
      contentLength: bodyText.length,
    },
  };
}

/** 一批原始电报 → 事件数组（按时间正序） */
export function toEvents(items, options = {}) {
  const events = [];
  const seen = new Set();
  for (const item of items) {
    if (seen.has(item.id)) continue;
    seen.add(item.id);
    const e = toEvent(item, options);
    if (e) events.push(e);
  }
  return events.sort((a, b) => new Date(a.publishedAt) - new Date(b.publishedAt));
}

/**
 * 事件脉络：同一真实主题下的多事件。
 * - 主题来自财联社自带 subject（人工维护的报道栏目，不是模型推断）；
 *   同一电报命中的多个主题会拆到多条脉络（一条事件可属于多条脉络）。
 * - 只有出现 ≥ 2 次的主题才成为脉络，避免一条事件占一张卡片。
 * - 脉络按其中的事件数取前 N 条，卡片标题用主题名本身，不另写概述。
 */
const GENERIC_SUBJECTS_FOR_THREADS = new Set([
  '环球市场情报', '期货市场情报', '盘面直播', 'A股公告速递', 'A股风险提示公告', '提醒电报',
  '投资日历', '时政新闻播报', '新闻联播', 'A股上市公司业绩巡礼', 'A股上市公司业绩预告',
  '互动平台精选', '券商策略', '经济数据及解读', '宏观新闻', '宏观流动性', '科创板公司面面观',
]);

const CATEGORY_TOPIC = {
  monetary_policy: 'policy',
  fiscal_policy: 'policy',
  inflation_employment: 'macro_data',
  growth_activity: 'macro_data',
  financial_markets: 'markets',
  energy_commodities: 'markets',
  trade_geopolitics: 'trade_industry',
  tech_industry: 'trade_industry',
};

export function buildThreads(events, rawSubjects, { maxThreads = 24, minEvents = 2 } = {}) {
  // 事件 ID → 主题名列表（来自原始电报的 subjects）
  const subjectsByEvent = new Map();
  for (const item of rawSubjects) {
    const names = (item.subjects ?? [])
      .map((s) => s.subject_name)
      .filter((n) => !GENERIC_SUBJECTS_FOR_THREADS.has(n));
    if (names.length > 0) subjectsByEvent.set(`cls_${item.id}`, names);
  }

  const groups = new Map();
  for (const e of events) {
    for (const name of subjectsByEvent.get(e.id) ?? []) {
      if (!groups.has(name)) groups.set(name, []);
      groups.get(name).push(e);
    }
  }

  const threads = [];
  for (const [name, list] of groups) {
    if (list.length < minEvents) continue;
    const sorted = [...list].sort((a, b) => new Date(a.publishedAt) - new Date(b.publishedAt));
    // 主题落到一级主题：按「该类别在本主题中的占比」选出最能代表该主题的类别，
    // 否则占比最大的科技与产业会把所有主题都吸走。
    const totalByCategory = new Map();
    for (const e of events) totalByCategory.set(e.category, (totalByCategory.get(e.category) ?? 0) + 1);
    const counts = new Map();
    for (const e of sorted) counts.set(e.category, (counts.get(e.category) ?? 0) + 1);
    const topCategory = [...counts.entries()]
      .map(([cat, n]) => [cat, n / (totalByCategory.get(cat) ?? n)])
      .sort((a, b) => b[1] - a[1] || CATEGORY_ORDER.indexOf(a[0]) - CATEGORY_ORDER.indexOf(b[0]))[0][0];
    threads.push({
      // 稳定的脉络 ID：由主题名派生，重跑不变
      id: `cls_thread_${slug(name)}`,
      topicId: CATEGORY_TOPIC[topCategory],
      title: name,
      summary: `${name}：共 ${sorted.length} 条相关电报，按发布时间先后排列。`,
      isDemo: false,
      eventIds: sorted.map((e) => e.id),
      /** 审计字段：主题名与所属类别 */
      _audit: { subjectName: name, topCategory, categoryCounts: Object.fromEntries(counts) },
    });
  }

  return threads
    .sort((a, b) => b.eventIds.length - a.eventIds.length)
    .slice(0, maxThreads)
    .map((th, i) => ({ ...th, id: `cls_thread_${i + 1}_${slug(th.title)}` }));
}

/**
 * 脉络内的事件按「每个自然日每条脉络最多 perDay 条」截断，取重要程度高的。
 * 卡片上仍显示该脉络抓到的全部条数（totalEvents），避免读者以为数据缺失。
 */
export function limitThreadEvents(events, threads, { perDay = 5 } = {}) {
  const byId = new Map(events.map((e) => [e.id, e]));
  return threads.map((th) => {
    const seen = new Set();
    const buckets = new Map();
    for (const id of th.eventIds) {
      const e = byId.get(id);
      if (!e || seen.has(id)) continue;
      seen.add(id);
      const key = dayKeyOf(e.publishedAt);
      if (!buckets.has(key)) buckets.set(key, []);
      buckets.get(key).push(e);
    }
    const kept = [];
    for (const list of buckets.values()) {
      list.sort(
        (a, b) =>
          IMPORTANCE_RANK[a.importance] - IMPORTANCE_RANK[b.importance] ||
          (b._audit?.readingNum ?? 0) - (a._audit?.readingNum ?? 0),
      );
      kept.push(...list.slice(0, perDay));
    }
    kept.sort((a, b) => new Date(a.publishedAt) - new Date(b.publishedAt));
    // totalEvents 计去重后的条数，避免重复 ID 把规模算大
    return { ...th, totalEvents: seen.size, eventIds: kept.map((e) => e.id) };
  });
}

/** 主题名 → ID 片段（保留中文，仅去掉不安全字符） */
function slug(name) {
  return name.replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-|-$/g, '').slice(0, 24);
}

/**
 * 每日快照：每个「展示时区的自然日 × 类别」最多保留 perDayPerCategory 条，
 * 先按重要程度、再按阅读量取前面的，保证时间线在两个月的跨度上依然可用。
 * 落选事件仍保留在 events.json 里，不会丢失。
 */
export function buildSnapshot(events, threads, { perDayPerCategory = 8 } = {}) {
  const buckets = new Map();
  for (const e of events) {
    const key = `${dayKeyOf(e.publishedAt)}|${e.category}`;
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key).push(e);
  }

  const kept = [];
  for (const list of buckets.values()) {
    list.sort(
      (a, b) =>
        IMPORTANCE_RANK[a.importance] - IMPORTANCE_RANK[b.importance] ||
        (b._audit?.readingNum ?? 0) - (a._audit?.readingNum ?? 0),
    );
    kept.push(...list.slice(0, perDayPerCategory));
  }
  kept.sort((a, b) => new Date(a.publishedAt) - new Date(b.publishedAt));

  const keptIds = new Set(kept.map((e) => e.id));
  const visibleThreads = threads
    .map((th) => ({ ...th, eventIds: th.eventIds.filter((id) => keptIds.has(id)) }))
    .filter((th) => th.eventIds.length >= 2);

  const threadByEvent = new Map();
  for (const th of visibleThreads) {
    for (const id of th.eventIds) if (!threadByEvent.has(id)) threadByEvent.set(id, th.id);
  }

  return {
    events: kept,
    threads: visibleThreads,
    // 每条事件挂在第一条（事件数最多的）脉络上；多脉络关系保留在事件文件里
    eventThread: Object.fromEntries(threadByEvent),
  };
}
