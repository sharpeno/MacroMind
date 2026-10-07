from pathlib import Path
import re, json, hashlib, collections

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'golden_sample_002'
OUT.mkdir(exist_ok=True)
BASE=Path('G:/BilibiliDown.v6.41.release/download/有何高见9527')
PREFIX='《第七百六八期》当前背景下如何深刻认识中国金融结构变迁-p01-16'
CUTOFF='2026-09-21T10:32:21+08:00'
RETRIEVED='2026-09-24'
def dump(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''): h.update(b)
    return h.hexdigest()
raw_srt=(BASE/(PREFIX+'.srt')).read_text(encoding='utf-8-sig')
raw_txt=(BASE/(PREFIX+'.自动转写.txt')).read_text(encoding='utf-8-sig')
cues=[]
for block in re.split(r'\n\s*\n',raw_srt.strip()):
    lines=block.splitlines(); start,end=lines[1].split(' --> ')
    cues.append(dict(cue_id=int(lines[0]),start=start,end=end,text='\n'.join(lines[2:]),source_id='SRC03'))
def evidence(a,b=None):
    b=b or a
    return dict(source_id='SRC03',cue_start=a,cue_end=b,start=cues[a-1]['start'],end=cues[b-1]['end'],raw_text=''.join(c['text'] for c in cues[a-1:b]),alignment='ASR cue boundary; not audio-verified')
boundaries=[(1,'文章时点、央行立场与外部加息'),(24,'紧缩情景、美元信用与短期策略'),(96,'债权人损失厌恶及二战历史类比'),(169,'文章结构与本期范围'),(191,'融资结构总论与直接/间接融资定义'),(232,'2013年分界、信任及2025年融资增量'),(277,'文章安抚功能与结构信息'),(300,'化债、成本叙事与谈判过程'),(390,'从融资分类变化推论化债成效'),(432,'平陆运河投资与政府信用信号'),(481,'企业融资比值、相对成本与国家信用空间'),(533,'存量结构、股票占比与未来比例'),(563,'银行利润、业务转型及职业选择'),(605,'信贷投向、机会识别与血液类比'),(656,'科技企业生命周期与非银行融资'),(697,'中美早期风险资本比较与汇率叙事'),(713,'人民币资本竞争结论与收束')]
segments=[]
for i,(a,topic) in enumerate(boundaries):
    b=boundaries[i+1][0]-1 if i+1<len(boundaries) else len(cues)
    segments.append(dict(segment_id=f'SG{i+1:02}',start=cues[a-1]['start'],end=cues[b-1]['end'],topic=topic,cue_start=a,cue_end=b,source_id='SRC03',boundary_precision='cue-level; some 20-second cues contain multiple topics'))
def segment(a): return next(s['segment_id'] for s in segments if s['cue_start']<=a<=s['cue_end'])

