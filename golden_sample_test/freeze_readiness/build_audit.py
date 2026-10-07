"""Read-only source audit; writes only sibling audit artifacts. No migrations/imports."""
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
PROJECT = ROOT.parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

paths = {'GS001': ROOT/'golden_report.md'}
for n in range(2,6):
    paths[f'GS00{n}'] = ROOT/f'golden_sample_00{n}'/f'golden_sample_00{n}{".ma1_accepted" if n>=4 else ""}.json'
paths.update({
 'PROMPT':PROJECT/'prompt/MacroMind Core Ontology V0.3.md',
 'V02':PROJECT/'迭代/MacroMind V0.2 Patch.md',
 'V03':PROJECT/'迭代/MacroMind Ontology  Schema  Extraction Spec V0.3 Patch.md',
 'MA':PROJECT/'迭代/MacroMind V0.3.1-MA.md',
 'MA1':PROJECT/'迭代/MacroMind V0.3.1-MA.1 Minor Patch.md',
 'EX03':PROJECT/'prompt/V03.MD',
 'EX031':PROJECT/'prompt/V0.3.1.md',
 'HORMUZ':PROJECT/'prompt/V0.3追加.md',
 'G3SC':ROOT/'golden_sample_003/scenario_tree.json',
 'G3SV':ROOT/'golden_sample_003/source_versions.json',
 'G4LOG':ROOT/'golden_sample_004/finalization/gs004_finalization_log.json',
 'G4VAL':ROOT/'golden_sample_004/finalization/validation_after_finalization.json',
 'G4DIFF':ROOT/'golden_sample_004/finalization/gs004_finalization_diff.md',
 'G4MIG':ROOT/'golden_sample_004/gs004_ma1_migration_report.md',
 'G5SUP':ROOT/'golden_sample_005/golden_sample_005_ma1_supplement.md',
 'G5DIFF':ROOT/'golden_sample_005/migration/ma1/diff_summary.md',
 'G5FIN':ROOT/'golden_sample_005/finalization/finalization_log.json',
 'G5OLDVAL':ROOT/'golden_sample_005/finalization/validation_after_finalization.json',
 'G5LOG':ROOT/'golden_sample_005/finalization/hotfix_1_1/hotfix_log.json',
 'G5VAL':ROOT/'golden_sample_005/finalization/hotfix_1_1/validation_after_hotfix_1_1.json',
 'G5HOTDIFF':ROOT/'golden_sample_005/finalization/hotfix_1_1/hotfix_diff.md',
 'VAL4':ROOT/'validate_gs004_ma1.py',
 'VAL5':ROOT/'migrate_gs005_ma1.py',
 'MIG4':ROOT/'migrate_gs004_ma1.py',
 'CONTRACT5':ROOT/'golden_sample_005/migration/ma1/schema_contract.json',
})
for n in range(2,6): paths[f'REPORT{n}']=ROOT/f'golden_sample_00{n}'/f'golden_sample_00{n}_report.md'
before = {k:sha(p) for k,p in paths.items()}
data = {k:read(p) for k,p in paths.items() if p.suffix=='.json'}
evidence=[]
def ref(eid, key, pointer, note):
    p=paths[key]
    if pointer.startswith('/'):
        node=data[key]
        for token in pointer[1:].split('/'):
            token=token.replace('~1','/').replace('~0','~')
            node=node[int(token)] if isinstance(node,list) else node[token]
        selector={'json_pointer':pointer}
    else:
        assert pointer in p.read_text(encoding='utf-8-sig'), (eid,pointer)
        selector={'text_anchor':pointer}
    evidence.append(dict(evidence_id=eid,source=key,path=p.as_posix(),**selector,note=note))
    return eid
ref('E01','GS001','## 结论','摘要级证据；旧版直接冲突判断须结合 V0.2 后续时间/Population 裁决。')
ref('E02','V02','ExpectationSnapshot','共识快照、Population/量词/模态与时间范围；不新增核心类型。')
ref('E03','GS002','/18_schema_ontology_extraction_issues_found/7','SC08 是 V0.2 当时的 StructuralProcess 缺口，V0.3 已补；未实例化。')
ref('E04','GS002','/16_candidate_heuristics','HC01/HC02 为候选方法，不是已验证技能；GS002 cutoff 为 9 月 21 日。')
ref('E05','GS002','/07_actors_events_indicators_observations_policies','流量/存量、政策与事件；EV03 已宣布、未来生效。')
ref('E06','GS002','/11_arguments','AR04/06/08/09/11/12：分类、数量、成本、结果跨越和模型桥接。')
ref('E07','GS002','/conflict_checks','CF01–04 不能由表面不一致直接创建 CONTRADICTS 或核心 Contradiction。')
ref('E08','GS003','/19_FORECASTS','46 个旧版 Forecast；FC-C026 双分支未选择，是收紧准入规则的复核候选。')
ref('E09','G3SC','/creator_branches','场景树保留条件结构，但复用旧 Forecast 对象，不等于已通过新门槛。')
ref('E10','G3SV','/0','LV01 等有条目时间与抓取时间，历史快照缺失。')
ref('E11','GS003','/auxiliary/post_cutoff_quarantine','LV06–09 超 cutoff，LV10 时间未知；后期 EIA 等隔离。')
ref('E12','GS003','/09_EVENTS','EV06–08 市场基础设施通知适合 Event subtype；不证明结构过程。')
ref('E13','GS003','/23_SCHEMA_ONTOLOGY_EXTRACTION_ISSUES_FOUND/2','IS03 区分消费库存、产地库存、剩余库容。')
ref('E14','GS003','/08_ACTORS','国家/机构作为行动主体；地理空间不可仅凭同名归为 Actor。')
ref('E15','GS004','/auxiliary/method_recurrence','B 已隔离未来 GS002；A uncertain；C partial。')
ref('E16','GS004','/18_ARGUMENTS','AR05 模型桥接与主播边分开；DA01 为模型诊断；不以补链冒充方法。')
ref('E17','GS004','/26_ANALYST_METHOD_SIGNALS','8 个信号，失败行为与评价观察者分离；没有升级 Heuristic。')
ref('E18','GS004','/19_MECHANISMS','共享 ME01–03 attribution unknown，不反推作者。')
ref('E19','GS004','/20_MECHANISM_USAGE','实际使用记录与共享机制分离，使用归因不等于机制所有权。')
ref('E20','GS004','/13_INDICATORS_OBSERVATIONS','OB20 原话 3 % 保留、comparison unknown，不补成百分点。')
ref('E21','G4LOG','/human_decisions','6 项验收裁决及其来源；不是所有知识已核验。')
ref('E22','G4VAL','/scope','最终本地校验 ERROR 0 / WARNING 80 / PASS 3388。')
ref('E23','GS005','/08_CLAIMS/4','C005 Hotfix 后 unknown 字段补齐，原命题语义保留。')
ref('E24','GS005','/21_SCENARIOS/0','SC01 不准入原因 condition_not_endorsed_no_branch_selection；不是单凭低 resolvability。')
ref('E25','GS005','/auxiliary/technical_to_industry_audit','技术事件到经济复用/产业变化需要独立桥接和跨期证据。')
ref('E26','GS005','/18_ARGUMENTS','AR04 回收不等于成本下降；DA01 模型诊断不得当主播推理。')
ref('E27','GS005','/13_INDICATORS_OBSERVATIONS','目标/实际、估值/价格、数量/容量、降低到/降低了应区别。')
ref('E28','GS005','/26_ANALYST_METHOD_SIGNALS/method_recurrence/2','MR03 prior_ref=GS002/HC02，但 evaluation_time 在事后且 historical_evidence_use=false。')
ref('E29','GS005','/09_CLAIM_OCCURRENCES','OC130 对齐风险待复核，不能由存在指针推出引用有效。')
ref('E30','G5LOG','/validation','Hotfix 1.1 最终 ERROR 0 / WARNING 69 / PASS 1805；旧失败仍留历史。')
ref('E31','G5VAL','/scope','本地迁移契约，不是事实或冻结认证。')
ref('E32','EX03','# 21. StructuralProcess','跨时间现实结构变化；V0.3 明确核心类型。')
ref('E33','EX03','# 47. Contradiction','持续多目标/约束冲突、多个 Event 和 Thesis；不同于命题冲突边。')
ref('E34','EX031','# 23. Forecast Ledger准入','无条件判断、分支选择或可判定条件预测；单纯可能性不准入。')
ref('E35','MA1','# 0. Patch定位','MA.1 保持 14 核心；扩展方法匹配、观察者、comparison 与 role。')
ref('E36','VAL4',"'V-MA111'",'GS004 有样本特定未来 prior 拦截；需要推广为时间驱动通用规则。')
ref('E37','VAL5','def validate','GS005 本地规则与 GS004 并非同一覆盖；0 ERROR 不证明所有跨样本规则通过。')
ref('E38','GS004','/finalization','最终 completed/validation_passed 与人工裁决来源完整留存。')
ref('E39','GS005','/finalization_hotfix_1_1','最终状态优先于历史 finalization.completed=false。')
ref('E40','GS003','/21_CANDIDATE_HEURISTICS','HC01/HC02 有规则、限度及反例；候选而非技能。')
ref('E41','GS002','/09_veracity_assessments','引述吻合不等于测量和因果命题已验证。')
ref('E42','GS004','/16_VERACITY_ASSESSMENTS','推导错误/源文件披露范围不应传播为现实真假。')
ref('E43','GS005','/auxiliary/forecast_exclusions','C005 条件未背书；回顾性自称及工程能力不回填历史 Forecast。')

