import { useMemo } from 'react';
import { t } from '../i18n/strings';
import type { ImportanceLevel, NewsEvent } from '../types';
import { CATEGORY_MAP, NEWS_CATEGORIES } from '../config/categories';
import { formatMonthDay } from '../utils/time';

const DAY_MS = 24 * 60 * 60 * 1000;
const DAYS = 14;
const TICK_H: Record<ImportanceLevel, number> = { high: 56, medium: 32, low: 16 };

const eventMs = (e: NewsEvent) => new Date(e.occurredAt ?? e.publishedAt).getTime();

/**
 * 事件脉搏：对话页空状态的主视觉。
 * 最近 14 天每天一列，每个事件一根刻度（颜色 = 类别，高度 = 重要程度）。
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
    const catOrder = new Map(NEWS_CATEGORIES.map((c, i) => [c.id, i]));
    const cols = Array.from({ length: DAYS }, (_, i) => ({
      ms: start + i * DAY_MS + 1,
      events: [] as NewsEvent[],
    }));
    for (const e of events) {
      const idx = Math.floor((eventMs(e) - start) / DAY_MS);
      if (idx >= 0 && idx < DAYS) cols[idx].events.push(e);
    }
    for (const c of cols) c.events.sort((a, b) => catOrder.get(a.category)! - catOrder.get(b.category)!);
    const recent = events
      .filter((e) => eventMs(e) >= start)
      .sort((a, b) => {
        const rank = (e: NewsEvent) => (e.importance === 'high' ? 0 : e.importance === 'medium' ? 1 : 2);
        return rank(a) - rank(b) || eventMs(b) - eventMs(a);
      })
      .slice(0, 3);
    return { days: cols, highlights: recent };
  }, [events]);

  if (days.length === 0) return null;
  const total = days.reduce((n, d) => n + d.events.length, 0);

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
          <div key={d.ms} className="flex h-24 items-end justify-center gap-[3px] px-px">
            {d.events.map((e, i) => (
              <span
                key={e.id}
                title={e.title}
                className="tick-rise w-1 rounded-t-[1px]"
                style={{
                  height: TICK_H[e.importance ?? 'low'],
                  background: `var(${CATEGORY_MAP[e.category].colorVar})`,
                  animationDelay: `${col * 35 + i * 15}ms`,
                }}
              />
            ))}
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