# Fields: ID | cue range | proposition | type | reference time | population | quantifier | expressed certainty | evidence sources | veracity rationale
ROWS='''
C001|1|潘功胜在9月13日发表本期讨论的求是文章。|factual|2026-09-13（年份依本期语境）|one_article|one|肯定陈述|SRC06|uncertain:网页标示9月16日；网址路径9月15日也不能代替发布时间，未确认是否另有提前版本。
C002|1-2|美联储刚刚加息。|factual|2026-09 视频发布前|Federal_Reserve|one|肯定陈述|SRC09|verified:9月16日FOMC公告支持加息事实。
C003|17|日本央行也已加息。|factual|2026-09 视频发布前|Bank_of_Japan|one|肯定陈述|SRC10|likely_true:9月18日已宣布，9月24日生效；只有按宣布口径成立。
C004|18|欧洲央行也加息。|factual|2026-09 视频发布前|ECB（欧洲依语境解析）|one|肯定陈述|SRC11|verified:9月10日决定加息，9月16日生效。
C005|2-3|潘功胜写文章时应已深刻把握美联储的处境及选择。|motive_attribution|文章写作时，确切日期unknown|Pan_Gongsheng|one|我认为；应该；非常非常清楚|none|unverifiable:同为央行行长不能证明私人认知或写作意图。
C006|8-12|文章没有直接写外国却为中国之外金融系统变化提供背景定调。|interpretive|本篇文章|one_article|one|我觉得；可能|SRC06|uncertain:是9527的潜台词解读，不能归给官方。
C007|20-23|2024年以来的宽松环境已经转为紧缩。|interpretive|2024至2026-09|global_financial_environment|unknown|彻底反过来|SRC09,SRC10,SRC11|uncertain:部分央行加息不足以判定全球金融条件总体转向。
C008|21|9527自称此前讲过八年宽松、两年紧缩的美元潮汐节奏。|factual|此前unknown|9527_prior_content|one|之前聊过|none|unverifiable:未定位历史节目，不创建历史Forecast。
C009|21-23|美元潮汐的通常节奏是八年宽松、两年紧缩。|interpretive|历史区间unknown|US_monetary_cycles|unknown|一般化陈述|none|uncertain:没有周期定义和统计序列。
C010|25|大家普遍认为此次紧缩不会持续很久。|factual|视频录制时unknown|unspecified|majority|普遍|none|unverifiable:无人群边界、调查时间和样本，不建ExpectationSnapshot。
C011|26-29|此次紧缩可能持续很长时间。|forecast|视频之后unknown|US_monetary_policy|unknown|如果；可能|none|uncertain:情景讨论而非基准预测，时窗未知。
C012|30-31|worker所指时代美联储曾一下子加息到20%。|factual|历史时期unknown（疑指沃尔克时期）|Federal_Reserve|one|一下子；从未有先例|none|uncertain:人名、利率种类、渐进还是单次均需核验，不接受数字纠错。
C013|33-35|现有美债规模使美联储不能把利率升到此前所述高位。|causal|当下及假设高利率情景|US_federal_debt|unknown|现在的说法|none|uncertain:9527转述的未署名观点；需债务期限、再定价及财政约束模型。
C014|37-41|若利率升到所讨论高位，债务利息成本会超过美国GDP。|counterfactual|假设高利率情景|US_federal_debt|unknown|就已经比GDP更高|none|uncertain:缺债务口径、实际付息率、GDP和再定价速度；不能当现状数据。
C015|38-48|暴力加息可能首先损害美元信用。|forecast|未来条件情景|USD_credit|unknown|可能最先|none|uncertain:财政信用与利差吸引力方向可能相反，未给判别条件。
C016|56-60|若竞争对手更差且缺替代品，美国仍能保持相对优势。|causal|一般条件情景|US_and_alternatives|unknown|只要；就可能|none|uncertain:相对优势机制可讨论，但竞争者变差与替代约束未被证明。
C017|66-68|美国可能从一开始就没有偿还债务的打算。|motive_attribution|债务形成时unknown|US_government|unknown|有没有可能|none|unverifiable:猜测意图，且滚续不等于拒绝履约。
C018|69-82|美国可能利用激进加息的短期收益与长期副作用的时差过关。|forecast|未来unknown|US_policy_makers|unknown|是不是可能选择|none|uncertain:缺行为证据，收益主体与成本承担者混用。
C019|96-98|美国在提高利率时仍不停扩表。|factual|本轮紧缩，区间unknown|Federal_Reserve|unknown|不停|SRC09|uncertain:维持充足准备金不等于已验证持续扩表，需资产负债表序列。
C020|99-102|加息同时扩表会加快美债规模膨胀。|forecast|未来unknown|US_federal_debt|unknown|会|none|uncertain:央行资产负债表与财政债务不是同一变量，缺传导机制。
C021|103-113|大量美债持有者可能因损失厌恶而更容忍美国政策风险。|forecast|未来unknown|large_Treasury_holders|unknown|会不会；可能|none|uncertain:也可能减持、对冲或要求更高风险溢价。
C022|114-122|英法容忍德国挑衅是为将其引向对抗苏联。|motive_attribution|二战前|UK_and_France_governments|unknown|因果肯定|none|uncertain:单一动机解释，未提供历史档案。
C023|128-136|一战损失使二战前英法社会极度厌战。|causal|一战后至二战前|UK_and_France_societies|all|肯定都不想再打仗|none|uncertain:方向可讨论，人口全称与具体因果未获验证。
C024|136-142|英法对德国闪击波兰采取视而不见态度。|factual|1939 波兰战役语境|UK_and_France_governments|all|都是睁只眼闭只眼|none|uncertain:需区分宣战、军事实效、此前绥靖，并需音频确认原句。
C025|143-147|张伯伦在战争已打响后与希特勒谈判并回国宣称带来和平。|factual|所指谈判日期unknown|Neville_Chamberlain|one|战争都已经打响|SRC14|likely_false:如指慕尼黑协议，则1938年在波兰战争之前；地名和引语也待听。
C026|151-157|美联储可能像类比中的行动者一样利用对方损失厌恶取得优势。|forecast|未来unknown|Federal_Reserve_and_counterparties|unknown|可不可能|none|uncertain:历史类比不能证明当代意图或效果。
C027|159-168|识别上述外部风险才是该文章未明说而值得关注的逻辑。|interpretive|本篇文章|one_article|one|真正值得关注|SRC06|uncertain:9527解读，未见文章直接论述该阴谋式策略。
C028|194-195|央行行长首先必定站在银行利益立场上。|motive_attribution|本篇文章语境|central_bank_governor|one|肯定首先|none|unverifiable:央行和商业银行职责不能等同，缺个人意图证据。
C029|196-199|中国以银行贷款为主体的间接融资占比近年来下降。|factual|近年来unknown|China_financing|unknown|持续|SRC06|likely_true:原文方向相符，原始统计表未独立复算。
C030|200-202|中国直接融资占比近年来上升。|factual|近年来unknown|China_financing|unknown|稳步|SRC06|likely_true:原文方向相符；不代表纯民间股权融资。
C031|207-210|2013年以前新增间接融资占社融增量超过80%。|factual|2013年以前，起点unknown|China_TSF_increment|unknown|80%以上|SRC06|likely_true:引用相符；间接融资不能完全等同贷款。
C032|212-219|直接融资就是资金需求方向资金持有方借款。|interpretive|概念定义|direct_financing|all|定义式|none|uncertain:债权情形有解释力，但把股权融资概括为借款不充分。
C033|217|发行股票相当于发债券、打借条。|interpretive|概念定义|equity_financing|all|也是；相当于|none|likely_false:股权与债权偿付义务不同；仍须音频排除识别错误。
C034|222-231|间接融资由银行连接储蓄者和借款企业并赚取息差。|interpretive|一般银行业务|commercial_banks|unknown|定义式|none|likely_true:是简化描述，不是完整货币创造或风险模型。
C035|232-244|过去民间融资困难源于互不信任和缺少合适投资市场。|causal|2013年以前语境|China_private_financing|unknown|非常非常难|none|uncertain:信任机制合理但未排除监管、市场基础设施等因素。
C036|245-255|2013年美国发生次贷危机次生灾害，使中国获得金融市场发展空间。|causal|2013年|China_US_financial_markets|unknown|肯定陈述|none|uncertain:事件界定不清，因果未证实；需拆出2013事件事实核验。
C037|256-257|2025年社融增量为35.6万亿元。|factual|2025全年|China_TSF_increment|unknown|数值陈述|SRC06|likely_true:与文章一致，但年度原始统计表尚未定位。
C038|258|2025年企业债、政府债和股票融资合计占社融增量约47%。|factual|2025全年|China_TSF_increment|unknown|约47%|SRC06|likely_true:引用口径相符；不是股权占47%。
C039|259|2025年债券和股票融资合计增量首次超过贷款。|factual|2025全年及此前历史|China_TSF_increment|one|首次|SRC06|likely_true:文章有此表述，首次仍需历史序列。
C040|260-269|贷款在新增融资中的占比从八成以上降到47%以下，几乎腰斩。|comparative|2013年前 对比2025|China_loan_increment|unknown|几乎腰斩|SRC06|uncertain:起点是间接融资占比，终点是贷款比较上界，口径不严格相同。
C041|270-276|上述增量变化代表银行间接融资渠道已退居次席。|interpretive|2025|China_financing_channels|unknown|已经|SRC06|uncertain:增量单年与存量主导地位不同，且直接融资包含政府债。
C042|277-286|最近社融扩张不好且经常负增长。|factual|最近一段时间unknown|China_TSF|unknown|老是负增长|none|uncertain:存量、月增量、同比增长均未明确，转写涉容涉零待听。
C043|277-299|文章写作背景是为不佳金融数据稳定人心。|motive_attribution|文章写作时|one_article|one|稳稳态度；稳定人心|none|unverifiable:9527对动机的归因，不是官方承认的目的。
C044|287-299|该文章的结构分析价值超出安抚需求。|interpretive|本篇文章|one_article|one|质量非常扎实|none|unverifiable:评价性判断；与安抚动机并不逻辑矛盾。
C045|300-306|政府债融资与隐性债务置换推高债券占比。|causal|过去几年unknown|China_financing|unknown|使|SRC06,SRC12|likely_true:分类替代机制有支持，定量贡献未分解。
C046|300-306|银行核销不良贷款促使贷款占比下降。|causal|过去几年unknown|China_financing|unknown|使|SRC06|uncertain:需区分贷款存量核销、社融增量中核销项和统计处理。
C047|326-332|所讨论地方政府借债成本约4%甚至5%。|factual|过去unknown|local_government_related_borrowing|some|有的；4%往上|none|uncertain:地区、平台、币种、期限不明确。
C048|333-342|由中央出面发债可以把成本压至2%以下。|counterfactual|假设置换场景|central_government_borrowing|unknown|可以；2%以下|none|uncertain:转写同时有20%、2%点几；还混合国债与地方专项债。
C049|333-338|中央可以在外边发行熊猫债。|interpretive|融资方式语境|central_government|one|无论；或者|none|uncertain:熊猫债用语、境内境外和发行人均需审核，不静默改成其他债种。
C050|343-346|以年化2%的债置换4%的债能降低付息压力。|counterfactual|假设相同本金置换|debtors|unknown|一下子释放很大负担|none|likely_true:静态利差方向成立，规模期限费用及折价未计，不证明实际全部实现。
C051|347-363|隐性债务合规与确权问题会增加重组过程成本。|causal|过去化债实践unknown|hidden_debt_workouts|many|很多；非常严重|none|uncertain:未列案件；过程成本概念不能验证规模强度。
C052|364-389|债务认定和重组结果受到历史私人关系及逐案谈判影响。|causal|过去至当前unknown|local_debt_workouts|unknown|完全取决于关系|none|uncertain:强因果与量词无案件证据，不能概括全部化债。
C053|390-399|过去隐债置换都是一事一议闭门谈判展期。|factual|过去几年unknown|hidden_debt_swaps|all|都是|SRC12|disputed:存在法定限额及债券置换机制，谈判不是排他解释；不能抹去可能存在的谈判。
C054|400-419|融资比例变化说明政府债务压力已骤减。|causal|过去几年至当前|China_government_debt|unknown|骤然|none|uncertain:分类变化不等于本金减少，也不充分测量现金流和偿付能力。
C055|415-419|过去隐性债务问题已经基本妥善解决。|interpretive|截至视频时|China_hidden_debt|nearly_all|基本妥善解决|SRC12|uncertain:历史政策存在不能验证截至2026年完成，需余额、违约和现金流证据。
C056|420-431|2023年美国金融机构曾预言中国债务大爆发。|factual|2023年|US_financial_institutions_unspecified|unknown|那些金融机构|none|unverifiable:未提供机构、报告或原句。
C057|420-431|到2026年已无人再提中国债务爆发问题。|factual|2026年最近|unspecified|all|已经没人提|none|uncertain:与紧邻的经常看到危言耸听有表面张力，但人群范围可能不同。
C058|432|9527自称前几天讨论过平陆运河。|factual|前几天unknown|9527_prior_content|one|我前几天|none|unverifiable:历史源未提供，不推建历史Forecast。
C059|433-437|推进长回收期大型工程体现政府决心与公信力。|interpretive|平陆运河建设时期|China_government|one|本身就代表|none|uncertain:项目推进也可能来自补贴或行政动员，公信力非直接观测量。
C060|438-440|平陆运河整体投资规模为700多亿元。|factual|项目建设投资预算|Pinglu_Canal|one|700多个亿|SRC07|likely_true:估算总投资727.3亿元支持数量级，非已完成决算。
C061|440-444|平陆运河每年创造五十多亿元综合社会效益。|factual|运营后预测年unknown|Pinglu_Canal|one|五十几个亿|SRC08|uncertain:来源是预计节约运输费用，不是已实现综合效益或项目现金收入。
C062|445-446|平陆运河按所述效益计算大概需要134年回本。|interpretive|假设静态回收|Pinglu_Canal|one|大概|none|uncertain:134可能是十三四的ASR；即便除法正确也不能以运输节约充当现金回款。
C063|447-458|平陆运河乐观估计也要三四十年才能回本。|forecast|投运后约30至40年|Pinglu_Canal|one|乐观估计；难得回本|none|uncertain:没有收入、费用、折现及爬坡模型，不能作为财务预测基准。
C064|458-474|平陆运河需大规模拓宽挖深河道并通过闸门保水。|factual|项目建设阶段|Pinglu_Canal|one|工程量巨大|SRC07|uncertain:工程总体存在，但具体水深水宽及水量说法未核验。
C065|475-480|长期建设决心所形成的信心是有效化债的关键。|causal|长期一般命题|government_creditors|unknown|真正有效的信心|none|uncertain:项目存在不等于偿债能力改善，更不证明既有隐债已解决。
'''
ROWS+='''
C066|481-486|剔除化债等因素后中国融资结构变化依然显著。|interpretive|过去几年unknown|China_financing|unknown|显著|SRC06|uncertain:原文表达一致，但没有给出剔除方法或分解表。
C067|487-488|企业债券融资增量与同期贷款增量之比在2023年为7%。|factual|2023年|China_corporate_financing|unknown|7%|SRC06|likely_true:文本有支持，分母是否企业贷款及期限口径需原始表。
C068|489|同一企业债融资与贷款增量之比在2026上半年接近20%。|factual|2026上半年|China_corporate_financing|unknown|近20%|SRC06|likely_true:首次读数清楚；后文重述转写损坏单独留Review。
C069|492-496|当前银行对优质项目贷款成本低且信贷条件宽松。|interpretive|视频时点|high_quality_borrowers|unknown|极宽松；打开绿灯|none|uncertain:优质项目非全部企业，无报价和审批数据。
C070|503-508|债券融资相对贷款增长表明直接融资成本比低息银行贷款还低。|causal|2023至2026上半年|China_corporate_financing|unknown|还要低|none|uncertain:数量比不能识别相对成本，受准入、期限和企业构成影响。
C071|509-515|国有银行间接融资占用国家信用资本。|interpretive|一般融资结构|state_owned_banks|unknown|国家信用担保|none|uncertain:隐性支持、显性担保及资本约束需分开，并非统一信用额度池。
C072|516-532|更多直接融资、较少银行担保将为国家未来举债释放空间。|causal|当前至未来|China_state_credit_capacity|unknown|很大；有利条件|none|uncertain:银行持债、承销、或有负债和政府债发行可能使风险仍回到银行或财政。
C073|532-533|贷款或间接融资占比下降时绝对值仍在增加。|factual|当前趋势，统计区间unknown|China_lending|unknown|不是绝对值；绝对值还在增加|none|uncertain:概念区分明确，但统计范围未给；与C094需核对时间口径。
C074|533-545|20世纪90年代初间接融资占社融存量接近100%。|factual|20世纪90年代金融市场建设早期|China_TSF_stock|nearly_all|接近百分之百|SRC06|likely_true:文章如此描述，历史社融回溯序列未独立复核。
C075|534-543|90年代融资几乎必须通过银行，是因为陌生人之间信用成本很高。|causal|20世纪90年代|China_nonkin_borrowers|nearly_all|所有；必须；除非亲戚朋友|none|uncertain:信任因素非排他解释，忽略制度与市场准入。
C076|546-549|2026年6月末间接融资占社融存量约三分之二。|factual|2026-06-30|China_TSF_stock|unknown|约三分之二|SRC06|likely_true:文章支持，待统计表复核。
C077|550|同期贷款余额占社融存量约60%。|factual|2026-06-30|China_TSF_stock|unknown|约60%|SRC06|likely_true:与间接融资不是同一指标。
C078|551|同期直接融资余额占社融存量约三分之一。|factual|2026-06-30|China_TSF_stock|unknown|约三分之一|SRC06|likely_true:文章支持；不可直接解释为民间风险资本。
C079|552|同期债券融资占社融存量约30%。|factual|2026-06-30|China_TSF_stock|unknown|约30%|SRC06|likely_true:需区分政府债和企业债。
C080|553-556|反推可得股票融资占比约10%。|interpretive|2026-06-30|China_TSF_stock|unknown|基本上10%左右|none|likely_false:若同分母且直接融资仅由债券与股票构成，1/3减30%约3.3个百分点；不是核实的股票观测值。
C081|557|中国融资结构已从间接融资主导转为直接与间接协调发展。|interpretive|截至2026-06|China_financing|unknown|已经|SRC06|uncertain:属于结构评价，协调没有可检验阈值。
C082|558-560|直接融资比重未来仍会继续积极扩大。|forecast|未来unknown|China_direct_financing|unknown|肯定还会|none|uncertain:趋势外推无窗口，不能等同官方目标。
C083|560-562|直接融资占三分之二、间接占三分之一是合理状态。|normative|未来理想状态|China_financing|unknown|我认为；应该|none|unverifiable:规范性比例主张，不冒充承诺达到该值的预测。
C084|563-568|许多银行从业者最近抱怨日子不好过。|factual|最近unknown|commercial_bank_employees|many|很多很多|none|unverifiable:无抽样、机构和收入数据。
C085|569-574|若结构趋势延续且不转型，银行整体盈利能力将继续下降。|forecast|未来unknown|commercial_banks|unknown|还会继续；除非|none|uncertain:占比不推出总利润，需净息差、规模、信用成本及证券业务。
C086|575-582|传统银行业务萎缩趋势非常确定。|forecast|未来unknown|traditional_bank_business|unknown|非常非常确定|none|uncertain:未界定萎缩指标，数量、占比和利润可异向。
C087|581-583|银行未来盈利规模会随趋势下降。|forecast|未来unknown|commercial_banks|unknown|会|none|uncertain:利润规模和盈利能力不同，必须单独评估。
C088|588-597|银行表外业务是未来十年级别的利润来源方向。|forecast|十年级，精确起止unknown|commercial_banks|unknown|肯定；大趋势|none|uncertain:表外、非标、中间业务不能混为一类，需监管和风险调整收益。
C089|588-604|银行从业者应优先选择能创造额外利润的业务方向。|normative|未来职业选择|commercial_bank_employees|unknown|你得瞄准|none|unverifiable:职业建议不是事实，不能推出个体必然获益。
C090|598-601|为公司创造额外利润的人将获得更高地位和晋升速度。|forecast|未来unknown|employees_generating_extra_profit|unknown|谁能；谁就|none|uncertain:组织任用还受风控、资历、考核和治理影响。
C091|608-611|近十年房地产与基建新增贷款占比从60%以上降到约10%。|factual|近十年，端点unknown|China_property_infrastructure_new_loans|unknown|60%以上至10%左右|SRC06|uncertain:原文也写在全部贷款中，增量/存量分母歧义须保留。
C092|612-615|金融五篇大文章领域新增贷款占比超过70%。|factual|当前统计期unknown|five_finance_fields_new_loans|unknown|70%以上|SRC06|uncertain:分母、分类交叉去重和起止时间未给。
C093|617|科技型中小企业贷款增速近几年约20%。|factual|过去几年unknown|technology_SMEs|unknown|约20%|SRC06|likely_true:文章支持；增速基期和定义须原表补充。
C094|660|贷款整体规模在下降。|factual|当前趋势unknown|China_lending|unknown|整体规模下降|none|uncertain:与C073的绝对值仍增加不一致，但同时间同口径未满足，不直接建CONTRADICTS。
C095|618|普惠小微贷款近几年年均增速约20%。|factual|过去几年unknown|inclusive_small_micro_loans|unknown|年均约20%|SRC06|likely_true:与科技中小企业增速不合并，复合年均或算术平均未知。
C096|619-620|绿色贷款保持两位数以上增长。|factual|过去几年unknown|green_loans|unknown|两位数以上|SRC06|likely_true:单独拆分，不把绿色与养老当一个指标。
C097|619-620|养老产业贷款保持两位数以上增长。|factual|过去几年unknown|pension_industry_loans|unknown|两位数以上|SRC06|likely_true:与绿色贷款是不同统计对象。
C098|621|上述重点领域贷款增速均高于全部贷款增速。|comparative|过去几年unknown|listed_loan_categories|all|均明显高于|SRC06|uncertain:逐年还是期间平均不明，需要同基期比较。
C099|622-627|资金流向能够指示市场机会所在。|interpretive|一般分析方法|economic_sectors|unknown|就流向市场机会|none|uncertain:政策扶持、风险补偿、纾困也可带来资金流入。
C100|628-655|获得更充分金融供给的科技、普惠、绿色和养老领域未来发展空间更大。|forecast|未来unknown|supported_sectors|unknown|很有想象空间；更有条件|none|uncertain:供给是条件而非结果，血液类比不能替代收益和生产率证据。
C101|661-668|贷款未覆盖的高科技产业在直接融资市场增长得更快。|comparative|当前unknown|high_tech_nonloan_financed_sectors|unknown|增长更厉害|none|uncertain:缺直接融资分行业、分阶段、净新增序列。
C102|669-678|科技企业融资需求随初创、成长和成熟阶段不同。|interpretive|企业生命周期|technology_firms|unknown|阶段式陈述|SRC06|likely_true:有理论和文章支持，不等于所有企业同轨迹。
C103|678-679|银行缺乏承担科技企业早期高失败风险的能力。|interpretive|早期融资阶段|commercial_banks|all|没能力|SRC06|uncertain:core_claim_supported但quantifier_overstated；约束不等于全部银行完全不能参与。
C104|680-687|民间天使投资在早期科技企业融资中起主角作用。|interpretive|早期融资阶段|early_stage_technology_firms|majority|主要部分；主角|SRC06|uncertain:方向有支持，民间占比和主导份额未证明。
C105|688|这些早期投资与银行没有关系。|interpretive|当下早期融资|early_stage_financing|all|没关系|none|uncertain:排他量词过强，需考虑银行系机构、托管和间接参与。
C106|689|早期非银行融资比例正在迅速增高。|factual|当前unknown|early_stage_nonbank_financing|unknown|迅速|none|uncertain:社融直接融资包含政府债，不能当作创投份额序列。
C107|691-696|上述融资转向说明新旧动能转换正在实际落地。|interpretive|当前unknown|China_industrial_transition|unknown|非常具体地落地|none|uncertain:融资分类变化不是产出、效率或创新成功的充分指标。
C108|697-701|早期风险投资是美国传统优势业务。|comparative|过去unknown|US_vs_China_venture_capital|unknown|非常有优势|none|uncertain:需募投退、阶段和币种可比数据。
C109|702|过去美国资本较愿意为中国企业早期机会提供启动资金。|causal|过去unknown|US_investors_in_China_startups|many|很多；稍微有一点机会|none|uncertain:缺投资样本、选择机制和失败案例。
C110|703|过去这类早期融资机会只能在美国找到。|comparative|过去unknown|early_stage_funding_opportunities|exclusive|只能|none|uncertain:强排他量词无支持，不能把相对优势改写成独占。
C111|703-704|100万美元折成人民币的数额在原转写中为将近100万就是0万。|factual|汇率时点unknown|USD_CNY_conversion|one|数字损坏|none|uncertain:保留损坏文本，数值设null，不猜600万或700万。
C112|704|对美国投资者100万美元投资的主观负担类似国内投资者投1万元人民币。|comparative|过去投资语境unknown|US_vs_China_investors|unknown|差不多|none|unverifiable:是主观类比，不是汇率换算或可比购买力观测。
C113|705-712|汇率和金融资本优势使美元投资中国新兴产业更划算。|causal|过去unknown|USD_investors_in_China|unknown|事半功倍|none|uncertain:需共同币种、估值、回报、退出和汇率风险比较。
C114|715-722|人民币资本现在走上台前是已经观察到的趋势。|interpretive|过去几年至当前|RMB_risk_capital|unknown|不是一厢情愿；数据观察|none|uncertain:援引文章总体数据不能单独证明人民币早期风险资本增长。
C115|724-726|中国正在挑战美国传统金融优势领域。|interpretive|当前unknown|China_vs_US_risk_capital|unknown|这才是关键|none|uncertain:跨越融资类别、产业、币种及跨国比较多个层级，缺直接比较证据。
C116|2|本篇文章发表早于本次美联储加息。|factual|2026-09|article_and_FOMC|one|注意；之前|SRC06,SRC09|verified:已定位网页发布时间早于FOMC公告；仅证实发表顺序，不证实准确写作时间。
C117|246-251|2013年发生过第二次金融危机或次贷危机的次生灾害。|factual|2013年|unspecified_financial_crisis|one|不是第二次吗|none|uncertain:事件地域和定义不明，不能擅自映射为中国钱荒或欧债危机。
'''

