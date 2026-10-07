"""One-shot local freeze packaging, not a Phase 1 schema or Golden migration.
Candidate artifacts remain staged until all integrity gates pass. Refuses overwrite.
"""
import hashlib
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMIT = ROOT/'freeze_commit'
AUDIT = ROOT/'freeze_readiness'
FINAL = ROOT/'core_ontology/v0.3'
STAGE = COMMIT/'staging/v0.3'
PROMPT = ROOT.parent/'prompt/MacroMind Core Ontology V0.3 Freeze Commit.md'
VERSION = 'CORE-ONTOLOGY-V0.3-FREEZE-COMMIT-1'
NAMES = 'Source Claim Event StructuralProcess Actor Indicator Policy Mechanism Argument Thesis Forecast Contradiction Assessment Heuristic'.split()
LAYERS = ['field','auxiliary_object','relation','registry','validator','review']
NOW = datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def writej(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def text(path):return path.read_text(encoding='utf-8-sig')
def record(path,role,version,read_status):return dict(path=path.resolve().as_posix(),sha256=sha(path),role=role,version=version,read_status=read_status)
def snapshot(dirs,extra=()):
    files=set(extra)
    for d in dirs:files.update(p for p in d.rglob('*') if p.is_file())
    return {p.resolve().as_posix():sha(p) for p in sorted(files)}
def audit_section(n):
    found=re.search(r'^## '+str(n)+r'\. [^\n]+\n\n(.*?)(?=^## |\Z)',report,re.M|re.S)
    if not found:raise ValueError(f'Missing audit section {n}')
    return found.group(1).strip()

if FINAL.exists() or STAGE.exists() or (COMMIT/'freeze_commit_log.json').exists():
    raise SystemExit('Refusing to overwrite a frozen version or prior commit attempt.')
COMMIT.mkdir(exist_ok=True)
golden_dirs=[p for p in ROOT.glob('golden_sample_*') if p.is_dir()]
golden_before=snapshot(golden_dirs,[ROOT/'golden_report.md'])
audit_before=snapshot([AUDIT])
writej(COMMIT/'protected_input_snapshot.json',{'captured_at':NOW,'goldens':golden_before,'audit':audit_before})
prior_manifest=load(AUDIT/'input_manifest.json')
inputs=[]
for x in prior_manifest['inputs']:
    p=Path(x['path'])
    # Read historical material without running scripts or modifying historical state.
    text(p)
    if p.suffix=='.json':load(p)
    key=x['source_id']
    role='historical_spec_or_local_contract'
    version={'V02':'0.2','V03':'0.3','MA':'0.3.1-MA','MA1':'0.3.1-MA.1','EX03':'V0.3 extraction prompt','EX031':'V0.3.1-MA sample extraction prompt'}.get(key,'as_hashed')
    status='read_for_history_and_provenance_only'
    if key in NAMES:raise ValueError('Unexpected source key')
    if re.fullmatch('GS00[1-5]',key):
        role='final_golden_evidence';version={'GS001':'summary_only','GS002':'V0.2 legacy final available','GS003':'V0.3 legacy final available','GS004':'MA.1 accepted finalized','GS005':'MA.1 accepted Hotfix 1.1'}[key]
    r=record(p,role,version,status);r['source_id']=key;r['matches_audit_input_hash']=r['sha256']==x['sha256'];inputs.append(r)
for p in sorted(AUDIT.iterdir()):
    if p.is_file() and p.suffix in ['.json','.md']:
        text(p)
        inputs.append(record(p,'freeze_readiness_authority_or_support','CORE-ONTOLOGY-V0.3-FREEZE-READINESS-1','read_current_final'))
inputs.append(record(PROMPT,'explicit_user_authorized_freeze_commit_prompt',VERSION,'read_full'))
writej(COMMIT/'input_manifest.json',{'freeze_commit_version':VERSION,'created_at':NOW,'inputs':inputs,'historical_spec_note':'Standalone V0.3.1 Patch unavailable in supplied iteration files; V0.3.1.md is explicitly classified as a sample extraction prompt, never invented as a separate patch.'})

audit=load(AUDIT/'core_ontology_v0.3_freeze_readiness.json')
boundary_audit=load(AUDIT/'core_boundary_matrix.json')['boundaries']
ledger=load(AUDIT/'freeze_debt_ledger.json')
blockers=load(AUDIT/'core_blocker_register.json')
report=text(AUDIT/'core_ontology_v0.3_freeze_readiness_audit.md')
prompt=text(PROMPT)
principle_matches=list(re.finditer(r'^P(\d{2}) ([^\n]+)$',prompt,re.M))
principles=[]
for i,m in enumerate(principle_matches):
    end=principle_matches[i+1].start() if i+1<len(principle_matches) else prompt.index('\n============================================================\n11.',m.end())
    lines=prompt[m.end():end].splitlines()
    body=' '.join(l.strip() for l in lines if l.strip() and not re.fullmatch('[-=]+',l.strip()))
    principles.append(dict(principle_id='P'+m.group(1),title=m.group(2),frozen_rule=body,ontology_version='0.3',freeze_status='FROZEN',source_commit_prompt_ref={'path':PROMPT.as_posix(),'sha256':sha(PROMPT),'anchor':m.group(0)},rule_derivation='exact_prompt_text_whitespace_normalized'))
principle_map={p['principle_id']:p for p in principles}
bindings={
 'Source':['P01','P02','P13'],'Claim':['P01','P02','P12','P13','P15'],
 'Event':['P03','P07','P13'],'StructuralProcess':['P03'],
 'Actor':[],'Indicator':['P06','P12'],'Policy':['P07'],
 'Mechanism':['P08','P09'],'Argument':['P02','P08','P15','P16'],
 'Thesis':['P02','P05'],'Forecast':['P04','P05','P13'],
 'Contradiction':[],'Assessment':['P01','P02','P10','P15'],
 'Heuristic':['P11','P16']}
objects=[]
for i,o in enumerate(audit['core_object_assessments']):
    invariants=[o['core_definition']]+[principle_map[p]['frozen_rule'] for p in bindings[o['object_name']]]
    for b in boundary_audit:
        sides=b['boundary'].split(' ↔ ')
        if o['object_name'] in sides:invariants.append(b['resolution'])
    objects.append(dict(object_name=o['object_name'],ontology_version='0.3',freeze_status='FROZEN',core_definition=o['core_definition'],semantic_invariants=invariants,principle_refs=bindings[o['object_name']],known_nonblocking_debts=o['known_debts'],allowed_extension_layers=LAYERS,source_audit_refs=[{'path':(AUDIT/'core_ontology_v0.3_freeze_readiness.json').as_posix(),'json_pointer':f'/core_object_assessments/{i}','evidence_refs':o['evidence_refs']}],coverage_note=o['coverage_note']))
boundaries=[dict(boundary_id=b['boundary_id'],boundary=b['boundary'],ontology_version='0.3',freeze_status='FROZEN',frozen_semantic_rule=b['resolution'],implementation_status=b['status'],implementation_status_note='Inherited audit status, not implementation certification; even stable requires Phase 1 implementation as applicable.',resolution_layer=b['resolution_layer'],core_change_required=b['core_change_required'],debt_refs=b['debt_refs'],source_audit_refs=[{'path':(AUDIT/'core_boundary_matrix.json').as_posix(),'json_pointer':f'/boundaries/{i}','evidence_refs':b['evidence_refs']}]) for i,b in enumerate(boundary_audit)]
noncore='SourceVersion SourceEntry SourceSegment SourceFamily ClaimOccurrence TranscriptCorrection IndicatorObservation InformationSet ExpectationSnapshot SourceSegmentAnnotation Scenario ReviewQueue AnalystModel AnalystMethodSignal MechanismUsage'.split()
not_frozen=['field-level schema details','enum registries','semantic_role enum','recognition_stage enum','failure taxonomy','recurrence taxonomy','validator implementation','validator rule count','database schema','DuckDB / SQLite / Neo4j implementation','Context Manifest','retrieval strategy','Agent Runtime','Hermes integration','MCP/API','Skill format','Analyst Model format','UI','Prompt templates','Model selection']
extension_policy='普通案例只能进行保持核心定义、边界和原则不变的 V0.3-compatible evolution：字段增加、enum 扩展、辅助对象与关系增加、Validator/Registry/Review policy、Analyst layer 和 Runtime 扩展。新增辅助对象不自动获得 Core 地位。实现细节可迭代，不能以字段或枚举名义绕过冻结语义。'
change_policy='''# MacroMind Core Ontology V0.3 Change Policy

V0.3 是 FROZEN VERSIONED SEMANTIC CONTRACT。普通案例不得直接改变14个 Core 类型、核心定义、核心边界、provenance、temporal、cutoff 或 reasoner/observer 原则。

## V0.3-compatible evolution

允许字段增加、enum 扩展、Auxiliary Object/Relation 增加、Validator 规则增加、Registry 扩展、Review policy 调整、Analyst layer 与 Runtime 扩展；前提是既有核心语义不变。为实现层版本建立独立版本和变更记录，不静默编辑 Frozen 文件。

## Core Change RFC

RFC 必须给出 problem statement、affected Core Objects、affected Goldens、尽可能跨案例证据，逐项说明 field、Auxiliary Object、Relation、Validator、Review 为什么不足，给出 proposed Core change、migration impact、backward compatibility risk、new version target。

新增类型还须回答：现有14类型为何不能表达，为什么不能作为字段、辅助对象、关系或 Assessment，是否有至少两个独立 Golden，以及不新增会导致何种具体重复语义错误。重要性或实现便利不足以构成必要性。

只有通过 RFC → Review → Migration Plan → Compatibility Plan，才进入 Core Ontology V0.4；不得把普通案例困难变成 V0.3 静默重设计。

## Frozen artifact 不可原地静默修改

CORE_ONTOLOGY_V0.3_FROZEN.md、core_objects.json、core_boundaries.json、core_principles.json、freeze_manifest.json 都是不可静默编辑的历史版本。发现问题先建立独立 errata 或 RFC。

typo、broken link、metadata 等非语义修复也须 patch record，保存旧字节 hash、新 hash、原因、作者/时间、影响和 semantic_hash 检查。不覆盖或抹去历史产物；优先生成独立修订记录。semantic_hash 必须保持不变，或明确记录变化并进入相应语义变更流程。

## Hash 与审计链

SHA-256 是文件原始字节完整性校验。semantic_hash 是 semantic_contract_projection.json 的排序键、UTF-8、ensure_ascii=false、无多余空白 JSON 序列化的 SHA-256；它覆盖14定义与语义不变量、15规则、16原则、时间/溯源/归因规则、扩展范围和本政策。它不替代人的语义审查，也不是同义改写的自动等价证明。

freeze_manifest.json 记录输入与合同输出 hash，不自引用自己的 hash；freeze_commit_log.json 记录 manifest 和所有交付文件 hash，不自引用 log 的 hash。外部仓库或签名可以进一步提供防篡改锚点，本任务不创建 Git commit 或外部签名。

原审计 formal_freeze_executed=false 和20项债务必须保留。新的 Freeze Manifest 才记录正式冻结。D01 仅在独立 overlay 标为 addressed_by_freeze_commit，其他债务继续待后续阶段处理；Core 冻结不传播为 Skill 或 Production Ready。
'''

STAGE.mkdir(parents=True)
writej(STAGE/'core_objects.json',{'ontology_version':'0.3','freeze_status':'FROZEN','objects':objects})
writej(STAGE/'core_boundaries.json',{'ontology_version':'0.3','freeze_status':'FROZEN','boundaries':boundaries})
rules={
 'temporal_integrity':audit['temporal_audit']['axes'],
 'provenance_contract':audit_section(13),
 'reasoner_observer_contract':audit_section(14),
 'forecast_scenario_thesis_contract':audit_section(15),
 'event_structural_process_contract':audit_section(16),
 'argument_mechanism_contract':audit_section(17)}
writej(STAGE/'core_principles.json',{'ontology_version':'0.3','freeze_status':'FROZEN','principles':principles,'accepted_audit_rule_details':rules,'explicitly_non_core_objects':noncore,'explicitly_not_frozen':not_frozen})
(STAGE/'freeze_debt_ledger.json').write_bytes((AUDIT/'freeze_debt_ledger.json').read_bytes())
(STAGE/'CHANGE_POLICY.md').write_text(change_policy,encoding='utf-8')

def table(headers,rows):
    def c(v):return str(v).replace('|','／').replace('\n','<br>')
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(c(v) for v in row)+' |' for row in rows])
sections=[]
def sec(name,body):sections.append(f'## {len(sections)+1}. {name}\n\n{body}')
sec('Version Metadata',f'Ontology: MacroMind Core Ontology；Version: **0.3**；Freeze Commit: `{VERSION}`；Freeze timestamp: `{NOW}`。\n\n本文件是正式冻结后唯一的人类可读 Canonical Contract。Schema、Validator、Registry、Migration、Audit Pipeline、Analyst Model 和 Skill Compiler 应引用本文件及配套 JSON，不再自行拼接历史 Patch。机器可读定义与本文件来自同一审计定义，字节哈希以 `freeze_manifest.json` 为准。')
sec('Freeze Status','**FROZEN VERSIONED SEMANTIC CONTRACT**。本状态仅在同目录 freeze_manifest.json 的 formal_freeze_executed=true 且完整性检查 ERROR=0 时有效。\n\n采用 READY_TO_FREEZE_WITH_NONBLOCKING_DEBTS；Core blocker=0；没有新增、删除或改变 Core 语义。Analyst Model、9527 Analyst Skill、MacroMind Core Skill 均 NOT_READY，production_import_ready=false，Codex Phase 1=NOT_STARTED。')
sec('Scope','冻结14种核心类型、定义、15条语义边界及核心 provenance、temporal、Knowledge Cutoff/Information Set、Reasoner/Observer 原则。语义冻结不等于字段 schema、validator 或生产系统已实现。旧 Golden 的缺字段和待核验内容保留其历史状态。')
sec('14 Core Objects','、'.join(NAMES)+'。\n\n不得增加或减少；辅助对象的重要性不构成晋升 Core 的依据。')
sec('Core Object Definitions','以下14条 core_definition **逐字复制已接受审计**，未进行定义改写。\n\n'+'\n\n'.join('### '+o['object_name']+'\n\n'+o['core_definition']+'\n\n语义不变量：\n\n'+'\n'.join('- '+s for s in o['semantic_invariants'])+'\n\n保留债务：'+', '.join(o['known_nonblocking_debts'])+'。覆盖说明：'+o['coverage_note'] for o in objects))
sec('Core Semantic Boundaries','以下冻结的是语义规则；implementation_status 原样承接审计，needs_validator/needs_field 不表示语义尚未冻结，stable 也不声明生产实现已完成。\n\n'+table(['Boundary','冻结规则','实现状态 / 层','Debt'],[(b['boundary_id']+' '+b['boundary'],b['frozen_semantic_rule'],b['implementation_status']+' / '+b['resolution_layer'],', '.join(b['debt_refs'])) for b in boundaries])+'\n\n### Forecast / Scenario / Thesis 准入与区分\n\n'+rules['forecast_scenario_thesis_contract']+'\n\n### Event / StructuralProcess 证据门槛\n\n'+rules['event_structural_process_contract']+'\n\n### Argument / Mechanism\n\n'+rules['argument_mechanism_contract'])
sec('Core Cross-Object Principles','以下 P01–P16 来自本次授权 Prompt，仅折叠换行，不改动规则用词。\n\n'+'\n\n'.join('### '+p['principle_id']+' '+p['title']+'\n\n'+p['frozen_rule'] for p in principles)+'\n\nHeuristic 可处于 candidate；生命周期描述不把已有候选伪装为经过所有验证的规则。技术成功 ≠ 经济成功；Recovery ≠ Cost Decline；Order ≠ Revenue ≠ Cash Receipt；Design Target ≠ Observed Performance。这些区分沿用审计，不能用模型补链填成已证实事实。')
sec('Temporal Integrity',table(['轴','冻结原则','Evidence'],[(x['axis'],x['assessment'],', '.join(x['evidence_refs'])) for x in rules['temporal_integrity']])+'\n\n样本 chronology 和当前 metadata 缺口属于证据/债务，不把它们硬编码为通用 validator 实现。公开时间、抓取时间、事件生效时间和预测结算时间不能互代。')
sec('Provenance',rules['provenance_contract']+'\n\n原始来源、版本、片段、命题、模型推理、迁移与裁决来源必须可追溯；未知的历史网页版本不能冒充已存档版本。证据索引 E01–E43 解析至 freeze_readiness/evidence_catalog.json，其文件 hash 记录在本次输入清单中。')
sec('Knowledge Cutoff / Information Set','冻结 P13/P14：信息资格必须按真实 content chronology、来源版本与用途区分。历史重建、外部核验、事后方法比较使用各自 Information Set；不能用事后 evaluation_time 把晚出现的样本变为历史 prior。GS 编号不是时间顺序。未来生效但 cutoff 前已宣布的决定，与 cutoff 后新信息不同。unknown 时间不自动获得资格；预测结算标准的 creator/model/human 来源和评分许可分开。')
sec('Reasoner / Observer Attribution',rules['reasoner_observer_contract'])
sec('Reality / Claim / Assessment Separation','Source ≠ Claim ≠ Reality；准确引述不等于命题已核实。Assessment 保存目标、标准、时点、信息集与观察者；“论证不足”不是“原子事实为假”。前提的数据可信度不自动传播到因果、解释、结论或 Thesis。源文件披露范围、模型诊断和现实状态分别保留。现实不是此次新增的第15种对象。')
sec('Extension Policy',extension_policy)
sec('Explicitly Non-Core Objects',', '.join(noncore)+'。\n\n以上可属于 Auxiliary、Governance、Analyst、Temporal、Evidence 等层，具体格式与实现继续演化。它们不替代 Heuristic 等 Core；MechanismUsage 的使用归因不等于共享 Mechanism 的作者。')
sec('Explicitly Not Frozen','\n'.join('- '+x for x in not_frozen)+'\n\n上述内容允许在 Codex Phase 1、Batch Pilot、Analyst Mining 继续迭代，必须遵守已冻结核心语义。')
sec('Freeze Debt Reference','`freeze_debt_ledger.json` 是审计20项历史债务的逐字节副本。原 nonblocking_debt_count=20 与 D01 记录永远保留；`freeze_debt_status_overlay.json` 是本次新增覆盖层，仅当合同与 hash 校验成功才将 D01 标为 addressed_by_freeze_commit。其余19项不宣称解决。\n\n保留 GS001 summary only、StructuralProcess/Contradiction 正式正例缺失、Heuristic validated Skill 缺失等限制。它们不是通过冻结消失，也不伪造正例。')
sec('Change Policy Reference','`CHANGE_POLICY.md` 是本版本的变更治理政策：普通兼容扩展与 Core Change RFC 分开；Core 改变须 RFC → Review → Migration Plan → Compatibility Plan → V0.4。Frozen artifact 不得静默编辑；错误用独立 errata/RFC，非语义修正也须 patch record、旧新 hash 和 semantic_hash 检查。\n\n审计中 formal_freeze_executed=false 是历史事实，不回写。正式 true 状态仅由新的 manifest 建立。')
history_rows=[]
for k,label in [('V02','Expectation/Population 与评价分离历史'),('V03','StructuralProcess 与时间/来源/推理边界'),('EX03','V0.3 抽取规范中详细定义'),('EX031','样本 Prompt 的 Forecast 准入；不是独立 Patch'),('MA','Analyst/Shared Knowledge、Reasoner、MechanismUsage'),('MA1','匹配精度、失败观察者、comparison、semantic role')]:
    r=next(x for x in inputs if x.get('source_id')==k);history_rows.append((k,r['path'],label))
