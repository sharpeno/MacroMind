// 事件生成、脉络归组与每日快照截断的回归测试。
import { describe, expect, it } from 'vitest';
import { buildSnapshot, buildThreads, dayKeyOf, limitThreadEvents, toEvent, toEvents } from './pipeline.mjs';

const raw = (patch = {}) => ({
  id: 1000,
  ctime: 1791900000, // 2026-10-13 21:20 +08:00
  content: '财联社10月13日电，美国8月CPI同比增长3.4%。',
  level: 'C',
  subjects: [],
  stock_list: [],
  ...patch,
});

describe('toEvent', () => {
  it('采纳命中的电报，并保留来源链接与发布时间', () => {
    const e = toEvent(raw());
    expect(e.category).toBe('inflation_employment');
    expect(e.isDemo).toBe(false);
    expect(e.sources[0].url).toBe('https://www.cls.cn/detail/1000');
    expect(e.publishedAt).toBe(new Date(1791900000 * 1000).toISOString());
  });

  it('事件发生时间未知时不做猜测：occurredAt 为空、精度为 unknown', () => {
    const e = toEvent(raw());
    expect(e.occurredAtPrecision).toBe('unknown');
    expect(e.occurredAt).not.toBeNull();
  });

  it('栏目稿与未命中类别的电报不产生事件', () => {
    expect(toEvent(raw({ subjects: [{ subject_name: '提醒电报' }] }))).toBeNull();
    expect(toEvent(raw({ content: '财联社10月13日电，某地举办社区活动。' }))).toBeNull();
  });

  it('保留正文原文，并把媒体报道归入「明确归属的主张」', () => {
    const e = toEvent(raw({ content: '财联社10月13日电，据报道，鲍威尔表示通胀仍具粘性。' }));
    expect(e.body).toContain('鲍威尔表示');
    expect(e.attributedClaims?.[0]?.attribution).toContain('鲍威尔');
    // 真实新闻不写 Agent 解释，避免把生成的解读混入事实层
    expect(e.agentInterpretation).toBeUndefined();
  });
});

describe('toEvents', () => {
  it('按时间正序输出，且同 ID 只出现一次', () => {
    const items = [
      raw({ id: 3, ctime: 1791900600 }),
      raw({ id: 1, ctime: 1791900000 }),
      raw({ id: 3, ctime: 1791900600 }),
    ];
    const events = toEvents(items);
    expect(events.map((e) => e.id)).toEqual(['cls_1', 'cls_3']);
  });
});

describe('buildThreads', () => {
  it('把出现两次以上的真实主题归成脉络，事件数不足的不成脉络', () => {
    const items = [
      raw({ id: 1, subjects: [{ subject_name: '中东冲突' }] }),
      raw({ id: 2, subjects: [{ subject_name: '中东冲突' }] }),
      raw({ id: 3, subjects: [{ subject_name: '天气变化' }] }),
    ];
    const events = toEvents(items);
    const threads = buildThreads(events, items);
    expect(threads).toHaveLength(1);
    expect(threads[0].title).toBe('中东冲突');
    expect(threads[0].eventIds).toHaveLength(2);
    expect(threads[0].isDemo).toBe(false);
  });

  it('通用栏目 subject 不会成为脉络', () => {
    const items = [
      raw({ id: 1, subjects: [{ subject_name: '环球市场情报' }] }),
      raw({ id: 2, subjects: [{ subject_name: '环球市场情报' }] }),
    ];
    expect(buildThreads(toEvents(items), items)).toHaveLength(0);
  });

  it('脉络按占比归入一级主题，而不是被事件最多的类别吸走', () => {
    // 中东冲突主题里的事件多归到贸易与地缘政治；同时存在大量科技类事件
    const items = [
      raw({ id: 1, subjects: [{ subject_name: '中东冲突' }], content: '财联社10月13日电，以军空袭加沙，哈马斯回应。' }),
      raw({ id: 2, subjects: [{ subject_name: '中东冲突' }], content: '财联社10月13日电，伊朗与以色列局势升级，外交斡旋继续。' }),
      ...Array.from({ length: 40 }, (_, i) =>
        raw({ id: 100 + i, content: '财联社10月13日电，某公司发布AI大模型与芯片新品。' }),
      ),
    ];
    const threads = buildThreads(toEvents(items), items);
    expect(threads[0].topicId).toBe('trade_industry');
    expect(threads[0].title).toBe('中东冲突');
  });

  it('脉络 ID 稳定：同一输入重跑得到同一 ID', () => {
    const items = [
      raw({ id: 1, subjects: [{ subject_name: '中东冲突' }] }),
      raw({ id: 2, subjects: [{ subject_name: '中东冲突' }] }),
    ];
    const a = buildThreads(toEvents(items), items)[0].id;
    const b = buildThreads(toEvents(items), items)[0].id;
    expect(a).toBe(b);
  });
});