debt_rows=[
 ('D01','D1 Schema','整理唯一版本化语义合同与跨版映射；当前定义分散在 V0.3/MA/MA.1 及样本 Prompt，未找到独立 V0.3.1 Patch 文件。',list(paths)[:5],'high','pre_phase1',['E32','E34','E35']),
 ('D02','D1 Schema','GS001–003 未补齐 MA.1 字段，保留旧值/null/unknown；迁移须另立任务、不得把缺字段当核心失败。',['GS001','GS002','GS003'],'medium','codex_phase1',['E01','E03','E08']),
 ('D03','D2 Validator','建立通用 Scenario/Forecast admission 检查；复核 GS003 FC-C026 等旧 conditional_forecast，不把 46 条全部当新规合格预测。',['GS003','GS004','GS005'],'high','codex_phase1',['E08','E09','E24','E34']),
 ('D04','D6 Temporal Metadata','将 recurrence comparison_time、样本内容时间、历史 prior eligibility 分开；GS005 MR03 较晚 GS002 只属事后比较，GS004 隔离规则需通用化。',['GS002','GS003','GS004','GS005'],'high','codex_phase1',['E15','E28','E36','E37']),
 ('D05','D6 Temporal Metadata','GS001 cutoff 未知，其他样本 recorded_at 未知；发布代理、视频偏移不能变成真实 asserted_at。',list(paths)[:5],'medium','batch_pilot',['E01','E05','E10','E23']),
 ('D06','D6 Temporal Metadata','抓取时间晚于发布，滚动源缺历史快照；保留版本突变风险和未知条目隔离。',['GS002','GS003','GS004','GS005'],'high','batch_pilot',['E10','E11','E15']),
 ('D07','D3 Registry','正式全库对象/关系/枚举及 identity registry 不完整；同源转载须按命题及片段 origin family 去重。',['GS002','GS003','GS004','GS005'],'medium','codex_phase1',['E05','E11','E18','E35']),
 ('D08','D4 Data Quality','数字、ASR、来源元数据与 GS005 OC130 对齐风险待人工核验；候选文本规范化不等于听音确认。',['GS002','GS003','GS004','GS005'],'high','batch_pilot',['E20','E27','E29']),
 ('D09','D5 Review Queue','知识 Review 继续独立：GS002 41、GS003 36，GS004 最终 78、GS005 最终 68；这些数量不是核心阻塞数。',['GS002','GS003','GS004','GS005'],'high','batch_pilot',['E21','E22','E30']),
 ('D10','D7 Analyst Modeling','GS004 共享机制 attribution unknown 是已接受的未知；使用者/作者/观测者身份不相互填充。',['GS004','GS005'],'medium','analyst_mining',['E18','E19','E26']),
 ('D11','D2 Validator','Argument 图须验证 role/stage 转换、单位/分母、图距离、shortcut 和 fragile-step 定位；链存在不等于推理成立。',['GS002','GS003','GS004','GS005'],'high','codex_phase1',['E06','E16','E20','E26','E27']),
 ('D12','D8 Evaluation','StructuralProcess 缺正式实例正例：GS002 提出过程但未实例化，GS003–005 均 0。另建跨期充分证据的正例和生命周期测试。',['GS002','GS003','GS004','GS005'],'high','batch_pilot',['E03','E32','E25']),
 ('D13','D8 Evaluation','Contradiction 在 GS002–005 均 0，GS001 摘要无实例证明；须补长期互动正例与命题冲突负例，不能声称正例覆盖。',list(paths)[:5],'high','batch_pilot',['E07','E33']),
 ('D14','D8 Evaluation','Heuristic 只有摘要或候选；缺跨样本已验证规则、失败率与独立反例集，不足以生成 Skill。',list(paths)[:5],'high','pre_skill',['E01','E04','E17','E40']),
 ('D15','D8 Evaluation','Forecast resolution criteria 的 creator/model/human/scoring 时间分开；缺后验结算并非 Ontology 问题，不允许事后改口径评分。',['GS002','GS003','GS004','GS005'],'medium','batch_pilot',['E08','E24','E43']),
 ('D16','D1 Schema','comparison_basis、semantic_role、recognition_stage 和 storage_role 按来源保留 unknown；单位、目标/实绩、订单/收入/现金不可自动转换。',['GS002','GS003','GS004','GS005'],'high','codex_phase1',['E13','E20','E23','E27']),
 ('D17','D7 Analyst Modeling','Failure origin 与 observed reasoner/annotation observer 分开；partial/analogous/uncertain 不得升级完整复现或稳定方法。',['GS003','GS004','GS005'],'high','analyst_mining',['E15','E17','E28','E35']),
 ('D18','D9 Runtime / Tooling','建立只读导入、版本选择、审计留痕和回归 runner；本地 0 ERROR 不能作为生产认证，GS005 历史失败不能覆盖 Hotfix 成功。',['GS004','GS005'],'high','codex_phase1',['E22','E30','E31','E38','E39']),
 ('D19','D8 Evaluation','GS001 只有摘要，覆盖声明需保留 summary_only，不能重建不存在的对象 ID/时间/图；有原始包后另行补审。',['GS001'],'medium','later',['E01','E02']),
 ('D20','D2 Validator','Actor/Geography/narrative role、Assessment target 与事实真值不传播需批量负例检查，防止词面同名和 verified 标志误读。',['GS001','GS002','GS003','GS004','GS005'],'medium','codex_phase1',['E07','E14','E41','E42']),
]
debts=[dict(debt_id=i,category=c,description=t,affected_goldens=gs,severity=s,blocks_core_freeze=False,recommended_phase=p,evidence_refs=e,problem_type='DATA_REVIEW' if i=='D08' else 'NON_BLOCKING_DEBT') for i,c,t,gs,s,p,e in debt_rows]