ROWS=ROWS.replace('C050|343-346|','C050|342-346|').replace('C065|475-480|','C065|466-478|').replace('C069|492-496|','C069|492-498|').replace('C071|509-515|','C071|509-517|').replace('C074|533-545|','C074|533-546|').replace('C076|546-549|','C076|548-549|').replace('C085|569-574|','C085|567-577|').replace('C087|581-583|','C087|580-581|').replace('C090|598-601|为公司创造额外利润的人将获得更高地位和晋升速度。','C090|597-598|为公司创造额外利润的人将获得更高内部地位。')
ROWS+='''
C118|531-532|融资结构变化将为未来国家举债打开空间。|forecast|未来unknown|China_sovereign_borrowing_capacity|unknown|打开很好的空间|none|uncertain:从风险转移机制进一步外推主权举债能力，非既有事实。
C119|599-600|创造额外利润的员工晋升速度会加快。|forecast|未来unknown|employees_generating_extra_profit|unknown|就会加快|none|uncertain:晋升与地位不同，需组织层面验证。
C120|600-601|创造额外利润的员工调配资源会更顺畅。|forecast|未来unknown|employees_generating_extra_profit|unknown|也会|none|uncertain:组织规则未知，不能与晋升共用验证结论。
C121|339|所讨论长期债务成本都是压在20%。|factual|债务置换语境unknown|long_term_debt_unspecified|all|都是；20%|none|uncertain:与相邻2%以下不一致，疑似ASR但不改原句。
C122|340|中国30年期国债收益率在2%点几。|factual|时点unknown|China_30Y_government_bond|one|2%点几|none|uncertain:未指定日期、券种和到期收益率口径。
C123|351-353|许多隐债经手人后来被抓或被双规。|factual|过去unknown|hidden_debt_handlers|many|很多|none|unverifiable:没有案件、样本和人名，不能据此推断化债全貌。
C124|458|平陆运河相关河道从几米深挖到十几米深。|factual|工程建设期unknown|Pinglu_Canal_channel|unknown|几米到十几米|none|uncertain:水深、挖深和底高程可能混淆，需设计断面。
C125|459|平陆运河相关河道从几米宽拓到几十米宽。|factual|工程建设期unknown|Pinglu_Canal_channel|unknown|几米到几十米|none|uncertain:需航道设计资料，不能以工程存在确认尺寸。
'''
ROWS=ROWS.replace('C116|2|本篇文章发表早于本次美联储加息。','C116|2|本篇文章写在本次美联储加息之前。').replace('verified:已定位网页发布时间早于FOMC公告；仅证实发表顺序，不证实准确写作时间。','likely_true:网页公开早于FOMC公告可支持文章先已写成；未获手稿或确切写作时间。').replace('C064|458-474|平陆运河需大规模拓宽挖深河道并通过闸门保水。','C064|457-465|平陆运河工程量巨大。').replace('C100|628-655|获得更充分金融供给的科技、普惠、绿色和养老领域未来发展空间更大。','C100|628-655|获得更充分金融供给的领域未来更有发展条件。')
claims=[]; assessments=[]
official_ids={29,30,31,37,38,39,45,46,66,67,68,74,76,77,78,79,81,91,92,93,95,96,97,98,102}
for line in ROWS.strip().splitlines():
    if not line.strip(): continue
    cid,rg,statement,ct,rt,pop,q,certainty,srcs,result=line.split('|')
    nums=[int(x) for x in rg.split('-')]; a,b=nums[0],nums[-1]
    ev=evidence(a,b); n=int(cid[1:]); status,reason=result.split(':',1)
    official=n in official_ids
    deriv='paraphrased'
    if ct=='causal': deriv='causal_inference'
    if n in {62,80}: deriv='calculated'
    if n in {26,100,112}: deriv='historical_analogy' if n==26 else 'inferred'
    if ct=='normative': deriv='recommendation'
    claim=dict(claim_id=cid,segment_id=segment(a),claimant='A002' if official else 'A001',asserted_by='A001',attribution='9527转述潘功胜；不据此推断朗读全文' if official else '9527自身陈述；有嵌套归因者另注',statement=statement,claim_type=ct,derivation_type=deriv,temporal_mode='ex_ante' if ct=='forecast' else ('retrospective' if n in {8,58} else 'contemporaneous'),asserted_at={'recorded_at':None,'publication_proxy':CUTOFF,'media_offset_start':ev['start'],'media_offset_end':ev['end'],'precision':'录制绝对时间unknown；不得将发布时间加偏移当实际发言时间'},reference_time=rt,knowledge_cutoff=CUTOFF,population=pop,quantifier=q,certainty_expressed=certainty,source_segment=f'SS-{cid}',atomicity_group_id=f'AG-{segment(a)}',information_gain='high' if n in {55,70,72,80,85,88,107,115} else 'medium',epistemic_layer='official_reported' if official else 'creator_statement')
    claims.append(claim)
    assessments.append(dict(assessment_id='VA-'+cid,claim_id=cid,observer='model',assessed_at=RETRIEVED,as_of=CUTOFF,veracity=status,evidence_sources=[] if srcs=='none' else srcs.split(','),evidence_provenance='SRC03 proves transcript attribution only; TXT/SRT are not independent corroboration',reason=reason,verification_scope='proposition, not merely that someone said it',external_quote_match='matched_in_official_article' if official else 'not_applicable',admit_to_verified_knowledge=status=='verified',audio_status='not_listened'))
source_segments=[dict(source_segment_id='SS-'+c['claim_id'],**evidence(*([int(x) for x in next(l for l in ROWS.strip().splitlines() if l.startswith(c['claim_id']+'|')).split('|')[1].split('-')]))) for c in claims]

sources=[]
for sid,ext,title in [('SRC01','.mp4','原视频'),('SRC02','.自动转写.txt','自动转写TXT'),('SRC03','.srt','SRT字幕'),('SRC04','.mp3','本地音频')]:
    p=BASE/(PREFIX+ext)
    sources.append(dict(source_id=sid,title=title,role='primary_evidence',time=CUTOFF,time_provenance='user-provided video publication; not file creation',version='SHA256:'+sha(p),path=str(p),size_bytes=p.stat().st_size,read_status='full_text_read' if sid in {'SRC02','SRC03'} else 'registered_and_hashed_not_played',source_family='video_768_ASR_family',independent_evidence=False))
URLS=[
('SRC05','财联社参考文章','creator_reference','2026-09-16T09:43:00+08:00','https://www.cls.cn/detail/2484394','full_article_read; HTML returned'),
('SRC06','潘功胜求是原文','verification_added','2026-09-16T09:00:00+08:00','https://www.qstheory.cn/20260915/1c41fc49b4b44db4b2550ddd41f40315/c.html','full_article_read'),
('SRC07','发改委：平陆运河正式开工建设','verification_added','2022-09-09','https://www.ndrc.gov.cn/fggz/dqjj/202209/t20220909_1368749.html','search_returned_article_text_read'),
('SRC08','发改委：平陆运河全线动工建设','verification_added','2023-05-29','https://www.ndrc.gov.cn/fggz/dqjj/202305/t20230529_1368966.html','search_returned_article_text_read'),
('SRC09','FOMC statement','verification_added','2026-09-16T14:00:00-04:00','https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm','search_returned_full_statement_read'),
('SRC10','日本央行9月18日决定','verification_added','2026-09-18T11:54:00+09:00','https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/k260918a.pdf','PDF_extracted_text_all_6_pages_read; not_visual_QA'),
('SRC11','ECB monetary policy decisions','verification_added','2026-09-10','https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp260910~314e508016.en.html','search_returned_full_statement_read'),
('SRC12','财政部2024年中国财政政策执行情况报告','verification_added','2025-03-24','https://www.mof.gov.cn/zhengwuxinxi/caizhengxinwen/202503/t20250324_3960464.htm','relevant_search_excerpt_read; not_full_report'),
('SRC13','财政部2024和2025地方专项债务余额表','verification_added','2025-03-24','https://yss.mof.gov.cn/2025zyczys/202503/t20250324_3960454.htm','search_returned_table_and_notes_read'),
('SRC14','帝国战争博物馆：1938慕尼黑和平文件说明','verification_added','2017-05-22（URL日期，文档确切首发unknown）','https://www.iwm.org.uk/sites/default/files/documents/2017_05_22_transforming_iwm_london_2.pdf','search_excerpt_only; temporal_provenance_not_fully_verified')]
for sid,title,role,time,url,read in URLS:
    sources.append(dict(source_id=sid,title=title,role=role,time=time,version='live_page_retrieved_2026-09-24; historical snapshot unavailable',url=url,read_status=read,retrieved_at=RETRIEVED,availability_at_cutoff='date_supported' if sid!='SRC14' else 'provisional_pre_cutoff_URL_date',independent_evidence=sid not in {'SRC05','SRC06'},source_family='Pan_article_reprint_family' if sid in {'SRC05','SRC06'} else sid))
sources.append(dict(source_id='SRC15',title='用户提供视频标题、发布时间与参考链接',role='primary_evidence',time='message_time_unknown',version='current_conversation',read_status='read',video_published_at=CUTOFF,independent_evidence=False))
sources.append(dict(source_id='SRC16',title='已有Golden #001摘要（registry search only）',role='verification_added',time='unknown',version='SHA256:'+sha(ROOT/'golden_report.md'),path=str(ROOT/'golden_report.md'),read_status='full_read_for_registry_search_only',use='不用于核验本期经济事实；只有摘要，无稳定Thesis ID'))
sources.append(dict(source_id='SRC17',title='日本央行当前首页（排除使用）',role='post_cutoff_source',time='page includes rates effective 2026-09-24',version='search snapshot 2026-09-24',url='https://www.boj.or.jp/en/',read_status='search_excerpt_seen_quarantined',use='不用于当时判断；改用9月18日决定文本'))
sources.extend([
dict(source_id='SRC18',title='中国人民银行人民币国际化报告（2025），熊猫债章节',role='verification_added',time='2025（报告年度）；2025-10-31（文件路径日期）',version='PDF retrieved as search excerpt 2026-09-24; no historical archive',url='https://www.pbc.gov.cn/huobizhengceersi/214481/3871621/5885243/2025103108544623039.pdf',read_status='relevant_search_excerpt_read_not_full_report',retrieved_at=RETRIEVED,availability_at_cutoff='pre_cutoff_report_year_and_file_date',independent_evidence=True),
dict(source_id='SRC19',title='SEC投资者教育公告：What Are Corporate Bonds?',role='verification_added',time='2013-06-04',version='dated bulletin retrieved as search excerpt 2026-09-24',url='https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins/what-are',read_status='definition_and_equity_comparison_excerpt_read',retrieved_at=RETRIEVED,availability_at_cutoff='pre_cutoff_dated_bulletin',independent_evidence=True)])
for a in assessments:
    if a['claim_id']in {'C032','C033'}:
        a['evidence_sources']=['SRC19']
        a['reason']+=' SEC 2013教育公告明确区分股票所有权与债券偿债义务；不代表已听验原话。'
    if a['claim_id']=='C049':
        a['evidence_sources']=['SRC18']; a['veracity']='likely_false'
        a['reason']='熊猫债是境外机构在境内发行人民币债券；中国中央在境外发债不属该定义。原声音及是否口误仍需复核，不改转写。'
historical_claims={12,22,23,24,25,31,35,36,37,38,39,40,45,46,47,51,52,53,56,60,64,67,68,74,75,76,77,78,79,80,91,93,95,96,97,98,108,109,110,113,117,123,124,125}
for c in claims:
    n=int(c['claim_id'][1:])
    if n in historical_claims:c['temporal_mode']='ex_post'
    if n in {52}:c['quantifier']='exclusive'
    if n in {90,119,120}:c['quantifier']='all'
    if n in official_ids:c['original_source_asserted_at']='2026-09-16T09:00:00+08:00'

