import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[2]; H=ROOT/'phase1/holdout_evaluation'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if (P/'manifest.json').exists():raise SystemExit('Sealed: create a new run.')
protected={}
for folder in [ROOT/'phase1/framework_review/v03_frozen_001']+[H/f'run_{i:03}{s}' for i in range(1,5) for s in ['', '_review_001']]:
 for n,h in read(folder/'manifest.json').items():
  assert sha(folder/n)==h,str(folder/n)
  protected[(folder/n).relative_to(ROOT).as_posix()]=h
 protected[(folder/'manifest.json').relative_to(ROOT).as_posix()]=sha(folder/'manifest.json')
write('protected_inputs.json',protected)
# These are new assistant diagnoses of existing reviewed differences, not new human approvals.
specs=[
('D472A',472,'R01','内部控制链',[(290,375),(586,610)],'一般分歧没有展开为消息矛盾、撤离迹象、管理脱节与盟友亲自介入的链条。','执行不足','M01已有约束；具体控制机制未展开。','输入差异：不能确认原新闻包含所有异常线索。','E02','作者作较强控制失灵推断；不是独立核验事实。'),
('D472B',472,'R02','角色约束与说话动机',[(237,289)],'已识别耶伦身份，没有串起身份、事件态度、不能示弱的约束和壮胆动机。','执行不足','身份字段不能代替角色与表达之间的关系推理。','方法表示也需补充角色怎样限制表达。','E01','保留作者“唯一的正确答案”“心里面虚”的强判断。'),
('D472C',472,'R03','短期判断与未知因果',[(586,637)],'有更新触发器，没有还原3—5天和平判断以及同时承认因果说不清。','执行不足','不能因为范围模糊就删除作者说出的时间判断。','和平的定义不清，不能据此评分现实命中。','E07','保留“起码3~5天”和“说不清楚”，按命题分别记确信程度。'),
('D473A',473,'R01','场景中的行动信号',[(11,82)],'身份表没有表达多边活动、外部局势、参与方式和接待关系的共同作用。','方法表示不足','用户强调的是线索在具体场景中的联系。','原新闻未必含姿态与接待细节，不能全归因于框架。','E01','依最新用户修订，收窄为以众多参与者之一参加盛会，不扩大为全面认可秩序。'),
('D473B',473,'R02','预期渠道与长期推演',[(83,113),(391,470)],'原答案等待实体协议，漏掉沟通与利益协调、争斗需求、供应风险预期和价格的链条。','执行不足','M04允许传导，但执行把渠道收窄为实体交付。','原输入缺独立价格数据，短期价格不能证明长期秩序解释。','E03','保留作者对供应风险暴涨剧本不太可能的倾向；长期推演另列。'),
('D473C',473,'R03','案例示范与路径吸引',[(269,390),(489,544)],'合同与交付区分没有覆盖技术回流、市场整合和案例激发合作向往。','方法表示不足','需要记录案例怎样改变其他参与者的选择。','产业与历史知识不都来自当期新闻；目前主要是单期支持。','E03','示范效果是作者解释，不写成已验证结果。'),
('D474A',474,'R01','分支与区分性观察',[(134,303),(328,392),(429,496)],'保持未定，没有展开有意施压与非预期后失控两支及后续观察。','执行不足','已有备选与更新要求，但具体推演未执行。','责任和技术前提未核验；后续行为不能唯一识别过去意图。','E07','责任倾向与是否有意分开；不把作者猜测升级成事实。'),
('D474B',474,'R02','话语策略用途',[(497,600)],'没有还原支持话语可能借交付限制甩责、停止要求可能为介入铺垫。','方法表示不足','表态执行区分尚未生成具体话语功能。','执行也有强度丢失，不能将整段统一降为猜测。','E01','伊朗“未来一定会下场”为强断言；给拜登设局在后文只是猜测之一。'),
('D474C',474,'R03','责任分散与纠偏困难',[(23,56),(345,392),(601,662)],'外部压力分析漏掉多环节责任、战时不能停机排查及高层难控基层。','方法表示不足','需展开执行层、反馈和纠偏，而非把国家视作单一意志。','已有利益约束规则也可能因执行不足未展开，需控制实验区分。','E02','保留作者关于持续越线的强判断，不将它晋升为普遍定律。'),
('D475A',475,'R01','目标与既有手段',[(367,431),(496,532)],'区分预期与政策，但漏掉抑制通胀目标、高息持续作用和无需追加加息的倾向。','方法表示不足','最新用户意见要求先判断既有手段是否仍起作用。','也涉及判断偏好；本例优先看持续高息不等于永远忽略强数据。','E04','保留“最后的结果呢还是不加息”与油价暴涨例外，不改成马上降息。'),
('D475B',475,'R02','结果反推未见机制',[(432,495)],'未复现作者以消费韧性支持隐蔽注水旧判断。','历史状态缺口','作者称此前一直提醒，但更早原始记录未定位，不可回填首提时间。','同时涉及用异常结果支持旧解释的偏好，稳定性待检验。','E05','作者说“证实”又说管道看不到，两者同时保留，不补造管道。'),
('D475C',475,'R03','主要矛盾与等待成本',[(496,648)],'并行解释未表达国内通胀优先、美以等待成本冲突和明确倾向。','判断偏好','最新用户修订突出主要矛盾排序，而不只是时间窗口。','一般关系表的执行不足也是可能原因，尚未隔离。','E06','保留“美国一定不会”“板上钉钉”；不被绑定不等于终止全部军援。')]
evidence={}; diagnoses=[]
for did,ep,rid,title,ranges,gap,primary,reason,confound,op,force in specs:
 run=H/f'run_{ep-471:03}';rev=H/f'run_{ep-471:03}_review_001';t=read(run/'target_transcript.json')
 adopted=[]
 if ep in [473,475]:
  d=read(rev/'revisions.json');adopted=[x for x in d['revisions' if ep==473 else 'items'] if x['id']==rid]
 evidence[did]={'episode':ep,'source':(run/'target_transcript.json').relative_to(ROOT).as_posix(),'source_sha256':sha(run/'target_transcript.json'),'excerpts':[{'from':a,'to':b,'cues':[c for c in t['cues'] if a<=c['cue']<=b]} for a,b in ranges],'latest_review':(rev/'REPORT.md').relative_to(ROOT).as_posix(),'latest_review_sha256':sha(rev/'REPORT.md'),'adopted_user_revision':adopted,'note':'原自动字幕逐字保留，未经核听；历史审阅不等于新分类获批。'}
 diagnoses.append(dict(id=did,episode=ep,review_item=rid,title=title,observed_gap=gap,primary_diagnosis=primary,reason=reason,confound=confound,candidate_operation=op,author_force_and_scope=force,evidence_ref=did,status='ASSISTANT_DIAGNOSIS_NOT_CAUSALLY_ISOLATED'))
