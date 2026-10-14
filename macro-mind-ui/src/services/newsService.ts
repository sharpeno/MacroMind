import type { EventThread, NewsEvent } from '../types';
import { DEMO_EVENTS, DEMO_THREADS, DEMO_DATA_UPDATED_AT } from './demoEvents';

/** 数据来源：本地服务 / 随前端发布的静态快照 / 明确虚构的演示数据 */
export type NewsSourceKind = 'server' | 'snapshot' | 'demo';

export interface NewsPayload {
  events: NewsEvent[];
  /** 事件脉络元数据（画廊卡片的标题与说明） */
  threads: EventThread[];
  updatedAt: string;
  isDemo: boolean;
  source: NewsSourceKind;
  /** 抓取来源说明（server / snapshot 来自财联社时给出） */
  sourceLabel?: string;
  /** 数据覆盖范围 */
  coverage?: { from: string; to: string };
  /** 已抓取到的全部事件数（展示快照会按每日每类别截断） */
  total?: number;
  /** 事件正文未经独立核实 */
  epistemicStatus?: string;
}

/**
 * 新闻服务适配层。
 * - ServerNewsService：本地服务 /api/news（由 server/news 从财联社电报生成）
 * - SnapshotNewsService：随前端构建发布的 public/news.snapshot.json（未启动服务时用）
 * - DemoNewsService：固定且明确虚构的演示数据（两者都拿不到时才用）
 */
export interface NewsService {
  fetchEvents(): Promise<NewsPayload>;
}

/** 静态快照路径（public/news.snapshot.json → 构建后位于站点根目录） */
export const SNAPSHOT_URL = `${import.meta.env.BASE_URL ?? '/'}news.snapshot.json`.replace('//', '/');

function normalize(
  body: Partial<NewsPayload> & { events?: NewsEvent[] },
  source: NewsSourceKind,
): NewsPayload {
  return {
    events: body.events ?? [],
    threads: body.threads ?? [],
    updatedAt: body.updatedAt ?? new Date().toISOString(),
    isDemo: false,
    source,
    sourceLabel: body.sourceLabel,
    coverage: body.coverage,
    total: body.total,
    epistemicStatus: body.epistemicStatus,
  };
}

export class DemoNewsService implements NewsService {
  async fetchEvents(): Promise<NewsPayload> {
    return {
      events: DEMO_EVENTS,
      threads: DEMO_THREADS,
      updatedAt: DEMO_DATA_UPDATED_AT,
      isDemo: true,
      source: 'demo',
    };
  }
}

/** 本地服务 /api/news（真实抓取数据，附审计与覆盖范围） */
export class ServerNewsService implements NewsService {
  async fetchEvents(): Promise<NewsPayload> {
    const res = await fetch('/api/news');
    if (!res.ok) throw new Error(`GET /api/news ${res.status}`);
    const body = (await res.json()) as Partial<NewsPayload>;
    if (!body.events || body.events.length === 0) throw new Error('快照为空');
    return normalize(body, 'server');
  }
}

/** 随前端发布的静态快照：不启动本地服务也能看到真实数据 */
export class SnapshotNewsService implements NewsService {
  async fetchEvents(): Promise<NewsPayload> {
    const res = await fetch(SNAPSHOT_URL);
    if (!res.ok) throw new Error(`GET ${SNAPSHOT_URL} ${res.status}`);
    const body = (await res.json()) as Partial<NewsPayload>;
    if (!body.events || body.events.length === 0) throw new Error('快照为空');
    return normalize(body, 'snapshot');
  }
}

/**
 * 按优先级取第一个可用的数据源：本地服务 → 静态快照 → 演示数据。
 * 返回结果带上 source，界面据此说明数据来自哪里。
 */
export async function loadNews(services: NewsService[] = [
  new ServerNewsService(),
  new SnapshotNewsService(),
  new DemoNewsService(),
]): Promise<NewsPayload> {
  for (const service of services) {
    try {
      return await service.fetchEvents();
    } catch {
      /* 换下一个来源 */
    }
  }
  // 正常情况下不会走到这里（演示服务不会失败）
  return new DemoNewsService().fetchEvents();
}

/** 兼容旧名：本地服务适配器 */
export const ProxyNewsService = ServerNewsService;
