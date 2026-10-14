// 归类规则的回归测试：固定样例 + 真实电报片段，防止规则改动后口径漂移。
import { describe, expect, it } from 'vitest';
import {
  classify,
  classifyImportance,
  classifyRegion,
  deriveSummary,
  deriveTitle,
  extractEntities,
  isDroppable,
} from './rules.mjs';

const item = (patch = {}) => ({
  id: 1,
  ctime: 1791900000,
  content: '财联社10月13日电，某条电报正文。',
  level: 'C',
  subjects: [],
  stock_list: [],
  ...patch,
});

describe('isDroppable', () => {
  it('丢弃提醒电报与投资日历栏目稿', () => {
    expect(isDroppable(item({ subjects: [{ subject_name: '提醒电报' }] }))).toBe(true);
    expect(isDroppable(item({ subjects: [{ subject_name: '投资日历' }] }))).toBe(true);
  });

  it('丢弃订阅类栏目稿（盘中宝/风口研报等）', () => {
    expect(isDroppable(item({ title: '【盘中宝】某公司订单饱满' }))).toBe(true);
    expect(isDroppable(item({ title: '【金牌纪要库】AI内容工业化拐点渐近' }))).toBe(true);
  });

  it('保留普通事件稿', () => {
    expect(isDroppable(item({ title: '美国8月非农就业人数意外大增16.2万人' }))).toBe(false);
  });

  it('通用栏目类 subject 不导致丢弃', () => {
    expect(isDroppable(item({ subjects: [{ subject_name: '环球市场情报' }] }))).toBe(false);
  });
});

describe('classify', () => {
  it('央行与利率相关 → 货币政策', () => {
    expect(classify('美联储主席鲍威尔表示，将维持政策利率不变')?.category).toBe('monetary_policy');
  });

  it('就业与物价 → 通胀与就业', () => {
    expect(classify('美国8月非农就业人数大增，失业率报4.1%')?.category).toBe('inflation_employment');
  });

  it('产需景气 → 增长与经济活动', () => {
    expect(classify('8月制造业PMI重回扩张区间，社会消费品零售同比增长')?.category).toBe('growth_activity');
  });

  it('财政与楼市政策 → 财政政策', () => {
    expect(classify('两部门：将个人住房贷款期限延长，专项债加快发行')?.category).toBe('fiscal_policy');
  });

  it('关税、地缘冲突 → 贸易与地缘政治', () => {
    expect(classify('以军称在加沙北部打死两名哈马斯指挥官')?.category).toBe('trade_geopolitics');
  });

  it('股债汇市场 → 金融市场', () => {
    expect(classify('美国30年期国债收益率升至5.34%，创2007年以来最高')?.category).toBe('financial_markets');
  });

  it('原油与大宗 → 能源与大宗商品', () => {
    expect(classify('布伦特原油期货跌幅扩大至3%')?.category).toBe('energy_commodities');
  });

  it('AI 与半导体 → 科技与产业', () => {
    expect(classify('英伟达发布基于2纳米制程的A20 Pro芯片')?.category).toBe('tech_industry');
  });

  it('完全不命中的电报不进入时间线', () => {
    expect(classify('某地举办社区志愿服务活动')).toBeNull();
  });

  it('返回命中的关键词，便于人工复核归类原因', () => {
    const got = classify('美联储宣布加息25个基点');
    expect(got?.hits).toContain('加息');
  });

  it('ASCII 关键词按词边界匹配，不误命中包含它的长词', () => {
    expect(classify('公司发布 AI 大模型')?.category).toBe('tech_industry');
    // AIRCRAFT 里的 AI 不应命中
    expect(classify('AIRCRAFT LEASING RATES ROSE')).toBeNull();
  });
});

