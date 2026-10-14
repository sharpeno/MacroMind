import { useRef, useState } from 'react';
import { t } from '../i18n/strings';
import type { EventContextRef } from '../types';
import { CATEGORY_MAP } from '../config/categories';

/**
 * 聊天输入区：多行输入，Enter 发送，Shift+Enter 换行。
 * 正确处理输入法组字状态（compositionstart/end + keydown isComposing 双重判断），
 * 避免中文输入过程中按 Enter 误发送。
 */
export function ChatComposer(props: {
  draft: string;
  onDraftChange: (v: string) => void;
  attachedEvents: EventContextRef[];
  onRemoveAttached: (eventId: string) => void;
  canSend: boolean;
  isGenerating: boolean;
  onSend: () => void;
  onStop: () => void;
}) {
  const { draft, onDraftChange, attachedEvents, onRemoveAttached, canSend, isGenerating, onSend, onStop } = props;
  const [composing, setComposing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  return (
    <div className="px-5 pb-4 pt-2">
      <div className="mx-auto w-full max-w-2xl">
      {attachedEvents.length > 0 && (
        <div className="mb-2">
          <div className="mb-1 text-xs text-[var(--text-muted)]">{t.chat.attachedEvents}</div>
          <ul className="flex flex-wrap gap-1.5">
            {attachedEvents.map((e) => (
              <li
                key={e.eventId}
                className="flex max-w-full items-center gap-1 rounded-md border border-[var(--border)] bg-[var(--bg-subtle)] py-0.5 pl-2 pr-1 text-xs"
              >
                <span
                  aria-hidden
                  className="h-2 w-2 shrink-0 rounded-full"
                  style={{ background: `var(${CATEGORY_MAP[e.category].colorVar})` }}
                />
                <span className="truncate" title={e.title}>
                  {e.title}
                </span>
                <button
                  aria-label={`${t.chat.removeAttached}：${e.title}`}
                  onClick={() => onRemoveAttached(e.eventId)}
                  className="rounded px-1 text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
                >
                  ×
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="flex items-end gap-2 rounded-xl border border-[var(--border-strong)] bg-[var(--bg-panel)] p-2 focus-within:border-[var(--accent)]">
        <textarea
          ref={textareaRef}
          value={draft}
          onChange={(e) => onDraftChange(e.target.value)}
          onCompositionStart={() => setComposing(true)}
          onCompositionEnd={() => setComposing(false)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              // 输入法组字中不发送
              if (composing || e.nativeEvent.isComposing) return;
              e.preventDefault();
              if (canSend) onSend();
            }
          }}
          placeholder={t.chat.inputPlaceholder}
          rows={Math.min(6, Math.max(2, draft.split('\n').length))}
          aria-label={t.chat.inputPlaceholder}
          className="min-h-[48px] flex-1 resize-none bg-transparent px-2 py-1.5 text-sm text-[var(--text)] outline-none placeholder:text-[var(--text-muted)] focus-visible:outline-none"
        />
        {isGenerating ? (
          <button
            onClick={onStop}
            className="shrink-0 rounded-lg border border-[var(--border-strong)] px-4 py-1.5 text-sm text-[var(--text)] hover:bg-[var(--bg-hover)]"
          >
            {t.chat.stop}
          </button>
        ) : (
          <button
            onClick={onSend}
            disabled={!canSend}
            className="shrink-0 rounded-lg bg-[var(--accent)] px-4 py-1.5 text-sm font-medium text-[var(--on-accent)] hover:brightness-110 disabled:cursor-not-allowed disabled:bg-[var(--bg-subtle)] disabled:text-[var(--text-muted)]"
          >
            {t.chat.send}
          </button>
        )}
      </div>
      </div>
    </div>
  );
}
