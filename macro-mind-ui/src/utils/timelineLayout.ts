import type { EventThread, NewsCategoryId, NewsEvent, TimelineFilters, TopicId } from '../types';

/**
 * 时间线筛选、分组与画廊组织逻辑（纯函数，与展示组件分离）。
 * 日期按展示时区（Asia/Shanghai，UTC+8，无夏令时）的自然日划分。
 */

export const DAY_MS = 24 * 3600 * 1000;
const TZ_OFFSET_MS = 8 * 3600 * 1000;

/** 事件用于时间线定位的时间：优先发生时间，未知时用发布时间 */
export function eventTimeMs(e: NewsEvent): number {
  return new Date(e.occurredAt ?? e.publishedAt).getTime();
}

/** 某时刻所在展示时区自然日的 0 点（毫秒） */
export function dayStartMs(ms: number): number {
  return Math.floor((ms + TZ_OFFSET_MS) / DAY_MS) * DAY_MS - TZ_OFFSET_MS;
}

/** 展示时区日期键 YYYY-MM-DD（用作分组与锚点 ID） */
export function dayKey(ms: number): string {
  return new Date(dayStartMs(ms) + TZ_OFFSET_MS).toISOString().slice(0, 10);
}

export function applyFilters(events: NewsEvent[], f: TimelineFilters): NewsEvent[] {
  const kw = f.keyword.trim().toLowerCase();
  const fromMs = f.dateFrom ? new Date(`${f.dateFrom}T00:00:00+08:00`).getTime() : -Infinity;
  // dateTo 含端点：加一天
  const toMs = f.dateTo ? new Date(`${f.dateTo}T00:00:00+08:00`).getTime() + DAY_MS : Infinity;

  return events.filter((e) => {
    if (f.categories.length > 0 && !f.categories.includes(e.category)) return false;
    if (f.regions.length > 0 && !f.regions.includes(e.region)) return false;
    if (f.importance.length > 0) {
      if (!e.importance || !f.importance.includes(e.importance)) return false;
    }
    const t = eventTimeMs(e);
    if (t < fromMs || t >= toMs) return false;
    if (kw) {
      const hay = `${e.title} ${e.summary} ${(e.entities ?? []).join(' ')}`.toLowerCase();
      if (!hay.includes(kw)) return false;
    }
    return true;
  });
}

export interface DayGroup {
  key: string;
  startMs: number;
  events: NewsEvent[];
}

/**
 * 按自然日分组；只包含有事件的日期。
 * order='asc'（默认）：最早在上，适合按顺序阅读一条脉络；'desc'：最新在上。
 */
export function groupByDay(events: NewsEvent[], order: 'asc' | 'desc' = 'asc'): DayGroup[] {
  const map = new Map<string, DayGroup>();
  const sign = order === 'asc' ? 1 : -1;
  const sorted = [...events].sort((a, b) => sign * (eventTimeMs(a) - eventTimeMs(b)));
  for (const e of sorted) {
    const ms = eventTimeMs(e);
    const key = dayKey(ms);
    let g = map.get(key);
    if (!g) {
      g = { key, startMs: dayStartMs(ms), events: [] };
      map.set(key, g);
    }
    g.events.push(e);
  }
  return [...map.values()];
}

// ---------------- 画廊：脉络卡片 ----------------

/** 零散事件卡片的 ID 前缀（未归入任何脉络的事件按主题聚成一张卡片） */
export const LOOSE_PREFIX = 'loose:';

export interface ThreadCard {
  /** 脉络 ID；零散事件为 `loose:<topicId>` */
  id: string;
  topicId: TopicId;
  /** 配置中的标题；零散事件或配置缺失时为 null，由界面给出兜底文案 */
  title: string | null;
  summary: string | null;
  /** 该脉络抓取到的全部条数（快照只保留抽样，界面据此说明） */
  totalEvents: number | null;
  isLoose: boolean;
  /** 卡片内事件，按时间正序 */
  events: NewsEvent[];
  startMs: number;
  endMs: number;
}

/**
 * 把（已筛选的）事件组织为画廊卡片：
 * - 有 threadId 的事件按脉络归组；脉络元数据来自 threads 配置，缺失时用首个事件兜底。
 * - 无 threadId 的事件按类别所属主题聚成「零散事件」卡片。
 * - 没有事件的脉络不出卡片；卡片按最近一次事件时间倒序（最近有动态的在前），零散卡片排在最后。
 */
export function buildThreadCards(
  events: NewsEvent[],
  threads: EventThread[],
  categoryTopic: Record<NewsCategoryId, TopicId>,
): ThreadCard[] {
  const meta = new Map(threads.map((t) => [t.id, t]));
  const groups = new Map<string, NewsEvent[]>();
  for (const e of events) {
    const id = e.threadId ?? `${LOOSE_PREFIX}${categoryTopic[e.category]}`;
    const list = groups.get(id);
    if (list) list.push(e);
    else groups.set(id, [e]);
  }

  const cards: ThreadCard[] = [];
  for (const [id, list] of groups) {
    const sorted = [...list].sort((a, b) => eventTimeMs(a) - eventTimeMs(b));
    const isLoose = id.startsWith(LOOSE_PREFIX);
    const m = isLoose ? undefined : meta.get(id);
    cards.push({
      id,
      topicId: isLoose
        ? (id.slice(LOOSE_PREFIX.length) as TopicId)
        : (m?.topicId ?? categoryTopic[sorted[0].category]),
      title: m?.title ?? (isLoose ? null : sorted[0].title),
      summary: m?.summary ?? null,
      totalEvents: m?.totalEvents ?? null,
      isLoose,
      events: sorted,
      startMs: eventTimeMs(sorted[0]),
      endMs: eventTimeMs(sorted[sorted.length - 1]),
    });
  }
  return cards.sort((a, b) => Number(a.isLoose) - Number(b.isLoose) || b.endMs - a.endMs);
}

/**
 * 缩略线上的避让：位置（0–1，已排序）相距小于 minGap 的点放到更高一层，
 * 贪心分配最低可用层。返回每个点的层号（0 = 线上）。
 */
export function stripLanes(positions: number[], minGap: number, maxLanes = 3): number[] {
  const lastInLane: number[] = [];
  return positions.map((p) => {
    let lane = lastInLane.findIndex((last) => p - last >= minGap);
    if (lane === -1) lane = lastInLane.length < maxLanes ? lastInLane.length : maxLanes - 1;
    lastInLane[lane] = p;
    return lane;
  });
}

/** 脉络缩略线上的位置（0–1）：按真实时间比例；单个事件或零时长居中 */
export function stripPosition(ms: number, startMs: number, endMs: number): number {
  if (endMs <= startMs) return 0.5;
  return (ms - startMs) / (endMs - startMs);
}