sec('Freeze Evidence','权威顺序：最终 Freeze Readiness Audit → Final Accepted Golden → Final Human Adjudication → 最新 Validator/Finalization Log → MA.1 → MA → V0.3.1 → V0.3 → 旧 Prompt/Draft。历史文件只用于溯源，不覆盖最终定义。\n\n'+table(['源','文件','本次整合用途'],history_rows)+'\n\n最终审计：14对象、15边界、20非阻塞债务、0 Core blocker。GS001 是摘要；GS002/003 保留旧最终可用文件；GS004 是 Finalized accepted；GS005 是 Hotfix 1.1 后 accepted，不取代为旧失败 Finalization。\n\n具体输入路径、版本、read_status 和 SHA-256 见 ../../freeze_commit/input_manifest.json；所有正式输出哈希见 freeze_manifest.json，提交记录见 ../../freeze_commit/freeze_commit_log.json。源到 Canonical 的映射见 source_mapping.json。冻结不修改任何 Golden、旧 Patch 或审计产物。')
contract='# MacroMind Core Ontology V0.3 — FROZEN\n\n'+'\n\n'.join(sections)+'\n'
(STAGE/'CORE_ONTOLOGY_V0.3_FROZEN.md').write_text(contract,encoding='utf-8')
projection={'version':'0.3','objects':[{'object_name':o['object_name'],'core_definition':o['core_definition'],'semantic_invariants':o['semantic_invariants']} for o in objects],'boundaries':[{'boundary_id':b['boundary_id'],'boundary':b['boundary'],'frozen_semantic_rule':b['frozen_semantic_rule']} for b in boundaries],'principles':[{'principle_id':p['principle_id'],'title':p['title'],'frozen_rule':p['frozen_rule']} for p in principles],'accepted_audit_rule_details':rules,'extension_policy':extension_policy,'noncore':noncore,'not_frozen':not_frozen,'change_policy':change_policy,'canonical_contract_body_excluding_metadata_and_evidence':sections[2:17]}
semantic_hash=hashlib.sha256(json.dumps(projection,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
writej(STAGE/'semantic_contract_projection.json',projection)
writej(STAGE/'source_mapping.json',{'definition_policy':'Exact copy from authoritative audit, not re-derived from historical patches.','objects':[{'object_name':o['object_name'],'target':'core_objects.json#/objects/'+str(i),'source':o['source_audit_refs'][0]} for i,o in enumerate(objects)],'boundaries':[{'boundary_id':b['boundary_id'],'target':'core_boundaries.json#/boundaries/'+str(i),'source':b['source_audit_refs'][0]} for i,b in enumerate(boundaries)],'principles':[{'principle_id':p['principle_id'],'source':p['source_commit_prompt_ref'],'normalization':'whitespace_only'} for p in principles],'historical_documents':history_rows,'rule_detail_source':'freeze_readiness audit sections 12–17; exact content preserved or machine-readable axes copied','missing_standalone_v031_patch':True})

manifest={'ontology_name':'MacroMind Core Ontology','version':'0.3','status':'FROZEN','freeze_commit_version':VERSION,'formal_freeze_executed':True,'freeze_timestamp':NOW,'freeze_commit':{'completed':True},'core_object_count':len(objects),'core_objects':NAMES,'core_boundary_count':len(boundaries),'core_principle_count':len(principles),'freeze_readiness_decision':audit['decision'],'freeze_readiness_audit_version':audit['audit_version'],'core_blockers':audit['core_blockers'],'new_core_object_required':False,'core_boundary_changes_required':False,'audit_nonblocking_debt_count':20,'blocking_debt_count':0,'analyst_model_status':'NOT_READY','analyst_skill_status':'NOT_READY','macromind_core_skill_status':'NOT_READY','production_import_ready':False,'codex_phase1_status':'NOT_STARTED','research_phase_core_ontology_exploration':'COMPLETE','goldens_modified':False,'semantic_changes_during_freeze_commit':False,'input_provenance':inputs,'input_manifest':record(COMMIT/'input_manifest.json','freeze_commit_input_manifest',VERSION,'generated'),'semantic_hash':semantic_hash,'semantic_hash_method':'SHA256 of semantic_contract_projection.json parsed and reserialized as UTF-8 JSON with sort_keys=True, ensure_ascii=False, separators=(comma,colon). Includes normative details and change policy; not an automatic natural-language equivalence proof.','canonical_output_hashes':[],'hash_chain_note':'Manifest omits its own hash; commit log binds final manifest and all other delivered files. No external signature or Git commit implied.'}
for p in sorted(STAGE.iterdir()):manifest['canonical_output_hashes'].append({'path':(FINAL/p.name).as_posix(),'sha256':sha(p),'role':'frozen_contract_or_support'})

# Validate actual staged files; never mutate protected input or weaken checks on failure.
actual_o=load(STAGE/'core_objects.json')['objects'];actual_b=load(STAGE/'core_boundaries.json')['boundaries'];actual_p=load(STAGE/'core_principles.json')['principles']
actual_contract=text(STAGE/'CORE_ONTOLOGY_V0.3_FROZEN.md')
golden_after=snapshot(golden_dirs,[ROOT/'golden_report.md']);audit_after=snapshot([AUDIT])
checks=[]
def check(n,ok,evidence):checks.append({'check_id':f'FZ-{n:03}','status':'PASS' if ok else 'ERROR','evidence':evidence})
names=[o['object_name'] for o in actual_o]
check(1,len(actual_o)==14,{'count':len(actual_o)})
check(2,names==NAMES,{'actual':names,'expected':NAMES})
check(3,not(set(names)-set(NAMES)),{'new':sorted(set(names)-set(NAMES))})
check(4,not(set(NAMES)-set(names)),{'removed':sorted(set(NAMES)-set(names))})
check(5,blockers=={'blockers':[]} and audit['core_blockers']==[],{'register_sha256':sha(AUDIT/'core_blocker_register.json')})
check(6,audit['decision']=='READY_TO_FREEZE_WITH_NONBLOCKING_DEBTS' and audit['freeze_recommendation'] is True and not audit['new_core_object_required'] and not audit['core_boundary_changes_required'],{'decision':audit['decision']})
check(7,len(actual_b)==15 and [b['boundary_id'] for b in actual_b]==[f'B{i:02}' for i in range(1,16)],{'boundary_count':len(actual_b)})
check(8,all(b['core_change_required'] is False for b in actual_b),{'core_change_required_values':[b['core_change_required'] for b in actual_b]})
check(9,sha(STAGE/'freeze_debt_ledger.json')==sha(AUDIT/'freeze_debt_ledger.json') and len(ledger['debts'])==20 and audit['nonblocking_debt_count']==20,{'ledger_hash':sha(STAGE/'freeze_debt_ledger.json'),'historical_count':20})
check(10,all(d['blocks_core_freeze'] is False for d in ledger['debts']),{'blocking_core_debt':sum(d['blocks_core_freeze'] for d in ledger['debts'])})
check(11,golden_before==golden_after,{'files_compared':len(golden_before),'snapshot_file':'protected_input_snapshot.json','comparison':'file inventory and raw bytes SHA256 before/after'})
check(12,golden_before==golden_after,{'reason':'All Golden files byte-identical; no extraction/migration/finalization code executed.'})
definitions_exact=[o['core_definition'] for o in actual_o]==[o['core_definition'] for o in audit['core_object_assessments']]
boundaries_exact=all(b['boundary']==a['boundary'] and b['frozen_semantic_rule']==a['resolution'] and b['implementation_status']==a['status'] and b['debt_refs']==a['debt_refs'] for b,a in zip(actual_b,boundary_audit))
check(13,definitions_exact and boundaries_exact and actual_p==principles and all(o['core_definition'] in actual_contract for o in actual_o) and all(b['frozen_semantic_rule'] in actual_contract for b in actual_b),{'definitions_exact_copy':definitions_exact,'boundary_rules_exact_copy':boundaries_exact,'principles_source':'user-authorized prompt P01–P16; whitespace-only normalization','semantic_hash':semantic_hash,'scope':'Mechanical consolidation plus reviewed semantic preservation, not automated theorem proving.'})
check(14,audit_before==audit_after and audit['formal_freeze_executed'] is False,{'audit_files_compared':len(audit_before),'historical_formal_freeze_executed':audit['formal_freeze_executed']})
check(15,len(sections)==18 and len(actual_contract)>0 and all(f'## {i}. ' in actual_contract for i in range(1,19)),{'contract':'CORE_ONTOLOGY_V0.3_FROZEN.md','section_count':len(sections)})
check(16,any(x['path'].endswith('/CORE_ONTOLOGY_V0.3_FROZEN.md') and x['sha256']==sha(STAGE/'CORE_ONTOLOGY_V0.3_FROZEN.md') for x in manifest['canonical_output_hashes']),{'contract_sha256':sha(STAGE/'CORE_ONTOLOGY_V0.3_FROZEN.md')})
check(17,all(p in principle_map for p in ['P13','P14']) and all(t in actual_contract for t in ['knowledge_cutoff','asserted_at','reference_time','prediction_window','captured_at','published_at','SourceVersion','InformationSet','Forecast resolution time','recurrence chronology']),{'principles':['P13','P14'],'axes':len(rules['temporal_integrity'])})
check(18,all(t in actual_contract for t in ['SourceVersion','ClaimOccurrence','origin family','迁移','裁决','hash']),{'section':'9. Provenance','input_records':len(inputs)})
check(19,all(p in principle_map for p in ['P15','P16']) and all(t in actual_contract for t in ['reasoner_id','analysis_context','annotation_observer']),{'principles':['P15','P16']})
check(20,'Source ≠ Claim ≠ Reality' in actual_contract and 'P01' in principle_map,{'principles':['P01','P02','P10']})
check(21,any(b['boundary_id']=='B09' and b['freeze_status']=='FROZEN' for b in actual_b) and rules['forecast_scenario_thesis_contract'] in actual_contract,{'boundary':'B09','detail':'accepted audit section 15'})
check(22,any(b['boundary_id']=='B03' and b['freeze_status']=='FROZEN' for b in actual_b) and rules['event_structural_process_contract'] in actual_contract,{'boundary':'B03'})
check(23,all(any(b['boundary_id']==x for b in actual_b) for x in ['B12','B13']) and 'P11' in principle_map and 'Heuristic' in names and 'AnalystMethodSignal' not in names,{'boundaries':['B12','B13'],'principle':'P11'})
check(24,manifest['production_import_ready'] is False,{'production_import_ready':manifest['production_import_ready']})
check(25,manifest['analyst_skill_status']=='NOT_READY',{'analyst_skill_status':manifest['analyst_skill_status']})
check(26,manifest['macromind_core_skill_status']=='NOT_READY',{'macromind_core_skill_status':manifest['macromind_core_skill_status']})
supplemental=[]
def extra(name,ok,detail):supplemental.append({'check_id':name,'status':'PASS' if ok else 'ERROR','evidence':detail})
extra('FZ-X01',all(x.get('matches_audit_input_hash',True) and sha(Path(x['path']))==x['sha256'] for x in inputs),'All supplied input hashes match audited versions and commit baseline.')
extra('FZ-X02',[p['principle_id'] for p in actual_p]==[f'P{i:02}' for i in range(1,17)],'All 16 principles present, exact prompt text with whitespace normalized.')
extra('FZ-X03',all(sha(STAGE/Path(x['path']).name)==x['sha256'] for x in manifest['canonical_output_hashes']),'Staged output SHA256 read back from disk.')
extra('FZ-X04',all(o['freeze_status']=='FROZEN' and o['allowed_extension_layers']==LAYERS and o['source_audit_refs'] for o in actual_o),'Object status, provenance and allowed extension fields complete.')
for gid,logkey in [('GS004','G4LOG'),('GS005','G5LOG')]:
    g=next(x for x in inputs if x.get('source_id')==gid);l=next(x for x in inputs if x.get('source_id')==logkey)
    extra('FZ-X05-'+gid,g['sha256']==load(Path(l['path']))['output_sha256'],'Latest accepted Golden bound to finalization/hotfix output hash.')
warnings=[{'code':'FZ-W01','debt_refs':['D19'],'message':'GS001 summary only; complete machine-readable evidence unavailable.'},{'code':'FZ-W02','debt_refs':['D12'],'message':'StructuralProcess formal positive instance missing.'},{'code':'FZ-W03','debt_refs':['D13'],'message':'Contradiction formal positive instance missing.'},{'code':'FZ-W04','debt_refs':['D14'],'message':'Heuristic validated Skill example missing; candidate is not Skill.'}]
errors=sum(x['status']=='ERROR' for x in checks+supplemental)
validation={'validator_version':'CORE-ONTOLOGY-FREEZE-INTEGRITY-1','validated_at':NOW,'phase':'staged_artifacts_before_formal_manifest_publication','scope':'Freeze packaging integrity only, not Golden factual validation or Phase 1 implementation.','ERROR':errors,'WARNING':len(warnings),'PASS':sum(x['status']=='PASS' for x in checks+supplemental),'hard_checks':checks,'supplemental_checks':supplemental,'warnings':warnings,'status':'PASS_WITH_WARNINGS' if errors==0 else 'FREEZE_COMMIT_FAILED'}
writej(COMMIT/'freeze_integrity_validation.json',validation)
if errors:
    writej(COMMIT/'freeze_commit_log.json',{'executed_at':NOW,'freeze_commit':{'completed':False},'formal_freeze_executed':False,'status':'FREEZE_COMMIT_FAILED','validation':validation,'staging_retained':True,'prompt_sha256':sha(PROMPT)})
    raise SystemExit(f'Freeze integrity failed: {errors}; staged artifacts not published.')

# Only after ERROR=0 may a new manifest declare formal freeze and D01 be addressed.
overlay={'overlay_version':VERSION,'historical_ledger_sha256':sha(STAGE/'freeze_debt_ledger.json'),'historical_audit_nonblocking_debt_count':20,'freeze_debt_status_overlay':{'D01':{'status':'addressed_by_freeze_commit','at':NOW,'scope':'Unique versioned canonical semantic contract consolidated; executable legacy data mapping remains Phase 1 work.','canonical_contract_sha256':sha(STAGE/'CORE_ONTOLOGY_V0.3_FROZEN.md'),'integrity_validation_sha256':sha(COMMIT/'freeze_integrity_validation.json')}},'other_debts':'D02–D20 retain audit status; no resolution claimed.'}
writej(STAGE/'freeze_debt_status_overlay.json',overlay)
manifest['canonical_output_hashes'].append({'path':(FINAL/'freeze_debt_status_overlay.json').as_posix(),'sha256':sha(STAGE/'freeze_debt_status_overlay.json'),'role':'post_validation_debt_status_overlay'})
manifest['integrity_validation']={'path':(COMMIT/'freeze_integrity_validation.json').as_posix(),'sha256':sha(COMMIT/'freeze_integrity_validation.json'),'ERROR':0,'WARNING':len(warnings),'PASS':validation['PASS']}
writej(STAGE/'freeze_manifest.json',manifest)
FINAL.parent.mkdir(exist_ok=True)
STAGE.rename(FINAL)

diff='''# Core Ontology V0.3 Freeze Diff

Golden semantic changes: 0
Golden files modified: 0
New Core Objects: 0
Removed Core Objects: 0
Core semantic changes: 0
Core definitions consolidated: 14
Core boundaries consolidated: 15
Freeze Readiness recommendation adopted: yes
Historical Freeze Debt records preserved: 20
Formal Freeze status created: yes
Canonical Contract created: yes
D01 status overlay: addressed_by_freeze_commit

14 definitions and 15 semantic boundary rules are exact copies of the final audit. P01–P16 are consolidated from the authorized Freeze Commit Prompt, with whitespace normalization only. Implementation statuses are preserved separately from FROZEN semantics. Detailed admission, temporal and attribution rules are copied from accepted audit content.

The historical debt ledger is byte-identical, D01 is retained, and only the separate overlay records its canonical-contract status. Audit formal_freeze_executed=false remains unchanged; the new manifest records true. Golden inventories and file hashes were compared before and after. No extraction, migration, human adjudication, Phase 1 implementation, Git commit or production import performed.

Added formal files are in core_ontology/v0.3; commit input manifest, protected snapshot, integrity validation, publication verification, handoff, this diff and execution log provide provenance. The one-shot packaging script is supplemental reproducibility evidence, not a Phase 1 runtime.
'''
(COMMIT/'freeze_diff.md').write_text(diff,encoding='utf-8')
handoff='''# Codex Phase 1 Handoff

Core Ontology V0.3: FROZEN. Research Phase / Core Ontology Exploration: COMPLETE.
Codex Phase 1: NOT_STARTED. Analyst Model, 9527 Skill, MacroMind Core Skill and Production: NOT_READY.

## Authoritative inputs

Resolve from the workspace root:

- core_ontology/v0.3/CORE_ONTOLOGY_V0.3_FROZEN.md — sole human-readable semantic contract.
- core_ontology/v0.3/core_objects.json — 14 definitions and invariants.
- core_ontology/v0.3/core_boundaries.json — 15 frozen rules, distinct implementation statuses.
- core_ontology/v0.3/core_principles.json — 16 principles and accepted audit rule details.
- core_ontology/v0.3/freeze_manifest.json — frozen version, provenance and output SHA256.
- core_ontology/v0.3/freeze_debt_ledger.json — all 20 historical debts retained.
- core_ontology/v0.3/CHANGE_POLICY.md — compatible evolution and Core Change RFC.
- core_ontology/v0.3/freeze_debt_status_overlay.json — D01 addressed at contract level only.
- core_ontology/v0.3/source_mapping.json and semantic_contract_projection.json — derivation and semantic hash input.

Check file hashes before using the contract. Historical audit and Golden objects are evidence, not alternate definitions to combine into a new contract. The original audit remains a recommendation snapshot with formal_freeze_executed=false.

## Planning scope

Plan Executable Schema, Validator Engine, Registry, Version / Migration Framework, Audit Runner and Tests. Prioritize general content chronology, Scenario/Forecast admission, role/unit transitions, attribution and immutable provenance. Reuse existing local validators only with their explicitly limited scope; do not assume they implement the production contract.

Preserve unknown/null/review, do not fabricate data to satisfy schema. Address D02–D20 in their recorded phases; supplement Process/Contradiction positive cases and negative regressions during the pilot. Heuristic candidates do not imply Skill readiness.

Do not edit frozen artifacts in place. Nonsemantic errata require patch records and hash review; core changes require RFC, Review, Migration Plan and Compatibility Plan toward V0.4. This handoff describes future work only; no Phase 1 implementation has started.
'''
(COMMIT/'codex_phase1_handoff.md').write_text(handoff,encoding='utf-8')
published=load(FINAL/'freeze_manifest.json')
publication={'verified_at':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),'manifest_sha256':sha(FINAL/'freeze_manifest.json'),'all_output_hashes_match':all(sha(Path(x['path']))==x['sha256'] for x in published['canonical_output_hashes']),'all_input_hashes_match':all(sha(Path(x['path']))==x['sha256'] for x in inputs),'golden_inventory_and_bytes_unchanged':snapshot(golden_dirs,[ROOT/'golden_report.md'])==golden_before,'audit_inventory_and_bytes_unchanged':snapshot([AUDIT])==audit_before,'manifest_declares_frozen':published['formal_freeze_executed'] is True and published['status']=='FROZEN','debt_copy_byte_identical':sha(FINAL/'freeze_debt_ledger.json')==sha(AUDIT/'freeze_debt_ledger.json'),'D01_overlay_hash_bound':overlay['freeze_debt_status_overlay']['D01']['canonical_contract_sha256']==sha(FINAL/'CORE_ONTOLOGY_V0.3_FROZEN.md')}
ok=all(v for k,v in publication.items() if isinstance(v,bool))
publication['passed']=ok
writej(COMMIT/'publication_verification.json',publication)
files=list(FINAL.iterdir())+[p for p in COMMIT.iterdir() if p.is_file() and p.name!='freeze_commit_log.json']
log={'executed_at':NOW,'completed_at':publication['verified_at'],'freeze_commit_version':VERSION,'freeze_commit':{'completed':ok},'formal_freeze_executed':ok,'status':'FROZEN' if ok else 'FREEZE_COMMIT_FAILED','prompt_sha256':sha(PROMPT),'input_manifest_sha256':sha(COMMIT/'input_manifest.json'),'audit_artifact_hashes':audit_before,'final_golden_hashes':{x['source_id']:x['sha256'] for x in inputs if x['role']=='final_golden_evidence'},'canonical_output_hashes':[{ 'path':p.as_posix(),'sha256':sha(p)} for p in sorted(FINAL.iterdir()) if p.is_file()],'all_changes':[{'action':'create','path':p.as_posix(),'sha256':sha(p)} for p in sorted(files)],'self_record_note':'This log is newly created and intentionally does not hash itself.','integrity_validator_result':{'ERROR':errors,'WARNING':len(warnings),'PASS':validation['PASS']},'publication_verification_sha256':sha(COMMIT/'publication_verification.json'),'golden_files_modified':0,'audit_files_modified':0,'new_core_objects':0,'removed_core_objects':0,'core_semantic_changes':0,'historical_freeze_debts_preserved':20,'D01_overlay':'addressed_by_freeze_commit' if ok else 'not_addressed','production_import_ready':False,'analyst_skill_status':'NOT_READY','macromind_core_skill_status':'NOT_READY','codex_phase1_status':'NOT_STARTED','git_commit_created':False}
writej(COMMIT/'freeze_commit_log.json',log)
if not ok:raise SystemExit('Publication verification failed. Failure logged; do not announce successful freeze.')
print(json.dumps({'status':log['status'],'ERROR':errors,'WARNING':len(warnings),'PASS':validation['PASS'],'golden_files_protected':len(golden_before),'audit_files_protected':len(audit_before),'canonical_sha256':sha(FINAL/'CORE_ONTOLOGY_V0.3_FROZEN.md'),'semantic_hash':semantic_hash,'formal_freeze_executed':True},ensure_ascii=False))