corrections=[]
correction_specs=[
('潘刚盛','潘功胜','high','SRC06','1'),('潘光盛','潘功胜','high','SRC06','280'),('潘东升','潘功胜','high','SRC06','669-674'),('求市','求是','high','SRC06','1'),
('平论运河','平陆运河','high','SRC07','438-478'),('平路运河','平陆运河','high','SRC07','432'),('评论和','平陆运河','medium','SRC07','439'),
('闪击波澜','闪击波兰','high','context','137'),('清江','钦江','high','SRC07','457-461'),('素台德','苏台德','high','context','139'),('worker','沃尔克','medium','context','31'),
('退居慈禧','退居次席','high','context','276'),('隐形债务','隐性债务','high','SRC06','301'),('专细查','赚息差','high','context','511'),('表白业务','表外业务','high','context','595'),
('涉容涉零','社融/信贷？','low','context','282'),('134年','十三四年？','medium','arithmetic_not_sufficient','445'),('20%','2%？','medium','adjacent_context_not_sufficient','339'),('百分之百2020年上半年','2026年上半年？','medium','SRC06_and_cue489','502'),('100万就是0万人民币','unknown','low','none','703-704'),('进攻/天河堡','unknown（或指慕尼黑/其他会面地点）','low','none','144')]
for i,(raw,norm,conf,basis,rg) in enumerate(correction_specs,1):
    a,*rest=[int(n) for n in rg.split('-')]; b=rest[0] if rest else a
    corrections.append(dict(correction_id=f'TC{i:02}',raw=raw,normalized_candidate=norm,status='candidate_correction',confidence=conf,basis=basis,evidence=evidence(a,b),needs_audio_review=True,applied=False,reason='音频文件存在但本次未实际听验；上下文/文章可支持规范实体，不能证明是ASR而非口误'))
annotations=[]
def annotation(a,b,kind,note): annotations.append(dict(annotation_id=f'AN{len(annotations)+1:02}',annotation_type=kind,evidence=evidence(a,b),note=note,confirmed_by_audio=False))
annotation(393,394,'self_correction','转写中先说低成本换成，接着改说高成本换成低成本；保留两次表述。')
annotation(513,514,'self_correction','转写中直接融资改为间接融资；不将前半句独立认作金融理论。')
annotation(545,546,'self_correction','百分之百随即限定为接近百分之百。')
annotation(144,145,'ambiguous_reference','本人在转写中说我忘了；地点不明。')
annotation(25,25,'ambiguous_reference','大家的Population未知。')
annotation(282,285,'ambiguous_reference','负增长与剪刀差指标和基期未明确。')
annotation(300,323,'mixed_fact_and_opinion','朗读融资分类说明后转入闭门谈判实操解释。')
annotation(487,508,'mixed_fact_and_opinion','企业融资比值是引述数据；相对成本更低是主播推论。')
annotation(548,556,'mixed_fact_and_opinion','存量占比引述与股票10%算术推断分开。')
annotation(608,655,'mixed_fact_and_opinion','投向数据与发展机会判断、血液类比分开。')
annotation(715,725,'mixed_fact_and_opinion','以已经观察到的趋势修辞强化中美竞争解释，官方并未直接提出该竞争命题。')

model_specs=[
('MC01','假如直接融资替代的是银行原可取得的贷款，银行可获得的传统信贷需求相对反事实减少。',['C029','C030','C085'],567,579),
('MC02','若利差、定价及其他收入不能补偿，减少的贷款需求会压低传统信贷净收益。',['C085','C086'],567,579),
('MC03','还需假定规模增长、信用成本下降及非信贷收入均不足补偿，才能推出银行总利润下降。',['C085','C087'],567,581),
('MC04','若直接融资风险真正由外部投资者承担且无国家回兜，银行体系的潜在公共信用支持负担才可能下降。',['C071','C072'],509,532),
('MC05','要从社融结构推到人民币早期风险资本扩张，须证明新增直接融资中相应币种与投资阶段资金确有增长。',['C078','C106','C114'],656,722),
('MC06','要从国内融资扩张推到中美竞争地位改善，须证明同口径资金、创新产出与退出能力相对美国改善。',['C108','C114','C115'],697,725)]
for cid,st,refs,a,b in model_specs:
    claims.append(dict(claim_id=cid,segment_id=segment(a),claimant='model',asserted_by='model',attribution='诊断推理所需的条件；非9527原话',statement=st,claim_type='causal',derivation_type='model_generated',temporal_mode='contemporaneous',asserted_at={'recorded_at':None,'publication_proxy':None,'extracted_at':RETRIEVED},reference_time='条件式机制，非新增事实',knowledge_cutoff=CUTOFF,population='conditional_scope',quantifier='unknown',certainty_expressed='conditional',source_segment='SS-'+cid,atomicity_group_id='AG-MODEL',information_gain='high',epistemic_layer='model_reconstruction',context_claims=refs))
    source_segments.append(dict(source_segment_id='SS-'+cid,**evidence(a,b),role='context_only_not_creator_quote'))
    assessments.append(dict(assessment_id='VA-'+cid,claim_id=cid,observer='model',assessed_at=RETRIEVED,as_of=CUTOFF,veracity='uncertain',evidence_sources=['SRC03'],reason='条件结构用于定位缺失环节；条件是否满足未获证明。',admit_to_verified_knowledge=False,verification_scope='model bridge, not creator assertion'))

byid={c['claim_id']:c for c in claims}
arguments=[]
def arg(aid,title,premises,steps,conclusion,lim,atype='causal',analogy=None):
    out=[]
    for fr,to,mode,level,why in steps:
        refs=list(dict.fromkeys(fr+[to])); ev=['SS-'+x for x in refs]
        out.append(dict(step_id=f'{aid}.{len(out)+1}',**{'from':fr,'to':to},relation='INFERENTIAL_SUPPORT_CANDIDATE',inference_mode=mode,expression_level=level,evidence=ev,explanation=why,limitations=lim if level=='model_reconstruction' else '成立程度见逐Claim评估；'+lim.split('；')[0]))
    levels=list(dict.fromkeys(s['expression_level'] for s in out))
    ob=dict(argument_id=aid,title=title,analyst='9527 (reconstructed by model)',argument_type=atype,premises=premises,steps=out,conclusion=conclusion,inference_mode=list(dict.fromkeys(s['inference_mode'] for s in out)),expression_level=levels,hop_count=len(out),hop_definition='listed edges; branching depth separately audited',limitations=lim,weakest_step='model_reconstruction桥接或最后从条件推到总量结论；详见各步',status='reconstructed_not_validated')
    if analogy: ob.update(analogy)
    arguments.append(ob)
arg('AR01','由央行共同处境推断文章隐含外部风险信号',['C002','C003','C004'],[(['C002','C003','C004'],'C005','analogy','explicit','同职业与相近政策环境被用作能够预判的理由'),(['C005'],'C006','speculation','explicit','从可预判推为文章潜台词'),(['C006','C026'],'C027','speculation','explicit','把美元风险场景读入文章')],'C027','最弱处是把角色相似推成私人认知，再把认知推成写作意图；发布时间先后不能验证目的。')
arg('AR02','高债务、相对优势与短期加息策略',['C013','C014','C016'],[(['C013','C014'],'C015','causal','explicit','高息增加负担而损害信用'),(['C015','C016'],'C018','speculation','explicit','相对优势可能使短期收益先于长期成本兑现'),(['C019','C020'],'C021','speculation','explicit','大额持仓的损失厌恶可能强化容忍')],'C021','利息/GDP算术缺输入；财政与央行资产负债表不可混同；债权人也可能退出；三个分支非完整线性证明。')
arg('AR03','从英法绥靖类比美元债权人容忍',['C022','C023','C024','C025'],[(['C022','C023','C024','C025'],'C026','analogy','explicit','把损失厌恶与策略性试探迁移到美联储'),(['C026'],'C021','analogy','strongly_implied','以历史类比增强大而不能倒的可行性')],'C021','历史时序及总体动机有疑点；国家战争决策与可交易债券持仓的退出机制、目标和约束不同。',atype='historical_analogy',analogy=dict(source_case='二战前英法对纳粹德国的绥靖（按9527叙述）',target_case='美债持有者对美国激进政策的容忍',shared_mechanism='既有损失暴露与风险厌恶可能被策略性利用',limits_of_analogy='外交安全承诺不是可出售债券；不能用希特勒的意图证明美联储意图。'))
arg('AR04','融资结构分类变化到化债基本解决',['C045','C046','C050','C051','C053'],[(['C045','C046','C053'],'C054','causal','explicit','把贷款转债券及谈判展期视作债务压力减轻的表现'),(['C054'],'C055','causal','explicit','由压力缓释升级为基本解决')],'C055','最弱是最后一步；统计分类替代、降息、展期、本金削减和可持续偿债分别不同；未给隐债余额及现金流，政府债也可能被银行持有。')
arg('AR05','平陆运河长期投入到化债信心',['C060','C061','C062','C063','C064'],[(['C060','C061','C063','C064'],'C059','causal','explicit','长期低现金回报工程能够推进，被视作政府承诺可信'),(['C059'],'C065','causal','explicit','长期承诺转换为债权人信心')],'C065','社会运输成本节约不是项目现金流；投资/社会效益不是财务回收期；能动员项目资金不等于能偿还所有债务。',atype='case_based_signal_inference',analogy=dict(source_case='平陆运河长期建设',target_case='政府化债信用',shared_mechanism='以可见的长期投入传递承诺',limits_of_analogy='本段是当期案例信号推理，并非历史跨案例类比；若强制只提供historical_analogy枚举会误分类。'))
arg('AR06','企业融资数量比到直接融资成本更低',['C067','C068','C069'],[(['C067','C068','C069'],'C070','causal','explicit','在低贷款利率下仍转向债券，被解释为债券融资更便宜')],'C070','最弱是以数量选择反推价格；贷款分母变动、融资期限、主体资质、准入和发行政策都可产生同样数量比。')
arg('AR07','直接融资风险转移到主权举债空间',['C071','C072'],[(['C071','C072'],'MC04','causal','model_reconstruction','拆出风险确实离开银行且财政不回兜的必要条件'),(['MC04'],'C118','causal','model_reconstruction','尚需财政担保负担与主权举债空间相连才能完成推导')],'C118','最弱是把国家信用当固定额度池；直接融资不等于无银行、无担保、无财政风险；MC04条件未被主播证明。')
arg('AR08','直接融资替代到银行利润压力',['C029','C030','C076','C078'],[(['C029','C030','C078'],'MC01','causal','model_reconstruction','区分市场份额变化与真实贷款替代'),(['MC01'],'MC02','causal','model_reconstruction','加入利差与收入补偿条件'),(['MC02'],'C086','causal','strongly_implied','传统业务承压是主播明说的方向，机制只部分交代'),(['C086'],'MC03','causal','model_reconstruction','加入总量增长、信用成本、非信贷收入补偿条件'),(['MC03'],'C087','causal','model_reconstruction','条件均满足才推出总利润下降'),(['C085','C087'],'C088','speculation','explicit','主播据此主张表外业务是未来利润方向')],'C088','最弱是传统信贷份额下降跳到总利润下降；直接融资可能增加银行持债、承销与托管收入；非标、表外和中间业务不等价；长期不能当短期择业保证。')
arg('AR09','资金流向到新产业机会',['C091','C092','C093','C095','C096','C097'],[(['C091','C092','C093','C095','C096','C097'],'C099','statistical','explicit','把投向变化当市场机会分布的观察信号'),(['C099'],'C100','analogy','explicit','用血液供给比喻融资条件与未来成长空间'),(['C100','C106'],'C107','causal','explicit','由机会和早期资本扩张推到动能转换正在实现')],'C107','最弱是从资金供给推为转型结果；投向可能由政策补贴或纾困驱动，需产出、生产率及违约数据；血液比喻只提供启发。',atype='mixed_statistical_and_analogy',analogy=dict(source_case='人体供血与组织功能（比喻）',target_case='产业融资供给和成长',shared_mechanism='资源支持影响活动空间',limits_of_analogy='生理系统与投资市场的资源配置机制不同；不是历史类比，更不是收益率证明。'))
arg('AR10','科技企业生命周期与银行适配约束',['C102'],[(['C102'],'C103','causal','explicit','早期回报滞后及失败风险限制传统银行'),(['C103'],'C104','causal','explicit','高风险承受能力由天使等资本补充'),(['C104'],'C106','statistical','explicit','主播进一步断言此类资金比例迅速提升')],'C106','最弱是从功能适配推到已观测规模增长；没能力与完全无关系是过强表述；需生命周期分组及银行系投资关系。')
arg('AR11','国内融资变化到中美风险资本竞争',['C078','C102','C104','C106','C108'],[(['C078','C106'],'MC05','statistical','model_reconstruction','剥离政府债和普通企业债，要求识别人民币早期股权资金'),(['MC05','C104'],'C114','causal','model_reconstruction','人民币风险资本确有扩张才支持走上台前'),(['C108','C114'],'MC06','statistical','model_reconstruction','补同口径跨国、币种、阶段和退出能力比较'),(['MC06'],'C115','causal','model_reconstruction','比较成立才支持相对竞争地位改善')],'C115','最弱是两次跨口径迁移：社融直接融资→早期人民币风险资本，国内规模→相对美国竞争力；四步都是诊断性拆分，非主播逐句论证。')
arg('AR12','美元汇率优势到美国早期投资优势',['C109','C110','C111','C112'],[(['C109','C111','C112'],'C113','causal','explicit','名义换算和主观负担类比被作为项目便宜的依据'),(['C113'],'C108','causal','explicit','投资划算被用来解释美国风险资本优势')],'C108','最弱是把币值面额差异等同真实资本成本优势；换算原句损坏，主观类比不可计算，且需估值、汇兑、退出和资本供给数据。')

actors=[]
for aid,name,aliases,kind in [
('A001','有何高见9527',['9527','主播'],'person_or_channel'),('A002','潘功胜',['潘刚盛','潘光盛','潘东升','潘行长'],'person'),('A003','中国人民银行',['央行','人民银行','PBOC'],'institution'),('A004','商业银行',['银行系统','银行'],'population'),('A005','中国中央政府',['中央','国家（财政信用语境）'],'government'),('A006','中国地方政府',['地方政府'],'population'),('A007','科技型企业',['高科技企业','科技企业'],'population'),('A008','美联储',['美国央行','Federal Reserve'],'institution'),('A009','日本银行',['日本央行'],'institution'),('A010','欧洲中央银行',['欧洲这边（加息语境）'],'institution'),('A011','美国政府',['美国（财政债务语境）'],'government'),('A012','美债大额持有者',['国家以及民间持有者'],'population'),('A013','天使及风险投资者',['天使投资','民间早期资本'],'population'),('A014','英国政府',['英方'],'government'),('A015','法国政府',['法方'],'government'),('A016','纳粹德国及希特勒',['德国（该历史语境）'],'historical_actor_group'),('A017','张伯伦',['Neville Chamberlain'],'person'),('A018','银行从业者',['银行工作人员'],'population'),('A019','美国金融机构（未具名）',['那些金融机构'],'unresolved_population'),('A020','国有银行',['国有商业银行'],'population'),('A021','苏联',['苏联'],'historical_state'),('A022','中国企业',['企业'],'population')]:
    actors.append(dict(actor_id=aid,canonical_name=name,aliases=aliases,kind=kind,resolution_status='context_resolved; ASR sound unconfirmed' if aid=='A002' else 'context_scoped',notes='同名词随语境区分：央行不等于商业银行，国家不等于银行；分组实体后续可细分。'))
