import type { ChatRequest, ChatStreamEvent, ModelOption } from '../types';
import type { ChatService } from './chatService';

/**
 * 本地服务适配器：请求同源 /api/*，由本地服务进程持有密钥并转发到
 * 已配置的模型 API（见 server/README 与 macro-mind-engine/model.local.json）。
 * 前端代码不接触任何服务提供方密钥。
 */
export class ProxyChatService implements ChatService {
  async listModels(): Promise<ModelOption[]> {
    const res = await fetch('/api/models');
    if (!res.ok) throw new Error(`GET /api/models ${res.status}`);
    const data = (await res.json()) as { models: ModelOption[] };
    return data.models;
  }

  async *stream(req: ChatRequest, signal: AbortSignal): AsyncGenerator<ChatStreamEvent> {
    let res: Response;
    try {
      res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          modelId: req.modelId,
          mode: req.mode,
          messages: req.messages,
          maxOutputTokens: req.maxOutputTokens,
        }),
        signal,
      });
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return;
      yield { type: 'error', message: err instanceof Error ? err.message : String(err) };
      return;
    }
    if (!res.ok || !res.body) {
      const text = await res.text().catch(() => '');
      yield { type: 'error', message: `HTTP ${res.status}${text ? `: ${text.slice(0, 200)}` : ''}` };
      return;
    }

    // 解析 SSE：每行 "data: {json}"，以 "data: [DONE]" 结束
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    try {
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';
        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data:')) continue;
          const payload = trimmed.slice(5).trim();
          if (payload === '[DONE]') {
            yield { type: 'done' };
            return;
          }
          try {
            const evt = JSON.parse(payload) as ChatStreamEvent;
            yield evt;
            if (evt.type === 'done' || evt.type === 'error') return;
          } catch {
            // 跳过无法解析的行
          }
        }
      }
      // 流意外结束（未收到 done）
      yield { type: 'error', message: '响应流意外中断' };
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return;
      yield { type: 'error', message: err instanceof Error ? err.message : String(err) };
    }
  }
}

/** 探测本地服务是否可用 */
export async function probeBackend(timeoutMs = 2500): Promise<boolean> {
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), timeoutMs);
    const res = await fetch('/api/health', { signal: ctrl.signal });
    clearTimeout(t);
    return res.ok;
  } catch {
    return false;
  }
}
