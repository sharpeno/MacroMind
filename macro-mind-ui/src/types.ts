// 领域类型契约：聊天、模型、新闻事件。
// 所有时间戳统一存储为 ISO 8601 字符串（含时区），展示时按选定时区格式化。

export type ChatMode = 'fast' | 'research';

export interface ModelOption {
  /** 服务提供方使用的模型 ID（请求时发送） */
  id: string;
  /** 界面展示名称，与 ID 分离 */
  displayName: string;
  /** 模型提供来源说明（如 "本地配置 model.local.json" / "演示"） */
  providerLabel: string;
  /** 支持的模式；不支持的组合在界面上禁用并说明 */
  supportedModes: ChatMode[];
  /** 是否可用（后端探测失败时为 false，仍展示但禁用） */
  available: boolean;
  /** 不可用原因说明 */
  unavailableReason?: string;
  /** 是否为演示模型（回答为演示数据） */
  isDemo: boolean;
}

/** 设置：单个模型条目（不含密钥，只有是否已设置） */
export interface ModelConfigEntry {
  id: string;
  label: string;
  protocol: 'chat_completions';
  base_url: string;
  model: string;
  chat_token_parameter: 'max_tokens' | 'max_completion_tokens';
  timeout_seconds: number;
  max_output_tokens: number;
  /** 服务端解析出的主机名，界面用于快速辨认 */
  host: string;
  /** 是否已设置密钥（密钥本身永远不回传前端） */
  hasKey: boolean;
}

export interface SettingsSnapshot {
  version: number;
  activeModelId: string;
  models: ModelConfigEntry[];
}

/** 保存时只提交可编辑字段 */
export type ModelConfigInput = Omit<ModelConfigEntry, 'host' | 'hasKey'>;

export type MessageRole = 'user' | 'assistant';

export type MessageStatus =
  | 'pending' // 已发送，等待首个响应
  | 'streaming' // 流式生成中
  | 'done'
  | 'cancelled'
  | 'error';

/** 研究模式的工作流程阶段 */
export type ResearchStage = 'collect' | 'compare' | 'synthesize';

export interface ResearchProgress {
  stage: ResearchStage;
  /** 已完成的阶段 */
  completed: ResearchStage[];
}

export interface EventContextRef {
  eventId: string;
  title: string;
  category: NewsCategoryId;
  occurredAt: string;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  createdAt: string;
  status: MessageStatus;
  /** 本条回答实际使用的模型与模式（仅 assistant） */
  usedModelId?: string;
  usedModelDisplayName?: string;
  usedMode?: ChatMode;
  /** 是否演示回答 */
  isDemo?: boolean;
  /** 错误信息（status === 'error'） */
  errorMessage?: string;
  /** 研究模式进度（流式期间更新） */
  researchProgress?: ResearchProgress;
  /** 附加到该用户消息的新闻事件上下文 */
  attachedEvents?: EventContextRef[];
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
}

export interface ChatRequest {
  conversationId: string;
  modelId: string;
  mode: ChatMode;
  /** 完整消息历史（role/content），由请求构建层生成 */
  messages: { role: 'system' | 'user' | 'assistant'; content: string }[];
  /** 模式 → 请求参数映射后的配置 */
  maxOutputTokens: number;
}

/** 流式响应事件 */
export type ChatStreamEvent =
  | { type: 'delta'; text: string }
  | { type: 'research_progress'; progress: ResearchProgress }
  | { type: 'done' }
  | { type: 'error'; message: string };

// ---------------- 新闻时间线 ----------------

export type NewsCategoryId =
  | 'monetary_policy'
  | 'inflation_employment'
  | 'growth_activity'
  | 'fiscal_policy'
  | 'trade_geopolitics'
  | 'financial_markets'
  | 'energy_commodities'
  | 'tech_industry';

export interface NewsCategory {
  id: NewsCategoryId;
  label: string;
  /** 仅用于识别类别的颜色（CSS 变量名），不暗示利多利空 */
  colorVar: string;
}

export type RegionId = 'us' | 'cn' | 'eu' | 'jp' | 'global' | 'mideast' | 'other';

export type ImportanceLevel = 'high' | 'medium' | 'low';

/** 一级主题（画廊标签），由 config/topics.ts 配置 */
export type TopicId = 'policy' | 'macro_data' | 'markets' | 'trade_industry';

export interface Topic {
  id: TopicId;
  label: string;
}

/** 事件脉络：一组相关事件组成的一条时间线（画廊中的一张卡片） */
export interface EventThread {
  id: string;
  topicId: TopicId;
  title: string;
  summary: string;
  isDemo: boolean;
  /** 展示快照中该脉络保留的事件数 */
  eventCount?: number;
  /** 该主题抓取到的全部条数（大于 eventCount 时界面说明是抽样展示） */
  totalEvents?: number;
}

export interface NewsSource {
  name: string;
  /** 演示数据不提供伪造的有效链接，url 可缺失 */
  url?: string;
}

export interface NewsEvent {
  /** 稳定事件 ID */
  id: string;
  /** 事件发生时间（ISO 8601）；未知时为 null */
  occurredAt: string | null;
  /** 事件时间精度：未知时间需明确说明，不赋予误导性精度 */
  occurredAtPrecision: 'exact' | 'date_only' | 'unknown';
  /** 新闻发布时间（ISO 8601） */
  publishedAt: string;
  category: NewsCategoryId;
  region: RegionId;
  title: string;
  summary: string;
  /** 报道正文（有原文时保留，详情面板折叠展示） */
  body?: string;
  sources: NewsSource[];
  /** 数据提供时才有 */
  importance?: ImportanceLevel;
  /** 事件脉络 ID（同一脉络的事件相关联） */
  threadId?: string;
  /** 相关实体 */
  entities?: string[];
  /** 是否为演示数据 */
  isDemo: boolean;
  /**
   * 内容分层：有资料记录的事实 / 明确归属的主张 / Agent 解释。
   * 详情面板分区展示。
   */
  recordedFacts?: string[];
  attributedClaims?: { attribution: string; claim: string }[];
  agentInterpretation?: string;
}

export interface TimelineFilters {
  categories: NewsCategoryId[];
  regions: RegionId[];
  importance: ImportanceLevel[];
  keyword: string;
  /** 日期范围（ISO date, 含端点），null 表示不限制 */
  dateFrom: string | null;
  dateTo: string | null;
}
