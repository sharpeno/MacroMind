import { useCallback, useRef, useState } from 'react';
import type {
  ChatMessage,
  ChatMode,
  Conversation,
  EventContextRef,
  ModelOption,
  ResearchProgress,
} from '../types';
import type { ChatService } from '../services/chatService';
import { buildChatRequest, buildUserContent } from '../services/chatService';
import { genId } from '../utils/time';
import { t } from '../i18n/strings';

/**
 * 聊天状态管理：发送 / 停止 / 重试 / 新建对话。
 * - 每次请求携带 (conversationId, messageId)；响应回写前校验当前对话，
 *   防止取消或切换对话后迟到的响应写入错误位置。
 */

function newConversation(): Conversation {
  return {
    id: genId('conv'),
    title: t.chat.conversationFallbackTitle,
    messages: [],
    createdAt: new Date().toISOString(),
  };
}

export interface UseChatResult {
  conversation: Conversation;
  isGenerating: boolean;
  send(text: string, model: ModelOption, mode: ChatMode, attached: EventContextRef[]): void;
  stop(): void;
  retryLast(model: ModelOption, mode: ChatMode): void;
  startNewConversation(): void;
}

/** service 为 null 表示本地服务未连接：没有可用模型，发送直接失败并说明原因 */
export function useChat(service: ChatService | null): UseChatResult {
  const [conversation, setConversation] = useState<Conversation>(newConversation);
  const [isGenerating, setIsGenerating] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  // 当前活跃的 (conversationId, assistantMessageId)；迟到响应据此丢弃
  const activeRef = useRef<{ convId: string; msgId: string } | null>(null);

  const patchMessage = useCallback(
    (convId: string, msgId: string, patch: Partial<ChatMessage> | ((m: ChatMessage) => ChatMessage)) => {
      setConversation((prev) => {
        if (prev.id !== convId) return prev; // 已切换对话：丢弃
        return {
          ...prev,
          messages: prev.messages.map((m) =>
            m.id === msgId ? (typeof patch === 'function' ? patch(m) : { ...m, ...patch }) : m,
          ),
        };
      });
    },
    [],
  );

  const runRequest = useCallback(
    (conv: Conversation, userText: string, model: ModelOption, mode: ChatMode, attached: EventContextRef[]) => {
      const userMsg: ChatMessage = {
        id: genId('msg'),
        role: 'user',
        content: userText,
        createdAt: new Date().toISOString(),
        status: 'done',
        attachedEvents: attached.length > 0 ? [...attached] : undefined,
      };
      const assistantMsg: ChatMessage = {
        id: genId('msg'),
        role: 'assistant',
        content: '',
        createdAt: new Date().toISOString(),
        status: 'pending',
        usedModelId: model.id,
        usedModelDisplayName: model.displayName,
        usedMode: mode,
      };

      const nextMessages = [...conv.messages, userMsg, assistantMsg];
      const title =
        conv.messages.length === 0 ? userText.slice(0, 24) || conv.title : conv.title;
      setConversation({ ...conv, title, messages: nextMessages });

      // 构建请求（历史 = 之前完成的消息 + 本条用户消息；错误/取消的回答不进入上下文）
      const history = [
        ...conv.messages
          .filter((m) => m.status === 'done' && m.content)
          .map((m) => ({
            role: m.role,
            content:
              m.role === 'user' && m.attachedEvents
                ? buildUserContent(m.content, m.attachedEvents)
                : m.content,
          })),
        { role: 'user' as const, content: buildUserContent(userText, attached) },
      ];
      const req = buildChatRequest({
        conversationId: conv.id,
        modelId: model.id,
        mode,
        history,
      });

      const ctrl = new AbortController();
      abortRef.current = ctrl;
      activeRef.current = { convId: conv.id, msgId: assistantMsg.id };
      setIsGenerating(true);

      void (async () => {
        const isActive = () =>
          activeRef.current?.convId === conv.id && activeRef.current?.msgId === assistantMsg.id;
        let progress: ResearchProgress | undefined;
        // 未连接本地服务：没有可用的模型，直接给出原因
        if (service === null) {
          if (isActive()) {
            patchMessage(conv.id, assistantMsg.id, { status: 'error', errorMessage: t.errors.noModel });
            activeRef.current = null;
            setIsGenerating(false);
          }
          return;
        }
        try {
          for await (const evt of service.stream(req, ctrl.signal)) {
            if (!isActive()) return; // 迟到响应：丢弃
            if (evt.type === 'delta') {
              patchMessage(conv.id, assistantMsg.id, (m) => ({
                ...m,
                status: 'streaming',
                content: m.content + evt.text,
                researchProgress: progress,
              }));
            } else if (evt.type === 'research_progress') {
              progress = evt.progress;
              patchMessage(conv.id, assistantMsg.id, { status: 'streaming', researchProgress: progress });
            } else if (evt.type === 'done') {
              patchMessage(conv.id, assistantMsg.id, { status: 'done' });
            } else if (evt.type === 'error') {
              patchMessage(conv.id, assistantMsg.id, {
                status: 'error',
                errorMessage: evt.message,
              });
            }
          }
          // 流正常结束但未显式 done（演示服务取消时直接 return）
          if (isActive()) {
            patchMessage(conv.id, assistantMsg.id, (m) => ({
              ...m,
              status: m.status === 'streaming' || m.status === 'pending' ? (ctrl.signal.aborted ? 'cancelled' : 'done') : m.status,
            }));
          }
        } catch (err) {
          if (isActive()) {
            patchMessage(conv.id, assistantMsg.id, {
              status: ctrl.signal.aborted ? 'cancelled' : 'error',
              errorMessage: err instanceof Error ? err.message : String(err),
            });
          }
        } finally {
          if (isActive()) {
            setIsGenerating(false);
            activeRef.current = null;
          }
        }
      })();
    },
    [patchMessage, service],
  );

  const send = useCallback(
    (text: string, model: ModelOption, mode: ChatMode, attached: EventContextRef[]) => {
      const trimmed = text.trim();
      if (!trimmed || isGenerating) return;
      runRequest(conversation, trimmed, model, mode, attached);
    },
    [conversation, isGenerating, runRequest],
  );

  const stop = useCallback(() => {
    const active = activeRef.current;
    abortRef.current?.abort();
    if (active) {
      patchMessage(active.convId, active.msgId, (m) => ({
        ...m,
        status: m.status === 'done' || m.status === 'error' ? m.status : 'cancelled',
      }));
    }
    activeRef.current = null;
    setIsGenerating(false);
  }, [patchMessage]);

  /** 重试最后一条失败/取消的请求：移除旧的 assistant 消息，重发对应用户消息 */
  const retryLast = useCallback(
    (model: ModelOption, mode: ChatMode) => {
      if (isGenerating) return;
      const msgs = conversation.messages;
      const last = msgs[msgs.length - 1];
      if (!last || last.role !== 'assistant' || (last.status !== 'error' && last.status !== 'cancelled')) return;
      const userMsg = msgs[msgs.length - 2];
      if (!userMsg || userMsg.role !== 'user') return;
      const trimmedConv: Conversation = {
        ...conversation,
        messages: msgs.slice(0, -2),
      };
      runRequest(trimmedConv, userMsg.content, model, mode, userMsg.attachedEvents ?? []);
    },
    [conversation, isGenerating, runRequest],
  );

  const startNewConversation = useCallback(() => {
    abortRef.current?.abort();
    activeRef.current = null; // 之后到达的响应全部丢弃
    setIsGenerating(false);
    setConversation(newConversation());
  }, []);

  return { conversation, isGenerating, send, stop, retryLast, startNewConversation };
}
