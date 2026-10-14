import type { NewsCategory, NewsCategoryId } from '../types';

/**
 * 新闻类别配置（可配置、顺序即时间线行序）。
 * 颜色仅用于识别类别，不暗示利多或利空。
 */
export const NEWS_CATEGORIES: NewsCategory[] = [
  { id: 'monetary_policy', label: '货币政策', colorVar: '--cat-monetary' },
  { id: 'inflation_employment', label: '通胀与就业', colorVar: '--cat-inflation' },
  { id: 'growth_activity', label: '增长与经济活动', colorVar: '--cat-growth' },
  { id: 'fiscal_policy', label: '财政政策', colorVar: '--cat-fiscal' },
  { id: 'trade_geopolitics', label: '贸易与地缘政治', colorVar: '--cat-trade' },
  { id: 'financial_markets', label: '金融市场', colorVar: '--cat-markets' },
  { id: 'energy_commodities', label: '能源与大宗商品', colorVar: '--cat-energy' },
  { id: 'tech_industry', label: '科技与产业', colorVar: '--cat-tech' },
];

export const CATEGORY_MAP: Record<NewsCategoryId, NewsCategory> = Object.fromEntries(
  NEWS_CATEGORIES.map((c) => [c.id, c]),
) as Record<NewsCategoryId, NewsCategory>;

/** 展示时区（明确显示，默认 Asia/Shanghai） */
export const DISPLAY_TIMEZONE = 'Asia/Shanghai';