object_rows=[
 ('Source','信息载体及其来源身份；真实性评价与载体存在分离。','GS001 GS002 GS003 GS004 GS005','D06 D07 D19','E01 E10 E11','跨版本/转载不是新 Core。'),
 ('Claim','带说话者、时间、Population、量词、模态与来源的可断言命题。','GS001 GS002 GS003 GS004 GS005','D02 D05 D08 D20','E02 E23 E41','原话、事件与真实性不合并。'),
 ('Event','具有相对明确时间边界的状态变化；宣布/生效/发生分别记录。','GS001 GS002 GS003 GS004 GS005','D05 D06','E05 E12 E25','通知是已宣布事件，不推出所宣称结果已实现。'),
 ('StructuralProcess','跨一段时间持续发生、由多时期观测/时间序列/多事件政策支持的现实结构变化。','GS002 GS003 GS004 GS005','D12','E03 E25 E32','需求正例与拒绝升格负例已覆盖；正式正例尚无。'),
 ('Actor','具有行动或决策归属的主体；同名地理位置和叙事角色不是主体身份。','GS002 GS003 GS004 GS005','D07 D20','E05 E14','国家作为主体与作为地理范围须分开引用。'),
 ('Indicator','可重复使用的指标定义及口径；某时值由辅助 Observation 承载。','GS002 GS003 GS004 GS005','D11 D16','E05 E13 E20 E27','flow/stock、价格/量、目标/实际为定义或观测字段。'),
 ('Policy','持续有效的制度/政策安排；宣布、调整、执行是相关 Event。','GS002 GS003 GS004 GS005','D05 D07','E05 E12','PL01 与 EV05 分开，未来生效不等于未来信息。'),
 ('Mechanism','在适用条件下可跨案例复用的因果机制；使用实例不等于共享机制作者。','GS001 GS002 GS003 GS004 GS005','D07 D10','E06 E18 E19','candidate 状态不妨碍类型存在。'),
 ('Argument','连接前提、推理边、中间与最终结论的论证；保存表达层、reasoner、距离及脆弱环节。','GS001 GS002 GS003 GS004 GS005','D11 D17','E06 E16 E26','model bridge 与 creator shortcut 不同；无需拆分 Core。'),
 ('Thesis','对事件、过程、指标组合的持久解释或结构判断，可由后续证据支持/反驳。','GS001 GS002 GS003 GS004 GS005','D12 D15','E01 E03 E25','现实过程本身不重复包装成 Thesis。'),
 ('Forecast','主体对未来结果承担的判断：Claim + cutoff + window + modality + resolution criteria，受准入门槛约束。','GS001 GS002 GS003 GS004 GS005','D03 D15','E08 E24 E34 E43','条件推演与押注区别；低可判定性不自动排除明确判断。'),
 ('Contradiction','跨时持续、多个目标/约束冲突并由多个 Event/Thesis 与互动支持的结构性张力。','GS002 GS003 GS004 GS005','D13 D20','E07 E33','仅负例/拒绝自动生成覆盖；不能等同 claim_relation=CONTRADICTS。'),
 ('Assessment','特定观察者按标准、时点和信息集对目标作出的评价。','GS001 GS002 GS003 GS004 GS005','D08 D20','E01 E41 E42','评价不是现实本身；source fidelity 不向因果真实性传播。'),
 ('Heuristic','潜在跨事件复用的分析动作或检查规则，具有适用范围、限制和失败条件；可处于候选状态。','GS001 GS002 GS003 GS004 GS005','D14 D17','E01 E04 E17 E40','MethodSignal 是局部观察，SkillRule 是经验证可执行产物；没有降级 Core 的结构证据。'),
]
objects=[dict(object_name=n,core_definition=t,definition_stability='stable',tested_by_goldens=g.split(),boundary_conflicts=[note],known_debts=d.split(),recommended_freeze_status='freeze_with_note',evidence_refs=e.split(),coverage_note=note) for n,t,g,d,e,note in object_rows]
objects[3]['coverage_level']='conceptual_positive_and_negative_admission_only_no_formal_positive_instance'
objects[11]['coverage_level']='negative_admission_only_no_formal_positive_instance'
objects[13]['coverage_level']='candidate_only_no_validated_skill'
for o in objects:
    o['boundary_conflicts']=[dict(type='resolved_or_nonblocking',description=o['boundary_conflicts'][0])]

