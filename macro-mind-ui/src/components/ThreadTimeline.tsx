import { useEffect, useMemo, useRef } from 'react';
import { t } from '../i18n/strings';
import { CATEGORY_MAP } from '../config/categories';
import { TOPIC_MAP } from '../config/topics';
import type { ImportanceLevel, NewsEvent } from '../types';
import type { UseTimelineResult } from '../hooks/useTimeline';
import { DAY_MS, eventTimeMs, groupByDay, type ThreadCard } from '../utils/timelineLayout';
import { formatDayHeading, formatSpan, formatTime } from '../utils/time';
import { ThreadStrip } from './ThreadStrip';
import { cardTitle } from '../utils/threadText';

const DOT_SIZE: Record<ImportanceLevel, number> = { high: 12, medium: 9, low: 7 };

const prefersReducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/** 单条事件：书脊上的圆点 + 右侧条目。整条可点开事件详情。 */
function EventEntry(props: { event: NewsEvent; selected: boolean; onSelect: (id: string) => void }) {
  const { event, selected, onSelect } = props;
  const cat = CATEGORY_MAP[event.category];
  const color = `var(${cat.colorVar})`;
  const imp = event.importance ?? 'low';
  const size = DOT_SIZE[imp];
  const timeLabel =
    event.occurredAt === null
      ? t.timeline.occurredUnknown
      : event.occurredAtPrecision === 'date_only'
        ? '全天'
        : formatTime(eventTimeMs(event));
  const title = event.title.replace(/^【演示】/, '');

  return (
    <li className="relative">
      {/* 书脊圆点：高重要度实心，其余空心描边 */}
      <span
        aria-hidden
        className="absolute top-[13px] -translate-x-1/2 rounded-full"
        style={{
          left: 0,
          width: size,
          height: size,
          background: imp === 'high' ? color : 'var(--bg)',
          boxShadow: `0 0 0 ${imp === 'high' ? 3 : 2}px ${imp === 'high' ? 'var(--bg)' : color}`,
        }}
      />
      <button
        onClick={() => onSelect(event.id)}
        aria-pressed={selected}
        aria-label={`${title}，${t.timeline.openDetail}`}
        data-event-id={event.id}
        className={`ml-5 block w-[calc(100%-1.25rem)] rounded-lg border px-4 py-3 text-left transition-colors ${
          selected
            ? 'border-[var(--accent)] bg-[var(--accent-soft)]'
            : 'border-transparent hover:border-[var(--border)] hover:bg-[var(--bg-panel)]'
        }`}
      >
        <div className="flex flex-wrap items-baseline gap-x-2.5 gap-y-0.5 text-xs">
          <time className="tabular-nums text-[var(--text-muted)]">{timeLabel}</time>
          <span style={{ color }}>{cat.label}</span>
          <span className="text-[var(--text-muted)]">{t.timeline.regions[event.region]}</span>
        </div>
        <h3
          className={`mt-1 leading-snug text-[var(--text)] ${
            imp === 'high' ? 'text-lg font-semibold' : imp === 'medium' ? 'text-base font-medium' : 'text-[15px]'
          }`}
        >
          {title}
        </h3>
        <p className="mt-1.5 max-w-[66ch] text-[13px] leading-relaxed text-[var(--text-secondary)]">
          {event.summary}
        </p>
        <div className="mt-2 text-[11px] text-[var(--text-muted)]">{t.timeline.sourcesCount(event.sources.length)}</div>
      </button>
    </li>
  );
}

/**
 * 单条脉络的时间线（点开画廊卡片后的页面），占据几乎整个面板：
 * - 头部：返回、主题、标题、说明、事件数与时间跨度，以及可点击的时间分布缩略线。
 * - 主体：按发生时间先后排列（最早在上），按自然日分组；日期之间标出间隔天数。
 * - 点击事件打开事件详情面板。
 */
