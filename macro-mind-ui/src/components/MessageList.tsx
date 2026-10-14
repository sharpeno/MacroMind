import { useState, type ReactNode } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { t } from '../i18n/strings';
import type { ChatMessage, ResearchStage } from '../types';
import { formatMessageTime } from '../utils/time';
import { CATEGORY_MAP } from '../config/categories';

const STAGE_ORDER: ResearchStage[] = ['collect', 'compare', 'synthesize'];

/** 研究模式工作流程状态：收集来源 → 比较证据 → 整理分析 */
function ResearchProgressBar(props: { message: ChatMessage }) {
  const p = props.message.researchProgress;
  if (!p) return null;
  const done = props.message.status === 'done';
  return (
    <ol className="mb-2 flex flex-wrap items-center gap-1 text-xs" aria-label="研究流程状态">
      {STAGE_ORDER.map((stage, i) => {
        const isDone = done || p.completed.includes(stage);
        const isCurrent = !done && p.stage === stage && !isDone;
        return (
          <li key={stage} className="flex items-center gap-1">
            {i > 0 && <span aria-hidden className="text-[var(--text-muted)]">→</span>}
            <span
              className={`rounded px-1.5 py-0.5 ${
                isDone
                  ? 'bg-[var(--accent-soft)] text-[var(--accent-text)]'
                  : isCurrent
                    ? 'bg-[var(--bg-subtle)] font-medium text-[var(--text)]'
                    : 'text-[var(--text-muted)]'
              }`}
            >
              {isDone ? '✓ ' : ''}
              {t.chat.researchStages[stage]}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

function AssistantMeta(props: { m: ChatMessage }) {
  const { m } = props;
  const modeLabel = m.usedMode === 'research' ? t.chat.modeResearch : t.chat.modeFast;
  return (
    <div className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[11px] text-[var(--text-muted)]">
      {m.usedModelDisplayName && <span>{t.chat.usedWith(m.usedModelDisplayName, modeLabel)}</span>}
      {m.isDemo && (
        <span className="rounded bg-[var(--bg-subtle)] px-1 py-px text-[var(--text-secondary)]">
          {t.chat.demoAnswerNote}
        </span>
      )}
      <span>{formatMessageTime(m.createdAt)}</span>
    </div>
  );
}

export function MessageList(props: {
  messages: ChatMessage[];
  onRetry: () => void;
  canRetry: boolean;
  onSuggestion: (text: string) => void;
  /** 空状态主视觉（事件脉搏） */
  emptyVisual?: ReactNode;
}) {
  const { messages, onRetry, canRetry, onSuggestion, emptyVisual } = props;
  const [copiedId, setCopiedId] = useState<string | null>(null);

  if (messages.length === 0) {
    return (
      <div className="mx-auto flex min-h-full w-full max-w-2xl flex-col justify-center gap-10 px-5 py-10">
        <header>
          <h1 className="text-[1.75rem] font-semibold leading-tight tracking-tight text-[var(--text)]">
            {t.chat.emptyTitle}
          </h1>
          <p className="mt-2 text-sm text-[var(--text-muted)]">{t.chat.emptyHint}</p>
        </header>
        {emptyVisual}
        <section aria-label={t.chat.suggestionsTitle}>
          <h2 className="mb-2 text-sm font-semibold text-[var(--text)]">{t.chat.suggestionsTitle}</h2>
          <ul className="grid gap-x-6 sm:grid-cols-2">
            {t.chat.suggestions.map((s) => (
              <li key={s}>
                <button
                  onClick={() => onSuggestion(s)}
                  className="group flex w-full gap-2 rounded-md py-2 text-left text-sm text-[var(--text-secondary)] hover:text-[var(--text)]"
                >
                  <span aria-hidden className="text-[var(--text-muted)] group-hover:text-[var(--accent-text)]">
                    ↳
                  </span>
                  <span>{s}</span>
                </button>
              </li>
            ))}
          </ul>
        </section>
      </div>
    );
  }

  const copy = async (m: ChatMessage) => {
    try {
      await navigator.clipboard.writeText(m.content);
      setCopiedId(m.id);
      setTimeout(() => setCopiedId((prev) => (prev === m.id ? null : prev)), 1500);
    } catch {
      /* 剪贴板不可用时忽略 */
    }
  };

  return (
    <ol className="mx-auto flex w-full max-w-2xl flex-col gap-7 px-5 py-6">
      {messages.map((m, idx) => {
        const isLast = idx === messages.length - 1;
        if (m.role === 'user') {
          return (
            <li key={m.id} className="flex justify-end">
              <div className="max-w-[88%]">
                <div className="whitespace-pre-wrap rounded-lg rounded-br-sm bg-[var(--bg-subtle)] px-3.5 py-2 text-sm text-[var(--text)]">
                  {m.content}
                </div>
                {m.attachedEvents && m.attachedEvents.length > 0 && (
                  <ul className="mt-1 flex flex-wrap justify-end gap-1">
                    {m.attachedEvents.map((e) => (
                      <li
                        key={e.eventId}
                        className="flex items-center gap-1 rounded border border-[var(--border)] px-1.5 py-px text-[11px] text-[var(--text-muted)]"
                      >
                        <span
                          aria-hidden
                          className="h-1.5 w-1.5 rounded-full"
                          style={{ background: `var(${CATEGORY_MAP[e.category].colorVar})` }}
                        />
                        <span className="max-w-[200px] truncate">{e.title}</span>
                      </li>
                    ))}
                  </ul>
                )}
                <div className="mt-1 text-right text-[11px] text-[var(--text-muted)]">
                  {formatMessageTime(m.createdAt)}
                </div>
              </div>
            </li>
          );
        }
        // assistant
        return (
          <li key={m.id} className="flex justify-start">
            <div className="w-full min-w-0">
              {/* 回答不用气泡：左侧一条琥珀细线标记「这是分析」，正文直接排版 */}
              <div className="border-l-2 border-[var(--accent)] pl-4">
                {m.usedMode === 'research' && <ResearchProgressBar message={m} />}
                {m.status === 'pending' && (
                  <div className="text-sm text-[var(--text-muted)]" role="status">
                    {t.chat.statusPending}
                  </div>
                )}
                {m.content && (
                  <div className={`md-body text-sm ${m.status === 'streaming' ? 'stream-cursor' : ''}`}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                  </div>
                )}
                {m.status === 'cancelled' && (
                  <div className="mt-1 text-xs text-[var(--text-muted)]">{t.chat.statusCancelled}</div>
                )}
                {m.status === 'error' && (
                  <div className="mt-1 rounded bg-[var(--danger-soft)] px-2 py-1 text-xs text-[var(--danger)]" role="alert">
                    {t.errors.requestFailed(m.errorMessage ?? '')}
                  </div>
                )}
              </div>
              <div className="flex items-center gap-2">
                <AssistantMeta m={m} />
                {m.status === 'done' && m.content && (
                  <button
                    onClick={() => copy(m)}
                    className="mt-1.5 text-[11px] text-[var(--text-muted)] underline-offset-2 hover:text-[var(--text)] hover:underline"
                  >
                    {copiedId === m.id ? t.chat.copied : t.chat.copy}
                  </button>
                )}
                {isLast && canRetry && (m.status === 'error' || m.status === 'cancelled') && (
                  <button
                    onClick={onRetry}
                    className="mt-1.5 text-[11px] text-[var(--accent-text)] underline-offset-2 hover:underline"
                  >
                    {t.chat.retry}
                  </button>
                )}
              </div>
            </div>
          </li>
        );
      })}
    </ol>
  );
}