boundary_rows=[
 ('Source ↔ Claim','needs_validator','GS001 GS002 GS003 GS004 GS005','转载计独立支持；引述正确被当事实正确。','Source→片段/版本→Claim；独立 Assessment；按命题 origin 去重。','validator','E02 E10 E41','D07 D20'),
 ('Claim ↔ Event','needs_validator','GS002 GS003 GS004 GS005','宣称封锁、拟开放或一次回收被当全部结果发生。','Claim 保存说法；Event 的状态和发生证据单列。','validator','E05 E12 E25','D20'),
 ('Event ↔ StructuralProcess','stable','GS002 GS003 GS004 GS005','一场冲突/一次回收被扩成格局或产业转型。','跨期证据门槛；证据不足保留 Claim/Thesis。','validator','E03 E25 E32','D12'),
 ('Actor ↔ Geography','needs_validator','GS002 GS003','国家主体、海峡地域、卖铲人角色可能词面混同。','主体身份与 location/role 关系分开。','registry','E05 E14','D07 D20'),
 ('Indicator ↔ IndicatorObservation','needs_field','GS002 GS003 GS004 GS005','比值当价格；库容当库存；目标当实绩。','指标定义稳定，观测带 value_kind、period、comparison、role/stage。','field','E05 E13 E20 E27','D16'),
 ('Policy ↔ Policy Event','stable','GS002 GS003 GS004 GS005','已宣布但未来生效误判成未来污染或已经执行。','政策持久状态与宣布/实施事件分别记录并关联。','field','E05 E12','D05'),
 ('Mechanism ↔ Argument','stable','GS002 GS004 GS005','一次故事当机制；共享机制变成主播完整推理。','机制保留可复用因果结构，Argument 保存本次前提和实际推理边。','relation','E06 E16 E18 E26','D10 D11'),
 ('Thesis ↔ Forecast','needs_validator','GS001 GS003 GS004 GS005','长期产业解释直接进入单一预测账本。','持久结构解释与带时间/条件的未来判断分别引用。','validator','E01 E08 E25 E34','D03 D15'),
 ('Scenario ↔ Forecast','needs_validator','GS003 GS004 GS005','GS003 FC-C026 枚举两种可能；GS005 C005 条件未背书。','Scenario 保留分支；Forecast 必须满足主体判断准入；不以 resolvability 单独替代准入。','validator','E08 E09 E24 E34','D03'),
 ('Assessment ↔ Claim','stable','GS001 GS002 GS004 GS005','某推导无效被误作原子事实为假。','Assessment 指向目标/标准/观察者；不改写原 Claim。','field','E01 E41 E42','D20'),
 ('Assessment ↔ Reality','needs_validator','GS002 GS003 GS004 GS005','官方说过、模型判错、文件披露被推成现实全部成立。','评价作用范围和真值不传播原则。','validator','E10 E41 E42','D20'),
 ('Heuristic ↔ AnalystMethodSignal','stable','GS002 GS003 GS004 GS005','部分相似或事后观察当完整稳定规则。','局部行为观察→候选模式→规则，保留失败与匹配范围。','auxiliary_object','E04 E15 E17 E40','D14 D17'),
 ('Heuristic ↔ Skill Rule','stable','GS001 GS002 GS003 GS004 GS005','候选规则直接可执行化。','Core Heuristic 可候选；Skill 需跨案稳定性、反例与验证。','review','E01 E04 E40','D14'),
 ('Mechanism ↔ MechanismUsage','stable','GS004 GS005','使用者当机制创建者或 unknown 被补成 analyst。','共享机制和使用实例分别 attribution。','auxiliary_object','E18 E19 E26','D10'),
 ('Event ↔ Market Infrastructure Event subtype','stable','GS003','Platts 报价通知因重要性被升级新核心对象或过程。','以 Event subtype 和 registry 扩展表示通知动作。','registry','E12','D07'),
]
boundaries=[dict(boundary_id=f'B{i:02}',boundary=n,status=s,evidence_goldens=g.split(),known_failure_cases=[f],resolution=r,resolution_layer=l,evidence_refs=e.split(),debt_refs=d.split(),core_change_required=False) for i,(n,s,g,f,r,l,e,d) in enumerate(boundary_rows,1)]

cards=[]
card_specs=[
 ('GS001','利率决策、市场预期与宏观叙事','partial','Source Claim Event Assessment Argument Mechanism Thesis Forecast Heuristic','B01 B08 B10 B11 B13','只有摘要；旧 source_conflict 后经时间范围裁决收窄；Expectation/Population 不需新 Core。','D05 D19 D20','E01 E02','field auxiliary_object review'),
 ('GS002','中国金融结构、债务处置与资本配置','structured_legacy','Source Claim Event Actor Indicator Policy Assessment Argument Mechanism Thesis Forecast Heuristic','B01 B03 B05 B06 B07 B12','SC08 曾是 V0.2 类型缺口，已由当前 StructuralProcess 解决；数量到价格、分类到化债结果仍须证据。','D02 D08 D11 D12 D13','E03 E04 E05 E06 E07','field validator review'),
 ('GS003','霍尔木兹冲突、能源库存与市场基础设施','structured_legacy','Source Claim Event Actor Indicator Policy Assessment Argument Mechanism Thesis Forecast Heuristic','B02 B03 B04 B05 B08 B09 B15','条件分支可表达但旧账本准入需复核；滚动源历史版本不全，库存语义需细分。','D03 D06 D12 D13 D16','E08 E09 E10 E11 E12 E13 E40','field auxiliary_object validator review'),
 ('GS004','AI 云资本开支、收入与折旧、叙事分析','accepted_local_ma1_knowledge_review_pending','Source Claim Event Actor Indicator Policy Assessment Argument Mechanism Thesis Forecast','B03 B05 B07 B09 B10 B12 B14','未来 GS002 prior 已隔离；机制 attribution 已接受 unknown；量纲和角色跨越保留审查。','D10 D11 D16 D17 D18','E15 E16 E17 E18 E19 E20 E21 E22','field auxiliary_object registry validator review'),
 ('GS005','火箭回收、经济复用与产业商业化','accepted_hotfix_1_1_knowledge_review_pending','Source Claim Event Actor Indicator Policy Assessment Argument Mechanism Thesis Forecast','B02 B03 B05 B07 B09 B12 B14','C005 Scenario-only 已裁决；技术到产业的补链归模型；未来样本事后比较与历史 prior 的消费者语义需统一。','D03 D04 D08 D11 D16 D18','E23 E24 E25 E26 E27 E28 E29 E30','field auxiliary_object validator review'),
]
for gid,domain,complete,exercised,bs,problem,ds,es,fix in card_specs:
    cards.append(dict(golden_id=gid,domain=domain,evidence_completeness=complete,core_objects_exercised=exercised.split(),core_boundaries_tested=bs.split(),new_problem_discovered=problem,problem_type='NON_BLOCKING_DEBT',additional_problem_types=['DATA_REVIEW'],existing_ontology_can_express='yes',required_fix_layer=fix.split(),core_change_required='no',evidence_refs=es.split(),debt_refs=ds.split(),result='PASS_WITH_LIMITATION',notes='PASS 指当前 Core 表达能力；不是全部数据正确、现代 schema 合格或生产就绪。StructuralProcess/Contradiction 的负例覆盖另列，不计正式正例。'))