write('evidence.json',evidence);write('diagnosis.json',{'scope':'12 reviewed topics, not exhaustive four-episode extraction','items':diagnoses})
ops=[
('E01','在场景中理解身份和言行',['D472B','D473A','D474B'],'遇到关键讲话、到访或姿态，先记录活动性质、局势、身份关系与时点，再追问角色能说什么、不能说什么，以及行为怎样改变他人预期。','情境与角色→表达约束→策略用途或动机→作者倾向。','单个姿态不证明心理；忠实保留作者的推断及其强度。','比较同角色不同场景及同场景不同角色；不能处处套用心虚。'),
('E02','追查内部执行和纠偏能力',['D472A','D474C'],'出现消息、命令或行为矛盾，追问谁决定、谁执行、谁能阻止，以及能否暂停、追责和纠偏。','异常→作者推断的内部关系→控制能力→其他参与者响应。','分歧不自动等于失控；隐含前提和助手重建分别标记。','寻找贯彻命令、纠偏成功的反例，不能只积累失控案例。'),
('E03','区分实体效果与预期示范',['D473B','D473C'],'对会议、合同、案例，分别分析实体产出、风险预期、路径吸引以及作者延伸的长期解释。','沟通或案例→未来利益预期→行为需求变化→风险价格→长期推演。','各链单列，不能以短期价格验证整条长期解释。','目前主要来自473期，需跨期与反例检验稳定性。'),
('E04','从目标和既有手段判断追加动作',['D475A'],'先问作者认定的政策目标，再看现有政策水平和持续时间的作用，最后判断追加力度的必要性。','目标→既有手段作用→追加必要性→特殊触发条件→倾向。','不加息不等于降息；本例倾向不能机械跨政策环境。','寻找相似目标下作者仍支持追加动作的案例。'),
('E05','用异常结果追问未见机制',['D475B','D472A'],'列作者原有预期及出处，再记录如何从异常结果推断不可见过程，是否视为旧判断得到支持。','旧判断→新观察→推断机制→作者确信→机制仍未知部分。','作者称证实与系统核验状态分开；不虚构渠道或早期预测记录。','两例对象不同，只构成候选；不能断言异常必由隐藏操作造成。'),
('E06','表达矛盾排序和行动窗口',['D475C'],'多个目标冲突时，识别作者优先的目标及依据，再问谁能等、谁不能等、等待改变什么。','主要矛盾→资源时机约束→等待成本→主导解释与结论。','无证据时排序未知；不能设定国内永远高于国外。','目前是475期局部证据，需要不同领域和反向排序案例。'),
('E07','按命题保留确信和更新',['D472C','D474A','D474B'],'责任、动机、未来行动、时间范围分开，逐项记录断言、倾向、猜测、未知和更新指标。','命题→强度原文→范围条件→观察如何改变命题。','不能把一项猜测标签传给整段，也不能凭修辞生成数值概率。','核查同段限定与后文回撤，冲突保留不替作者消解。')]
write('framework_candidate.json',{'id':'9527-fidelity-candidate-0.1','status':'ASSISTANT_RESEARCH_CANDIDATE_NOT_HUMAN_APPROVED','parent_framework':'phase1/framework_review/v03_frozen_001/framework.json','parent_sha256':sha(ROOT/'phase1/framework_review/v03_frozen_001/framework.json'),'purpose':['faithful_reconstruction','view_generation_transfer'],'composition':'v0.3 + conditional candidate operations; no global activation','operations':[dict(id=i,title=t,evidence_refs=refs,when_and_question=q,procedure=proc,boundary=b,counterexample_probe=probe,attribution='ASSISTANT_OPERATIONALIZATION',stable_trait_verified=False) for i,t,refs,q,proc,b,probe in ops],'training_episodes':[472,473,474,475],'execution':'RUN_PROMPT.md; prompt package, not deployed engine','semantic_approval':False,'out_of_sample_fidelity_verified':False})
states=[('S472-control',472,'D472A','作者认为以色列管理脱节，以此解释拜登临时到访。','strong_assertion'),('S472-time',472,'D472C','到访争取起码3—5天和平，同时承认与会议的因果说不清。','mixed_requires_split'),('S473-cooperation',473,'D473B','合作发展力量可缓和供应风险预期，因中东失序而油价暴涨的剧本不太可能。','directional_judgment'),('S474-branches',474,'D474A','有意施压与非预期失控两支，后续是否继续袭击民用设施用作区分观察。','hypotheses'),('S474-iran',474,'D474B','伊朗未来一定下场；形式与期限未在此卡完整界定。','strong_assertion'),('S475-policy',475,'D475A','倾向不再加息，高息持续起作用，油价暴涨保留为例外。','directional_judgment'),('S475-channel',475,'D475B','消费上涨被作者称为证实旧注水判断，但具体管道看不到。','claimed_confirmation'),('S475-priority',475,'D475C','国内调整优先与美以等待成本冲突，作者强断言美国不会被绑定。','strong_assertion')]
write('analyst_state.json',{'status':'PARTIAL_RECONSTRUCTION_NOT_COMPLETE_MEMORY','cutoff_rule':'Target N uses only observed_episode < N, with publication order separately established. Do not backdate retrospective claims.','entries':[dict(id=s,observed_episode=ep,evidence_ref=ref,belief=b,author_force=f,verification_status='NOT_INDEPENDENTLY_VERIFIED',earliest_original_statement='UNKNOWN',available_for_own_episode_transfer=False,author='ASSISTANT_RECONSTRUCTION') for s,ep,ref,b,f in states],'missing_history':['完整472期之前状态','475提及旧观点的原始首发记录','完整更新与撤回关系']})
rows=['# 四期忠实度诊断\n','整理12项既有审阅主题，采用最新用户修订。原因分类是助手提出的待检验诊断，非已隔离的因果结论；不代表对四期全部内容重新验收。\n']
for d in diagnoses:
 e=evidence[d['id']]
 rows += [f"## 第{d['episode']}期 {d['title']}\n",d['observed_gap']+'\n',f"主要诊断：{d['primary_diagnosis']}。{d['reason']}\n",'其他影响：'+d['confound']+'\n','还原要求：'+d['author_force_and_scope']+'\n',f"候选操作：{d['candidate_operation']}。证据键：{d['id']}。\n",f"[最新修订](../../../{e['latest_review']}) · [原字幕](../../../{e['source']})\n"]
