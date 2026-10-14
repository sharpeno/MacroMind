import { useEffect, useRef } from 'react';
import { t } from '../i18n/strings';
import { CATEGORY_MAP } from '../config/categories';
import type { NewsEvent } from '../types';
import { formatDateTime } from '../utils/time';

/**
 * 事件详情面板（在脉络时间线中点击事件打开）。
 * - 分别显示事件发生时间与新闻发布时间；未知时间明确说明。
 * - 区分：有资料记录的事实 / 明确归属的主张 / Agent 的解释。
 * - 同一脉络的其他事件就在左侧时间线上，面板只讲这一个事件。
 */
export function EventDetailPanel(props: {
  event: NewsEvent;
  attached: boolean;
  onClose: () => void;
  onAddToChat: (e: NewsEvent) => void;
  onAnalyze: (e: NewsEvent) => void;
  /** 数据来源说明（真实数据为财联社，演示数据为空） */
  dataNote?: string | null;
  /** 小屏抽屉模式 */
  asDrawer?: boolean;
}) {
  const { event, attached, onClose, onAddToChat, onAnalyze, asDrawer, dataNote } = props;
  const cat = CATEGORY_MAP[event.category];
  const closeRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLElement>(null);

  // 打开时聚焦，Esc 关闭
  useEffect(() => {
    closeRef.current?.focus();
  }, [event.id]);
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, [onClose]);

  const sectionCls = 'border-t border-[var(--border)] px-4 py-3';
  const headingCls = 'mb-1.5 text-xs font-medium text-[var(--text-muted)]';

  return (
    <aside
      ref={panelRef}
      role={asDrawer ? 'dialog' : 'complementary'}
      aria-modal={asDrawer ? true : undefined}
      aria-label={`${t.detail.title}：${event.title}`}
      className={
        asDrawer
          ? 'fixed inset-x-0 bottom-0 z-50 flex max-h-[80vh] flex-col rounded-t-xl border border-[var(--border)] bg-[var(--bg-panel)] shadow-2xl'
          : 'flex h-full w-[380px] shrink-0 flex-col border-l border-[var(--border)] bg-[var(--bg-panel)]'
      }
    >
      {/* 头部 */}
      <div className="flex items-start gap-2 px-4 py-3">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-[var(--text-muted)]">
            <span aria-hidden className="h-2 w-2 rounded-sm" style={{ background: `var(${cat.colorVar})` }} />
            <span>{cat.label}</span>
            <span>·</span>
            <span>{t.timeline.regions[event.region]}</span>
            {event.importance && (
              <>
                <span>·</span>
                <span>
                  {t.timeline.filterImportance}
                  {t.timeline.importance[event.importance]}
                </span>
              </>
            )}
            {event.isDemo && (
              <span className="rounded bg-[var(--bg-subtle)] px-1 py-px text-[var(--text-secondary)]">
                {t.detail.demoBadge}
              </span>
            )}
          </div>
          <h2 className="mt-1 text-sm font-semibold leading-snug text-[var(--text)]">{event.title}</h2>
        </div>
        <button
          ref={closeRef}
          onClick={onClose}
          aria-label={t.detail.close}
          className="shrink-0 rounded-md px-2 py-1 text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
        >
          ✕
        </button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {/* 摘要 */}
        <div className="px-4 pb-3 text-sm text-[var(--text-secondary)]">{event.summary}</div>

        {/* 报道原文（真实新闻才有）：折叠展示，便于与摘要对照，不做改写 */}
        {event.body && (
          <div className={sectionCls}>
            <details>
              <summary className="cursor-pointer text-xs font-medium text-[var(--text-muted)]">
                {t.detail.reportText}
                <span className="ml-2 font-normal">{t.detail.reportTextNote}</span>
              </summary>
              <p className="mt-2 whitespace-pre-wrap text-xs leading-relaxed text-[var(--text-secondary)]">
                {event.body}
              </p>
            </details>
          </div>
        )}

        {/* 时间 */}
        <div className={sectionCls}>
          <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-xs">
            <dt className="text-[var(--text-muted)]">{t.detail.occurredAt}</dt>
            <dd className="text-[var(--text)]">
              {event.occurredAt === null
                ? t.timeline.occurredUnknown
                : `${formatDateTime(event.occurredAt)}${event.occurredAtPrecision === 'date_only' ? ` ${t.timeline.dateOnlyNote}` : ''}`}
            </dd>
            <dt className="text-[var(--text-muted)]">{t.detail.publishedAt}</dt>
            <dd className="text-[var(--text)]">{formatDateTime(event.publishedAt)}</dd>
          </dl>
          <div className="mt-1 text-[10px] text-[var(--text-muted)]">
            {t.timeline.timezoneLabel}：{t.timeline.timezone}
          </div>
          {event.occurredAtPrecision === 'unknown' && (
            <p className="mt-1 text-[10px] text-[var(--text-muted)]">{t.timeline.occurredAtUnknownNote}</p>
          )}
        </div>

        {/* 实体 */}
        {event.entities && event.entities.length > 0 && (
          <div className={sectionCls}>
            <h3 className={headingCls}>{t.detail.entities}</h3>
            <ul className="flex flex-wrap gap-1">
              {event.entities.map((en) => (
                <li key={en} className="rounded border border-[var(--border)] bg-[var(--bg-subtle)] px-1.5 py-0.5 text-xs">
                  {en}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* 内容分层 */}
        {event.recordedFacts && event.recordedFacts.length > 0 && (
          <div className={sectionCls}>
            <h3 className={headingCls}>{t.detail.recordedFacts}</h3>
            <ul className="list-disc pl-4 text-xs text-[var(--text)]">
              {event.recordedFacts.map((f, i) => (
                <li key={i} className="mb-0.5">
                  {f}
                </li>
              ))}
            </ul>
          </div>
        )}
        {event.attributedClaims && event.attributedClaims.length > 0 && (
          <div className={sectionCls}>
            <h3 className={headingCls}>{t.detail.attributedClaims}</h3>
            <ul className="text-xs text-[var(--text)]">
              {event.attributedClaims.map((c, i) => (
                <li key={i} className="mb-1">
                  <span className="text-[var(--text-muted)]">{c.attribution}：</span>
                  <span>“{c.claim}”</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {event.agentInterpretation && (
          <div className={sectionCls}>
            <h3 className={headingCls}>{t.detail.agentInterpretation}</h3>
            <div className="rounded-md border border-dashed border-[var(--border-strong)] bg-[var(--bg-subtle)] px-2.5 py-2 text-xs text-[var(--text-secondary)]">
              <div className="mb-1 text-[10px] text-[var(--text-muted)]">{t.detail.agentInterpretationNote}</div>
              {event.agentInterpretation}
            </div>
          </div>
        )}

        {/* 来源 */}
        <div className={sectionCls}>
          <h3 className={headingCls}>
            {t.detail.sources}（{event.sources.length}）
          </h3>
          <ul className="text-xs">
            {event.sources.map((s, i) => (
              <li key={i} className="mb-0.5">
                {s.url ? (
                  <a href={s.url} target="_blank" rel="noreferrer" className="text-[var(--accent-text)] underline">
                    {s.name}
                  </a>
                ) : (
                  <span className="text-[var(--text-secondary)]">
                    {s.name}
                    {event.isDemo && <span className="text-[var(--text-muted)]"> {t.detail.sourceNoUrl}</span>}
                  </span>
                )}
              </li>
            ))}
          </ul>
          {!event.isDemo && dataNote && (
            <p className="mt-1.5 text-[10px] leading-relaxed text-[var(--text-muted)]">{dataNote}</p>
          )}
        </div>

      </div>

      {/* 操作 */}
      <div className="flex gap-2 border-t border-[var(--border)] px-4 py-3">
        <button
          onClick={() => onAddToChat(event)}
          disabled={attached}
          className="flex-1 rounded-md border border-[var(--border)] px-3 py-1.5 text-xs text-[var(--text)] hover:bg-[var(--bg-hover)] disabled:opacity-50"
        >
          {attached ? t.detail.addedToChat : t.detail.addToChat}
        </button>
        <button
          onClick={() => onAnalyze(event)}
          className="flex-1 rounded-md bg-[var(--accent)] px-3 py-1.5 text-xs font-medium text-[var(--on-accent)] hover:brightness-110"
        >
          {t.detail.analyzeEvent}
        </button>
      </div>
    </aside>
  );
}
