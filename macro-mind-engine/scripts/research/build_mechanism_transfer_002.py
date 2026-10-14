"""Build bounded historical mechanism additions and exercise retrieval boundaries."""
from pathlib import Path
from copy import deepcopy
import json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from macromind.methods.conditional_retrieval import retrieve_mechanisms
BASE=ROOT/'phase1/topic_mining';OUT=BASE/'mechanism_transfer_002'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
cases=read(BASE/'explanation_selection_001/cases.json');evidence={}
for case in cases:
 for e in case['evidence']:
  evidence[e['id']]={'id':e['id'],'episode':case['episode'],'observed_on':case['analysis_date'],'cue_range':e['cue_range'],'cues':e['cues'],'event_cluster':str(case['episode'])}
def newev(ep,date,label,lo,hi,cluster):
 cs=read(OUT/f'ep{ep}_cues.json');eid=f'EP{ep}:{label}'
 evidence[eid]={'id':eid,'episode':ep,'observed_on':date,'cue_range':[lo,hi],'cues':[c for c in cs if lo<=c['cue']<=hi],'event_cluster':cluster};return eid
newev(1048,'2025-01-20','credit',395,407,'tiktok_reopening')
newev(1048,'2025-01-20','feedback',527,590,'tiktok_reopening')
newev(1048,'2025-01-20','substitute',63,77,'tiktok_reopening')
newev(1048,'2025-01-20','bargain',749,789,'tiktok_reopening')
newev(1182,'2025-08-03','substitute',314,356,'july_jobs_firing')
newev(1182,'2025-08-03','buffer',423,487,'july_jobs_firing')
def version(date,chain,ids,scope):
 return {'observed_on':date,'chain':chain,'author_evidence':[{k:v for k,v in evidence[i].items() if k!='cues'} for i in ids],'support_scope':scope}
def mechanism(i,name,triggers,conditions,alts,checks,boundary,versions):
 return {'id':i,'name':name,'triggers':triggers,'trigger_groups':[triggers],'required_conditions':conditions,'alternatives':alts,'discriminating_observations':checks,'boundary':boundary,'versions':versions}
m7=['比较公开目标与可归功的即时收益','列出受益者和承担成本者','比较兑现时间、政绩归属和组织支持','形成当期解释排序，保留长期代价']
m8=['行动者依靠公众支持维持权力或价值','短期姿态带来支持','检查生活收益能否兑现和信用能否维持','支持流失会反过来削弱原有优势']
m9=['原渠道提供的服务仍被需要','限制或信用损失削弱原渠道吸引力','存在可用替代渠道时需求可能迁移','替代是否持续取决于可用性与信任']
m10=['区分长期矛盾与眼前失控','检查可动用资源及承接渠道','资源可暂时缓冲压力并换取时间','缓冲不等于根本矛盾消失']
m11=['观察强硬威胁及实际接受的条件','比较对方付出与原先宣示目标','推断实际交换对象与行动约束','同时保留暂缓后继续施压的阶段可能']
new=[
 mechanism('M7','即时政治收益与长期经济收益的排序',['public_policy_action','visible_credit_channel'],['beneficiaries_identified','credit_attributable'],['长期产业安全目标','纯粹行政效率'],['承诺是否兑现','谁能获得政绩、谁承担成本'],'可理解政治动机不等于政策正确；不得从受益倒推事先策划。',[version('2024-05-15',m7,['EP798:E3','EP798:E4'],'关税单事件直接比较；尚未跨题'),version('2025-01-20',m7,['EP798:E3','EP798:E4','EP1048:credit'],'关税与平台重开两类事件有共同结构；非普遍定律')]),
 mechanism('M8','公众支持形成优势，也构成后续反噬条件',['support_based_power','cost_or_delivery_pressure'],['supporters_experience_cost','credit_attributable'],['支持者长期容忍成本','组织资源替代公众支持'],['支持者生活变化','支持或信任是否实际下降'],'没有测得支持下降时只能作条件假说；不等于凡强硬必反噬。',[version('2024-12-19',m8,['EP1016:E2'],'政治联盟单事件'),version('2025-01-20',m8,['EP1016:E2','EP1048:feedback'],'联盟与个人声誉价值两类应用；不是对手因压力团结的证据')]),
 mechanism('M9','服务仍被需要时，限制或失信可能推动替代',['channel_disruption_or_distrust','alternative_channel_visible'],['alternative_can_serve_need','users_can_switch'],['原渠道不可替代','迁移成本过高'],['使用者是否迁移','替代服务能否承接需求'],'平台迁移与货币体系只支持抽象关系类比，不可宣称已复现统计信用到美元的完整链。',[version('2025-01-20',m9,['EP1048:substitute'],'平台关闭后用户转向替代平台'),version('2025-08-03',m9,['EP1048:substitute','EP1182:substitute'],'跨领域的模型抽象候选；货币段为作者假说，非实证因果')]),
 mechanism('M10','可用资源暂压矛盾并改变时间窗口',['system_stress','financing_tool_available'],['resources_deployable','funding_absorption_path'],['工具无法执行','信任流失快于资金投入'],['资金是否实际投放','市场是否承接与响应'],'不能从资源存在推出必定救助或危机必然来临；具体稳定币链仅见同一就业事件。',[version('2023-11-10',m10,['EP520:E4'],'政府举债暂压政治矛盾；选举前景有条件'),version('2025-08-03',m10,['EP520:E4','EP1182:buffer'],'两事件支持一般缓冲结构；短债与稳定币具体链为单事件')]),
 mechanism('M11','用实际交换条件检验强硬姿态的目标',['coercive_threat','conditional_concession'],['exchange_value_assessable','actor_can_execute_threat'],['长期战略没有变只是分步执行','执行成本迫使临时退让'],['承诺与最终行动是否一致','对方真正付出什么'],'接受条件与实际退让须区分；只宣布豁免时，尚不能认定交易已经完成。',[version('2025-01-20',m11,['EP1048:bargain'],'平台事件筹码与交换关系'),version('2025-02-04',m11,['EP1048:bargain','EP1056:E2','EP1056:E3'],'平台与关税两类事件；当期退让不等于永久放弃')])]