export function ThreadTimeline(props: {
  tl: UseTimelineResult;
  card: ThreadCard | null;
  dataStatus: { isDemo: boolean; label: string };
}) {
  const { tl, card, dataStatus } = props;
  const { selectedEventId, setSelectedEventId } = tl;
  const scrollRef = useRef<HTMLDivElement>(null);
  const backRef = useRef<HTMLButtonElement>(null);

  const groups = useMemo(() => (card ? groupByDay(card.events, 'asc') : []), [card]);

  // 进入脉络页：回到顶部，焦点放在返回按钮上
  const cardId = card?.id;
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: 0 });
    backRef.current?.focus();
  }, [cardId]);

  // 选中事件（含从缩略线点选）时，把对应条目滚入视野
  useEffect(() => {
    if (!selectedEventId) return;
    const node = scrollRef.current?.querySelector(`[data-event-id="${selectedEventId}"]`);
    node?.scrollIntoView({ block: 'nearest', behavior: prefersReducedMotion() ? 'auto' : 'smooth' });
  }, [selectedEventId]);

  const back = (
    <button
      ref={backRef}
      onClick={() => tl.setOpenThreadId(null)}
      className="rounded-md px-2 py-1 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
    >
      ← {t.timeline.back}
    </button>
  );

  // 筛选条件使这条脉络没有事件
  if (!card) {
    return (
      <div className="flex h-full flex-col">
        <div className="px-4 pt-4 sm:px-8">{back}</div>
        <div className="flex flex-1 flex-col items-center justify-center gap-2 px-4 text-center">
          <p className="text-sm text-[var(--text-secondary)]">{t.timeline.emptyFiltered}</p>
          <p className="text-xs text-[var(--text-muted)]">{t.timeline.emptyFilteredHint}</p>
          {tl.hasActiveFilters && (
            <button
              onClick={tl.resetFilters}
              className="mt-1 rounded-md border border-[var(--border)] px-2.5 py-1 text-xs text-[var(--accent-text)] hover:bg-[var(--bg-hover)]"
            >
              {t.timeline.resetFilters}
            </button>
          )}
        </div>
      </div>
    );
  }

  const title = cardTitle(card);

  return (
    <div ref={scrollRef} className="h-full overflow-y-auto">
      <article aria-label={title} className="mx-auto w-full max-w-[1040px] px-4 pb-24 pt-4 sm:px-8">
        <div className="-ml-2">{back}</div>

        <header className="mt-6">
          <div className="text-xs text-[var(--text-muted)]">{TOPIC_MAP[card.topicId].label}</div>
          <h2 className="mt-2 max-w-[28ch] text-[1.75rem] font-semibold leading-tight tracking-tight text-[var(--text)] sm:text-[2rem]">
            {title}
          </h2>
          <p className="mt-3 max-w-[64ch] text-sm leading-relaxed text-[var(--text-secondary)]">
            {card.summary ?? t.timeline.looseSummary}
          </p>
          {card.totalEvents && card.totalEvents > card.events.length && (
            <p className="mt-1 text-xs text-[var(--text-muted)]">
              {t.timeline.sampledNote(card.events.length, card.totalEvents)}
            </p>
          )}
          <div className="mt-3 flex flex-wrap gap-x-5 gap-y-1 text-xs tabular-nums text-[var(--text-muted)]">
            <span className="text-[var(--text-secondary)]">
              {card.totalEvents && card.totalEvents > card.events.length
                ? t.timeline.cardEventsOfTotal(card.events.length, card.totalEvents)
                : t.timeline.cardEvents(card.events.length)}
            </span>
            <span>{formatSpan(card.startMs, card.endMs)}</span>
            <span>
              {t.timeline.timezoneLabel}：{t.timeline.timezone}
            </span>
            {!dataStatus.isDemo && <span>{dataStatus.label}</span>}
          </div>
          <div className="mt-8 rounded-xl border border-[var(--border)] bg-[var(--bg-panel)] px-5 pb-3 pt-5">
            <ThreadStrip
              events={card.events}
              startMs={card.startMs}
              endMs={card.endMs}
              size="lg"
              onPick={setSelectedEventId}
            />
          </div>
          <p className="mt-3 text-xs text-[var(--text-muted)]">{t.timeline.threadOrderNote}</p>
        </header>

        <div className="mt-8">
          {groups.map((g, i) => {
            const gapDays = i > 0 ? Math.round((g.startMs - groups[i - 1].startMs) / DAY_MS) - 1 : 0;
            return (
              <div key={g.key}>
                {gapDays > 0 && (
                  <div className="grid md:grid-cols-[148px_1fr]">
                    <span className="hidden md:block" />
                    <div className="ml-1.5 border-l border-dashed border-[var(--border-strong)] py-3 pl-6 text-[11px] text-[var(--text-muted)]">
                      {t.timeline.gapDays(gapDays)}
                    </div>
                  </div>
                )}
                <section data-day={g.key} aria-labelledby={`day-${g.key}`} className="grid md:grid-cols-[148px_1fr]">
                  <h3
                    id={`day-${g.key}`}
                    className="sticky top-0 z-10 flex items-baseline gap-3 self-start bg-[var(--bg)] pb-2 pt-4 md:flex-col md:gap-1 md:bg-transparent md:pt-[18px]"
                  >
                    <span className="text-[15px] font-semibold text-[var(--text)]">{formatDayHeading(g.startMs)}</span>
                    <span className="text-xs text-[var(--text-muted)]">{t.timeline.dayCount(g.events.length)}</span>
                  </h3>
                  <ol className="ml-1.5 space-y-2 border-l border-[var(--border-strong)] py-2">
                    {g.events.map((e) => (
                      <EventEntry
                        key={e.id}
                        event={e}
                        selected={selectedEventId === e.id}
                        onSelect={setSelectedEventId}
                      />
                    ))}
                  </ol>
                </section>
              </div>
            );
          })}
        </div>
      </article>
    </div>
  );
}
