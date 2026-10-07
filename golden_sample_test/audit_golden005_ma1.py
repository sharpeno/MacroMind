import json,hashlib,collections
from pathlib import Path
from datetime import datetime,timezone,timedelta
R=Path(__file__).resolve().parent;O=R/'golden_sample_005'
D=json.loads((O/'golden_sample_005.json').read_text(encoding='utf-8'))
patch=Path(r'G:\youhegaojian\迭代\MacroMind V0.3.1-MA.1 Minor Patch.md')
continuation=Path(r'C:\Users\无语\.codex\attachments\547bb087-d209-4712-91fd-b6663b41b53a\已粘贴的文本.txt')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
M=D['26_ANALYST_METHOD_SIGNALS']['signals'];A=D['18_ARGUMENTS'];C=D['08_CLAIMS'];V=D['16_VERACITY_ASSESSMENTS'];I=D['13_INDICATORS_OBSERVATIONS']['indicators'];B=D['13_INDICATORS_OBSERVATIONS']['observations']
required_m=['domain','transferability','recurrence_match','matched_prior_signal_refs','matched_scope','recurrence_evidence']
required_a=['inference_modes','expression_levels','most_fragile_step','inferential_distance','creator_shortcuts']
veracity_enum={'verified','likely_true','uncertain','disputed','likely_false','false','unverifiable'}
cmp_enum={'none','yoy','qoq','mom','sequential','versus_consensus','versus_guidance','versus_baseline','versus_prior_period','percentage_point_change','absolute_delta','indexed_to','other','unknown'}
f=[m for m in M if m['signal_type']=='failure_pattern']
findings=dict(method_fields_missing={k:sum(k not in m for m in M) for k in required_m},failure_fields_missing={k:sum(k not in m for m in f) for k in ['observed_action','failure_assessment','failure_type','assessment_confidence']},argument_fields_missing={k:sum(k not in a for a in A) for k in required_a},observation_baseline_source_ref_missing=sum('baseline_source_ref' not in b['comparison_basis'] for b in B),observation_recognition_stage_missing=sum('recognition_stage' not in b for b in B),claim_recognition_stage_missing=sum('recognition_stage' not in c for c in C),indicator_recognition_stage_missing=sum('recognition_stage' not in i for i in I),observation_comparison_type_outside_enum=[b['observation_id'] for b in B if b['comparison_basis']['comparison_type'] not in cmp_enum],veracity_status_outside_enum=sum(v['status'] not in veracity_enum for v in V),failure_dual_observer_pass=all(m.get('observed_reasoner_id')=='analyst_youhegaojian9527' and m.get('annotation_observer')=='model_gpt6' for m in f))
summary=dict(source_count=len(D['02_SOURCES']),source_family_count=None,source_family_count_status='not_separately_instantiated_in_baseline',origin_family_count=len(D['04_SOURCE_FAMILIES_ORIGIN_FAMILIES']['origin_families']),claim_count=len(C),claim_occurrence_count=len(D['09_CLAIM_OCCURRENCES']),actor_count=len(D['10_ACTORS']),event_count=len(D['11_EVENTS']),structural_process_count=0,indicator_count=len(I),observation_count=len(B),argument_count=len(A),creator_argument_count=17,model_diagnostic_argument_count=1,mechanism_count=3,new_mechanism_candidate_count=2,reused_mechanism_candidate_count=1,mechanism_usage_count=3,scenario_count=len(D['21_SCENARIOS']),thesis_count=len(D['22_THESES']),forecast_count=len(D['23_FORECASTS']),unconditional_forecast_count=5,conditional_forecast_count=0,branch_selection_forecast_count=5,conditional_count_definition='conditional denotes resolvable_conditional_forecast subtype only; branch selection counted separately',contradiction_count=0,candidate_heuristic_count=0,method_signal_count=len(M),method_signal_counts=dict(attention=1,question=1,evidence_preference=1,mechanism_usage=1,branching=1,judgment=2,analogy=1,falsification=0,failure=3),review_queue_count=sum(len(v) for v in D['27_REVIEW_QUEUE'].values()))
checks=[
 ('R056','partial','13条MR表有部分匹配理由，但11条Signal缺正式recurrence_match/matched_scope等字段，recurrence_status亦为自定义值。'),
 ('R057','partial','MR07/MR08能定位具体子动作；MR01只有GS001摘要，应降uncertain；MR03的“执行条件”过宽，需补具体变量否则uncertain。'),
 ('R058','pass','MS07—MS09均保存被观察推理者与模型标注者；但完整Failure Schema字段仍不齐。'),
 ('R059','pass','三个Failure均未升级稳定Pattern或Skill。需把promotion_status规范化。'),
 ('R060','partial','14条Observation都有比较框，但全部缺baseline_source_ref，类型也未按新增枚举规范。'),
 ('R061','partial','未见把percentage point当percent；但倍数/差值和降低到/下降混淆使完整比较校验不能通过。'),
 ('R062','partial','主要跨层结论拆开了；recognition_stage缺失，股价上涨X04/I06/O06误标valuation而非price。'),
 ('R063','partial','C001→C026、C110→C111等边明确且进入Review；部分端点角色unknown或遗漏，仍需逐边检查。')]
