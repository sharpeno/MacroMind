// 财联社电报 → 新闻事件的归类规则（纯函数，可单独测试与审计）。
//
// 设计原则：
// - 只做可复核的关键词归类，不使用模型推断；命中词一并写入事件（matchedTerms），
//   便于人工抽查某条事件为什么被归到某个类别。
// - 类别颜色只表示类别，不表示利多利空（沿用界面既有约定）。
// - 事件发生时间未知：财联社电报只提供发布时间，故 occurredAt = null、
//   occurredAtPrecision = 'unknown'，不臆造事件时间。
// - 分类只覆盖 8 个宏观类别的关键词；完全不命中的电报直接丢弃，不做兜底归类。

/** 类别关键词（命中即计分，取分值最高者） */
export const CATEGORY_TERMS = {
  monetary_policy: [
    '央行', '美联储', '加息', '降息', '降准', '货币政策', '利率决议', '议息', '政策利率',
    '联邦基金利率', 'LPR', 'MLF', '逆回购', '公开市场操作', '中期借贷便利', '再贷款', '再贴现',
    '存款准备金', '缩表', '购债', '量化宽松', '点阵图', '货币政策报告', '鲍威尔', '欧洲央行', '拉加德',
    '日本央行', '英国央行', '韩国央行', '加拿大央行', '澳洲联储', '政策声明', '货币政策委员会',
    '降息预期', '加息预期', '利率路径', '收益率曲线控制', '央行行长',
  ],
  inflation_employment: [
    'CPI', 'PPI', '通胀', '通货膨胀', '核心通胀', '核心CPI', '核心PCE', 'PCE', '物价',
    '非农', '就业', '失业率', '薪资', '工资', '平均时薪', '初请失业金', '职位空缺', 'JOLTS',
    '裁员', '招聘', '劳动力市场', '就业数据', '就业报告', '通胀预期', '消费者物价', '生产者物价',
    '就业市场', '失业救济', '劳动参与率',
  ],
  growth_activity: [
    'GDP', 'PMI', '采购经理', '制造业PMI', '服务业PMI', '工业增加值', '工业产出', '规模以上工业',
    '社会消费品零售', '零售销售', '固定资产投资', '经济增速', '经济增长', '经济活动', '经济复苏',
    '经济数据', '景气度', '产能利用率', '消费者信心', '企业景气', '用电量', '铁路货运', '经济前景',
    '增长预期', '经济下行', '经济衰退', '滞胀', '商业活动', '订单指数', '产出指数',
  ],
  fiscal_policy: [
    '财政', '财政部', '赤字', '专项债', '特别国债', '地方债', '超长期特别国债', '税收', '减税',
    '退税', '政府支出', '一般公共预算', '转移支付', '贴息', '财政支出', '国常会', '国务院常务会议',
    '财政政策', '以旧换新', '消费券', '化债', '债务置换', '城投', '基建投资', '基础设施投资',
    '楼市政策', '限购', '住房贷款', '住房公积金', '房贷利率', '收购存量', '房地产融资', '保交楼',
    '政策性开发性金融工具', '增量政策', '稳增长政策',
  ],
  trade_geopolitics: [
    '关税', '贸易', '出口管制', '制裁', '实体清单', '反倾销', '反补贴', '地缘', '冲突', '战争',
    '袭击', '停火', '军事', '军演', '导弹', '外交', '外交部', '会晤', '访问', '峰会', '大选',
    '选举', '谈判', '协议签署', '以色列', '伊朗', '哈马斯', '加沙', '中东', '俄乌', '俄罗斯',
    '乌克兰', '朝鲜', '台海', '台湾', '南海', 'WTO', '贸易协定', '脱钩', '供应链安全', '进出口',
    '出口', '进口', '港口', '航运', '红海', '胡塞', '曼德海峡', '霍尔木兹', '领海', '边境',
  ],
  financial_markets: [
    'A股', '上证指数', '深证成指', '创业板指', '科创50', '恒生指数', '恒生科技', '纳斯达克',
    '标普500', '道琼斯', '美股', '港股', '欧股', '日经', '债券收益率',
    '国债收益率', '美元指数', '汇率', '人民币汇率', '券商', '银行股', '保险股', '基金',
    '北向资金', '沪深港通', '成交额', '涨停', '跌停', '融资余额', '股债', '信用债', '可转债',
    '比特币', '市场情绪', '风险偏好', '指数期货', '回购利率', '银行间市场',
  ],
  energy_commodities: [
    '原油', '布伦特', 'WTI', '油价', '石油', 'OPEC', '减产', '增产', '天然气', 'LNG', '煤炭',
    '黄金', '白银', '铜', '铝', '镍', '锂', '稀土', '铁矿石', '钢材', '螺纹钢', '大豆', '小麦',
    '玉米', '农产品', '大宗商品', '商品价格', '燃料油', '成品油', '炼油', '库存', '钻机',
    '电力', '光伏', '风电', '储能', '铀', '碳酸锂', '磷酸铁锂', '页岩油',
  ],
  tech_industry: [
    '人工智能', 'AI', '芯片', '半导体', '算力', '数据中心', '机器人', '人形机器人', '大模型',
    '存储', '光刻', '晶圆', '英伟达', '台积电', '华为', '苹果', '特斯拉', '新能源汽车',
    '锂电池', '医药', '创新药', '生物医药', '船舶', '航天', '商业航天', '卫星', '核电',
    '可控核聚变', '量子', '5G', '6G', '通信', '智能手机', '消费电子', '自动驾驶', '低空经济',
    '先进制造', '设备更新', 'Meta', 'Facebook', '微软', '谷歌', '亚马逊', 'AMD', '英特尔',
    'OpenAI', 'Anthropic', 'xAI', '社交平台', '信息流', '云计算', '云服务', '软件', '开源',
    '大语言模型', '多模态', '智能体', '终端设备', '可穿戴', 'AR', 'VR', '折叠屏', '操作系统',
    '互联网平台', '电商', '短视频', '游戏行业', '生物技术', '基因', '医疗器械', '工程机械',
    '光伏组件', '风电装机', '电网投资', '核电装机',
  ],
};

