import { describe, expect, it } from 'vitest';
import type { EventThread, NewsEvent, TimelineFilters } from '../types';
import { CATEGORY_TOPIC } from '../config/topics';
import {
  applyFilters,
  buildThreadCards,
  dayKey,
  eventTimeMs,
  groupByDay,
  LOOSE_PREFIX,
  stripLanes,
  stripPosition,
} from './timelineLayout';

const base: Omit<NewsEvent, 'id' | 'occurredAt' | 'publishedAt'> = {
  occurredAtPrecision: 'exact',
  category: 'monetary_policy',
  region: 'us',
  title: '测试事件',
  summary: '摘要',
  sources: [{ name: '来源' }],
  isDemo: true,
};

function ev(id: string, iso: string, patch: Partial<NewsEvent> = {}): NewsEvent {
  return { ...base, id, occurredAt: iso, publishedAt: iso, ...patch };
}

const EMPTY: TimelineFilters = {
  categories: [],
  regions: [],
  importance: [],
  keyword: '',
  dateFrom: null,
  dateTo: null,
};

describe('eventTimeMs', () => {
  it('优先使用发生时间，未知时回退发布时间', () => {
    const withOccurred = ev('a', '2025-10-01T00:00:00Z');
    expect(eventTimeMs(withOccurred)).toBe(Date.parse('2025-10-01T00:00:00Z'));
    const unknown: NewsEvent = {
      ...base,
      id: 'b',
      occurredAt: null,
      occurredAtPrecision: 'unknown',
      publishedAt: '2025-10-02T12:00:00Z',
    };
    expect(eventTimeMs(unknown)).toBe(Date.parse('2025-10-02T12:00:00Z'));
  });
});

describe('dayKey', () => {
  it('按 Asia/Shanghai 自然日划分（UTC 16:00 即次日 0 点）', () => {
    expect(dayKey(Date.parse('2025-10-01T15:59:00Z'))).toBe('2025-10-01');
    expect(dayKey(Date.parse('2025-10-01T16:00:00Z'))).toBe('2025-10-02');
  });
});

describe('applyFilters', () => {
  const events = [
    ev('a', '2025-10-01T00:00:00Z', { importance: 'high' }),
    ev('b', '2025-10-05T00:00:00Z', { category: 'tech_industry', region: 'cn', title: '芯片补贴' }),
    ev('c', '2025-10-09T00:00:00Z'),
  ];

  it('空筛选返回全部', () => {
    expect(applyFilters(events, EMPTY)).toHaveLength(3);
  });

  it('按类别筛选', () => {
    const got = applyFilters(events, { ...EMPTY, categories: ['tech_industry'] });
    expect(got.map((e) => e.id)).toEqual(['b']);
  });

  it('按重要程度筛选时，缺失 importance 的事件被排除', () => {
    const got = applyFilters(events, { ...EMPTY, importance: ['high'] });
    expect(got.map((e) => e.id)).toEqual(['a']);
  });

  it('关键词命中标题', () => {
    const got = applyFilters(events, { ...EMPTY, keyword: '芯片' });
    expect(got.map((e) => e.id)).toEqual(['b']);
  });

  it('日期范围（Asia/Shanghai，含端点）', () => {
    const got = applyFilters(events, { ...EMPTY, dateFrom: '2025-10-04', dateTo: '2025-10-05' });
    expect(got.map((e) => e.id)).toEqual(['b']);
  });

  it('可产生空结果', () => {
    const got = applyFilters(events, { ...EMPTY, regions: ['jp'], importance: ['high'] });
    expect(got).toHaveLength(0);
  });
});

