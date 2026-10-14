import { useEffect, useRef } from 'react';
import { t } from '../i18n/strings';
import { TOPICS, TOPIC_MAP } from '../config/topics';
import type { TopicId } from '../types';
import type { UseTimelineResult } from '../hooks/useTimeline';
import type { ThreadCard } from '../utils/timelineLayout';
import { formatSpan } from '../utils/time';
import { cardTitle } from '../utils/threadText';
import { ThreadStrip } from './ThreadStrip';

/** 画廊中的一张脉络卡片：整张可点，打开该脉络的时间线 */
function ThreadCardView(props: { card: ThreadCard; onOpen: (id: string) => void }) {
  const { card, onOpen } = props;
  const title = cardTitle(card);
  return (
    <li className="min-w-0">
      <button
        onClick={() => onOpen(card.id)}
        data-thread-id={card.id}
        aria-label={t.timeline.openThread(title)}
        className={`group flex h-full w-full flex-col rounded-xl border px-5 pb-4 pt-4 text-left transition-colors ${
          card.isLoose
            ? 'border-dashed border-[var(--border-strong)] bg-transparent hover:bg-[var(--bg-panel)]'
            : 'border-[var(--border)] bg-[var(--bg-panel)] hover:border-[var(--border-strong)] hover:bg-[var(--bg-hover)]'
        }`}
      >
        <span className="text-xs text-[var(--text-muted)]">{TOPIC_MAP[card.topicId].label}</span>
        <div className="mt-4">
          <ThreadStrip events={card.events} startMs={card.startMs} endMs={card.endMs} size="sm" />
        </div>
        <h3
          className={`mt-4 leading-snug text-[var(--text)] ${
            card.isLoose ? 'text-base font-medium' : 'text-lg font-semibold tracking-tight'
          }`}
        >
          {title}
        </h3>
        <p className="mt-2 line-clamp-3 text-[13px] leading-relaxed text-[var(--text-secondary)]">
          {card.summary ?? t.timeline.looseSummary}
        </p>
        {/* 底部固定在卡片底端，便于整行对齐比较 */}
        <div className="mt-auto flex items-baseline justify-between gap-3 pt-5 text-xs tabular-nums text-[var(--text-muted)]">
          <span className="text-[var(--text-secondary)]">
            {card.totalEvents && card.totalEvents > card.events.length
              ? t.timeline.cardEventsSampled(card.events.length, card.totalEvents)
              : t.timeline.cardEvents(card.events.length)}
          </span>
          <span>{formatSpan(card.startMs, card.endMs)}</span>
        </div>
      </button>
    </li>
  );
}

/**
 * 时间线画廊（时间线页首页）：
 * - 顶部一级主题标签，选择后只显示该主题下的卡片。
 * - 每张卡片是一条事件脉络（二级主题）的时间线缩略；点开进入完整时间线。
 */
export function TimelineGallery(props: {
  tl: UseTimelineResult;
  /** 数据来源说明（真实数据给出条数与时间范围，演示数据给出明确提示） */
  dataStatus: { isDemo: boolean; label: string; note: string | null };
  onRefresh?: () => void;
  refreshing?: boolean;
  /** 从脉络页返回时，把焦点还给刚才打开的卡片 */
  returnFocusId: string | null;
}) {
  const { tl, dataStatus, onRefresh, refreshing, returnFocusId } = props;
  const { cards, topicCards, topic, setTopic } = tl;
  const listRef = useRef<HTMLUListElement>(null);

  useEffect(() => {
    if (!returnFocusId) return;
    listRef.current?.querySelector<HTMLElement>(`[data-thread-id="${returnFocusId}"]`)?.focus();
  }, [returnFocusId]);

  const countFor = (id: TopicId | null) =>
    id === null ? cards.length : cards.filter((c) => c.topicId === id).length;
  const topicOptions: { id: TopicId | null; label: string }[] = [
    { id: null, label: t.timeline.topicAll },
    ...TOPICS.map((x) => ({ id: x.id, label: x.label })),
  ];
  const eventTotal = topicCards.reduce((n, c) => n + c.events.length, 0);

  return (
    <div className="mx-auto w-full max-w-[1240px] px-4 pb-16 pt-8 sm:px-8">
      <header className="flex flex-wrap items-end justify-between gap-x-6 gap-y-2">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight text-[var(--text)]">{t.timeline.galleryTitle}</h2>
          <p className="mt-1 text-sm text-[var(--text-muted)]">
            {t.timeline.gallerySummary(topicCards.length, eventTotal)}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
          <p className="text-xs text-[var(--text-muted)]">
            {dataStatus.isDemo ? t.timeline.demoDataNotice : dataStatus.label}
          </p>
          {onRefresh && (
            <button
              onClick={onRefresh}
              disabled={refreshing}
              className="rounded-md border border-[var(--border)] px-2 py-0.5 text-xs text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text)] disabled:opacity-50"
            >
              {refreshing ? t.timeline.refreshingNews : t.timeline.refreshNews}
            </button>
          )}
        </div>
      </header>

      <div role="group" aria-label={t.timeline.topicLabel} className="mt-6 flex flex-wrap gap-2">
        {topicOptions.map((o) => {
          const active = topic === o.id;
          return (
            <button
              key={o.id ?? 'all'}
              onClick={() => setTopic(o.id)}
              aria-pressed={active}
              className={`flex items-baseline gap-2 rounded-full border px-4 py-1.5 text-sm transition-colors ${
                active
                  ? 'border-[var(--text)] bg-[var(--text)] text-[var(--bg)]'
                  : 'border-[var(--border-strong)] text-[var(--text-secondary)] hover:border-[var(--text-muted)] hover:text-[var(--text)]'
              }`}
            >
              {o.label}
              <span className={`text-xs tabular-nums ${active ? 'opacity-70' : 'text-[var(--text-muted)]'}`}>
                {countFor(o.id)}
              </span>
            </button>
          );
        })}
      </div>

      {topicCards.length === 0 ? (
        <div className="mt-16 flex flex-col items-center gap-2 text-center">
          <p className="text-sm text-[var(--text-secondary)]">
            {cards.length === 0 ? t.timeline.emptyFiltered : t.timeline.emptyTopic}
          </p>
          {tl.hasActiveFilters && (
            <button
              onClick={tl.resetFilters}
              className="mt-1 rounded-md border border-[var(--border)] px-2.5 py-1 text-xs text-[var(--accent-text)] hover:bg-[var(--bg-hover)]"
            >
              {t.timeline.resetFilters}
            </button>
          )}
        </div>
      ) : (
        <ul
          ref={listRef}
          aria-label={t.timeline.galleryTitle}
          className="mt-6 grid grid-cols-[repeat(auto-fill,minmax(min(100%,340px),1fr))] gap-4"
        >
          {topicCards.map((c) => (
            <ThreadCardView key={c.id} card={c} onOpen={tl.setOpenThreadId} />
          ))}
        </ul>
      )}
    </div>
  );
}