/** 地区关键词（命中数最多者胜出；并列时按 REGION_PRIORITY 顺序） */
export const REGION_TERMS = {
  us: [
    '美国', '美联储', '鲍威尔', '白宫', '特朗普', '拜登', '劳工部', '非农', '美债', '美股',
    '标普500', '纳斯达克', '道琼斯', '纽约联储', '美国国会', '参议院', '众议院', '美国财政部',
    '耶伦', '美国商务部', 'EIA', '美国能源信息署', '美国农业部', '美国证监会', 'SEC', '美元指数',
    '美国经济', '美联储官员',
  ],
  cn: [
    '中国', '我国', '国内', '央行', '人民银行', '国务院', '国常会', '发改委', '财政部', '商务部',
    '证监会', '金融监管总局', '住建部', '统计局', '工信部', '国资委', '海关总署', '税务总局',
    'A股', '沪深', '上证', '深证', '创业板', '科创板', '港股', '香港', '人民币', '中债', '国新办',
    '上海', '北京', '深圳', '广东', '江苏', '浙江', '中汽协', '中铁总', '国铁',
  ],
  eu: [
    '欧元区', '欧洲央行', 'ECB', '欧盟', '德国', '法国', '意大利', '西班牙', '荷兰', '比利时',
    '英国', '英国央行', '英格兰银行', '拉加德', '欧洲理事会', '欧委会',
  ],
  jp: [
    '日本', '日本央行', '日经', '日元', '东京', '日本银行', '日本政府', '日本财务省',
    '韩国', '韩国央行', '韩元', '首尔', 'KOSPI', '三星', 'SK海力士', '现代汽车',
  ],
  mideast: [
    '中东', '以色列', '伊朗', '哈马斯', '加沙', '沙特', '胡塞', '也门', '黎巴嫩', '真主党',
    '叙利亚', '巴勒斯坦', '阿联酋', '卡塔尔', '伊拉克', '红海', '霍尔木兹', '曼德海峡', '土耳其',
    '埃及', '约旦', '特拉维夫', '德黑兰',
  ],
  global: [
    '全球', '世界', 'G20', 'IMF', '世界银行', '联合国', '经合组织', 'OECD', 'WTO', '国际能源署',
    '欧元', '新兴市场', '发达国家', '发展中经济体',
  ],
};

/** 地区并列时的优先顺序（越靠前越优先） */
export const REGION_PRIORITY = ['mideast', 'us', 'cn', 'eu', 'jp', 'global'];

/** 重要程度：高——政策决定、央行行动、重大地缘与剧烈价格变动 */
const HIGH_TERMS = [
  '加息', '降息', '降准', '利率决议', '议息', '政策利率', '货币政策', '宣布', '决定',
  '否决', '签署', '生效', '出台', '印发', '停火', '宣战', '开战', '制裁', '关税',
  '出口管制', '实体清单', '袭击', '爆炸', '空袭', '封锁', '非农', 'CPI', 'PPI', 'PCE', 'GDP',
  'PMI', '失业率', '创历史新高', '历史新高', '创新高', '创历史新低', '暴跌', '暴涨', '熔断',
  '违约', '债务上限', '加息落地', '紧缩', '宽松',
];