describe('dayKeyOf', () => {
  it('按 Asia/Shanghai 自然日划分（UTC 晚间算次日）', () => {
    // 2026-10-13T16:30Z = 2026-10-14 00:30 +08:00
    expect(dayKeyOf('2026-10-13T16:30:00.000Z')).toBe('2026-10-14');
    expect(dayKeyOf('2026-10-13T15:30:00.000Z')).toBe('2026-10-13');
  });
});

describe('buildSnapshot', () => {
  const many = (dayIso, category, n) =>
    Array.from({ length: n }, (_, i) => ({
      id: `e_${dayIso}_${category}_${i}`,
      publishedAt: dayIso,
      occurredAt: dayIso,
      occurredAtPrecision: 'unknown',
      category,
      region: 'us',
      title: `事件 ${i}`,
      summary: '摘要',
      sources: [{ name: '财联社电报', url: 'https://www.cls.cn/detail/1' }],
      importance: i % 3 === 0 ? 'high' : 'low',
      isDemo: false,
      _audit: { readingNum: i },
    }));

  it('每个自然日每类别最多保留 8 条，优先重要程度与阅读量', () => {
    const events = many('2026-10-13T02:00:00.000Z', 'financial_markets', 20);
    const { events: kept } = buildSnapshot(events, [], { perDayPerCategory: 8 });
    expect(kept).toHaveLength(8);
    // 高重要度的（20 条里 7 条）优先保留，剩下的名额给低重要度中阅读量最高的
    expect(kept.filter((e) => e.importance === 'high')).toHaveLength(7);
    expect(kept.filter((e) => e.importance === 'low')).toHaveLength(1);
  });

  it('不同日期的同类事件互不影响', () => {
    const events = [
      ...many('2026-10-12T02:00:00.000Z', 'financial_markets', 10),
      ...many('2026-10-13T02:00:00.000Z', 'financial_markets', 10),
    ];
    const { events: kept } = buildSnapshot(events, [], { perDayPerCategory: 8 });
    expect(kept).toHaveLength(16);
  });

  it('只保留至少两条事件的脉络，并为事件标出所属脉络', () => {
    const events = [
      ...many('2026-10-13T02:00:00.000Z', 'trade_geopolitics', 3),
      ...many('2026-10-14T02:00:00.000Z', 'trade_geopolitics', 3),
    ];
    const threads = [
      { id: 't1', topicId: 'trade_industry', title: '中东冲突', summary: '', isDemo: false, eventIds: [events[0].id, events[1].id] },
      { id: 't2', topicId: 'trade_industry', title: '单一事件脉络', summary: '', isDemo: false, eventIds: [events[2].id] },
    ];
    const snap = buildSnapshot(events, threads, { perDayPerCategory: 8 });
    expect(snap.threads.map((t) => t.id)).toEqual(['t1']);
    expect(snap.eventThread[events[0].id]).toBe('t1');
    expect(snap.eventThread[events[2].id]).toBeUndefined();
  });
});

describe('limitThreadEvents', () => {
  const ev = (id, iso, importance = 'low', reading = 0) => ({
    id,
    publishedAt: iso,
    occurredAt: iso,
    occurredAtPrecision: 'unknown',
    category: 'trade_geopolitics',
    region: 'us',
    title: id,
    summary: '',
    sources: [],
    importance,
    isDemo: false,
    _audit: { readingNum: reading },
  });

  it('同一天内每条脉络最多保留 perDay 条，优先重要程度', () => {
    const events = [
      ev('a', '2026-10-13T02:00:00.000Z', 'low', 10),
      ev('b', '2026-10-13T03:00:00.000Z', 'high', 1),
      ev('c', '2026-10-13T04:00:00.000Z', 'low', 99),
      ev('d', '2026-10-14T02:00:00.000Z', 'low', 1),
    ];
    const [th] = limitThreadEvents(events, [
      { id: 't1', eventIds: events.map((e) => e.id), title: 'T', topicId: 'trade_industry' },
    ], { perDay: 2 });
    expect(th.eventIds).toEqual(['b', 'c', 'd']); // 10-13 保留重要度高的 b 与阅读量高的 c
    expect(th.totalEvents).toBe(4);
  });

  it('重复 ID 只保留一次', () => {
    const events = [ev('a', '2026-10-13T02:00:00.000Z')];
    const [th] = limitThreadEvents(events, [{ id: 't1', eventIds: ['a', 'a'], title: 'T', topicId: 'trade_industry' }]);
    expect(th.eventIds).toEqual(['a']);
    expect(th.totalEvents).toBe(1);
  });
});
