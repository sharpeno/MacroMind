import json,hashlib
from pathlib import Path
from macromind.methods.baseline import render_baselines
r=Path.cwd();o=r/'phase1/method_prototype/run_003';previous=r/'phase1/method_prototype/run_002'
shared={'source_case':'fed','evidence_cutoff':'2024-08-23','coverage':'selected_excerpts','evidence_scope':'仅沿用两处官方讲话选段；未系统观察后续政策、实施和群体反应。','review_horizon':'补充下一份相关材料时复核；尚未设定持续观察窗口，因此本轮不将迟迟未见动作计作反证。'}
items=[{**shared,'id':'baseline-plan','topic':'提前准备纠错方案并控制错误程度','working_judgment':'暂不计入尚未显现的替代方案所带来的改善，按已观察到的政策路径与约束继续分析。','consequences':['不以一个未被识别的预案，提前抵消当前情景中的风险。','可以推测已有内部准备，但需要说明它改变哪一步推演，而不是默认它必然有效。'],'alternative':'内部可能已有准备，尚未公开或尚未进入执行；保留这一分支，不把它当作确定改善。','upgrade_triggers':['出现具体工具、职责、资源或实施安排，且能说明如何改变当前约束。','实际执行或可归因的改善出现时，按落实程度调整，而非仅凭宣布假定效果全部兑现。'],'downgrade_triggers':['将来建立合理的观察窗口与应有执行信号后，若关键动作仍未出现，可削弱该预案已准备充分的解释。','出现明确撤回、实施受阻或与预期措施相反的实际行动。']},{**shared,'id':'baseline-guidance','topic':'与群体同行并引导认识','working_judgment':'暂不假定已经形成共识或降低执行阻力，仍把这些约束纳入分析。','consequences':['不把一次公开讲话直接换算成群体已接受方案或政策已顺利传导。','继续分析沟通不足、认知差异或执行阻力可能造成的影响，不因证据未知而停止推演。'],'alternative':'可能存在选段没有呈现的沟通与引导过程；后续反馈可能支持这一解释。','upgrade_triggers':['出现具体沟通过程，以及相关群体的理解、接受或行为变化证据。','实际配合和执行情况支持阻力下降时，调整主情景。'],'downgrade_triggers':['出现持续反对、误解或执行不配合，且能对应所分析的沟通目标。','建立合理观察窗口后，应有反馈或配合仍未显现；本轮两段材料不足以作此判断。']}]
(o/'baselines.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
(o/'inference.json').write_bytes((previous/'inference.json').read_bytes())
original=(previous/'TRACE.html').read_text(encoding='utf-8')
addition=render_baselines(items)
html=original.replace('<nav>',addition+'<nav>',1)
(o/'TRACE.html').write_text(html,encoding='utf-8')
assert html.replace(addition,'',1)==original
(o/'approval.json').write_text(json.dumps({'received_date':'2026-10-05','user_statement':'好的，然后除此之外的剩余内容都没有问题','scope':'同意新增两项暂定基础判断；其余现有内容认可，原样保留，不重复审核。','not_implied':['宏观事实已核实','推断已确证','方法有效性已验证','所有未来版本自动批准']},ensure_ascii=False,indent=2),encoding='utf-8')
(o/'changes.json').write_text(json.dumps({'unchanged_inference_sha256':hashlib.sha256((previous/'inference.json').read_bytes()).hexdigest(),'only_html_change':'Insert two working baseline cards; original HTML recoverable exactly by removing added section','added_baselines':2},indent=2),encoding='utf-8')
print('Two baselines added; original content preserved exactly')
