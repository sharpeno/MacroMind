"""Freeze a memory / generation / recognition diagnostic on exposed EP1183."""
import copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'phase1/topic_mining';OUT=BASE/'memory_connection_001'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 if OUT.exists():raise SystemExit('Run already exists; preserve frozen version')
 (OUT/'inputs').mkdir(parents=True);(OUT/'outputs').mkdir()
 src=read(BASE/'retrieval_experiment_001/A_input.json')
 evidence={x['id']:x for x in read(BASE/'mechanism_transfer_002/historical_evidence.json')}
 specs=[('H1','EP520:E4',544,558),('H2','EP1016:E2',490,533),('H3','EP1182:buffer',423,487)]
 memories=[]
 for mid,eid,lo,hi in specs:
  e=evidence[eid];cues=[c for c in e['cues'] if lo<=c['cue']<=hi]
  assert cues and e['observed_on']<'2025-08-04'
  memories.append({'id':mid,'episode':e['episode'],'observed_on':e['observed_on'],'source':'mechanism_transfer_002/historical_evidence.json#'+eid,'cue_range':[lo,hi],'attribution':'作者此前的判断及假说，不是已核实世界事实；数字保留字幕原样','cues':cues})
 write(OUT/'historical_memory.json',memories)
 options=[
 {'id':'P','explanation':'撤职能够维持支持者忠诚；既有救助资源提供容错空间，因此先稳住政治基本盘、随后处理经济问题，仍可能是较好的策略。'},
 {'id':'Q','explanation':'撤职只能暂时转移责任；既然仍有救助资源，便有处理经济压力的替代选择。若只换人而局面恶化，领导责任反而更难推卸。'},
 {'id':'R','explanation':'撤职的主要问题是统计程序与信用，应优先修复数据独立性。救助资源属于另一项政策议题，不必进入对此次撤职的核心评价。'},
 {'id':'S','explanation':'大幅修订需要先查清失职责任；是否有救助资源不能代替统计问责。因此暂缓评价撤职好坏，等待审查结果再形成主要判断。'}]
 common='仅使用给定新闻和可选历史记忆，预测作者会如何分析当前标题问题。历史记忆是作者在当时说过的看法，不是事实裁定，也不是必须继续坚持的结论。不要联网、读取其他材料或用你自己的历史知识补事实。允许大胆但标注归属的假说。不提供通用机制清单；请自行选择联系。输出合法JSON：answers数组，每项含question_id、main_judgment、reasoning_chain（每条含claim、source_refs、type，type为input_restated或new_inference）、ranked_explanations、revision_conditions；另含memory_use（使用了哪些记忆及用途）、missing_materials。正文约600—900汉字。'
 for arm in ['A','B','C','D']:
  for rep in [1,2]:
   packet={'title':src['title'],'cutoff':src['cutoff'],'questions':[q for q in src['questions'] if q['id'] in ['Q1','Q3']],'news':src['news'],'historical_memory':[] if arm=='A' else memories[:2] if arm=='B' else memories,'instruction':common}
   if arm=='D':
    packet['candidate_explanations']=options if rep==1 else list(reversed(options))
    packet['instruction']+=' 本输入另给出若干候选解释。对Q1先预测作者最可能优先哪条，按ID排序并说明理由，可以拒绝全部；保留上述answers格式，另增candidate_ranking数组。这些选项不是事实或作者原话，不保证有唯一正确选项。'
   write(OUT/'inputs'/f'{arm}{rep}.json',packet)
 protocol={'status':'frozen_awaiting_authorization','objective':'区分历史背景不足、联系生成不足和解释排序偏差','target_episode':1183,'target_is_exposed':True,'arms':{'A':'固定新闻，无作者记忆','B':'同新闻＋520/1016跨事件历史原文','C':'B＋1182同事件前一日资源原文','D':'C＋固定竞争解释，仅测识别排序'},'replicates_per_arm':2,'contexts':'8 fresh no-history agents; same inherited model; one input per agent','scope':'聚焦Q1行为评价与Q3持续条件；不与此前全题覆盖分数比较','generation_inputs_exclude_target_subtitle':True,'recognition_options_target_informed':True,'dates':'沿用已核对的标题日期，历史材料均早于2025-08-04；不批量补日期','new_subtitles':0,'new_news':0,'sealed_materials':0,'active_catalog_changes':False,'rubric':{'memory_recall':'是否正确使用历史判断并保留时点/归属；不计作新联系','resource_restatement':'债务空间、短债承接、短期缓冲已直接给在H3；出现只算记忆利用','connection_generation':'仅评价A/B/C是否自行连接：有可用资源→存在处理经济压力的替代行动→只撤职不解决压力→若恶化则领导责任更难转移。记录完整/部分/未出现及引用位置，不奖励仅提到救助工具。','recognition':'D是否优先Q，且能说明资源与行动必要性、后续责任的关系；选中ID而无连接理由不算完整识别。P/R/S可能合理，不作世界真假判定。','author_refs':['retrieval_experiment_001:J06','retrieval_experiment_001:J07','retrieval_experiment_001:J08','retrieval_experiment_001:J09','retrieval_experiment_001:J10'],'interpretation':{'B_over_A':'跨事件历史记忆有帮助的局部证据','C_over_B_recall_only':'近事件记忆改善内容覆盖，尚未证明联系生成改善','C_connection_over_B':'对本案例而言补资源背景有助生成联系，不能推广到所有主题','D_over_C':'能识别但未自行生成，提示假说发现瓶颈；仍可能是选项提示效应','C_and_D_fail':'不能单归因缺记忆；也可能记忆不适配、解释偏好或评分重建不准'}},'limits':['目标和材料选择受已见答案影响，属于有利条件下的诊断','C含同事件前一日记忆，不是独立泛化','D明确含目标启发的解释选项，不是盲生成','两次重复只检查初步一致性，不估计可靠统计效应','评分父代理知晓条件','记忆长度随条件增加，没有等长安慰剂，不能完全分离内容和长度作用','选中的历史记忆不等于作者完整背景','缺失其他作者链不计本轮核心失败']}
 write(OUT/'protocol.json',protocol)
 checks={'historical_dates_before_target':all(m['observed_on']<'2025-08-04' for m in memories),'target_not_in_memory':all(m['episode']!=1183 for m in memories)}
 for rep in [1,2]:
  packets=[read(OUT/'inputs'/f'{a}{rep}.json') for a in 'ABCD']
  checks[f'common_news_questions_{rep}']=all(p['news']==packets[0]['news'] and p['questions']==packets[0]['questions'] for p in packets)
  checks[f'memory_nested_{rep}']=packets[1]['historical_memory']==packets[2]['historical_memory'][:2] and packets[2]['historical_memory']==packets[3]['historical_memory']
 assert all(checks.values());write(OUT/'checks.json',checks);print('8 inputs frozen; dated historical excerpts and recognition-only options separated.')
if __name__=='__main__':main()