events=[
dict(event_id='EV01',name='潘功胜求是文章公开发表',occurred_at='2026-09-16T09:00:00+08:00',source_id='SRC06',claim_refs=['C001','C116'],status='publication_verified; writing_date_unknown'),
dict(event_id='EV02',name='FOMC宣布加息',occurred_at='2026-09-16T14:00:00-04:00',source_id='SRC09',claim_refs=['C002'],status='verified'),
dict(event_id='EV03',name='日本央行宣布利率调整',occurred_at='2026-09-18T11:54:00+09:00',effective_at='2026-09-24',source_id='SRC10',claim_refs=['C003'],status='announced_at_cutoff; effective_after_cutoff'),
dict(event_id='EV04',name='ECB宣布加息',occurred_at='2026-09-10',effective_at='2026-09-16',source_id='SRC11',claim_refs=['C004'],status='verified'),
dict(event_id='EV05',name='批准增加地方债务限额用于隐债置换',occurred_at='2024-11-08',source_id='SRC13',claim_refs=['C045','C053'],status='verification_added; not_claimed_as_specific_date_by_creator'),
dict(event_id='EV06',name='平陆运河项目开工',occurred_at='2022-08-28',source_id='SRC07',claim_refs=['C060','C064'],status='verification_added; not_inferred_debt_resolution')]
policies=[dict(policy_id='PL01',name='地方政府债务限额置换存量隐性债务安排',source_ids=['SRC12','SRC13'],event_id='EV05',implementing_period='2024—2026（限额安排）',claim_refs=['C045','C050','C053'],interpretation='地方债务限额政策，不能改写为中央直接接管全部债务或仅闭门展期。'),dict(policy_id='PL02',name='金融五篇大文章',source_ids=['SRC06'],claim_refs=['C092','C093','C095','C096','C097'],implementing_period='unknown',interpretation='政策分类、资金投向观测和效率结果分开；本期列举不是完整五项定义。')]
indicator_specs=[
('I01','社会融资规模增量','flow','一定期间实体经济从金融体系获得的融资','万亿元'),('I02','新增间接融资占社融增量比重','flow_share','间接融资增量/社融增量','%'),('I03','债券与股票合计占社融增量比重','flow_share','政府债+企业债+股票融资增量/社融增量','%'),('I04','企业债融资增量与同期贷款增量之比','flow_ratio','企业债融资增量/同期贷款增量；贷款分母范围待定','%'),('I05','间接融资占社融存量比重','stock_share','间接融资余额/社融余额','%'),('I06','贷款占社融存量比重','stock_share','贷款余额/社融余额','%'),('I07','直接融资占社融存量比重','stock_share','直接融资余额/社融余额','%'),('I08','债券融资占社融存量比重','stock_share','债券融资余额/社融余额','%'),('I09','股票融资占社融存量比重','stock_share','股票融资余额/社融余额','%'),('I10','房地产与基建新增贷款占比','ambiguous_share','分子为新增贷款；全部贷款分母是新增还是存量不明','%'),('I11','五篇大文章领域新增贷款占比','flow_share_unresolved','分母及交叉分类去重不明','%'),('I12','科技型中小企业贷款增速','growth','统计口径及基期unknown','%'),('I13','普惠小微贷款年均增速','average_growth','算术或复合平均unknown','%'),('I14','绿色贷款增速','growth','基期unknown','%'),('I15','养老产业贷款增速','growth','基期unknown','%'),('I16','平陆运河项目投资','investment_budget','估算总投资，不等于决算','亿元'),('I17','运河相关年运输费用节约','projected_external_benefit','非项目现金流','亿元/年'),('I18','银行利润','profit','净利润/利润总额及群体口径未确定','unknown'),('I19','人民币早期风险资本规模','flow_or_stock_unresolved','币种、阶段、投融资口径需单独建序列','unknown'),('I20','贷款绝对规模','stock_or_flow_unresolved','未明确贷款余额还是新增额','unknown'),('I21','隐性债务余额','stock','认定范围与或有负债需注明','亿元'),('I22','中国30年国债收益率','yield','日期与券种unknown','%')]
indicators=[dict(indicator_id=i,name=n,measure_type=t,definition=d,unit=u) for i,n,t,d,u in indicator_specs]
obs_specs=[('I01','C037',35.6,'2025','reported'),('I02','C031','>80','2013以前','reported'),('I03','C038','~47','2025','reported'),('I04','C067',7,'2023','reported'),('I04','C068','~20','2026H1','reported'),('I05','C074','~100','1990年代早期','reported'),('I05','C076','~66.7','2026-06-30','reported_rounded_fraction'),('I06','C077','~60','2026-06-30','reported'),('I07','C078','~33.3','2026-06-30','reported_rounded_fraction'),('I08','C079','~30','2026-06-30','reported'),('I09','C080','~10','2026-06-30','creator_calculated_quarantined'),('I10','C091','>60','近十年起点unknown','reported_denominator_unresolved'),('I10','C091','~10','近十年终点unknown','reported_denominator_unresolved'),('I11','C092','>70','unknown','reported_denominator_unresolved'),('I12','C093','~20','过去几年unknown','reported'),('I13','C095','~20','过去几年unknown','reported'),('I14','C096','两位数以上','过去几年unknown','reported'),('I15','C097','两位数以上','过去几年unknown','reported'),('I16','C060','700多','预算阶段unknown','creator_reported'),('I17','C061','50多','运营预测年unknown','creator_metric_mismatch_quarantined'),('I22','C122','2%点几','unknown','creator_reported_unverified')]
observations=[]
for i,(ind,cid,val,period,kind) in enumerate(obs_specs,1):
    observations.append(dict(observation_id=f'OB{i:02}',indicator_id=ind,claim_id=cid,reference_period=period,released_at='2026-09-16T09:00:00+08:00' if int(cid[1:]) in official_ids else None,asserted_in_video=CUTOFF,value=val,unit=next(x['unit'] for x in indicators if x['indicator_id']==ind),previous=None,revision=None,value_kind=kind,source_segment='SS-'+cid,verification=next(a['veracity'] for a in assessments if a['claim_id']==cid),canonical=False))
observations.extend([
dict(observation_id='OB22',indicator_id='I16',claim_id=None,reference_period='2022年开工时估算',released_at='2022-09-09',value=727.3,unit='亿元',previous=None,revision=None,value_kind='official_reported_estimate',source_id='SRC07',canonical='budget_fact_only_not_final_cost'),
dict(observation_id='OB23',indicator_id='I17',claim_id=None,reference_period='建成运营后预测年unknown',released_at='2023-05-29',value='>=52',unit='亿元/年',previous=None,revision=None,value_kind='projected_transport_cost_saving',source_id='SRC08',canonical=False)])
narratives=[
dict(assessment_id='NA01',observer='A001',time=CUTOFF,scope='SRC06文章外部语境',narrative_role='core_signal',claim_refs=['C006','C027'],accepts_fact='未否认文中融资变化',accepts_causal='添加未明说的美元风险因果',cause_or_effect='战略风险背景信号',missing_variable='未明确',information_gain='high',note='未称假新闻；潜台词属于9527。'),
dict(assessment_id='NA02',observer='A001',time=CUTOFF,scope='SRC06文章沟通背景',narrative_role='reassurance',claim_refs=['C043','C044'],accepts_fact='接受文中数据',accepts_causal='不以安抚目的否定分析价值',cause_or_effect='安抚是背景；结构转向是信息增量',missing_variable='unknown',information_gain='high',note='背景、目的、本质在原话中来回调整，应保留而非定为烟雾弹。'),
dict(assessment_id='NA03',observer='A001',time=CUTOFF,scope='高息换低息解释',narrative_role='causal_obscuring',claim_refs=['C050','C051','C052','C053'],accepts_fact='部分正确',accepts_causal='认为不是完整机制',cause_or_effect='成本下降解释遗漏实操过程',missing_variable='合规、确权、谈判与过程成本',information_gain='high',note='causal_obscuring为模型对9527明确批评的分类，不代表9527说该英文标签。'),
dict(assessment_id='NA04',observer='A001',time=CUTOFF,scope='信贷投向统计',narrative_role='core_signal',claim_refs=['C091','C099','C100'],accepts_fact=True,accepts_causal='从投向追加机会与转型解释',cause_or_effect='市场机会的信号和成长条件',missing_variable='unknown',information_gain='high'),
dict(assessment_id='NA05',observer='model',time=RETRIEVED,scope='C114/C115借用官方权威',narrative_role='supporting_signal',claim_refs=['C114','C115'],accepts_fact='只能确认官方提供总体结构数据',accepts_causal=False,cause_or_effect='数据到竞争结论尚缺桥梁',missing_variable='风险资本币种、阶段和跨国比较',information_gain='high',note='不得把9527关于中美竞争的结论归给潘功胜。')]

mechanisms=[
dict(mechanism_id='ME01',status='candidate',name='融资契约与企业阶段风险适配',chain=['早期研发现金流不确定','固定债务偿付与银行风控适配受限','可承受亏损并分享上行的股权资本相对适配'],argument_refs=['AR10','AR08'],claim_refs=['C102','C103','C104'],expression_level='mixed_explicit_and_model_reconstruction',scope='早期高不确定企业，不泛化全部科技/绿色/养老',limitations='轻资产抵押不足来自外部原文可作候选补充，但本期没有完整展开，不冒充主播核心前提。'),
dict(mechanism_id='ME02',status='candidate',name='融资渠道替代对银行收益的条件性影响',chain=['真实替代银行可做贷款','传统信贷净收益承压','证券投资及服务费等补偿决定总利润方向'],argument_refs=['AR08'],claim_refs=['C085','C086','C087','MC01','MC02','MC03'],expression_level='model_reconstruction_of_creator_direction',scope='必须控制总量、利差、信用损失和非息收入',limitations='占比下降本身不足以触发第二步，更不足以保证总利润下降。'),
dict(mechanism_id='ME03',status='candidate',name='债务再融资的负担与分类效应',chain=['债务换券或展期降息','融资统计分类及偿付时间分布改变','现金流压力可能缓释而本金与风险未必消失'],argument_refs=['AR04'],claim_refs=['C045','C050','C051','C053','C054'],expression_level='model_qualified_candidate',scope='同本金、期限和债权主体可识别的重组',limitations='不是认可闭门谈判穷尽全部政策，也不推出隐债基本解决。')]
theses=[
dict(thesis_id='TH01',statement='中国融资结构正走向渠道多元和投向重配，但产业转型成果尚不能仅由融资份额证明。',creator_claim='C081 / C107',status='candidate_with_model_scope_qualification',resolution='new_provisional',argument_refs=['AR09','AR10'],claim_refs=['C029','C030','C076','C078','C091','C092','C102','C107'],support_needed='同口径长期融资和实体产出序列',falsification='构成变化仅来自债务重分类或短期行政因素且缺持续投向变化'),
dict(thesis_id='TH02',statement='9527判断融资转型将长期压迫传统银行业务，促使利润来源转型。',creator_claim='C085 / C088',status='creator_thesis_unverified',resolution='new_provisional',argument_refs=['AR08'],claim_refs=['C029','C030','C078','C085','C086','C087','C088'],support_needed='银行分业务收益、资产规模、成本与监管序列',falsification='直接融资比重上升期间传统业务绝对利润持续增加或业务转型并无收益改善'),
dict(thesis_id='TH03',statement='9527把国内融资变化理解为人民币风险资本挑战美国传统优势。',creator_claim='C115',status='high_inferential_distance_unverified',resolution='new_provisional_related_to_GS001_capital_competition_theme',argument_refs=['AR10','AR11','AR12'],claim_refs=['C102','C104','C106','C108','C113','C114','C115','MC05','MC06'],support_needed='分币种/阶段可比募投退、创新产出和跨境投资数据',falsification='剔除政府债后早期股权资本并未增加，或相对美国差距未改善')]
for t in theses:
    t['registry_search']={'searched':['golden_report.md','workspace file inventory'],'found':'只有Golden #001摘要，无正式Thesis registry或完整对象','decision_scope':'不能声称全库无同题Thesis；临时new/related，待注册表核对'}
    t['traceability']=[dict(argument_id=a,claim_id=cid,source_segment='SS-'+cid,source_id='SRC03') for a in t['argument_refs'] for cid in t['claim_refs'] if cid in set(arguments[int(a[2:])-1]['premises']+[arguments[int(a[2:])-1]['conclusion']]+[x for s in arguments[int(a[2:])-1]['steps'] for x in s['from']+[s['to']]])]