/** 数据发布类（与 HIGH_TERMS 一起构成「高」的判定） */
const DATA_PATTERNS = [/(同比|环比)[^。；]{0,12}?(增长|下降|上升|回落|扩大|收窄)/, /(预期|预估|预测)为/];

/** 重要程度：中——有标题的正式电报，或明确的数据发布 */
const MEDIUM_TERMS = ['数据显示', '环比', '同比', '预估', '预期', '统计', '报告显示', '机构'];

// ---------------- 噪声过滤 ----------------

/** 订阅类栏目名（推广/研报摘要，不是事件） */
const PROMO_PREFIXES = [
  '盘中宝', '风口研报', '机构调研', '电报解读', '大佬持仓跟踪', '研选', '机构龙虎榜解读',
  '财联社早知道', '公告全知道', '季报高增长', '金牌纪要库',
];

/** 格式/栏目字段的 subject（不构成事件主题，也不进实体） */
const GENERIC_SUBJECTS = new Set([
  '环球市场情报', '期货市场情报', '盘面直播', 'A股公告速递', 'A股风险提示公告', '提醒电报',
  '投资日历', '时政新闻播报', '新闻联播', 'A股上市公司业绩巡礼', 'A股上市公司业绩预告',
  '互动平台精选', '券商策略', '经济数据及解读', '宏观新闻', '宏观流动性', '科创板公司面面观',
]);

/** 完全丢弃的电报（栏目稿、非事件） */
const DROP_SUBJECTS = new Set(['提醒电报', '投资日历', '新闻联播', '时政新闻播报']);

const reChar = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

/** 命中关键词统计：返回命中的不重复关键词 */
export function matchTerms(text, terms) {
  const hits = [];
  for (const term of terms) {
    // 纯 ASCII 关键词加词边界，避免 "AI" 命中 "AIR" 之类；中文关键词直接子串匹配
    const pattern = /^[\x20-\x7e]+$/.test(term)
      ? new RegExp(`(?<![A-Za-z0-9])${reChar(term)}(?![A-Za-z0-9])`, 'i')
      : null;
    if (pattern ? pattern.test(text) : text.includes(term)) hits.push(term);
  }
  return hits;
}

/** 是否为应丢弃的栏目稿 */
export function isDroppable(item) {
  const subjects = (item.subjects ?? []).map((s) => s.subject_name);
  if (subjects.some((s) => DROP_SUBJECTS.has(s))) return true;
  const text = item.title || item.content || '';
  const m = /^【([^】]{2,10})】/.exec(text.trim());
  if (m && PROMO_PREFIXES.some((p) => m[1].startsWith(p))) return true;
  return false;
}

/** 归类到 8 个类别之一；无命中返回 null（该电报不进时间线） */
export function classify(text) {
  let best = null;
  for (const [category, terms] of Object.entries(CATEGORY_TERMS)) {
    const hits = matchTerms(text, terms);
    if (hits.length === 0) continue;
    if (!best || hits.length > best.hits.length) best = { category, hits };
  }
  return best;
}

/** 判定地区 */
export function classifyRegion(text) {
  let best = null;
  for (const [region, terms] of Object.entries(REGION_TERMS)) {
    const hits = matchTerms(text, terms);
    if (hits.length === 0) continue;
    const better =
      !best ||
      hits.length > best.hits.length ||
      (hits.length === best.hits.length &&
        REGION_PRIORITY.indexOf(region) < REGION_PRIORITY.indexOf(best.region));
    if (better) best = { region, hits };
  }
  return best ?? { region: 'other', hits: [] };
}

/** 是否有标题（财联社有标题的电报一般是正式稿件，无标题的多为快讯） */
export function hasTitle(item) {
  return typeof item.title === 'string' && item.title.trim().length > 0;
}

/**
 * 判定重要程度：高 / 中 / 低。返回等级与命中依据（写入事件的审计字段）。
 *
 * 口径（可复核，不用模型判断）：
 * - 高：命中硬信号词（央行行动、重大地缘、制裁关税、宏观数据名）、
 *   数据发布句式，或幅度 ≥3% 的涨跌表述。
 * - 中：有标题的正式稿件。
 * - 低：其余快讯（多为盘中价格、单条转述）。
 * 盘中涨跌停/连板等交易情绪稿单独排除，不因“涨停”二字升为高。
 */
