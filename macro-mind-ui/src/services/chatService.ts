import type { ChatMode, ChatRequest, ChatStreamEvent, EventContextRef, ModelOption } from '../types';

/**
 * 聊天服务适配层接口。
 * 实现：ProxyChatService —— 经本地服务转发到设置里配置的模型 API（proxyChatService.ts），
 * 密钥只保存在本地服务进程内，不暴露给前端。
 * 没有配置模型时前端不使用任何替代实现：界面直接说明原因（见 ModelSelector / ChatPanel）。
 */
export interface ChatService {
  /** 从后端或集中配置加载可用模型 */
  listModels(): Promise<ModelOption[]>;
  /**
   * 发送聊天请求，流式返回。
   * 通过 AbortSignal 支持停止生成；调用方负责丢弃迟到响应。
   */
  stream(req: ChatRequest, signal: AbortSignal): AsyncGenerator<ChatStreamEvent>;
}

/** 模式 → 请求配置的明确映射（模式必须影响请求，不只改界面） */
export const MODE_CONFIG: Record<
  ChatMode,
  { maxOutputTokens: number; systemPrompt: string }
> = {
  fast: {
    maxOutputTokens: 800,
    systemPrompt:
      '你是 MacroMind 宏观经济研究助手。当前为快速模式：直接给出简洁、重点突出的回答，' +
      '控制在三段以内，不展开完整论证。回答使用简体中文。',
  },
  research: {
    maxOutputTokens: 3000,
    systemPrompt:
      '你是 MacroMind 宏观经济研究助手。当前为研究模式：按以下结构输出——' +
      '1) 问题拆解；2) 相关证据与数据（注明来源归属，区分记录的事实、归属于他人的主张与你的解释）；' +
      '3) 多角度比较；4) 结构化结论与不确定性说明。使用 Markdown，回答使用简体中文。' +
      '不要编造具体数据来源；不确定时明确说明。',
  },
};

/** 把事件上下文序列化进用户消息（请求构建层，与展示分离） */
export function buildUserContent(text: string, attached: EventContextRef[]): string {
  if (attached.length === 0) return text;
  const ctx = attached
    .map((e, i) => `${i + 1}. [${e.category}] ${e.title}（发生时间 ${e.occurredAt}）`)
    .join('\n');
  return `${text}\n\n--- 已附加的新闻事件上下文 ---\n${ctx}`;
}

export function buildChatRequest(params: {
  conversationId: string;
  modelId: string;
  mode: ChatMode;
  history: { role: 'user' | 'assistant'; content: string }[];
}): ChatRequest {
  const cfg = MODE_CONFIG[params.mode];
  return {
    conversationId: params.conversationId,
    modelId: params.modelId,
    mode: params.mode,
    maxOutputTokens: cfg.maxOutputTokens,
    messages: [{ role: 'system', content: cfg.systemPrompt }, ...params.history],
  };
}