counter_rows=[
 ('CE01','GS002','SC08 / TH01','旧版本无法直接建立金融结构变化对象。','曾真缺持续现实过程类型。','当前 V0.3 已有 StructuralProcess；旧 JSON 尚无实例是历史迁移/覆盖债。','NON_BLOCKING_DEBT','E03 E32','D02 D12'),
 ('CE02','GS003 GS005','FC-C026 / SC01(C005)','同是条件分支，旧 GS003 有 Forecast，GS005 仅 Scenario。','若所有分支都算承诺会系统性污染预测账本。','条件树已有辅助载体；更新准入并复核旧分类可修复，不改 Forecast 核心定义。','NON_BLOCKING_DEBT','E08 E09 E24 E34','D03'),
 ('CE03','GS004 GS005','MS02 / MR03','较晚 GS002 被放进 prior_ref，两个样本治理形态不同。','可能导致跨期方法复现证据倒灌。','GS004 已隔离；GS005 明确 evaluation_time 与 historical_evidence_use=false。尚未证明历史污染，但消费者需按时间资格区分事后比较。','NON_BLOCKING_DEBT','E15 E28 E36 E37','D04'),
 ('CE04','GS004 GS005','ME01–03 / MechanismUsage','共享机制创建者未知，实际使用者却已知。','一个对象可能同时承担共享知识和主体行为身份。','Usage 已能分离，unknown 是知识缺口，不是无法表达作者。','NON_BLOCKING_DEBT','E18 E19 E26','D10'),
 ('CE05','GS002 GS003 GS004 GS005','StructuralProcess collections / SC08','当前正式正例缺席，定义是否只在纸面成立？','可能隐藏过程粒度、起止和生命周期不稳定。','已有持续性/多时点门槛与拒绝单 Event 升格证据；无发现不可分类现实对象。正例不足限制置信度，需专项试点。','NON_BLOCKING_DEBT','E03 E25 E32','D12'),
 ('CE06','GS002 GS003 GS004 GS005','Contradiction collections / CF01–04','结构矛盾始终 0，与 CONTRADICTS 是否重叠？','名字相似可能误合并逻辑不一致和持续结构张力。','命题冲突为 Relation，结构张力有多事件/多 Thesis/持续互动要求；负例合理，正例尚待。','NON_BLOCKING_DEBT','E07 E33','D13 D20'),
 ('CE07','GS001 GS002 GS003 GS004 GS005','HC01/HC02 / MethodSignal','新增 MethodSignal 后，Heuristic 是否应降辅助层？','可能出现同一方法双重建模。','观察实例不同于可复用规则；candidate 身份不等于 validated；没有无法消除的跨样本重叠。','NON_BLOCKING_DEBT','E01 E04 E17 E40','D14 D17'),
 ('CE08','GS002 GS004 GS005','AR06 / AR01 / AR04','从数量到价格、时间比到泡沫倍数、回收到降本反复跳跃。','可能需要经济阶段/产业转型第 15 类型。','Indicator/Observation roles + Argument 边 + Thesis/Process 足以标明缺条件；错误在推理而非类型不足。','NON_BLOCKING_DEBT','E06 E16 E25 E26 E27','D11 D16'),
 ('CE09','GS003','EV06–08 / LV01–10','通知及滚动条目是否已成独立核心实体？','市场规则变化、版本溯源重要且多次出现。','通知仍有事件边界；版本与条目保留辅助身份。重要性不足以证明 Core 必要。','NON_BLOCKING_DEBT','E10 E11 E12','D06 D07'),
 ('CE10','GS004 GS005','VA-C020 / OC130','schema 合格仍可能有评价范围或证据片段错误。','Source→Claim 的语义链接可能表面完整实际失真。','指针与内容分别校验；审查对齐和 Assessment scope 即可，不更改 Source/Claim 边界。','DATA_REVIEW','E29 E42','D08 D20'),
]
counterexamples=[dict(counterexample_id=i,golden_ref=g.split(),object_ref=o,problem=p,why_it_might_be_core=w,why_existing_structure_may_still_be_enough=r,final_classification=c,evidence_refs=e.split(),debt_refs=d.split()) for i,g,o,p,w,r,c,e,d in counter_rows]

necessity=[]
for candidate,gs,representation,reason in [
 ('Scenario',['GS003','GS005'],'Claim + auxiliary Scenario + admitted Forecast','分支关系不等于预测承诺'),
 ('IndustrialTransitionStage',['GS002','GS005'],'Event + Indicator/Observation + StructuralProcess + Thesis + Argument','阶段是定义/观测/论证的属性，不是独立不可表达现实实体'),
 ('AnalystMethodSignal',['GS004','GS005'],'analyst-plane auxiliary observation + Heuristic candidate','观察方法行为不等于已抽象规则'),
 ('MarketInfrastructureEvent',['GS003'],'Event subtype + Policy relation','有时间边界的通知动作'),
]:
    necessity.append(dict(candidate=candidate,recommend_new_core_object=False,answers={
      'Q1':f'现有体系可表达：{representation}；不存在已证明的无法表达。',
      'Q2':f'可使用类型/阶段/准入字段；{reason}。复杂分支/观察记录可超出单字段但不超出辅助层。',
      'Q3':'可以使用有 ID 与 provenance 的辅助对象；未发现不足。',
      'Q4':'对象间条件/支持/使用/阶段关系可以保留，不需新 Core。',
      'Q5':'评价部分由 Assessment 表达；条件结构或现实动作不全是评价，但已有对象/辅助层可承担。',
      'Q6':f'本次相关样本：{", ".join(gs)}；'+('至少两个案例有相关概念，但不构成不能表达的重复缺口。' if len(gs)>=2 else '只有一个 Golden，尚不满足跨案必要性。'),
      'Q7':'没有证明不新增就必然产生且非核心层无法隔离的重复错误；错误准入/角色偷换/归因可由字段、关系、校验及 review 修复。'}))

gate_rows=[
 ('01','14 类足以表达所见核心对象；不把摘要/负例当正例完整覆盖。','E01 E03 E25 E32 E33','D12 D13 D19'),
 ('02','未发现必须新增第 15 类型的重复结构；四个候选通过七问后均不满足新增必要性。','E09 E12 E19 E25','D03 D07'),
 ('03','15 条边界都有现有非 Core 解法；实现校验和历史准入仍有债。','E05 E13 E16 E24 E35','D03 D11 D16 D20'),
 ('04','单事件与跨期过程规则稳定；过程正式正例不足，需试点补证。','E03 E25 E32','D12'),
 ('05','条件树、主体预测承诺、持久解释可分；GS003 旧准入不能视作全数通过。','E08 E09 E24 E34','D03 D15'),
 ('06','共享因果机制、案例论证和机制使用实例可分别表达。','E06 E16 E18 E19 E26','D10 D11'),
 ('07','来源、命题、评价作用范围与现实区分明确；需防 verified 标签传播。','E01 E41 E42','D07 D20'),
 ('08','多时间轴可表达未来生效、滚动版本与事后比较；metadata 与通用规则待补。','E05 E10 E11 E15 E28','D04 D05 D06'),
 ('09','reasoner/observer、analysis_context、expression_level 足以隔离主体行为和模型评价。','E16 E17 E18 E26','D10 D17'),
 ('10','已见 MA/MA.1 新问题均落辅助、字段、registry、validator 或 review；未见核心缺口。','E15 E19 E20 E23 E35','D11 D16 D17'),
 ('11','主动搜索到的重复问题均有非 Core 隔离方式；尚无 A1–A5 实证。','E06 E08 E15 E25 E28','D03 D04 D12 D13'),
 ('12','已有稳定语义合同可启动 Phase 1 的 schema/validator 工程；须先整理版本化规范，并非生产导入合同已实现。','E22 E30 E31 E32 E35','D01 D18'),
]
gates=[dict(gate_id='GATE-'+i,status='PASS_WITH_DEBT',evidence=e.split(),reason=r,blocking_issue=None,debt_refs=d.split()) for i,r,e,d in gate_rows]
time_axes=[
 ('knowledge_cutoff','资格边界按样本信息集保存，未知不可由编号推断。','E05 E10 E15 E28'),
 ('asserted_at','录制时间未知保持 null；publication proxy 与 media offset 单列。','E23 E05'),
 ('reference_time','命题谈论的时期/Population 与实际说话时间分开。','E02 E07'),
 ('prediction_window','可未知；不由评估时点倒填。','E08 E43'),
 ('captured_at','抓取晚不自动意味着全部内容晚；但无历史快照存在修改风险。','E10 E11'),
 ('published_at','整页发布日期不代表所有滚动条目时间。','E10 E11'),
 ('SourceVersion','保留 entry 时间、capture、cutoff eligibility、hash/未知历史修订。','E10 E11'),
 ('InformationSet','按 cutoff 与用途区分 creator reconstruction、外部核验、事后方法比较。','E15 E28'),
 ('Forecast resolution time','标准设定/批准/实际评估时间分开；未批准 model criteria 不评分。','E08 E43'),
 ('recurrence chronology','GS003→GS004→GS005→GS002；GS001 无可排序 cutoff；evaluation_time 不重写历史先后。','E15 E28 E36'),
 ('Event action times','announced/decided/scheduled/effective/occurred 不合并，EV03 是已知未来安排。','E05 E12'),
]
temporal=dict(temporal_model_status='stable',chronology=[{'golden_id':g,'knowledge_cutoff':data[g][next(iter(data[g]))]['knowledge_cutoff']} for g in ['GS003','GS004','GS005','GS002']],unplaced=['GS001'],axes=[dict(axis=a,assessment=t,evidence_refs=e.split()) for a,t,e in time_axes],debt_refs=['D04','D05','D06','D15'],historical_leakage_in_gs005_mr03='not_established_explicit_retrospective_comparison_consumer_ambiguity_remains')