export function classifyImportance(item, text) {
  const reasons = [];
  const high = matchTerms(text, HIGH_TERMS);
  if (high.length > 0) reasons.push(`命中:${high.slice(0, 3).join('/')}`);
  if (DATA_PATTERNS.some((re) => re.test(text))) reasons.push('数据发布');

  // 涨跌幅语境 + 绝对值 ≥3%，避免把「涨0.24%」或无关的两位数百分比当成大幅变动
  const pcts = [...text.matchAll(/(涨|跌|升|降|上行|下行|变动|扩大|收窄)[^%\n]{0,10}?(\d+(?:\.\d+)?)\s?%/g)];
  const pctHigh = pcts.some((m) => Number(m[2]) >= 3);
  if (pctHigh) {
    reasons.push('大幅变动');
    return { importance: 'high', reasons };
  }

  // 有硬信号或数据发布：一般为高；但盘中交易情绪稿（涨停/连板/异动）降为中
  if (reasons.length > 0) {
    if (/涨停|跌停|连板|异动|封板|打板/.test(text)) reasons.push('交易情绪稿降级');
    return { importance: reasons.includes('交易情绪稿降级') ? 'medium' : 'high', reasons };
  }

  if (hasTitle(item)) return { importance: 'medium', reasons: ['正式稿件'] };
  const medium = matchTerms(text, MEDIUM_TERMS);
  if (medium.length > 0) return { importance: 'medium', reasons: [`命中:${medium.slice(0, 2).join('/')}`] };
  return { importance: 'low', reasons: [] };
}

/** 相关实体：非栏目类主题名 + 关联个股名 */
export function extractEntities(item, limit = 5) {
  const out = [];
  for (const s of item.subjects ?? []) {
    if (GENERIC_SUBJECTS.has(s.subject_name)) continue;
    if (!out.includes(s.subject_name)) out.push(s.subject_name);
  }
  const stocks = (item.stock_list ?? []).map((s) => s.name).filter(Boolean);
  for (const name of stocks) {
    if (out.length >= limit) break;
    if (!out.includes(name)) out.push(name);
  }
  return out.slice(0, limit);
}

/** 归属主张：从正文抽出「某主体表示/称/宣布……」的表述（可复核，不做改写） */
export function extractClaims(content, limit = 3) {
  const out = [];
  // 只取「主体 + 明确表态动词」的表述；把「认为/预计」这类判断留给原文，避免误当引述
  const re = /([一-龥A-Za-z0-9·]{2,16})(表示|宣布|称|指出|强调|回应|警告|呼吁|要求|决定|披露|透露)/g;
  for (const m of content.matchAll(re)) {
    const clauseEnd = content.slice(m.index).search(/[。；]/);
    const clause = (clauseEnd === -1 ? content.slice(m.index) : content.slice(m.index, m.index + clauseEnd + 1)).trim();
    if (clause.length < 10 || clause.length > 140) continue;
    // 噪声：记者提问、转述媒体的口吻、没有具体主体的泛指
    if (/记者提问|记者问|据悉|据了解|投资者需|市场预计|报道称，?$/.test(clause)) continue;
    const attribution = m[1]
      .replace(/^(据|据报|据报道|援引|另据)/, '')
      .replace(/^(报道|消息)/, '')
      .trim();
    if (attribution.length < 2 || /^(记者|媒体|报道|消息)$/.test(attribution)) continue;
    if (out.some((c) => c.claim === clause)) continue;
    out.push({ attribution, claim: clause });
    if (out.length >= limit) break;
  }
  return out;
}

/** 去掉零宽字符、软连字符与多余空白（抓取到的正文里偶有出现） */
export function cleanText(text) {
  return text
    .replace(/[\u200b-\u200f\u202a-\u202e\ufeff\u00ad]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

/** 无标题电报的标题：去掉「财联社X月X日电，」前缀后取第一句 */
export function deriveTitle(item) {
  if (item.title) return cleanText(item.title);
  const raw = cleanText(item.content || '');
  const body = raw.replace(/^财联社\s?\d{1,2}月\d{1,2}日电[，,]/, '').trim();
  // 去掉正文开头的标点（有的电报以「，」「；」起头），避免标题以标点开场
  const first = (body.split(/[。；]/)[0] ?? body).replace(/^[，,、；;：:\s]+/, '').trim();
  return first.length > 44 ? `${first.slice(0, 44)}…` : first;
}

/** 摘要：正文去掉标题方括号前缀后的前一段 */
export function deriveSummary(item, maxLen = 200) {
  const raw = cleanText(item.content || '');
  const stripped = raw
    .replace(/^【[^】]{2,30}】/, '')
    .replace(/^财联社\s?\d{1,2}月\d{1,2}日电[，,]/, '')
    .replace(/^[，,、；;：:\s]+/, '')
    .trim();
  const body = stripped || raw;
  return body.length > maxLen ? `${body.slice(0, maxLen)}…` : body;
}

/** 影响一条电报重要程度的排序权重（用于每日每类别截断时取前 N 条） */
export const IMPORTANCE_RANK = { high: 0, medium: 1, low: 2 };