forecasts=[]
special_forecasts={
'C011':('US_tightening_duration','longer','unknown','if tightening persists unexpectedly','possible','low','需先约定本轮起点及很长的期限阈值'),
'C015':('USD_credit','deteriorate_first','unknown','暴力加息','possible','low','需美元信用指标及先于哪些变量的比较规则'),
'C018':('US_policy_strategy','short_run_gains','unknown','短期收益先于副作用且替代资产受限','possible','low','需政策目的与因果识别；不能仅凭短期市场涨跌'),
'C020':('US_debt_growth','accelerate','unknown','加息并扩表','likely','low','需债务口径、基准增速与政策贡献分解'),
'C021':('Treasury_holder_tolerance','increase','unknown','持仓巨大且替代选择有限','possible','low','需持仓行为、风险溢价及态度证据'),
'C026':('Federal_Reserve_strategy','exploit_loss_aversion','unknown','历史类比机制可迁移','possible','unresolvable','未指定行为与意图判据，不能把任何结果都解释为命中'),
'C063':('Pinglu_Canal_payback','long','运营后约30—40年；运营起点未给','乐观估计，考虑爬坡','possible','low','明确运营现金流、社会效益、补贴、折现和回本定义'),
'C082':('direct_financing_share','increase','unknown','结构趋势延续','near_certain','medium','可观察份额方向；但必须先补窗口与统计口径'),
'C085':('bank_profitability','decrease','unknown','趋势持续且不开展替代业务','likely','low','先选ROA/ROE等盈利能力指标；不得改用利润规模代替'),
'C086':('traditional_bank_business','shrink','unknown','缺少转型','near_certain','low','先区分份额、资产绝对额及收益；规定窗口'),
'C087':('bank_aggregate_profit','decrease','unknown','按上下文缺少转型','likely','medium','定义银行样本和净利润绝对额，锁定起止年'),
'C088':('bank_nontraditional_income','become_profit_source','十年级；非明确截至2036承诺','合规开展新业务','near_certain','low','先区分表外、非标、手续费及投资收益'),
'C090':('employee_internal_status','increase','unknown','创造额外利润','likely','low','样本、地位指标和组织制度需补充'),
'C100':('supported_sector_growth','more_opportunity','unknown','金融供给充分','plausible','low','先定义成长或机会指标；不得自行替换为股票回报'),
'C118':('sovereign_borrowing_capacity','increase','unknown','直接融资风险不回到银行/财政（后者为模型条件）','likely','low','需财政担保风险、债务容量和借款成本指标'),
'C119':('employee_promotion_speed','increase','unknown','创造额外利润','likely','low','需可比样本及晋升时长'),
'C120':('employee_resource_access','improve','unknown','创造额外利润','likely','low','需资源调配指标及组织范围')}
for c in claims:
    if c['claim_type']!='forecast': continue
    cid=c['claim_id']; target,direction,window,cond,modal,res,criteria=special_forecasts[cid]
    forecasts.append(dict(forecast_id=f'FC{len(forecasts)+1:02}',claim_id=cid,made_at={'recorded_at':None,'publication_proxy':CUTOFF,'source_offset':c['asserted_at']['media_offset_start']},knowledge_cutoff=CUTOFF,target=target,direction=direction,prediction_window=window,conditions=cond,modal_strength=modal,modal_mapping='model coding of original certainty; not numerical probability',original_modality=c['certainty_expressed'],resolution_criteria={'creator_specified':None,'model_proposed_for_future_review':criteria,'accepted_for_scoring':False},resolvability=res,source_segment=c['source_segment'],evaluation_status='not_resolved',post_cutoff_evaluation=None))
heuristics=[
dict(heuristic_id='HC01',status='candidate_only',rule='观察融资流量与存量结构来识别变化方向及潜在空间，再追问资金流向。',observed_in_arguments=['AR06','AR08','AR09'],source_segments=['SS-C067','SS-C068','SS-C078','SS-C099'],direct_method_evidence=evidence(533,533),why_method_not_conclusion='主播明确说增量看趋势、存量看空间，并在多处把投向作为观察方法；可以迁移到其他行业。',limits='份额空间不代表均衡目标；流量比值不能当价格证据；仅本期无法确认长期稳定性。'),
dict(heuristic_id='HC02',status='candidate_only',rule='对看似简单的债务处置结果，追问确权、利益相关者谈判与过程成本。',observed_in_arguments=['AR04'],source_segments=['SS-C050','SS-C051','SS-C052'],why_method_not_conclusion='关注解释中遗漏的执行过程是一种可跨政策复用的检查规则，不等于本期全部化债都靠谈判的判断。',limits='需要多期复现；方法有用不能替代具体案件证据。')]

reviews=[]
def rq(priority,kind,refs,issue,action):
    reviews.append(dict(review_id=f'RQ{len(reviews)+1:02}',priority=priority,category=kind,claim_refs=refs,source_segments=['SS-'+x for x in refs if x in byid],issue=issue,required_action=action,status='open',blocks_verified_knowledge=True))
rq('Critical','Data',['C080','C078','C079'],'股票10%不由三分之一减30%推出。','听验26:46—26:54；确认同分母、分类和原统计表。模型3.3仅是算术诊断，不替换主播数字。')
rq('Critical','Data',['C031','C040','C041'],'间接融资与贷款、流量与存量在论证中换用。','统一2013前与2025年分子分母后重算；不以增量排名推存量退居次席。')
rq('Critical','Data',['C073','C094'],'占比下降且绝对量增加，与后文整体规模下降不一致。','听验25:00—25:20及31:24—31:27，确认同时间同口径；未完成前不建CONTRADICTS。')
rq('Critical','Reasoning',['C054','C055'],'从重分类和谈判推到隐债基本解决。','补截至截止时间的隐债余额、期限、付息、拖欠、现金流及财政约束；先锁定基本解决判据。')
rq('Critical','Reasoning',['C067','C068','C070'],'融资数量比被当成相对融资价格。','匹配同主体、期限、担保和费用的贷款/债券成本；排除分母收缩及发行结构。')
rq('Critical','Reasoning',['C085','C086','C087','MC01','MC02','MC03'],'贷款份额变化跳到银行绝对盈利下降。','分解生息资产、净息差、信用成本、证券收益及手续费收入；验证替代而非新增互补。')
rq('Critical','Reasoning',['C106','C114','C115','MC05','MC06'],'社融直接融资跳到人民币早期资本与中美竞争。','增加分币种、投资阶段、跨国可比募投退和创新产出序列；不可用政府债增长代替创投。')
rq('High','ASR',['C001','C005','C060','C024'],'人名、刊物、运河及闪击波兰等专名。','按TC01—TC15回听；规范实体可先建立，ASR归因仍待确认。')
rq('High','Source',['C001','C116'],'9月13口述、URL路径9月15、网页9月16存在三种时间。','回听开场并核纸刊、网站首次发布及修订记录；分别记录写作、印刷、上线时间。')
rq('High','ASR',['C047','C048','C050','C121','C122'],'4%、5%、2%以下、20%、2%点几混杂。','回听15:15—16:22；每项绑定发行人、币种、期限和日期；不要据相邻句自动纠错。')
rq('High','ASR',['C062','C063'],'134年可能是十三四年，30—40年另为粗估预测。','回听20:33及20:59；区分静态社会收益比和财务回收期。')
rq('High','ASR',['C068'],'重复读数出现百分之百2020年上半年。','回听23:38—23:43；首读2026H1近20%保留，重复句记录redundant occurrence。')
rq('High','ASR',['C111','C112'],'美元人民币金额转写损坏且混主观负担。','回听33:19—33:59；换算数值保持null，不凭常识补数。')
rq('High','Data',['C091','C092','C098'],'新增贷款在全部贷款中分母歧义；领域可能交叉。','获取统计表、基期和去重规则；60/10/70不能直接相加。')
rq('High','Data',['C037','C038','C039'],'35.6万亿、47%及首次仅匹配文章，未独立复算原始年表。','查截至知识截止时间可获得的央行2025年数据及修订版本。')
rq('High','Data',['C067','C068'],'企业债/同期贷款比值的分母定义及全年对半年比较。','确认企业贷款还是全部贷款、净融资还是发行量；同比较期间。')
rq('High','Data',['C074','C076','C077','C078','C079'],'存量占比四舍五入且间接项不全是贷款。','取得1990年代回溯及2026年6月存量分类；不强制近似值相加为100。')
rq('High','Data',['C060','C061','C063'],'投资预算、年度运输节约、社会效益与项目回款混用。','核预算/决算、目标年、运量爬坡及收入归属；不把收益预测当实现值。')
rq('High','Ontology',['C032','C033'],'股票被当债券/借条。','听验10:31—10:37；债权和股权单独分类，不在Normalized层修成正确金融常识。')
rq('High','Ontology',['C049','C048','C053'],'熊猫债、中央国债、地方专项债和协商展期混用。','核发行人及债权债务主体；对照财政部法定额度，不以一事一议替代发债制度。')
rq('High','Ontology',['C071','C072','C118','MC04'],'直接融资、银行风险与国家信用空间被当单一路径。','确认持债机构、显性/隐性担保、财政兜底与资本占用。')
rq('High','Ontology',['C088','C103','C104','C105'],'非标、表外、天使投资、银行非传统业务并列混称。','拆金融工具、会计位置、风险承担主体及业务牌照；不把表外都视为高利润业务。')
rq('High','Source',['C024','C025','C022'],'二战时序、谈判地点和反苏动机混杂。','先听验，再用确切早于截止时间的历史文献区分1938慕尼黑和1939波兰战争。')
rq('High','Data',['C012','C014'],'20%加息与利息超过GDP缺指标和模型。','核利率种类、路径、债务总额、有效付息率与名义GDP；假设不得变现状。')
rq('High','Data',['C019','C020'],'美联储扩表与美国财政债务膨胀混为一谈。','取截止前资产负债表序列和财政发行数据，分别核验存量、变化及因果。')
rq('High','Source',['C003'],'日央行已宣布加息但生效日9月24在截止之后。','按9月18文件记录announced；不得用今天首页的已生效状态倒填。')
rq('High','Forecast',[x['claim_id'] for x in forecasts],'大部分预测没有时间窗口、对象或阈值；职业结果亦条件不全。','按Forecast逐项补可接受判据；模型提案未经确认不可拿来评分。')
rq('Medium','ForecastLineage',['C008','C058','C056'],'此前讲过/金融机构曾预测均无历史来源。','定位历史SourceSegment；只保留retrospective claim，不回造成功历史预测。')
rq('Medium','Quantifier',['C010','C023','C028','C052','C053','C057','C075','C103','C105','C110'],'大家、全部、完全、只能等范围不明确或过强。','按主体和时点补样本；只支持方向时标core_claim_supported而非整句verified。')
rq('Medium','Data',['C042'],'社融负增长与剪刀差所指指标unknown。','听验13:16—13:28，并核月增量、同比、余额及M1/M2是否真被说出。')
rq('Medium','Data',['C093','C095','C096','C097'],'贷款增速基期、年均算法和分类口径未知。','取得统计原表；各类别独立检验，不用一个相近数字覆盖全部。')
rq('Medium','Data',['C064','C124','C125'],'运河水深水宽及西江/钦江水量说法未核。','设计断面和水文资料核验，区分航道深度与开挖深度。')
rq('Medium','Reasoning',['C059','C065'],'工程推进到公信力、再到化债有效性有代理变量跳跃。','补债权人行为和偿债现金流；项目能建不能代替政府财务可持续性。')
rq('Medium','Reasoning',['C005','C017','C022','C028','C043'],'对央行、美国、英法的动机归因缺一手行为证据。','保留观察者归因，不升级为对象的客观动机。')
rq('Medium','Source',['C117','C036'],'2013第二次危机事件不明确。','回听并定位具体事件，不自动新建模糊金融危机Event。')
rq('Medium','Ontology',['C083'],'三分之二是合理状态还是确定预测？','暂按normative，不赋Forecast目标；须音频语气或后续说明才改变。')
rq('Medium','Ontology',[],'缺全量既有Thesis注册表。','取得注册表后重做same/update/related/new；当前new均为临时本地决定。')
rq('Medium','EvidenceIntegrity',[],'731个SRT cue中有多处20秒长段；TXT/SRT很可能同次ASR。','音频定位后细化边界；转写一致不能当两份独立证据。')
rq('Low','Method',['C099'],'一集只能支持方法候选，不能证明稳定有效。','在未来30期统计方法复现、成功/失败及适用边界。')
rq('Low','Source',[],'外部网页为当前检索版本，缺截止日前网页快照和完整原数据表。','保留引用日期及检索日志，后续补历史版本；不把本次检索日当源首发。')
rq('Medium','Source',['C123'],'多数隐债经手人受处分的样本不明确。','案件级资料核对；不将主播概括当事实比例。')

issues=[
dict(id='SC01',issue='需将“何时说”与“何时公开”及视频偏移分开',proposal='asserted_at.recorded_at允许null；published_at作为proxy；media_offset单列。',used_extension='structured asserted_at'),
dict(id='SC02',issue='政策宣布、实施、可知时间并不相同',proposal='Event增加announced_at/effective_at；未来生效但已公布不是事后污染。',used_extension='effective_at'),
dict(id='SC03',issue='Official quote matched 与 underlying proposition verified不同',proposal='分开source_fidelity/measurement_veracity；官方因果解释仍待验证。',used_extension='external_quote_match + independent Assessment'),
dict(id='SC04',issue='一条金融观测必须标流量、存量、增速、比值分母和时间窗',proposal='增加numerator/denominator、gross_net、period_basis、vintage及classification_version；无法确定即null。',used_extension='Indicator.definition + value_kind'),
dict(id='SC05',issue='预测的预期运输收益不能放进实现值观测',proposal='Observation增加observed/projected/calculated/reported类型；社会成本节约与项目收入建不同Indicator。',used_extension='value_kind；OB20隔离'),
dict(id='SC06',issue='ASR不确定、口误、概念错误和算术错误不能用一个corrected标志表达',proposal='correction_status、acoustic_confidence、semantic_confidence、speaker_slip_confirmation分别记录。',used_extension='候选纠错applied=false；无speaker_slip_confirmed'),
dict(id='SC07',issue='claimant、读出者、被转述观点和评价观察者不相同',proposal='增加asserted_by、attributed_to及归因链；SRC03证明9527说过不证明潘功胜作此判断。',used_extension='claimant + asserted_by + attribution'),
dict(id='SC08',issue='Structural Process缺少正式对象但又不应强塞Event',proposal='建议新增StructuralProcess/TrendObservation；本期暂不私自实例化，只在Thesis承载解释。',used_extension='none; schema proposal only'),
dict(id='SC09',issue='Reasoning hop_count受拆分粒度影响，分支边数不等于最长路径',proposal='分别存edge_count、longest_path、explicit_shortcuts和model_bridge_count。',used_extension='hop_definition + distance_audit'),
dict(id='SC10',issue='非历史类比、比喻和当期案例信号没有合适argument_type',proposal='开放case_based_signal_inference、mixed_statistical_and_analogy；只AR03为historical_analogy。',used_extension='AR05/AR09类型显式候选扩展'),
dict(id='SC11',issue='quantifier不能承担所有确定性与排他性',proposal='保存raw_quantifier和modal_strength；量词过强独立于核心方向是否有支持。',used_extension='certainty_expressed + VA reason + Forecast modality'),
dict(id='SC12',issue='模型提出的预测判据不可倒灌成主播承诺',proposal='creator_criteria与proposed_criteria分开，未授权不评分。',used_extension='resolution_criteria.accepted_for_scoring=false'),
dict(id='SC13',issue='来源非独立：TXT/SRT同源、财联社/求是为转载链',proposal='source_family、derived_from和证据独立性；不能凭四个Source计四次支持。',used_extension='source_family + independent_evidence'),
dict(id='SC14',issue='重复朗读的数字错误不能生成多个同权Claim',proposal='ClaimOccurrence持有每次原文及局部信息增量，唯一命题挂多个occurrence。',used_extension='claim_occurrences'),
dict(id='SC15',issue='强冲突关系与长期结构性Contradiction是两个层次',proposal='claim_relation单独记录候选张力；五同条件未满足不建CONTRADICTS；结构矛盾更需多事件多Thesis。',used_extension='conflict_checks，不建立Contradiction'),
dict(id='SC16',issue='规范目标比例与趋势预测在一句中并存',proposal='C082为预测、C083为规范主张；不把2/3当官方或主播承诺目标。',used_extension='atomicity separated'),
dict(id='SC17',issue='推理边关系尚无提供的正式Relation registry',proposal='使用显式候选INFERENTIAL_SUPPORT_CANDIDATE而不宣称已是正式关系；正式入库前映射。',used_extension='candidate relation namespace')]

