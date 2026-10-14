import type { NewsCategoryId, Topic, TopicId } from '../types';

/**
 * 一级主题（时间线画廊顶部的标签）。顺序即标签顺序。
 * 目前是静态配置；以后可改为从本地数据库或配置文件读取，只需替换此处导出。
 */
export const TOPICS: Topic[] = [
  { id: 'policy', label: '政策' },
  { id: 'macro_data', label: '宏观数据' },
  { id: 'markets', label: '市场与商品' },
  { id: 'trade_industry', label: '贸易与产业' },
];

export const TOPIC_MAP: Record<TopicId, Topic> = Object.fromEntries(TOPICS.map((t) => [t.id, t])) as Record<
  TopicId,
  Topic
>;

/** 未归入脉络的零散事件按类别映射到主题 */
export const CATEGORY_TOPIC: Record<NewsCategoryId, TopicId> = {
  monetary_policy: 'policy',
  fiscal_policy: 'policy',
  inflation_employment: 'macro_data',
  growth_activity: 'macro_data',
  financial_markets: 'markets',
  energy_commodities: 'markets',
  trade_geopolitics: 'trade_industry',
  tech_industry: 'trade_industry',
};