old=read(BASE/'conditional_retrieval_001/catalog.json')
for m in old:
 if m['id']=='M6':
  m['trigger_groups']=[['public_relief_promise','political_pressure']]
  m['boundary']='本候选目录要求救济承诺与政治压力同时出现；仅政治压力不足。未改写旧实验目录。'
catalog=old+new
save('catalog.json',catalog);save('historical_evidence.json',list(evidence.values()))
save('scope.json',{'newly_read_episodes':[1048,1182],'reused_evidence_episodes':[520,798,1016,1056],'target1183_excluded_from_rule_evidence':True,'same_event_not_independent':['1182与1183同属就业报告撤职事件'],'deferred':[{'name':'压力促成反对派团结','reason':'仅1183直接支持，未找到独立复现；不收入可检索通用机制。'},{'name':'统计信用→美联储依据→美元标准替代完整链','reason':'仍缺完整跨题证据，仅收录更抽象的替代关系并降低支持等级。'}],'historical_reference_limit':'1048按1183提到的日期定位，但未找到1183声称的完整就职时预测；不可据回顾补写旧判断。','all_rules_status':'research_candidates_not_promoted','feature_assignment':'manual_observable_labels_not_automatic_semantic_extraction'})
checks=[]
def obs(*features,date='2025-08-08T23:59:59+08:00'):
 return {f:{'state':'supported','source_refs':['test:'+f],'available_at':date} for f in features}
def retrieve(o,cutoff='2025-08-10T00:00:00+08:00',cat=catalog):return retrieve_mechanisms(cat,as_of=cutoff,observations=o)
def ids(r):return {m['id'] for m in r['candidates']}
assert not ids(retrieve(obs('political_pressure')));checks.append('political_pressure_alone_no_longer_retrieves_M6_in_new_catalog')
assert 'M7' not in ids(retrieve(obs('public_policy_action')));checks.append('one_generic_trigger_does_not_satisfy_joint_trigger')
r=retrieve(obs('public_policy_action','visible_credit_channel'));assert 'M7' in ids(r);assert next(c for c in r['candidates'] if c['id']=='M7')['unknown_conditions'];checks.append('joint_observations_allow_hypothesis_with_unknown_causal_conditions')
o=obs('public_policy_action','visible_credit_channel');o['credit_attributable']={'state':'contradicted','source_refs':['test:counter'],'available_at':'2025-08-08T00:00:00+08:00'}
assert next(c for c in retrieve(o)['candidates'] if c['id']=='M7')['status']=='candidate_with_counterevidence';checks.append('counterevidence_preserved')
r=retrieve(obs('channel_disruption_or_distrust','alternative_channel_visible',date='2025-01-21T00:00:00+08:00'),'2025-01-22T00:00:00+08:00');m=next(c for c in r['candidates'] if c['id']=='M9');assert all(e['episode']==1048 for e in m['author_evidence']);checks.append('early_query_excludes_later_monetary_evidence')
try:retrieve(obs('public_policy_action',date='2025-08-11T00:00:00+08:00'))
except ValueError:checks.append('future_observation_rejected')
else:raise AssertionError('future accepted')
legacy=read(BASE/'conditional_retrieval_001/catalog.json');q=read(BASE/'conditional_retrieval_001/query.json');expected=read(BASE/'conditional_retrieval_001/retrieval.json');assert retrieve_mechanisms(legacy,as_of=q['cutoff'],observations=q['observations'])==expected;checks.append('legacy_catalog_result_unchanged')
for m in new:
 for v in m['versions']:
  assert all(e['observed_on']<=v['observed_on'] for e in v['author_evidence'])
  for e in v['author_evidence']:
   assert evidence[e['id']]['cues']
checks.append('dated_evidence_present_for_every_version')
save('checks.json',{'passed':checks,'count':len(checks),'scope':'retrieval behavior and evidence availability; not generation benefit'})
print(json.dumps({'added':[m['id'] for m in new],'checks':len(checks)},ensure_ascii=False))