describe('classifyRegion', () => {
  it('美国', () => {
    expect(classifyRegion('美国8月CPI同比增长3.4%').region).toBe('us');
  });

  it('中国', () => {
    expect(classifyRegion('我国8月社会消费品零售总额同比增长').region).toBe('cn');
  });

  it('中东优先于其他地区（同一条同时提到美国与以色列）', () => {
    expect(classifyRegion('美国呼吁以色列保持克制，加沙局势升级').region).toBe('mideast');
  });

  it('日本与韩国', () => {
    expect(classifyRegion('日本央行加息25个基点').region).toBe('jp');
    expect(classifyRegion('韩国KOSPI指数跌幅扩大至4%').region).toBe('jp');
  });

  it('无地区线索时归为 other，不臆测', () => {
    expect(classifyRegion('现货黄金短线走低，向下跌破4340美元/盎司').region).toBe('other');
  });
});

describe('classifyImportance', () => {
  it('央行行动为高', () => {
    expect(classifyImportance(item({ title: '日本央行加息25个基点' }), '日本央行加息25个基点').importance).toBe('high');
  });

  it('宏观数据发布为高', () => {
    expect(classifyImportance(item({}), '美国7月核心PCE环比增长0.2%，预估为0.1%').importance).toBe('high');
  });

  it('大幅涨跌（≥3%）为高，小幅涨跌不为高', () => {
    expect(classifyImportance(item({}), '布伦特原油期货跌幅扩大至3.2%').importance).toBe('high');
    expect(classifyImportance(item({}), '韩国KOSPI指数开盘下跌0.24%报6611点').importance).not.toBe('high');
  });

  it('涨停/连板等盘中情绪稿不升为高', () => {
    const got = classifyImportance(item({ title: '农业板块反复走强 新农股份2连板' }), '农业板块反复走强 新农股份涨停');
    expect(got.importance).toBe('medium');
  });

  it('有标题的正式稿件为中', () => {
    expect(classifyImportance(item({ title: '某公司发布年度报告' }), '某公司发布年度报告').importance).toBe('medium');
  });

  it('无标题且无线索的快讯为低', () => {
    expect(classifyImportance(item({}), '现货黄金短线走低，向下跌破4340美元/盎司').importance).toBe('low');
  });
});

describe('deriveTitle / deriveSummary', () => {
  it('有标题时直接用标题', () => {
    expect(deriveTitle(item({ title: '美国8月CPI同比增长3.4%' }))).toBe('美国8月CPI同比增长3.4%');
  });

  it('无标题时去掉「财联社X月X日电」前缀并取第一句', () => {
    const got = deriveTitle(item({ content: '财联社10月13日电，美国8月CPI同比增长3.4%，符合预期。后续关注。' }));
    expect(got).toBe('美国8月CPI同比增长3.4%，符合预期');
  });

  it('过长标题截断', () => {
    const long = '财联社10月13日电，' + '很长的内容'.repeat(20) + '。';
    expect(deriveTitle(item({ content: long })).length).toBeLessThanOrEqual(45);
  });

  it('摘要去掉标题方括号与电头', () => {
    const got = deriveSummary(
      item({ content: '【美国8月CPI同比增长3.4%】财联社10月13日电，美国劳工部数据显示，8月CPI同比增长3.4%。' }),
    );
    expect(got.startsWith('美国劳工部数据')).toBe(true);
  });
});

describe('extractEntities', () => {
  it('排除通用栏目 subject，保留主题名', () => {
    const got = extractEntities(
      item({ subjects: [{ subject_name: '环球市场情报' }, { subject_name: '中东冲突' }] }),
    );
    expect(got).toContain('中东冲突');
    expect(got).not.toContain('环球市场情报');
  });

  it('附带关联个股名，且不超过上限', () => {
    const got = extractEntities(
      item({ stock_list: [{ name: '震裕科技' }, { name: '甘肃能源' }] }),
      3,
    );
    expect(got).toContain('震裕科技');
    expect(got.length).toBeLessThanOrEqual(3);
  });
});
