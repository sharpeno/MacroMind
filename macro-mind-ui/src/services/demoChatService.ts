import type { ChatRequest, ChatStreamEvent, ModelOption, ResearchStage } from '../types';
import type { ChatService } from './chatService';

/**
 * 演示聊天服务：不访问任何外部服务。
 * 回答为固定模板并明确标注“演示回答”，不呈现为实时数据。
 */

export const DEMO_MODEL: ModelOption = {
  id: 'demo-offline',
  displayName: '演示模型（离线）',
  providerLabel: '演示',
  supportedModes: ['fast', 'research'],
  available: true,
  isDemo: true,
};

const FAST_TEMPLATE = (q: string) =>
  `**【演示回答 · 非实时数据】**\n\n` +
  `这是快速模式下的演示回答，用于展示界面交互，内容不构成真实分析。\n\n` +
  `你的问题是：“${q.slice(0, 80)}${q.length > 80 ? '…' : ''}”\n\n` +
  `接入真实模型后，此处将显示模型生成的简洁回答。接入方式见项目 README（启动本地服务并配置 MACROMIND_LOCAL_API_KEY）。`;

const RESEARCH_TEMPLATE = (q: string) =>
  `**【演示回答 · 非实时数据】**\n\n` +
  `这是研究模式下的演示回答，用于展示结构化输出的排版效果，内容为虚构示例。\n\n` +
  `## 1. 问题拆解\n\n- 演示拆解要点一\n- 演示拆解要点二\n\n` +
  `## 2. 相关证据（虚构示例）\n\n| 证据 | 类型 | 归属 |\n|---|---|---|\n| 央行A声明措辞变化 | 记录的事实（虚构） | 演示来源 |\n| “路径取决于数据” | 归属的主张（虚构） | 央行A行长（虚构人物） |\n\n` +
  `## 3. 多角度比较\n\n演示内容：不同框架对同一证据可能得出不同结论。\n\n` +
  `## 4. 结论与不确定性\n\n演示结论：本回答为界面演示模板，不含真实分析。\n\n` +
  `> 原始问题：“${q.slice(0, 60)}${q.length > 60 ? '…' : ''}”`;

function sleep(ms: number, signal: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal.aborted) return reject(new DOMException('Aborted', 'AbortError'));
    const t = setTimeout(resolve, ms);
    signal.addEventListener(
      'abort',
      () => {
        clearTimeout(t);
        reject(new DOMException('Aborted', 'AbortError'));
      },
      { once: true },
    );
  });
}

export class DemoChatService implements ChatService {
  async listModels(): Promise<ModelOption[]> {
    return [DEMO_MODEL];
  }

  async *stream(req: ChatRequest, signal: AbortSignal): AsyncGenerator<ChatStreamEvent> {
    const lastUser = [...req.messages].reverse().find((m) => m.role === 'user');
    const question = lastUser?.content ?? '';

    try {
      if (req.mode === 'research') {
        // 演示研究模式的工作流程状态
        const stages: ResearchStage[] = ['collect', 'compare', 'synthesize'];
        const completed: ResearchStage[] = [];
        for (const stage of stages) {
          yield { type: 'research_progress', progress: { stage, completed: [...completed] } };
          await sleep(500, signal);
          completed.push(stage);
        }
        yield {
          type: 'research_progress',
          progress: { stage: 'synthesize', completed },
        };
      } else {
        await sleep(350, signal);
      }

      const text = req.mode === 'research' ? RESEARCH_TEMPLATE(question) : FAST_TEMPLATE(question);
      // 按小块模拟流式输出
      const chunkSize = 18;
      for (let i = 0; i < text.length; i += chunkSize) {
        yield { type: 'delta', text: text.slice(i, i + chunkSize) };
        await sleep(25, signal);
      }
      yield { type: 'done' };
    } catch (err) {
      if (err instanceof DOMException && err.name === 'AbortError') return; // 调用方处理取消状态
      yield { type: 'error', message: err instanceof Error ? err.message : String(err) };
    }
  }
}