occurrences=[dict(claim_id='C068',evidence=evidence(499,502),information_gain='redundant',status='ASR_damaged_repeat_do_not_replace_first_read'),dict(claim_id='C091',evidence=evidence(634,639),information_gain='redundant',status='repeat_with_context'),dict(claim_id='C092',evidence=evidence(640,645),information_gain='redundant',status='repeat_with_context')]
conflicts=[
dict(id='CF01',claims=['C073','C094'],same_proposition='unknown: absolute scale versus unclear scale',same_reference_time='unknown',same_population='likely_same',same_scope='unknown',logically_incompatible='only_if_same_metric_and_period',relation='UNRESOLVED_SCOPE',decision='no_CONTRADICTS'),
dict(id='CF02',claims=['C057'],related_evidence=evidence(420,426),same_proposition='related',same_reference_time='unclear',same_population='unknown: 最近评论者可能不同于2023美国机构',same_scope='unknown',logically_incompatible='not_established',relation='POSSIBLE_POPULATION_DIVERGENCE',decision='no_CONTRADICTS'),
dict(id='CF03',claims=['C055'],source='SRC12',same_proposition=False,same_reference_time=False,same_population='partly',same_scope='unknown',logically_incompatible=False,relation='DIFFERS_BY_SCOPE_AND_TIME',decision='2025政策计划不能直接反证2026完成，但也不能证明完成'),
dict(id='CF04',claims=['C001'],source='SRC06',same_proposition='publication_variant_unknown',same_reference_time='unknown',same_population=True,same_scope='print/online/written_unclear',logically_incompatible='not_established',relation='SOURCE_DATE_REVIEW',decision='不先定speaker_slip或CONTRADICTS')]
arguments[10]['distance_audit']={'creator_expressed_shortcuts':[{'from':'C106','to':'C107','expression_level':'explicit'},{'from':'C107','to':'C115','expression_level':'explicit'},{'from':'C108','to':'C115','expression_level':'explicit'}],'expanded_bridge_edges':4,'model_bridge_count':4,'end_to_end_note':'若从科技生命周期起算，AR10前两步（显式）+C104到已增长C106（显式但证据不足）+AR11四步桥接共7个分析步骤；不是客观固定距离，不把捷径再重复相加。'}

qa_answers={
'A. 本期最核心的3—5条Argument Chain':[
'AR04：官方所述债券/贷款分类变化 → 9527加入逐案谈判和展期 → 政府债务压力骤减 → 隐债基本解决。最后一步证据最弱。',
'AR06/AR07：企业债/贷款增量比7%→近20% + 贷款被称为低成本 → 直接融资更便宜 → 国家信用占用减少 → 国家举债空间增大。价格推断与信用容量推断是两个不同的缺口。',
'AR08：直接融资比重提高 → 真实替代银行贷款（模型条件） → 传统净收益承压（模型条件） → 缺补偿时总利润下降（模型条件） → 表外业务方向。主播说出了方向，但没有完整给出中间条件。',
'AR09/AR10：贷款投向变化 → 9527按供血比喻识别机会 → 科技企业早期风险更适合天使资本 → 新旧动能转换落地。融资观察与产业结果不能合并。',
'AR11/AR12：国内融资结构变化 → 人民币早期风险资本扩张（待证） → 与美国可比优势变化（待证） → 中国挑战美国。显式捷径和模型补出的四条桥接边分别保存。'],
'B. 事实数据 → 9527解释 → 9527结构性推论':[
'数据层：C037/C038、C067/C068、C076—C079是文章报告的数据；本样本仅确认引述有出处，尚未独立复算底表，故多为likely_true而非verified。',
'解释层：C070把数量比解释为融资价格优势；C054把融资结构解释为化债压力下降；C099把投向解释为机会。均须单独核因果。',
'结构层：C055化债基本解决、C085—C088银行转型、C107产业转换、C115中美竞争地位变化。不能让前提数据的可信度自动传递到这些结论。',
'“科技/绿色/养老”应分四层：政策重点（PL02）；文章报告的信贷流向（OB14—OB18等）；主播对未来机会的预测C100；实体转型解释C107。没有独立产业结果观测，因此不将最后一层写成事实。'],
'C. 哪些地方体现可复用分析方法':[
'最直接的方法表达是25:20附近的“增量看趋势，存量看空间”，以及29:52后从资金流向寻找机会；HC01保存这种读数方法，同时记录本期把数量读成价格的失败风险。',
'16:22—18:26主动追问确权、谈判及过程成本，形成HC02。这是检查解释遗漏变量的方法，不能替代个案取证。',
'由本期不能证明“稳定”。必须在多期复现且记录失败样本后，才可讨论稳定性和有效性。'],
'D. 哪些观点绝不能进入Verified Knowledge':[
'C055隐债基本解决；C070直接融资一定更便宜；C072/C118腾出国家信用空间；C080股票约10%；C085—C088银行盈利与业务方向；C106早期非银行资本迅速扩张；C114/C115中美风险资本竞争。',
'C005/C017/C022/C028/C043所有未经证实的动机归因；C014利息超过GDP；C061社会效益当现金回款；C062损坏回本年限；C111美元换算损坏数字。',
'全部Forecast保持待验证；MC01—MC06只是模型诊断条件，不是主播证据。'],
'E. V0.2仍难表达什么':[
'至少需要SC01—SC17所列的时间、分母、数据版本、嵌套归因、预测观测、来源依赖、ClaimOccurrence、推理边与多路径距离等扩展。',
'金融结构变化首先是持续的Structural Process及指标序列，不是一次Event；关于其方向、原因和后果的解释才是Thesis；可迁移的局部因果机制才是Mechanism。V0.2缺StructuralProcess对象，本次不偷偷新增正式实体。',
'事实已宣布但未来生效（日本加息）与事后信息完全不同；必须按可知时间过滤，不按事件生效日期一刀切。'],
'F. 未来30期最值得复用的对象':[
'Indicator优先：社融流量/存量及债券、贷款、股权分项，企业债/贷款增量比，分行业贷款增速；新增银行分业务利润、人民币风险资本币种/阶段序列。先锁口径和vintage。',
'Mechanism：ME01生命周期与融资适配、ME02替代与收益补偿、ME03债务分类/期限/成本变化；均为candidate，需跨案例检验。',
'Thesis：TH01多元融资与投向重配、TH02银行收益结构转型；TH03竞争地位仅作为高推理距离待证假说。',
'Heuristic Candidate：HC01、HC02；30期中统计复现、适用条件、反例及错误率，不预设最终validated。']}

summary={'creator_claim_count':sum(c['claimant']!='model' for c in claims),'model_reconstruction_claim_count':sum(c['claimant']=='model' for c in claims),'claim_count':len(claims),'argument_count':len(arguments),'mechanism_count':len(mechanisms),'thesis_count':len(theses),'forecast_count':len(forecasts),'contradiction_count':0,'heuristic_count':len(heuristics),'review_queue_count':len(reviews),'review_by_priority':dict(collections.Counter(x['priority'] for x in reviews)),'semantic_segments':len(segments),'sources':len(sources),'source_cues':len(cues),'assessment_count':len(assessments),'veracity_counts':dict(collections.Counter(a['veracity'] for a in assessments))}
data={
'01_executive_extraction_report':{'sample_id':'Golden Sample #002','title':'《第七百六八期》当前背景下如何深刻认识中国金融结构变迁','status':'extraction_complete_pending_audio_and_data_review; not_validated_golden','knowledge_cutoff':CUTOFF,'cutoff_utc':'2026-09-21T02:32:21Z','largest_uncertainty':['录制时间不明，SRT未听验；不能确认ASR还是主播口误','原始金融统计底表未复算；官方文章有些分母本身含混','核心推论有数量到价格、分类到偿债、国内到跨国的跳跃'],'core_structural_judgments':['融资结构变化以持续过程表达，非单一事件','直接融资份额上升不自动推出银行总利润下降','产业融资观察不能直接证明实体转型及中美竞争优势'],'post_cutoff_contamination':{'used_in_original_arguments':False,'retrieval_after_cutoff':True,'quarantined_sources':['SRC17'],'historical_snapshot_limit':'所有网页为本次读到版本，发布日期支持可知性但未取得当时快照。'},'instruction_precedence':'按用户完整V0.2及后续要求；既有prompt_gpt6_astra.md和golden_report.md不覆盖本期指令。'},
'02_sources':sources,'03_transcript_corrections':{'accepted_ASR_corrections':[],'candidate_corrections':corrections,'needs_audio_review':[x['correction_id'] for x in corrections],'normalized_layer_policy':'未获音频确认的候选不应用；normalized_text暂等于raw_text。实体规范名另存Actor，不冒充语音纠错。'},'04_source_segment_annotations':{'speaker_slip_confirmed':[],'annotations':annotations},'05_semantic_segments':segments,'06_claims':claims,'07_actors_events_indicators_observations_policies':{'actors':actors,'events':events,'indicators':indicators,'observations':observations,'policies':policies},'08_expectation_snapshots':[],'09_veracity_assessments':assessments,'10_narrative_assessments':narratives,'11_arguments':arguments,'12_mechanisms':mechanisms,'13_theses':theses,'14_forecasts':forecasts,'15_contradictions':[],'16_candidate_heuristics':heuristics,'17_review_queue':reviews,'18_schema_ontology_extraction_issues_found':issues,'19_golden_sample_summary':summary,'20_six_questions':qa_answers,'source_segments':source_segments,'claim_occurrences':occurrences,'conflict_checks':conflicts,'post_cutoff_evaluation':{'status':'none; not_performed','note':'只隔离截止后首页状态，没有用后来结果评价本期预测。'}}

def s(x):
    if x is None:return 'null'
    if isinstance(x,(dict,list)):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
    return str(x)
def table(headers,rows):
    safe=lambda v:s(v).replace('|','∣').replace('\n',' / ')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(safe(v) for v in row)+' |' for row in rows])+'\n'
def block(obj):return '\n```json\n'+json.dumps(obj,ensure_ascii=False,indent=2)+'\n```\n'