summary=dict(audit_version='CORE-ONTOLOGY-V0.3-FREEZE-READINESS-1',audit_generated_at=datetime.now(timezone.utc).isoformat(),scope=[f'GS00{n}' for n in range(1,6)],core_object_count=14,decision='READY_TO_FREEZE_WITH_NONBLOCKING_DEBTS',freeze_recommendation=True,core_blockers=[],new_core_object_required=False,core_boundary_changes_required=False,nonblocking_debt_count=len(debts),critical_debt_count=0,critical_debt_count_definition='No core-blocking critical debt. Ledger severity uses low/medium/high only; high is not silently renamed critical.',high_severity_nonblocking_debt_count=sum(d['severity']=='high' for d in debts),golden_results={c['golden_id']:c['result'] for c in cards},gate_results={g['gate_id']:g['status'] for g in gates},core_objects={o['object_name']:o['recommended_freeze_status'] for o in objects},core_object_assessments=objects,gate_details=gates,temporal_audit=temporal,counterexample_candidates=counterexamples,new_core_necessity_tests=necessity,analyst_skill_status='NOT_READY',macromind_core_skill_status='NOT_READY',production_import_ready=False,formal_freeze_executed=False,next_step='Core Ontology V0.3 Freeze Commit (separate authorization/task); then versioned contract and Codex Phase 1 schema/validator/registry work.',limitations=['GS001 summary only; no invented machine-readable objects or chronology.','GS002/003 legacy extraction, not fully MA.1 migrated or knowledge validated.','StructuralProcess and Contradiction formal positive coverage absent; Heuristic validated-skill coverage absent.','Latest local validation reused with accepted-file hash binding; no migration or factual verification rerun.','Readiness is bounded by five cases, not a statistical guarantee for 30–50 or 1900 episodes.'])

def table(headers, rows):
    def cell(x):return str(x).replace('|','／').replace('\n','<br>')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(cell(x) for x in row)+' |' for row in rows])
def er(ids):return '、'.join(ids)
sections=[]
def section(title,text):sections.append('## '+str(len(sections)+1)+'. '+title+'\n\n'+text)
section('Executive Decision',f'**{summary["decision"]}**。建议进入独立的 Core Ontology V0.3 Freeze Commit；本次不执行正式冻结。\n\n审计 5/5 个 Golden、14/14 类 Core Object、15 条边界、12 个 Gate。发现 0 个满足 A1–A5 的 Core blocker，20 项非阻塞债务；无需新增 Core 或改变现有核心边界。所有样本均为 PASS_WITH_LIMITATION，表示当前核心可表达其所见问题，绝不等于知识已全部验证。\n\n关键限制：GS001 只有摘要；GS002/003 是旧版本；StructuralProcess 与 Contradiction 缺正式正例，Heuristic 缺已验证技能正例。该结论支持稳定语义合同，不证明 1900 期已无风险。')
section('What Was Audited','优先级为 accepted/finalized 对象 → 人工裁决 → 最新 validator → diff → supplement → 原报告 → 旧 Prompt。GS004 使用 `.ma1_accepted.json`；GS005 使用同名文件的 Hotfix 1.1 后内容。哈希与最终日志绑定检查见 `integrity_check.json`，输入版本见 `input_manifest.json`。\n\n'+table(['样本','主证据','时点/状态'],[(g,str(paths[g].relative_to(ROOT)),('summary only；时间未知' if g=='GS001' else data[g][next(iter(data[g]))].get('knowledge_cutoff'))) for g in summary['scope']])+'\n\n已查阅命名的四份 Patch、V03.MD、V0.3.1.md、Hormuz Addendum、本地迁移契约和 validator。指定的“Core Ontology V0.3.md”实际是本次审计指令；未发现独立命名的 V0.3.1 Patch，相关规则来源标为样本 Prompt，不冒称完整规范文件。正式全库 registry 未在所查材料中提供，GS002 HC01/HC02 与 GS003 registry_search 仅作本地候选证据。')
section('Freeze Scope','建议冻结 14 类型、核心定义和边界，以及 provenance、temporal、knowledge cutoff、reasoner/observer 原则。Source ≠ Claim ≠ Reality；评价不传播为事实；单 Event 不自动成为 Process；技术成功、设计能力、经济成功分开。\n\n冻结的是语义合同，未来普通案例只能扩展非核心层；真正结构变更应 RFC → Migration Plan → V0.4。本报告未创建 FROZEN 状态，也未修改 Ontology 或 Golden。')
section('Evidence Completeness / Limitations','GS001 的33 Claims等数字仅为摘要报告数量，不能当逐对象验证。V0.2 对 GS001 的后续 adjudication 可修正审计解释，但不能证明完整 JSON 已迁移。GS002/003 可检查机器对象和 review，但没有后来 MA.1 验收。\n\nGS004 最终本地结果 ERROR=0、WARNING=80、PASS=3388；GS005 Hotfix 后 ERROR=0、WARNING=69、PASS=1805。GS005 初次 Finalization ERROR=4 是保留历史，不是当前状态。校验范围仅为本地迁移合同，不是本次独立重新认证；本次验证了文件与最终日志哈希绑定。\n\n本次读取结构、关键对象、规则与差异，不重听音、不联网核验、不重抽取、不重跑迁移。没有将旧报告中的事实断言升级为本次现实核验。多数未知值和人工判断应留存，不以猜测填补。跨五案“未发现 Core blocker”不等于对未见案例的数学证明。')
for c in cards:
    section(c['golden_id']+' Stress Test',table(['字段','结论'],[
      ('domain',c['domain']),('evidence_completeness',c['evidence_completeness']),('core_objects_exercised',er(c['core_objects_exercised'])),('core_boundaries_tested',er(c['core_boundaries_tested'])),('new_problem_discovered',c['new_problem_discovered']),('problem_type','NON_BLOCKING_DEBT；另有 DATA_REVIEW'),('existing_ontology_can_express','yes'),('required_fix_layer',er(c['required_fix_layer'])),('core_change_required','no'),('result',c['result']),('evidence_refs',er(c['evidence_refs'])),('debt_refs',er(c['debt_refs']))])+'\n\n'+c['notes'])
