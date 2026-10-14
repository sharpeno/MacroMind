"""Prepare and exercise conditional retrieval on an exposed title-aligned case."""
import json
from pathlib import Path
from macromind.methods.conditional_retrieval import retrieve_mechanisms
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'macro-mind-engine/phase1/topic_mining'
OUT=BASE/'conditional_retrieval_001';OUT.mkdir(parents=True,exist_ok=True)
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def save(name,x):(OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
lineage=read(BASE/'rice_lineage_001/lineage.json')
evidence={e['id']:e for e in read(BASE/'rice_lineage_001/evidence.json')}
evidence.update({e['id']:e for e in read(BASE/'rice_bridge_001/evidence.json')})
mechanisms=lineage['mechanisms']+[read(BASE/'rice_bridge_001/mechanism_additions.json')[0]]
features={
'M1':(['policy_ineffective'],['remedy_feasible','actor_has_control'],['加工物流能力不足','政策时滞'],['同等执行条件下可行补救被谁阻止','放粮到店的具体瓶颈']),
'M2':(['industry_protection','policy_ineffective'],['concentrated_beneficiaries','actor_has_control'],['公共粮食安全目标','无协调的分销延误'],['谁的利润增加','谁决定采购和释放价格']),
'M3':(['staple_price_rise'],['demand_inelastic','expectation_feedback'],['一次性收成冲击','旅游需求增加'],['替代品价格和购买量','囤货与预期变化']),
'M4':(['external_financial_loss'],['same_actor_loss_and_rents','actor_has_control','profit_transfer_path'],['银行自行重组与增资','粮价独立供需冲击'],['损失主体与渠道的组织连接','高价收益实际流向']),
'M5':(['direct_retail_release'],['limited_relief_supply','retailer_allocation_power'],['竞争传导降价','加工能力约束'],['低价米持续供应和覆盖','普通米价与储备米价是否分化']),
'M6':(['public_relief_promise','political_pressure'],['credit_attributable','concentrated_beneficiaries'],['单纯行政救急','真实供需修复'],['谁承诺、谁获得支持','政策失效时责任如何归属'])}
catalog=[]
for m in mechanisms:
 versions=m.get('versions') or [{'observed_on':m['observed_on'],'chain':m['chain'],'evidence':m['evidence']}]
 tr,co,al,di=features[m['id']]
 catalog.append({'id':m['id'],'name':m['name'],'triggers':tr,'required_conditions':co,'alternatives':al,'discriminating_observations':di,'versions':[{'observed_on':v['observed_on'],'chain':v['chain'],'author_evidence':[{'id':eid,'episode':evidence[eid]['episode'],'cue_range':evidence[eid]['cue_range'],'observed_on':evidence[eid]['date']} for eid in v['evidence']]} for v in versions]})
save('catalog.json',catalog)
observations={
 'policy_ineffective':{'state':'supported','source_refs':['title_aligned_001:N1','title_aligned_001:N2'],'note':'既有放粮未明显传导到零售端，报道层线索'},
 'industry_protection':{'state':'supported','source_refs':['title_aligned_001:N2'],'note':'高关税保护农户与自给目标'},
 'staple_price_rise':{'state':'supported','source_refs':['title_aligned_001:N1','title_aligned_001:N2']},
 'direct_retail_release':{'state':'supported','source_refs':['title_aligned_001:N3'],'note':'计划，不是已完成效果'},
 'public_relief_promise':{'state':'supported','source_refs':['title_aligned_001:N3']},
 'political_pressure':{'state':'supported','source_refs':['title_aligned_001:N2','title_aligned_001:N3']},
 'remedy_feasible':{'state':'unknown','source_refs':[]},
 'actor_has_control':{'state':'unknown','source_refs':[]},
 'concentrated_beneficiaries':{'state':'unknown','source_refs':[]},
 'credit_attributable':{'state':'unknown','source_refs':[]}}
news=read(BASE/'title_aligned_001/sources.json')['included']
from macromind.knowledge.store import bounds
source_times={'title_aligned_001:'+n['id']:bounds(n['published_at'],n['precision'],n.get('timezone'))[1] for n in news}
for observation in observations.values():
    if observation['state']!='unknown':
        observation['available_at']=max(source_times[ref] for ref in observation['source_refs'])
packet={'target_episode':1134,'cutoff':'2025-05-27T00:00:00+08:00','questions':read(BASE/'title_aligned_001/question_contract.json')['questions'],'observations':observations,'feature_assignment':'父代理依据既有冻结新闻显式标注；未实现从任意原文自动抽取特征。','classification':'exposed_case_retrieval_regression_not_blind_generation'}
save('query.json',packet)
result=retrieve_mechanisms(catalog,as_of=packet['cutoff'],observations=observations);save('retrieval.json',result)
assert {m['id'] for m in result['candidates']}=={'M1','M2','M3','M6'}
assert all(m['unknown_conditions'] for m in result['candidates'])
late=retrieve_mechanisms(catalog,as_of='2025-05-28T00:00:00+08:00',observations={'external_financial_loss':{'state':'supported','source_refs':['rice_bridge_001:bank_fy2024'],'available_at':'2025-05-23T00:00:00+08:00'}})
assert late['candidates'][0]['id']=='M4' and late['candidates'][0]['status']=='hypothesis_candidate'
assert 'profit_transfer_path' in late['candidates'][0]['unknown_conditions']
contrary=retrieve_mechanisms(catalog,as_of='2025-05-28T00:00:00+08:00',observations={'external_financial_loss':{'state':'supported','source_refs':['test:loss'],'available_at':'2025-05-23T00:00:00+08:00'},'profit_transfer_path':{'state':'contradicted','source_refs':['test:counterevidence'],'available_at':'2025-05-23T00:00:00+08:00'}})
assert contrary['candidates'][0]['status']=='candidate_with_counterevidence'
empty=retrieve_mechanisms(catalog,as_of=packet['cutoff'],observations={'country_japan':{'state':'supported','source_refs':['test:country'],'available_at':'2025-05-23T00:00:00+08:00'}})
assert empty['candidates']==[]
early=retrieve_mechanisms(catalog,as_of='2024-08-30T00:00:00+08:00',observations={'staple_price_rise':{'state':'supported','source_refs':['test:price'],'available_at':'2024-08-29T23:59:59+08:00'}})
assert [e['id'] for e in early['candidates'][0]['author_evidence']]==['E904d']
try:
    retrieve_mechanisms(catalog,as_of=packet['cutoff'],observations={'policy_ineffective':{'state':'supported','source_refs':['test:future'],'available_at':'2025-05-28T00:00:00+08:00'}})
except ValueError:
    pass
else:
    raise AssertionError('Future observation accepted')
save('checks.json',{'passed':['unknown_conditions_do_not_block_hypotheses','future_author_rules_excluded','past_versions_do_not_leak_later_evidence','counterevidence_returned_not_hidden','country_name_alone_does_not_trigger','financial_loss_not_promoted_to_profit_transfer_fact','future_observation_rejected'],'regression_candidates':['M1','M2','M3','M6']})
save('hypothesis_policy.json',{'claim_types':['source_reported_observation','author_hypothesis','model_hypothesis','externally_verified_claim'],'independent_axes':['作者原文与确信程度','材料支持的前提','模型连接的推理步骤','竞争解释与区分性观察'],'permission':'允许在缺少动机直接证据时提出大胆假说并作条件排序；未知不等于假，逻辑可行不等于已发生。','missing_bridge_policy':'注明连接依赖的假定和可观察后果；若多种解释都能产生同一现象，须说明优先哪种以及理由。','not_automatic':'检索相关度不决定最终解释排序；本次未调用模型生成或证明复现质量提升。'})
save('treasury_reference_search.json',{'user_description':'美债收益率异常→推断日本人砸盘','status':'exact_episode_not_located','reviewed_title_candidates':[222,326,352,434,485,486,535],'additional_search':'已暴露的908至1133区间129份字幕中，砸盘/收益率/抛售与前后20cue的日本共现，无命中。','excluded_reserved':[1022,1078],'not_claimed':'不能将用户回忆直接视为找到的原文，更未将日本卖出归因为已证实事件。','possible_inference_template':['在指定时间尺度定义预期与异常','比较宏观重定价与额外卖压','对可能卖方比较持仓能力、流动性需求、动机和时点','形成有归属标记的假说并说明区分条件'],'template_status':'一般推理结构示例，尚非作者规则','pending':'用户可提供期号/日期以定位原文；不阻塞检索实现。'})
print(json.dumps({'retrieved':[m['id'] for m in result['candidates']],'checks':7,'generation_experiment_run':False},ensure_ascii=False))