report=['# MacroMind Golden Sample #002 — V0.2 可审计抽取\n',f'视频：《第七百六八期》当前背景下如何深刻认识中国金融结构变迁\n\n知识截止：**{CUTOFF}**。抽取与核验日期：{RETRIEVED}。\n',
'主文件是本报告和 [完整结构化JSON](./golden_sample_002.json)。原句与字幕位置见 [逐Claim证据](./evidence_segments.md)，完整731条字幕的独立层见 [转写层](./normalized_transcript.md)。本目录未改动任何原始TXT、SRT、MP3或MP4。\n',
'## 1. EXECUTIVE EXTRACTION REPORT\n',
'**status：抽取完成，待音频及数据复核；尚不可标为已验证Golden。** 原字幕跨度为00:00:00,090—00:35:11,540，分为17个语义主题。125条来自主播表达或其转述，另6条明确标为model_reconstruction。\n',
'最大不确定性是语音未实听、数字口径不全，以及从比例变化跨越到成本、偿债能力和国际竞争的推理。已发现本地音视频并做哈希，不能因此声称已经听验。accepted ASR correction及speaker_slip_confirmed均为0；候选专名修正不改原话。\n',
'核心结构判断：本期确实围绕融资渠道和投向变化展开，但“隐债基本解决”“银行总利润必降”“中国挑战美国风险资本优势”均不能仅凭这些比例进入Verified Knowledge。金融结构变迁更适合持续过程；关于过程的解释才升级为少量Thesis。\n',
'**post-cutoff contamination：未将截止后结果用于原始Argument。** 检索发生在截止后，网页历史版本未获得。日本央行当前首页的9月24日状态已隔离；采用9月18日宣布、9月24日生效的原决定，区别已知未来安排与事后事实。没有进行事后预测评分。\n',
'## 2. SOURCES\n',
table(['ID','Source / role','time','version','read_status'],[(x['source_id'],('['+x['title']+']('+x['url']+')' if 'url'in x else x['title'])+' / '+x['role'],x['time'],x['version'],x['read_status']) for x in sources]),
'SRC01—04是同一视频证据家族，TXT/SRT不是独立验证；SRC05是SRC06文章的转载来源，不能叠加证据权重。用户仅提供一个参考链接，没有完整视频简介或平台视频URL。检索发现但未采用的旁支结果不作为支持来源；年度原始金融数据未找到，不能宣称核实完毕。\n',
'## 3. TRANSCRIPT CORRECTIONS\n',
'### accepted ASR corrections\n\nnone。\n\n### candidate corrections / needs_audio_review\n\n以下均未应用。高置信是文字和实体匹配置信度，不是已听验置信度。\n',
table(['ID','原转写','候选规范形式','置信度','SRT cues','处理'],[(x['correction_id'],x['raw'],x['normalized_candidate'],x['confidence'],str(x['evidence']['cue_start'])+'—'+str(x['evidence']['cue_end']),'needs_audio_review; applied=false') for x in corrections]),
'数字禁止按算术静默修正。“134”不能擅自改成“十三四”，“20%”不能自动改“2%”；“10%股票占比”保留为C080，另做算术诊断。\n',
'## 4. SOURCE SEGMENT ANNOTATIONS\n',
'speaker_slip_confirmed：none。self_correction仅指文本可见的自我重述，不声称音频确证。疑似事实/概念错误均留Review。\n',
table(['ID','annotation_type','cues','说明'],[(x['annotation_id'],x['annotation_type'],f"{x['evidence']['cue_start']}—{x['evidence']['cue_end']}",x['note']) for x in annotations]),
'## 5. SEMANTIC SEGMENTS\n',
table(['segment_id','start','end','topic','cues'],[(x['segment_id'],x['start'],x['end'],x['topic'],f"{x['cue_start']}—{x['cue_end']}") for x in segments]),
'按论证主题切分，边界采用SRT cue粒度；部分20秒长cue内包含多主题，未假装逐词对齐。\n',
'## 6. CLAIMS\n',
'以下每条均可回溯到同名SS-C…证据。`asserted_at`是录制时间unknown、发布时间proxy及SRT偏移的结构，不将发布时间加偏移冒充真实发言时刻。Claimant A001=9527，A002=潘功胜（由9527转述）；model=模型补出的条件。原文重复通过ClaimOccurrence合并，损坏重读不覆盖首次读数。\n']
for c in claims:
    report += [f"### {c['claim_id']} · {c['statement']}\n",f"- `segment_id`: {c['segment_id']}；`claimant`: {c['claimant']}；`asserted_by`: {c['asserted_by']}。{c['attribution']}\n",f"- `claim_type`: {c['claim_type']}；`derivation_type`: {c['derivation_type']}；`temporal_mode`: {c['temporal_mode']}。\n",f"- `asserted_at`: {s(c['asserted_at'])}\n",f"- `reference_time`: {c['reference_time']}；`knowledge_cutoff`: {c['knowledge_cutoff']}。\n",f"- `population`: {c['population']}；`quantifier`: {c['quantifier']}；`certainty_expressed`: {c['certainty_expressed']}。\n",f"- `source_segment`: [{c['source_segment']}](./evidence_segments.md#{c['source_segment'].lower()})；`atomicity_group_id`: {c['atomicity_group_id']}；`information_gain`: {c['information_gain']}。\n"]
report += ['## 7. ACTORS / EVENTS / INDICATORS / OBSERVATIONS / POLICIES\n','### Actors\n',table(['ID','规范实体','aliases','kind'],[(x['actor_id'],x['canonical_name'],x['aliases'],x['kind']) for x in actors]),'### Events\n',table(['ID','现实状态变化','occurred_at','effective_at','来源/属性'],[(x['event_id'],x['name'],x['occurred_at'],x.get('effective_at'),x['source_id']+' / '+x['status']) for x in events]),'不把中国金融结构变化建成一次Event；不把未指明的2013危机建成既定Event。\n','### Indicators\n',table(['ID','指标','类型','定义/分母','unit'],[(x['indicator_id'],x['name'],x['measure_type'],x['definition'],x['unit']) for x in indicators]),'### IndicatorObservations\n',table(['ID','Indicator / Claim','reference_period','released_at','value / unit','previous / revision','kind'],[(x['observation_id'],x['indicator_id']+' / '+s(x.get('claim_id')),x['reference_period'],x['released_at'],s(x['value'])+' '+x['unit'],s(x['previous'])+' / '+s(x['revision']),x['value_kind']) for x in observations]),'所有报告性观测保留来源身份，非已审计事实。OB11（股票10%）和OB20（社会效益50多亿）隔离，不作为canonical。三分之一记作~33.3仅为结构化近似表达，不提高原精度。\n','### Policies\n',block(policies),'## 8. EXPECTATION SNAPSHOTS\n','none。“大家普遍认为紧缩不久”缺Population边界；企业选择债券不自动等于可观察的集体预期。\n','## 9. VERACITY ASSESSMENTS\n','以下逐Claim评估。时间为2026-09-24、as_of固定知识截止；observer=model。verified只表示该命题已有足够直接支持，不把引述匹配当底层事实全部核实。\n',table(['assessment_id','Claim','veracity','evidence_sources','理由'],[(x['assessment_id'],x['claim_id'],x['veracity'],x['evidence_sources'],x['reason']) for x in assessments]),'所有数值类likely_true仍有对应Review；数字与原文一致、分母可靠、实际音频说法正确是三个不同检查。\n','## 10. NARRATIVE ASSESSMENTS\n',block(narratives),'## 11. ARGUMENTS\n','推理边`INFERENTIAL_SUPPORT_CANDIDATE`是本次明确申报的候选关系，不冒充已有registry枚举。每步限制均保存于JSON；下文保留from/to、模式、表达层级、证据与最弱环节。\n']
for a in arguments:
    report += [f"### {a['argument_id']} · {a['title']}\n",f"`argument_type`={a['argument_type']}；`premises`={s(a['premises'])}；`conclusion`={a['conclusion']}；`inference_mode`={s(a['inference_mode'])}；`expression_level`={s(a['expression_level'])}；`hop_count`={a['hop_count']}（列出边数，非总是最长路径）。\n",table(['step','from → to / relation','inference_mode','expression_level','evidence','解释 / limitations'],[(x['step_id'],s(x['from'])+' → '+x['to']+' / '+x['relation'],x['inference_mode'],x['expression_level'],x['evidence'],x['explanation']+' / '+x['limitations']) for x in a['steps']]),f"**Argument limitation：{a['limitations']}**\n"]
    if 'source_case'in a:report.append(block({k:a[k] for k in ['source_case','target_case','shared_mechanism','limits_of_analogy']}))
    if 'distance_audit'in a:report.append(block(a['distance_audit']))
report+=['## 12. MECHANISMS\n',block(mechanisms),'只建3个Candidate；美元损失厌恶类比和运河信用信号保留在Argument，未急于升级成通用机制。\n','## 13. THESES\n',block(theses),'注册表检索范围仅限当前工作区与Golden #001摘要。上期的安全资产、AI等主题不等同本期融资结构；资本竞争主题仅related，不能虚构其Thesis ID。\n','## 14. FORECASTS\n',block(forecasts),'C083的直接融资2/3是规范主张，未当成时间明确的预测。made_at用发布proxy并保留录制时间null。所有resolution_criteria均区分主播未给与模型建议，尚不可评分。\n','## 15. CONTRADICTIONS\n','none。没有满足“长期张力＋多事件＋多Thesis＋双方目标约束持续互动”的证据；中美、银行/资本市场和中央/地方不是自动Contradiction。\n\n局部命题冲突检查另列，不混同结构性Contradiction：\n',block(conflicts),'## 16. CANDIDATE HEURISTICS\n',block(heuristics),'## 17. REVIEW QUEUE\n']
for priority in ['Critical','High','Medium','Low']:
    report += [f'### {priority}\n',table(['ID','类别','Claims','问题','完成条件'],[(x['review_id'],x['category'],x['claim_refs'],x['issue'],x['required_action']) for x in reviews if x['priority']==priority])]
report+=['## 18. SCHEMA / ONTOLOGY / EXTRACTION ISSUES FOUND\n',table(['ID','不足','建议','本次显式处理'],[(x['id'],x['issue'],x['proposal'],x['used_extension']) for x in issues]),'## 19. GOLDEN SAMPLE SUMMARY\n',block(summary),'本次完成的是可审计抽取包，不是消除全部不确定性的最终认证。Traceability链已结构化；音频真值和数据底表仍须通过Review闭环。\n','## 额外六个问题\n']
for q,ans in qa_answers.items():report.extend(['### '+q+'\n','\n'.join('- '+x for x in ans)+'\n'])
report+=['## 附：复核入口\n','- 读数与原句：[逐Claim证据](./evidence_segments.md)。\n- 待听项目：[音频复核清单](./audio_review.md)。\n- 机器可读：[完整JSON](./golden_sample_002.json)。\n- 完整性结果：[validation.json](./validation.json)。\n- 原文件SHA256和检索依据：[sources.json](./sources.json)。\n']
(OUT/'golden_sample_002_report.md').write_text('\n'.join(report).replace('(./','('+OUT.as_posix()+'/'),encoding='utf-8')
dump('golden_sample_002.json',data)
dump('sources.json',sources)
dump('claims.json',claims)
dump('review_queue.json',reviews)
dump('source_segments.json',source_segments)
dump('normalized_transcript.json',[dict(**c,raw_text=c['text'],normalized_text=c['text'],normalization_status='no_candidate_applied_pending_audio') for c in cues])
(OUT/'normalized_transcript.md').write_text('# 独立转写层（尚未应用候选纠错）\n\n原始文件未修改。此层原样保留字幕文本；候选纠错另见报告。时间精度仅为ASR cue。\n\n'+'\n\n'.join(f"### Cue {c['cue_id']} · {c['start']}—{c['end']}\n\n{c['text']}" for c in cues),encoding='utf-8')
(OUT/'evidence_segments.md').write_text('# 逐Claim原始证据\n\n来源SRC03。保留原始ASR原句，未替换专名与数字。MC段只作模型重建的上下文，绝非主播说出该模型条件的证据。\n\n'+'\n\n'.join(f"## {e['source_segment_id']}\n\nSRT cues {e['cue_start']}—{e['cue_end']}；{e['start']}—{e['end']}；Source={e['source_id']}。\n\n> {e['raw_text']}" for e in source_segments),encoding='utf-8')
(OUT/'audio_review.md').write_text('# 音频复核入口\n\n尚未实际听验。复核时记录raw heard / ASR output / decision，不能仅按官方正确数字改字。\n\n'+table(['ID','start','end','raw','candidate'],[(c['correction_id'],c['evidence']['start'],c['evidence']['end'],c['raw'],c['normalized_candidate']) for c in corrections])+'\n\n重点：C080（26:46—26:54）、C094（31:24—31:27）、C033（10:31—10:37）、C049（15:41—15:43）、C025（07:09—07:25）。\n',encoding='utf-8')

# Integrity validation: meaningful checks of references, extraction coverage and untouched inputs.
errors=[]
ids={c['claim_id'] for c in claims}; ssids={e['source_segment_id'] for e in source_segments}; srcids={x['source_id'] for x in sources}
required=['claim_id','segment_id','claimant','statement','claim_type','derivation_type','temporal_mode','asserted_at','reference_time','knowledge_cutoff','population','quantifier','certainty_expressed','source_segment','atomicity_group_id']
for c in claims:
    if any(k not in c for k in required):errors.append('missing fields '+c['claim_id'])
    if c['source_segment'] not in ssids:errors.append('dangling evidence '+c['claim_id'])
    if c['knowledge_cutoff']!=CUTOFF:errors.append('cutoff mismatch '+c['claim_id'])
if len(ids)!=len(claims):errors.append('duplicate Claim IDs')
if collections.Counter(x['claim_id'] for x in assessments)!=collections.Counter(ids):errors.append('assessment coverage not exactly one each')
if {x['claim_id'] for x in forecasts}!={x['claim_id'] for x in claims if x['claim_type']=='forecast'}:errors.append('forecast coverage mismatch')
for a in arguments:
    if not a['limitations']:errors.append('missing limitation '+a['argument_id'])
    for st in a['steps']:
        if not set(st['from']+[st['to']])<=ids:errors.append('dangling argument '+a['argument_id'])
        if not set(st['evidence'])<=ssids:errors.append('dangling step evidence '+a['argument_id'])
if [i for sg in segments for i in range(sg['cue_start'],sg['cue_end']+1)]!=list(range(1,len(cues)+1)):errors.append('cue coverage mismatch')
for t in theses:
    if not t['traceability']:errors.append('empty thesis trace '+t['thesis_id'])
    for tr in t['traceability']:
        if tr['claim_id'] not in ids or tr['source_segment']not in ssids or tr['source_id']not in srcids:errors.append('invalid thesis trace '+t['thesis_id'])
for src in sources[:4]:
    if 'SHA256:'+sha(Path(src['path']))!=src['version']:errors.append('raw input modified '+src['source_id'])
for a in assessments:
    if 'SRC17'in a.get('evidence_sources',[]):errors.append('post-cutoff source used '+a['claim_id'])
txt_body=raw_txt[raw_txt.index('[00:00:00]'):]
txt_compact=re.sub(r'\s+','',re.sub(r'\[\d\d:\d\d:\d\d\]','',txt_body))
srt_compact=re.sub(r'\s+','',''.join(c['text'] for c in cues))
validation=dict(status='PASS' if not errors else 'FAIL',errors=errors,checks=['all_claim_fields_present','one_veracity_assessment_per_claim','every_forecast_claim_has_forecast','all_argument_claim_and_evidence_references_resolve','every_argument_has_limitations','semantic_segments_cover_all_cues_once','theses_have_resolvable_trace_chains','raw_input_SHA256_unchanged','no_quarantined_post_cutoff_source_in_veracity_support'],txt_srt_text_equal_ignoring_whitespace_and_txt_time_labels=txt_compact==srt_compact,summary=summary,limits=['not an audio verification','not an independent statistical replication','not a certification of causal validity','web pages lack archived as-of versions'])
dump('validation.json',validation)
print(json.dumps(validation,ensure_ascii=False,indent=2))
