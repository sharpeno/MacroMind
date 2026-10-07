import json,hashlib
from pathlib import Path
from macromind.methods.inference import render,validate
r=Path.cwd();o=r/'phase1/method_prototype/run_002';old=r/'phase1/method_prototype/run_001'
rd=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
quotes={str(x['cue_id']):x['quote'] for x in rd(r/'phase1/batch_pilot/run_005/EP002/segments.json')}
prior=rd(old/'public_case.packet.json')
def ep(*ids):return [{'source':'ep002','record':str(i),'quote':quotes[str(i)]} for i in ids]
fed=rd(old/'public_case_excerpts.json')
def fa(key):return [{'source':'fed2024','record':key,'quote':next(x['text'] for x in fed['records'] if x['id']==key)}]
def hyp(id,text,owner,force,refs,anchors,assumptions,alternatives,more,less):
 return {'id':id,'statement':text,'attribution':owner,'original_force':force,'observation_refs':refs,'attribution_anchors':anchors,'assumptions':assumptions,'alternatives':alternatives,'strengthen_with':more,'weaken_with':less,'epistemic_status':'HYPOTHESIS_FROM_INDIRECT_EVIDENCE','confirmation':'NOT_CONFIRMED'}
d={'version':'indirect-inference-1','correction':'上一版把提前识别问题的检查过度收窄为寻找事前直接记录。本版允许从公开论调、政策与行动的时机、准备周期和资源安排，反推可能的预案、动机及信息优势；再单独判断这些推断得到多强的支持。','method_distinction':'领导者如何准备和纠错，是被讨论的做法；博主如何从动作反推决策逻辑，是分析者的方法。这两层应关联而不混为一条已证实的因果链。','attribution_limit':'用户指出这是博主常用的方式。本轮核实了补库存这一具体例子，不以一个例子宣称已经测定其全库出现频率。条件和竞争解释由助手整理，尚未获得新的逐项人工确认。','sources':prior['sources'],'cases':[
 {'id':'oil','title':'原材料中的方法例子：多渠道进口与补库存','scope':'EP002原字幕99–121。这里只重建博主的分析方式，不将其所述进口、库存或地缘判断自动认证为外部事实。','observations':[
 {'id':'O1','statement':'博主称积极洽谈俄罗斯等渠道进口石油，并进行库存补充。','layer':'blogger_report','anchors':ep(99,100,101,102)}], 'hypotheses':[
 hyp('H1','这些动作可能反映防范供应中断、提前做多手准备的动机。','blogger_explicit','原话先用“如果说”铺陈，随后在cue121使用“肯定”；保留这个强断言的归属，但系统不因此将其认作已证实事实。',['O1'],ep(103,104,105,106,107,108,109,121),
 ['所述进口与库存动作确实发生，并且在时机、规模或来源安排上与风险准备有关。','这些动作所需的准备周期，与博主所推断的提前布局相容。'],
 ['常规库存管理或补回已有消耗也可能产生补库存动作。','价格、合同或来源多元化安排也可能解释相同动作；此处未验证这些解释。'],
 ['带日期的采购、谈判和运输安排，能显示准备开始时间及持续性。','与过去补库惯例比较，观察渠道、规模或时间是否出现有解释价值的变化。'],
 ['记录显示完全按既定周期补库，且没有与所推断风险对应的调整。','准备时间或动作本身与这一解释的关键前提不符。']),
 hyp('H2','决策层可能掌握了影响准备时机或规模的更多风险信息。','assistant_transfer','探索性假设；不是本段原话已经证实决策层掌握了某项战争情报。',['O1'],[],
 ['动作包含仅靠已知常规因素难以解释的提前量或资源投入。','相关决策者有可能接触到影响判断的信息；具体内容尚不清楚。'],
 ['无需非公开信息，仅对公开风险采取预防措施也能解释这些动作。','组织惯例和多种动机并存，也可能造成看似提前布局的现象。'],
 ['先建立采购与公开风险信息的时间线，再看动作是否确实领先。','寻找同时期信息来源、决策记录或后来可核验的披露。'],
 ['公开信息和既有惯例已足以解释动作，额外信息假设没有增加解释力。','材料显示实际是风险显现后的补救行动。'])]},
 {'id':'fed','title':'修正后的迁移示例：政策转向透露什么','scope':'沿用2024年公开讲话的两个选段；使用后来整理的方法作回看分析，不当作当时预测，也不是博主本人对这份讲话的评价。','observations':[
 {'id':'O1','statement':'官方讲话回顾认识到问题并开始转向。','layer':'official_statement','anchors':fa('pivot')},
 {'id':'O2','statement':'官方讲话表达政策需要调整。','layer':'official_statement','anchors':fa('adjust')}], 'hypotheses':[
 hyp('H1','公开的转向与调整表态，可以作为追问此前是否已有判断更新、准备或协调的间接线索。','assistant_transfer','可提出的推断；不再因缺少事前记录而停止分析，但两个选段不足以确定提前多久、准备到何种程度。',['O1','O2'],[],
 ['公开表态与实际决策过程存在联系，而不只是无约束的修辞。','若调整需要组织协调和准备，其公开节点可能晚于部分内部工作；所需周期仍要验证。'],
 ['可能是随新数据逐步改变判断，未必早有完整预案。','讲话可能在整理事后叙述，或是在引导预期，而不是披露内部准备时间线。'],
 ['比较连续会议纪要、此前讲话和实际执行安排，确定哪些变化先出现。','寻找准备周期、资源安排与决策分工资料，检验是否需要提前部署。'],
 ['同时期记录显示未提前准备，直到新信息出现后才开始设计方案。','表态未落实为行动，且材料显示其主要是沟通姿态。'])]}], 'semantic_acceptance':False,'skill_ready':False}
valid,_=validate(d,r)
(o/'inference.json').write_text(json.dumps(valid,ensure_ascii=False,indent=2),encoding='utf-8')
(o/'TRACE.html').write_text(render(valid,r),encoding='utf-8')
(o/'feedback.json').write_text(json.dumps({'received_date':'2026-10-05','user_correction':'博主会利用公开论调、决策与执行反推动机及决策层可能掌握的其他信息；补库存是例子。','scope':'修正方法表达，不把所有具体动机或非公开信息升级为事实','applied':'新增独立间接推断层；保留旧版和run_005'},ensure_ascii=False,indent=2),encoding='utf-8')
print('Validated 2 cases, 3 hypotheses; no facts or Skills auto-admitted')