section('14 Core Objects Assessment',table(['对象','核心定义','稳定性 / 建议','覆盖样本','冲突/限制','Debt / Evidence'],[(o['object_name'],o['core_definition'],'stable / freeze_with_note',er(o['tested_by_goldens']),o['coverage_note'],er(o['known_debts'])+' / '+er(o['evidence_refs'])) for o in objects])+'\n\n“稳定”评价的是定义和可表达性；所有对象均附 note，不表示全部被同强度测试。StructuralProcess 的正向需求来自 GS002 SC08，GS003–005 是拒绝不充分升格的负例；Contradiction 是负例覆盖。')
section('Core Boundary Matrix',table(['ID / 边界','状态','样本','失败候选','解法 / 层','Evidence'],[(b['boundary_id']+' '+b['boundary'],b['status'],er(b['evidence_goldens']),er(b['known_failure_cases']),b['resolution']+' / '+b['resolution_layer'],er(b['evidence_refs'])) for b in boundaries]))
section('Temporal Integrity Assessment','**temporal_model_status: stable**。真实内容顺序：GS003（2026-03-03）→ GS004（2026-08-05）→ GS005（2026-08-20）→ GS002（2026-09-21）；GS001 未知，不能补排。\n\n'+table(['时间轴','审计判定','Evidence'],[(x['axis'],x['assessment'],er(x['evidence_refs'])) for x in temporal['axes']])+'\n\nGS004 已将 GS002/HC01 从活动 prior 隔离。GS005 MR03 指向 GS002/HC02，但注明 9 月 26 日 evaluation_time、historical_evidence_use=false、stable_skill_promotion=false，因此不能指控已发生历史证据倒灌；`prior_ref` 名称仍可能误导消费者，记录 D04。GS004 的 V-MA111 为样本特定规则，尚不能替代通用 chronology resolver。unknown 时间不算已证明合格。')
section('Provenance Assessment','现有类型加辅助对象能够回答溯源问题；部分值未知是数据债，不是架构无法表示。\n\n'+table(['问题','可表达结构与本次证据','限制'],[
 ('谁说的/什么时候说','Claim.claimant/asserted_by、SourceSegment、asserted_at/proxy；E05、E23','录制时间未知不可用发布时间加偏移推算'),
 ('基于哪个来源/是否转载','Source→Version/Segment→ClaimOccurrence；origin family；E10、E11、E29','同源传播不增加独立支持；OC130 需内容对齐复核'),
 ('模型是否补推理','Argument expression_level、reasoner/context、DA01；E16、E26','模型桥接不归主播方法'),
 ('哪次迁移/谁裁决','migration/finalization metadata、prompt path/hash、decision_origin；E21、E38、E39','用户提供的外部裁决有来源记录，非独立身份鉴定'),
 ('网页是否改过','SourceVersion captured_at、历史快照/编辑未知状态；E10、E11','能表达风险，不宣称历史网页未修改')]))