(P/'DIAGNOSIS.md').write_text('\n'.join(rows),encoding='utf-8')
rows=['# 分析师框架候选\n','已有v0.3保留；以下七项是条件调用的助手候选，尚未证明是稳定特征，也不要求每期执行全部操作。\n']
for i,t,refs,q,proc,b,probe in ops:rows += [f'## {i} {t}\n',q+'\n',proc+'\n','边界：'+b+'\n','待检验：'+probe+'\n','证据：'+'、'.join(refs)+'，见[诊断](DIAGNOSIS.md)与[evidence.json](evidence.json)。\n']
rows += ['## 历史状态\n','状态表是作者在各期表达的观点，不是现实事实表。不得回填首次提出时间；目标期只使用较早且时序成立的记录。主要矛盾排序目前有475期局部支持，不能预设作者在所有场景都采用同一顺序。\n','## 独立使用\n','按RUN_PROMPT.md装配父框架、候选操作、截止日前状态和输入。还原模式可读目标字幕；迁移模式排除目标字幕、参考答案与目标期之后状态。方法来自472—475，这四期仅用于开发诊断。\n']
(P/'FRAMEWORK.md').write_text('\n'.join(rows),encoding='utf-8')
print(json.dumps(dict(diagnoses=len(diagnoses),operations=len(ops),states=len(states),protected_files=len(protected)),ensure_ascii=False))