stress=[
 ('T01','pass','C001回收与C026低成本分开；AR04保留Shortcut，DA01独立诊断。'),
 ('T02','pass','X03/O10是着陆腿媒体能力声称，实飞次数未填20。'),
 ('T03','pass','StructuralProcess=0；EV01/EV02不自动变经济产业过程。'),
 ('T04','pass','技术与利润分Claim，TH01待验证；此pass仅表示边界保留。'),
 ('T05','not_exercised','本期无具体订单→收入→利润数据链可检验；不能声称已充分验证该规则。'),
 ('T06','partial','没有把发射成本与企业总成本明确等同；X10/O13降幅口径仍有编码问题。'),
 ('T07','partial','保留中国/SpaceX差异限制；AR04/AR08的跨案例可比性仍需更明确角色与范围。'),
 ('T08','partial','17 Scenario与10 Forecast分列；C005表达条件后会超越，因不可结算而排除的准入理由应复审，不能把low resolvability当一概排除标准。'),
 ('T09','pass','M01—M05及DA01未变成9527方法证据。'),
 ('T10','pass','双observer已保存；完整Failure字段待补。'),
 ('T11','partial','旧MR表有exact/partial/analogous机制，缺none/uncertain正式表示及Signal字段。'),
 ('T12','needs_correction','O01把比例当差值，O13将歧义70写成delta；全部Observation缺baseline_source_ref。')]
