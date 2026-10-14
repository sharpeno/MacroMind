import { useEffect, useRef, type ReactNode } from 'react';
import { t } from '../i18n/strings';
import type { ChatMode, EventContextRef, ModelOption } from '../types';
import type { UseChatResult } from '../hooks/useChat';
import { ModeSelector } from './ModeSelector';
import { ModelSelector } from './ModelSelector';
import { ChatComposer } from './ChatComposer';
import { MessageList } from './MessageList';

/**
 * 聊天面板：工具行（模式/模型/新建对话）+ 消息列表（独立滚动）+ 输入区（始终可见）。
 */
export function ChatPanel(props: {
  chat: UseChatResult;
  models: ModelOption[];
  selectedModelId: string | null;
  onModelChange: (id: string) => void;
  mode: ChatMode;
  onModeChange: (m: ChatMode) => void;
  draft: string;
  onDraftChange: (v: string) => void;
  attachedEvents: EventContextRef[];
  onRemoveAttached: (id: string) => void;
  onClearAttached: () => void;
  emptyVisual?: ReactNode;
}) {
  const {
    chat,
    models,
    selectedModelId,
    onModelChange,
    mode,
    onModeChange,
    draft,
    onDraftChange,
    attachedEvents,
    onRemoveAttached,
    onClearAttached,
    emptyVisual,
  } = props;

  const selectedModel = models.find((m) => m.id === selectedModelId) ?? null;
  const scrollRef = useRef<HTMLDivElement>(null);
  const messages = chat.conversation.messages;

  // 新消息 / 流式更新时滚动到底部（仅当已接近底部，避免打断用户回看）
  const lastLen = useRef(0);
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const nearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 160;
    const grew = messages.length !== lastLen.current;
    lastLen.current = messages.length;
    // 空状态从顶部开始阅读，不自动滚到底
    if (messages.length > 0 && (grew || nearBottom)) el.scrollTop = el.scrollHeight;
  });

  const canSend =
    draft.trim().length > 0 &&
    !chat.isGenerating &&
    selectedModel !== null &&
    selectedModel.available &&
    selectedModel.supportedModes.includes(mode);

  const handleSend = () => {
    if (!canSend || !selectedModel) return;
    chat.send(draft, selectedModel, mode, attachedEvents);
    onDraftChange('');
    onClearAttached();
  };

  return (
    <section aria-label={t.chat.panelTitle} className="flex h-full min-w-0 flex-col">
      {/* 工具行 */}
      <div className="flex flex-wrap items-center gap-2 border-b border-[var(--border)] px-4 py-2">
        <ModeSelector mode={mode} onChange={onModeChange} model={selectedModel} disabled={chat.isGenerating} />
        <ModelSelector
          models={models}
          selectedId={selectedModelId}
          mode={mode}
          onChange={onModelChange}
          disabled={chat.isGenerating}
        />
        <div className="ml-auto flex items-center gap-2">
          <span className="hidden text-[11px] text-[var(--text-muted)] md:inline">
            {mode === 'fast' ? t.chat.modeFastHint : t.chat.modeResearchHint}
          </span>
          <button
            onClick={chat.startNewConversation}
            className="rounded-md border border-[var(--border)] px-2.5 py-1 text-xs text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text)]"
          >
            {t.chat.newConversation}
          </button>
        </div>
      </div>
      {/* 消息列表（独立滚动） */}
      <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto">
        <MessageList
          messages={messages}
          canRetry={!chat.isGenerating && selectedModel !== null}
          onRetry={() => selectedModel && chat.retryLast(selectedModel, mode)}
          onSuggestion={(s) => onDraftChange(s)}
          emptyVisual={emptyVisual}
        />
      </div>
      {/* 输入区（始终可见） */}
      <ChatComposer
        draft={draft}
        onDraftChange={onDraftChange}
        attachedEvents={attachedEvents}
        onRemoveAttached={onRemoveAttached}
        canSend={canSend}
        isGenerating={chat.isGenerating}
        onSend={handleSend}
        onStop={chat.stop}
      />
    </section>
  );
}