describe('groupByDay', () => {
  const events = [
    ev('a', '2025-10-01T02:00:00Z'),
    ev('b', '2025-10-03T09:00:00Z'),
    ev('c', '2025-10-01T08:00:00Z'),
    ev('d', '2025-10-03T01:00:00Z'),
  ];

  it('默认正序：日期与日内事件均为最早在上，不依赖输入顺序', () => {
    const shuffled = [events[3], events[0], events[2], events[1]];
    const groups = groupByDay(shuffled);
    expect(groups.map((g) => g.key)).toEqual(['2025-10-01', '2025-10-03']);
    expect(groups.map((g) => g.events.map((e) => e.id))).toEqual([
      ['a', 'c'],
      ['d', 'b'],
    ]);
  });

  it('desc：最新在上', () => {
    expect(groupByDay(events, 'desc').map((g) => g.events.map((e) => e.id))).toEqual([
      ['b', 'd'],
      ['c', 'a'],
    ]);
  });

  it('空输入返回空', () => {
    expect(groupByDay([])).toEqual([]);
  });
});

describe('buildThreadCards', () => {
  const threads: EventThread[] = [
    { id: 'th1', topicId: 'policy', title: '脉络一', summary: '说明一', isDemo: true },
    { id: 'th_old', topicId: 'markets', title: '旧脉络', summary: '说明', isDemo: true },
  ];
  const events = [
    ev('a', '2025-10-05T00:00:00Z', { threadId: 'th1' }),
    ev('b', '2025-10-01T00:00:00Z', { threadId: 'th1' }),
    ev('c', '2025-09-20T00:00:00Z', { threadId: 'th_old' }),
    ev('d', '2025-10-08T00:00:00Z', { threadId: 'th_unknown', title: '未配置脉络的首个事件' }),
    ev('e', '2025-10-09T00:00:00Z', { category: 'energy_commodities' }),
    ev('f', '2025-10-02T00:00:00Z', { category: 'financial_markets' }),
  ];
  const cards = buildThreadCards(events, threads, CATEGORY_TOPIC);
  const byId = Object.fromEntries(cards.map((c) => [c.id, c]));

  it('按 threadId 归组，卡片内事件按时间正序，并带起止时间', () => {
    expect(byId.th1.events.map((e) => e.id)).toEqual(['b', 'a']);
    expect(byId.th1.title).toBe('脉络一');
    expect(byId.th1.startMs).toBe(eventTimeMs(events[1]));
    expect(byId.th1.endMs).toBe(eventTimeMs(events[0]));
  });

  it('未配置的脉络用首个事件标题兜底，主题按类别映射', () => {
    expect(byId.th_unknown.title).toBe('未配置脉络的首个事件');
    expect(byId.th_unknown.topicId).toBe('policy');
  });

  it('无 threadId 的事件按主题聚成零散卡片', () => {
    const loose = byId[`${LOOSE_PREFIX}markets`];
    expect(loose.isLoose).toBe(true);
    expect(loose.title).toBeNull();
    expect(loose.events.map((e) => e.id)).toEqual(['f', 'e']);
  });

  it('按最近一次事件倒序，零散卡片排在最后', () => {
    expect(cards.map((c) => c.id)).toEqual(['th_unknown', 'th1', 'th_old', `${LOOSE_PREFIX}markets`]);
  });

  it('筛选后没有事件的脉络不出卡片', () => {
    expect(buildThreadCards(events.slice(0, 2), threads, CATEGORY_TOPIC).map((c) => c.id)).toEqual(['th1']);
  });
});

describe('stripPosition / stripLanes', () => {
  it('按真实时间比例定位，零时长居中', () => {
    expect(stripPosition(150, 100, 200)).toBe(0.5);
    expect(stripPosition(100, 100, 100)).toBe(0.5);
  });

  it('相距过近的点抬到上层，有空位时回到底层', () => {
    expect(stripLanes([0, 0.01, 0.02, 0.5, 0.51], 0.05)).toEqual([0, 1, 2, 0, 1]);
  });

  it('层数有上限', () => {
    expect(stripLanes([0, 0, 0, 0], 0.05, 2)).toEqual([0, 1, 1, 1]);
  });
});