audit=dict(audited_at=datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),scope='supplement_only_no_baseline_mutation',baseline=[dict(path=str(p),sha256=digest(p)) for p in [O/'golden_sample_005.json',O/'golden_sample_005_report.md',patch,continuation]],overall='partially_compliant_requires_targeted_revision',field_findings=findings,rules=[dict(rule=r,status=s,evidence=e) for r,s,e in checks],stress_tests=[dict(test=r,status=s,evidence=e) for r,s,e in stress],recounted_summary=summary,freeze_gate=dict(core_ontology_freeze_candidate='Yes_with_scope_limit',formal_core_ontology_freeze='Not Yet',golden005_audited_freeze='Not Yet',new_core_object_required='No',analyst_skill='NOT READY',macromind_core_skill='NOT READY'),golden_status='extraction_complete_ma1_revision_required_review_pending_not_frozen',status_note='审计结论；尚未回写原对象。原37项Review与本次新增审计发现分别计数。')
(O/'ma1_compliance_audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
report='''# Golden #005 — MA.1补充审计

本次以用户补全的第39—53节和《MacroMind V0.3.1-MA.1 Minor Patch》审计既有#005，不重新抽取视频，不用后续新闻补历史观点。审计对象以同目录 ma1_compliance_audit.json 的SHA256固定。以下修正均为审计建议，未回写原报告/JSON；不能把“建议补字段”计为“已合规”。

## 1. MA.1 compliance audit

**结论：部分合规，尚不能通过完整MA.1冻结验收。** 原validation.json的passed仅适用于其列出的引用链、归属等检查，不等于补全规范通过。

|规则|结论|证据与缺口|
|---|---|---|
'''
report+='\n'.join(f'|{r}|{s}|{e}|' for r,s,e in checks)
report+='''

**字段审计：** 11条Method Signal均缺domain、transferability、recurrence_match、matched_prior_signal_refs、matched_scope、recurrence_evidence。复现信息虽部分存在于MR侧表，但未按所需字段表达；`limited_match`与`first_observation_in_available_registry`也不是规定的recurrence_status枚举。匹配精度和出现频次应分开保存，partial/analogous不能自动等于完整方法repeated。

3条Failure均有双observer，均缺observed_action、failure_assessment、failure_type、assessment_confidence。18条Argument均缺规定名称的inference_modes、expression_levels、most_fragile_step、inferential_distance、creator_shortcuts：多数信息已有单数字段、边属性或文字，属于需要结构化迁移，不是重新发明推理。

14条Observation均缺baseline_source_ref与recognition_stage；139条Claim和14条Indicator均未给recognition_stage。并非所有对象都有会计确认阶段，应在适用项填写、其余unknown，不能根据字段缺失猜实际阶段。

139条Veracity Assessment均未使用第42节的七值验证状态。现有“来源声明被支持”“尚未评价预测”“模型诊断”等有价值，但属于不同评估维度，应留在assessment_kind/detail，另给规范verification_status；不能简单全映射为verified或unverifiable。

**专题与时间边界：** 航天、Moderna、债市、AI和汇率均已覆盖。后半跨域连接有主播原文依据，但不能让医药消息直接证明火箭商业化。Reuters原页时间仍unknown，隔离继续有效。X03应明确为Media Claim（关于部件能力），其工程依据target/estimate仍unknown，不能将这些类别混在同一轴。

**T01—T12专项压力测试：**

|测试|结论|依据|
|---|---|---|
'''
report+='\n'.join(f'|{r}|{s}|{e}|' for r,s,e in stress)
report+='''

通过表示本样本守住了相应表达边界，不证明主播结论正确，也不代表全库已验证。T05无充分实测案例，不以“没有犯错”冒充压力测试成功。

**Candidate A—D复现审查：**

|候选|recurrence_match|matched_scope|
|---|---|---|
|A 叙事之后追问约束/执行能力|partial|C050/C053/C054追问星链资金与付款者，C036—C040追问算力持续成本；未完整复现#003的通道控制判据。|
|B 增量与存量分开观察|none|数量扩容不等于分别用流量、存量作不同判断；本期没有完整证据。|
|C 成本与可持续时间/回收期|partial|C036/C037/C039使用寿命—替换成本子路径；没有完整回收期或可持续期限计算。|
|D 单次表现不是持续性充分证据|partial|C103拒绝用AI估值证明技术，C110—C112对药物利好追问盈利支撑；不是完整产业接受规则。|

MR01与#001摘要之间最多uncertain；MR03目前只剩泛化的“执行条件”，也应暂降uncertain，待补具体证据。MR09只能保留受限analogy类型相似，不能作为同一机制复现。MR10“比例传递到异质结果”可保留analogous，绝非稳定失败模式。MR02/MR11—MR13的未观察应表示none。exact仍为0。

## 2. Final Questions L–O

### L. 跨领域复现

**存在更强的potentially_general候选证据，但只有子动作层面。**

|分析动作|领域一证据|领域二证据|可以得出的结论|
|---|---|---|---|
|不止看资本故事，还追问经济支撑|太空算力：AR05，C036—C040、C042，SS-C036等，10:43—12:01|医药：AR15，C110—C112，SS-C110—SS-C112，29:12—29:45|跨领域共同使用成本/盈利作为解释约束；完整变量与判断门槛仅partial相同。|
|追问长期项目由谁付款、资金如何接续|星链：AR07，C050/C053/C054，约12:59—13:59|下行融资：AR09，C068—C070，约17:59—19:09；债市解释AR10|付款者/融资渠道子动作跨议题重复；“没人买美债”等答案不因此获得事实支持。|

相反证据也要保留：C026由回收直接推出低成本，C033正面使用上市估值作为融资示范，C060/C061跨越客户和成本证明。这限制了把上述方法写成“始终先核实经济性”的普遍规则。

这些段落都出自同一期、同一个分析师，且部分共同服务于中美资本竞争叙事；不是独立样本。最合适状态是potentially_general候选，仍需跨期反例、适用范围和人工复核。

### M. Failure Signal

已有三个信号均只保留single failure signal：

|对象|观察到的动作|模型的缺陷评估|failure_type建议|
|---|---|---|---|
|MS07 / AR04、AR08|C001→C026由回收推出已经低成本；C056→C061由成本优势推全球全部需求|未给经济复用证据；忽略需求、采购与市场边界|unsupported_causal_jump；第二条边另作scope_shift评估|
|MS08 / AR07|C045—C049将卫星数量扩张倍数传给带宽、网速、成本与替代光纤|这些变量不存在由数量本身保证的同比例关系|unsupported_causal_jump；不能仅因都是倍数就断言dimensional_error|
|MS09 / AR15|C110→C111从患者治疗昂贵推企业利润空间小|患者支付价格不等于企业成本或利润率|object_role_shift|

每项需要分别写observed_action与failure_assessment；统一observed_reasoner_id=analyst_youhegaojian9527、annotation_observer=model_gpt6，analysis_context=historical_reconstruction。对文本动作定位可有较高信心，对“稳定失败模式”的信心仍不足，且未听音。

C072→C073“回购→长债无人购买”也可定位为新的待审unsupported_causal_jump，但本次不为了数量新增Method对象；RQ11已保留。国内/国外证据门槛不对称可作反例检查，不应自动解释为偏见或动机。

### N. Core Ontology

**No：没有发现必须增加的新核心对象。**

着陆腿与整箭的范围可由Claim/Indicator的对象范围表达；能力/计划/已实现用value_status与recognition_stage区分；回收用Event，持续过程证据不足就不建StructuralProcess，产业判断放Thesis/Forecast。推理缺陷是Assessment，方法复现是辅助信号及匹配关系。SourceVersion、Observation、Scenario、MethodSignal仍为既有辅助结构，不因本期使用它们而扩充14个核心对象。

可考虑明确对象部件范围、比较值运算符、各评估维度和跨段连接归属等字段，但应列为Schema细化，不升级核心Ontology。

### O. Freeze Gate判断

**Core Ontology 0.3 → Freeze Candidate：Yes，有限度支持。** #005的难点可以由既有核心对象加辅助字段容纳，没有被迫新增核心类型。

**Core Ontology正式Freeze：Not Yet。** 本次没有重审五期全部原始证据；#001只有摘要，#004轻量迁移尚未在本次验证完成，#005本身又有MA.1字段和语义修正项。这个Yes是对结构稳定方向的支持，不是全库合格证明。

**把字段缺失当成需要否定14核心结构：No。** 当前缺口主要在抽取实现、字段契约和质量控制；没有理由据此推翻核心对象划分。

## 3. Freeze Gate

|门槛|当前状态|通过条件|
|---|---|---|
|核心对象是否足够表达本期|通过，支持Freeze Candidate|维持14核心；不为单个数值/部件问题增加核心类型|
|完整MA.1字段及枚举|未通过|补齐Signal、Failure、comparison、recognition与Argument结构；验证七值状态映射|
|数值及角色无静默转换|未通过|修O01与O13的delta，修X04/I06/O06的price角色；保留未知基准|
|跨样本复现可追溯|部分通过|规范none/uncertain；弱匹配降级；与#001的摘要级证据明确区分|
|Scenario/Forecast准入一致|待复核|复审C005是否仅因低可结算性被错误挡出Forecast；不在本次擅改数量|
|覆盖、归属、模型隔离|现有局部校验通过|新增测试也须覆盖语义有效性；不能仅检查ID存在|
|黄金样本人工裁决|未完成|优先处理关键ASR与影响主链的Review；可保留经裁决的unknown，不要求所有外部事实都变verified|

9527 Skill：NOT READY。MacroMind Core Skill：NOT READY。MA层可继续测试，不能把本次审计当作正式冻结批准。

## 4. 是否存在需要修正的已有对象

**存在。主要是定点迁移，无需整期重跑。**

1. **MS01—MS11 / MR表：** 补正式字段与合法recurrence_status，按“出现频次”与“匹配精度”分层；MR01/MR03降uncertain，未观察项用none。多先例不同精度保留逐对记录，Signal总括不可取最大值冒充所有匹配相同。
2. **MS07—MS09：** 增observed_action、failure_assessment、failure_type、assessment_confidence；规范promotion_status。已有双observer保留。
3. **C025/O01：** 0.1是相对比值，不是delta。保留raw与ratio_value=0.1（若采用辅助字段须声明），comparison_type可用other并给详细定义，delta_value=null；基准成本未知，不反算美元差额。
4. **X10/O13：** “降到”与“下降”未定时delta_value必须null；raw 70保留。不能先填70再仅靠Review文本抵消错误。
5. **X04/I06/O06：** 盘前股价变动应为price；C066/I05/O05的市值变动才是valuation。I03/I04卫星颗数更适合volume而不是自动等同服务capacity；许可数量与部署阶段另存。
6. **适用Claim/Indicator/Observation：** recognition_stage按来源填planned等或unknown；O12许可不能写deployed；O10设计/能力不能写实际utilized。补baseline_source_ref，即使unknown也明确null。technology等本期提示词专用角色与通用枚举的差异应写映射规则；不要把所有专用值误判为新增核心对象。
7. **全部Veracity Assessment：** 七值验证状态与证据状态拆开；“未评价预测”留在Forecast评价状态，不冒充verification enum。合理unknown不能机械标false或unverifiable。
8. **AR01—AR17/DA01：** 补规定字段，最脆弱边引用具体step；距离统计注明节点粒度、作者Shortcut和模型跨段整理。DA01保持model_diagnostic，绝不映射成历史重建。C005准入进入定点Review。
9. **辅助标签与证据质量：** 原研究只做文本规范化，accepted_ASR_corrections中的“信往回舟→网系回收”等不能宣称已确认ASR责任；蓝天→蓝箭可能是实体纠正，也可能原话口误，须保留failure_origin unknown。C003的重复Occurrence指向213—218字幕，实际谈故事空间而非十年技术进步，应复审/移除该重复映射。
10. **IS01/IS11/IS16、README、Summary、Final Questions、validation与生成脚本：** 保留“当时prompt缺失”的版本历史，当前规范已补全后不得继续说none/uncertain不被允许。原A—K编号与补全prompt题义不完全相同；需按新第51节重排并补成第30节。Summary补分项，SourceFamily不能拿OriginFamily数量代替。新验证脚本必须按六个comparison字段检查，避免以后重跑再次产生旧结构。

**SourceFamily备注：** 原第04节只有origin_families，没有单独建立SourceFamily对象集合，因此source_family_count=unknown；不能取Source数或OriginFamily数充数。

本次只保存审计补充，不改写原Claim及事实状态，不回写已冻结或待审的旧样本；上述清单是明确待迁移项。

## 5. Golden status

建议当前状态：

```yaml
golden_id: GS005
extraction_status: complete
ma1_compliance: partial_requires_revision
golden_status: extraction_complete_ma1_revision_required_review_pending_not_frozen
freeze_candidate_support: yes_for_core_ontology_only
frozen: false
audio_review: not_completed
analyst_skill: NOT_READY
macromind_core_skill: NOT_READY
```

**不是宣布样本失败，也不是宣布已达到冻结标准。** 主体抽取有价值；完整MA.1契约未满足、若干字段存在会误导机器使用的语义问题，须定点修正后再验收。

以下为对原对象的重新计数；并不代表修正已经完成。原37项Review与本次审计发现分开计数，避免虚构已新增到Review Queue的对象。

```json
'''
report+=json.dumps(summary,ensure_ascii=False,indent=2)+'\n```\n'
(O/'golden_sample_005_ma1_supplement.md').write_text(report,encoding='utf-8')
print(json.dumps(dict(field_findings=findings,summary=summary,baseline_unchanged=all(digest(Path(x['path']))==x['sha256'] for x in audit['baseline']),report=str(O/'golden_sample_005_ma1_supplement.md')),ensure_ascii=False,indent=2))