section('Reasoner / Observer Separation','analyst statement 由 Claim 与源片段固定；analyst reasoning 由 explicit/strongly_implied 边承载；model reconstruction/diagnostic 由独立 reasoner_id、analysis_context、expression_level 承载；human adjudication 保存 decision_origin、来源 Prompt 哈希和 resolved_at。\n\nGS004 AR05 的模型补链不计入主播方法证据，DA01 与 creator graph 分离。Failure 分开 observed_reasoner_id 与 annotation_observer；标签属于评价者判断，failure_origin 未核时维持 unknown。ME01–03 作者未知与 MU 的使用者已知并不矛盾。字段和辅助层已能表达，归为 D10/D17，不新增“推理观察者” Core。（E16–E19、E26、E35、E38–E39）')
section('Forecast / Scenario / Thesis Boundary','**Forecast**：主体对未来结果承担的判断，以 Claim、KnowledgeCutoff、PredictionWindow、ModalStrength、ResolutionCriteria 为骨架，并保留主体、条件、原模态和来源。window/criteria 不明可降低可判定性并进入 review，不能自行造一个承诺。\n\n**Scenario**：条件—结果或分支树，允许仅讨论可能性，没有必然的概率押注或选支。**Thesis**：跨单个时点的解释/结构判断，由 Argument 和证据支持，可持续修正，不等同过程本体或预测账本项。\n\n最小判别：先问是否有主体的未来判断，再问条件被如何使用、是否选支；若只是枚举“可能 A 也可能 B”，保留场景；若解释的是持久原因/结构意义，建立 Thesis。明确但模糊时间的未来判断可保留低 resolvability，不能以不够好评分为由抹去原判断。\n\nForecast admission gate：unconditional_forecast、明确 branch_selection 或满足条件承诺与可判定要求的 resolvable_conditional_forecast。Scenario-only gate：没有主体背书/选支或仅条件推演；GS005 C005/SC01 的已验收理由正是 condition_not_endorsed_no_branch_selection。Thesis durability gate：超越单条新闻复述，包含原因/后果/结构意义之一，有来源论证链和后续支持反证接口。\n\nGS003 FC-C026 的两种未来分支及 Addendum 旧准入习惯值得重审，46 条不能整批宣称现代 admission 合格。现有 Scenario 已足以保留它们；D03 是规则对齐而不是新增核心类型。GS005 10 Forecast 与17 Scenario 提供实际区分证据。creator/model/human resolution criteria 和实际评分时间必须隔离。（E08、E09、E24、E34、E43）')
section('Event / StructuralProcess Boundary','Process 至少要求持久、跨时和多时期 Observation/时间序列/多个 Event 或 Policy 的支持；证据数量必须同时满足时间与现实变化语义，重复转载不能凑数。事件重要性、技术突破修辞、连续数天战争都不是自动升格条件。\n\nGS002 的融资结构变化给出明确正向需求，V0.3 已提供对象；旧 JSON 仅在 Thesis/议题中提出，未建正式 Process。GS003–005 的 Process 集合均为空，合理保留负例但暴露 D12。GS005 的单次回收→操作复用→经济复用→商业可行→产业转型可以通过 Event、指标/观测、Argument、Thesis 及将来证据充分的 Process 表达；当前模型补链不是已发生过程。没有发现既不能归 Event 又不能由 Process/Claim/Thesis 表达的现实对象。（E03、E25、E32）')
section('Argument / Mechanism Boundary','Argument 保存本次 premise→inference edge→intermediate conclusion→final conclusion，边标 expression level/reasoner，另保存 inferential distance、creator shortcut 和 most_fragile_step。Mechanism 是可跨案例的因果结构，MechanismUsage 是本案如何使用。\n\nGS002 数量到成本、GS004 时间比到90倍与 RPO 成本化、GS005 回收到降本，都是 Argument 可表达且可标缺陷的跨越；并非因为结论有问题就需要拆 Argument Core。GS004 AR05 显式步骤与模型补边分离，creator shortcut 保留其表达性质，不伪装完整证明。图边数与最长路径不能互代，脆弱环节必须可定位、unknown 可 review。（E06、E16、E18、E19、E26；D10/D11）')
section('Cross-Golden Counterexamples',table(['候选 / 样本 / 对象','问题与 Core 风险','现有结构为何足够','最终分类 / Debt / Evidence'],[(c['counterexample_id']+' '+er(c['golden_ref'])+' '+c['object_ref'],c['problem']+' '+c['why_it_might_be_core'],c['why_existing_structure_may_still_be_enough'],c['final_classification']+' / '+er(c['debt_refs'])+' / '+er(c['evidence_refs'])) for c in counterexamples])+'\n\n没有建议第15个 Core。为避免用“重要”替代“必要”，对 Scenario、IndustrialTransitionStage、AnalystMethodSignal、MarketInfrastructureEvent 显式作七问：\n\n'+'\n\n'.join('### '+n['candidate']+'\n\n'+'\n\n'.join(f'**{q}**：{a}' for q,a in n['answers'].items()) for n in necessity))
section('Core Blocker Register','**blockers: []**。未发现满足 A1–A5、必须改变 Core 才能解决的问题。历史 V0.2 缺 Process 已由 V0.3 解决；现代旧账本准入、事后比较消费者歧义和正例不足均可在非 Core 层处理。\n\n若试点将来产生至少两案无法通过字段/辅助/关系/校验隔离的结构反例，再提交 RFC；本次不能将未发现等同永远不会发现。')
section('Freeze Debt Ledger',table(['ID / 分类','描述','样本','类型 / 严重度','阻塞 Core','阶段 / Evidence'],[(d['debt_id']+' '+d['category'],d['description'],er(d['affected_goldens']),d['problem_type']+' / '+d['severity'],False,d['recommended_phase']+' / '+er(d['evidence_refs'])) for d in debts])+'\n\n共20项；所有 blocks_core_freeze=false。D08 属内容复核，其余是架构配套或治理债，D09 管理的 Review 本身可包含内容问题。high 表示对生产/评估的重要性，不代表 Core 阻塞。critical_debt_count=0 表示本审计没有核心关键阻塞；不把 high 改名 critical。')
section('Gate Results GATE-01–GATE-12',table(['Gate','结果','依据/理由','Evidence / Debt','blocking_issue'],[(g['gate_id'],g['status'],g['reason'],er(g['evidence'])+' / '+er(g['debt_refs']),g['blocking_issue']) for g in gates]))
section('Final Freeze Recommendation','**freeze_recommendation: true**；决策为 **READY_TO_FREEZE_WITH_NONBLOCKING_DEBTS**。建议冻结语义骨架并显式携带覆盖限制、20项债务与治理原则。没有必要等待 ASR、所有 Review、完整 registry 或生产 schema 清零。\n\n这不构成正式 Freeze Commit：formal_freeze_executed=false。9527 Analyst Skill 与 MacroMind Core Skill 均 NOT_READY；production_import_ready=false。Heuristic 保持 Core 候选规则地位，没有跨案证据要求降级，亦没有证据允许晋升为技能。')
section('What Is Explicitly NOT Frozen','不冻结 SourceVersion/SourceEntry/SourceSegment/SourceFamily/ClaimOccurrence/TranscriptCorrection/IndicatorObservation/InformationSet/ExpectationSnapshot/SourceSegmentAnnotation/Scenario/ReviewQueue/AnalystModel/AnalystMethodSignal/MechanismUsage 等辅助对象的具体 schema。\n\n不冻结 enum registry、validator 实现与数量、method/failure taxonomy、semantic_role/recognition_stage 枚举细节、Skill 格式、MCP/API、Context Manifest、数据库与 Neo4j/DuckDB 选择、runtime、UI、retrieval、模型和 Prompt。未确认内容真假不被本次冻结结论升级。')
section('Next Step','单独执行 **Core Ontology V0.3 Freeze Commit**，固定规范版本、定义/边界/原则与本审计引用；不得悄然改变语义。之后启动 Codex Phase 1：优先 D01 规范整合，再实现通用 schema/validator、时间资格、registry 与审计 runner（D03/D04/D07/D11/D16/D18/D20）。30–50期试点补 Process/Contradiction 正例和反例回归，再谈 analyst mining 与 pre-skill 验证。\n\n本次未执行上述后续动作。以下为本报告证据索引，完整路径/JSON Pointer/文件哈希另见 `evidence_catalog.json` 和 `input_manifest.json`。\n\n'+table(['Evidence','来源 / 定位','审计用途'],[(e['evidence_id'],e['source']+' '+e.get('json_pointer',e.get('text_anchor','')),e['note']) for e in evidence]))

assert len(sections)==24 and len(objects)==14 and len(gates)==12 and len(boundaries)>=15 and len(cards)==5
ids={e['evidence_id'] for e in evidence}
for group in (cards,objects,boundaries,debts,counterexamples):
    for x in group: assert set(x['evidence_refs'])<=ids
for g in gates:assert set(g['evidence'])<=ids
assert all(sha(p)==before[k] for k,p in paths.items()), 'Input changed during audit'
binding={}
for gid,lid in [('GS004','G4LOG'),('GS005','G5LOG')]:
    binding[gid]={'accepted_sha256':before[gid],'log_output_sha256':data[lid]['output_sha256'],'matches':before[gid]==data[lid]['output_sha256']}
assert all(x['matches'] for x in binding.values())
manifest=[dict(source_id=k,path=p.as_posix(),sha256=before[k],size_bytes=p.stat().st_size,scope='targeted_semantic_and_structural_audit_not_factual_reverification') for k,p in paths.items()]
dump('input_manifest.json',{'audit_version':summary['audit_version'],'inputs':manifest,'missing_or_limited':['GS001 machine-readable objects unavailable','No standalone V0.3.1 Patch found among supplied iteration files; EX031 is a sample extraction prompt','No full production registry supplied']})
dump('evidence_catalog.json',{'evidence':evidence})
dump('core_ontology_v0.3_freeze_readiness.json',summary)
dump('core_boundary_matrix.json',{'boundaries':boundaries})
dump('golden_stress_test_matrix.json',{'golden_stress_test_cards':cards})
dump('freeze_debt_ledger.json',{'debt_count':len(debts),'debts':debts})
dump('core_blocker_register.json',{'blockers':[]})
(OUT/'core_ontology_v0.3_freeze_readiness_audit.md').write_text('# Core Ontology V0.3 Freeze Readiness Audit\n\n'+'\n\n'.join(sections)+'\n',encoding='utf-8')
dump('integrity_check.json',{'passed':True,'input_files_checked':len(paths),'all_audited_inputs_unchanged':True,'accepted_log_hash_bindings':binding,'evidence_selectors_resolved':len(evidence),'golden_count':len(cards),'core_objects':len(objects),'boundary_count':len(boundaries),'gate_count':len(gates),'markdown_sections':len(sections),'debt_count':len(debts),'golden_mutation_performed':False,'migration_rerun':False,'validator_rerun':False,'production_import_ready':False,'formal_freeze_executed':False})
print(json.dumps({'decision':summary['decision'],'files_written':len(list(OUT.glob('*.json')))+1,'debts':len(debts),'evidence_refs':len(evidence),'input_integrity':'passed'},ensure_ascii=False))
