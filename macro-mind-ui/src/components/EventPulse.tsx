import { useMemo } from 'react';
import { t } from '../i18n/strings';
import type { NewsCategoryId, NewsEvent } from '../types';
import { CATEGORY_MAP, NEWS_CATEGORIES } from '../config/categories';
import { formatMonthDay } from '../utils/time';

const DAY_MS = 24 * 60 * 60 * 1000;
const DAYS = 14;
/** 最忙的一天占满的高度（与下方容器的 h-24 = 96px 对应） */
const MAX_COL_H = 96;
/** 事件极少的日子也留一点高度，避免看不见 */
const MIN_COL_H = 3;

const eventMs = (e: NewsEvent) => new Date(e.occurredAt ?? e.publishedAt).getTime();

/**
 * 事件脉搏：对话页空状态的主视觉。
 * 最近 14 天每天一根实心柱：高度 = 当天事件量（按最忙的一天归一化），
 * 柱内按类别自下而上堆叠，颜色 = 类别。
 * 下方列出最新的重要事件，可直接加入对话上下文。
 */
export function EventPulse(props: {
  events: NewsEvent[];
  attachedIds: string[];
  onAttach: (e: NewsEvent) => void;
  onOpenTimeline: () => void;
}) {
  const { events, attachedIds, onAttach, onOpenTimeline } = props;

  const { days, highlights } = useMemo(() => {
    if (events.length === 0) return { days: [], highlights: [] };
    const latest = Math.max(...events.map(eventMs));
    const end = new Date(latest);
    end.setHours(23, 59, 59, 999);
    const start = end.getTime() - DAYS * DAY_MS;
    const cols = Array.from({ length: DAYS }, (_, i) => ({
      ms: start + i * DAY_MS + 1,
      counts: new Map<NewsCategoryId, number>(),
    }));
    for (const e of events) {
      const idx = Math.floor((eventMs(e) - start) / DAY_MS);
      if (idx >= 0 && idx < DAYS) {
        const c = cols[idx].counts;
        c.set(e.category, (c.get(e.category) ?? 0) + 1);
      }
    }
    const totals = cols.map((c) => [...c.counts.values()].reduce((a, b) => a + b, 0));
    const busiest = Math.max(1, ...totals);
    const days = cols.map((c, i) => ({
      ms: c.ms,
      /** 柱高按当天事件量归一化 */
      height: Math.max(MIN_COL_H, Math.round((totals[i] / busiest) * MAX_COL_H)),
      /** 柱内分段：按类别顺序自下而上，段高由 flex-grow 按条数分配 */
      segments: NEWS_CATEGORIES.filter((cat) => c.counts.has(cat.id)).map((cat) => ({
        id: cat.id,
        count: c.counts.get(cat.id)!,
        label: cat.label,
        colorVar: cat.colorVar,
      })),
    }));
    const recent = events
      .filter((e) => eventMs(e) >= start)
      .sort((a, b) => {
        const rank = (e: NewsEvent) => (e.importance === 'high' ? 0 : e.importance === 'medium' ? 1 : 2);
        return rank(a) - rank(b) || eventMs(b) - eventMs(a);
      })
      .slice(0, 3);
    return { days, highlights: recent };
  }, [events]);

  if (days.length === 0) return null;
  const total = days.reduce((n, d) => n + d.segments.reduce((m, s) => m + s.count, 0), 0);

  return (
    <section aria-label={t.pulse.title} className="w-full">
      <div className="mb-3 flex items-baseline justify-between gap-3">
        <h2 className="text-sm font-semibold text-[var(--text)]">{t.pulse.title}</h2>
        <button
          onClick={onOpenTimeline}
          className="text-xs text-[var(--text-muted)] underline-offset-4 hover:text-[var(--accent-text)] hover:underline"
        >
          {t.pulse.summary(total)}
        </button>
      </div>

      {/* 刻度带：纯展示，用 aria-hidden，可访问信息由下方列表与摘要提供 */}
      <div aria-hidden className="grid grid-cols-[repeat(14,minmax(0,1fr))] gap-1 border-b border-[var(--border-strong)]">
        {days.map((d, col) => (
          // 每天一根实心柱：柱高 = 当天事件量，柱内按类别堆叠。
          // 不用「一个事件一根固定宽度刻度」——每列只有约 40px，一天几十条时
          // 刻度会被 flex 压成 0 宽而整列消失。详见《UI问题清单.md》#7。
          // 柱宽上限 24px（不填满槽位，留白让画面透气）；段间 2px 表面间隙分隔，
          // 不描边；顶端 4px 圆角、底部与基线齐平。
          <div key={d.ms} className="flex h-24 items-end justify-center px-px">
            <div
              className="tick-rise flex w-full max-w-6 flex-col-reverse gap-[2px] overflow-hidden rounded-t-[4px]"
              style={{ height: d.height, animationDelay: `${col * 35}ms` }}
            >
              {d.segments.map((s) => (
                <span
                  key={s.id}
                  title={`${s.label} ${s.count} 条`}
                  style={{ flexGrow: s.count, flexBasis: 0, background: `var(${s.colorVar})` }}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
      <div aria-hidden className="mt-1 grid grid-cols-[repeat(14,minmax(0,1fr))] gap-1 text-center text-[10px] tabular-nums text-[var(--text-muted)]">
        {days.map((d, i) => (
          // 窄屏隔天显示，从最新一天往回数，保证最新日期总在
          <span key={d.ms} className={(DAYS - 1 - i) % 2 === 1 ? 'invisible sm:visible' : ''}>
            {formatMonthDay(d.ms)}
          </span>
        ))}
      </div>

      {/* 类别图例：8 个系列不能只靠颜色识别（浅色模式下部分类别色对表面的
          对比度低于 3:1），图例是可依赖的识别通道，始终显示。 */}
      <ul className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-[var(--text-muted)]">
        {NEWS_CATEGORIES.map((c) => (
          <li key={c.id} className="flex items-center gap-1.5">
            <span aria-hidden className="h-2 w-2 rounded-[2px]" style={{ background: `var(${c.colorVar})` }} />
            {c.label}
          </li>
        ))}
      </ul>

      <ul className="mt-5 divide-y divide-[var(--border)] border-y border-[var(--border)]">
        {highlights.map((e) => {
          const attached = attachedIds.includes(e.id);
          return (
            <li key={e.id} className="flex items-center gap-3 py-2.5">
              <span
                aria-hidden
                className="h-3.5 w-[3px] shrink-0 rounded-full"
                style={{ background: `var(${CATEGORY_MAP[e.category].colorVar})` }}
              />
              <span className="shrink-0 text-xs tabular-nums text-[var(--text-muted)]">
                {formatMonthDay(eventMs(e))}
              </span>
              <span className="min-w-0 flex-1 truncate text-left text-sm text-[var(--text-secondary)]" title={e.title}>
                {e.title}
              </span>
              <button
                onClick={() => onAttach(e)}
                disabled={attached}
                aria-label={`${attached ? t.pulse.attached : t.pulse.attach}：${e.title}`}
                className="shrink-0 rounded-md px-2 py-0.5 text-xs text-[var(--accent-text)] hover:bg-[var(--accent-soft)] disabled:text-[var(--text-muted)] disabled:hover:bg-transparent"
              >
                {attached ? t.pulse.attached : t.pulse.attach}
              </button>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
