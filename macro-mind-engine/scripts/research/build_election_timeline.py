"""Build an evidence-linked election judgment timeline; retrospection never backfills observations."""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'macro-mind-engine/phase1/topic_mining/election_timeline_001'
RESERVED={479,480,482,484,493,495,496,509,601,783,1022,1078,1208,1283,1458}
SPECS=[
(520,[(405,435),(544,583)],'biden_advantage_conditional','倾向拜登优势，若基层利益分配格局延续，特朗普不利。','较强但有条件','拜登通过行政资源维护基本盘；条件是相关迹象继续发展。','没有无条件民主党必胜断言。'),
(731,[(234,290)],'biden_advantage_strong_conditional','若拜登身体不出状况，特朗普毫无胜算。','强断言，明确前提','国会山事件在作者看来妨碍特朗普获得其他政治力量信任；拜登身体是主要变数。','原文把国会山事件年份说成2020，保留原句，不视为已验证事实。'),
(843,[(8,39),(77,108),(160,187),(389,405)],'biden_logic_retained_after_negative_signal','承认拜登辩论表现差，但认为可转为逆境叙事，特朗普仍有先天劣势。','维持原解释，未在片段中给胜率','弱势形象、资源分配和目标选民构成仍可支撑拜登；新闻转述同时出现特朗普交易升温。','市场或银行对特朗普胜选的预期不等于作者改判；不是所有坏消息都会改变主判断。'),
(859,[(565,627)],'biden_advantage_but_uncertain','枪击事件之后仍说胜负难料、优势在拜登；特朗普需要具体施政方案。','从毫无胜算变为存在竞争但偏拜登；强度变化属跨片段重建','若能向中间选民提供有效方案，作者表示会改判；仍以拜登身体不出问题为条件。','不能把枪击事件单独标成已经导致作者转向特朗普。'),
(867,[(400,450),(457,484)],'harris_vulnerability_not_exact_win_probability','换为哈里斯后担忧其竞选能力、党内服从和组织凝聚，提出支持不足会分裂的场景。','明显负面，所读窗口无明确总胜率','新候选人面临不同的期待、资历与党内山头关系；原拜登优势不能直接继承。','这是方向变化的早期证据，不足以定位首次宣布特朗普必胜的时刻。'),
(882,[(22,31),(128,158),(545,575)],'trump_advantage_harris_partial_recovery','作者给哈里斯选择沃尔兹加分，但认为远未扭转弱势。','作者口述概率含转写和口径歧义，保持原文','拜登退选改变摇摆州匹配；副手补强根基，但最终仍需施政方案。','cue565-569同时出现10%、20%、二三成且旧值转写异常，不规范化为精确数值。'),
(912,[(170,176),(584,587),(650,679)],'retrospective_transition_explanation','当前称特朗普势头上升，同时明确回顾枪击未足以改判、拜登退选后才翻盘。','当前方向偏特朗普；回顾对事件作用有强断言','枪击改变作者所说的底层逻辑，但对手仍是拜登时不足以翻转；候选人替换是其回顾中的关键条件。','这是9月6日的回顾证据，不能伪造为7月当日的原话或精确改判时间。')]

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 wanted={s[0] for s in SPECS};assert not wanted&RESERVED
 folders={}
 for folder in (ROOT/'有何高见9527视频集').glob('*/*'):
  m=re.search(r'第(\d+)期',folder.name)
  if m and int(m[1]) in wanted|{862,973}:folders[int(m[1])]=folder
 observations=[]
 for ep,ranges,state,judgment,confidence,reason,caution in SPECS:
  folder=folders[ep];intro=(folder/'视频简介.txt').read_text(encoding='utf-8-sig')
  title=intro.splitlines()[0].removeprefix('标题：');d=re.search(r'(?<!\d)(20\d{6})(?!\d)',title)[1]
  day=f'{d[:4]}-{d[4:6]}-{d[6:]}'
  path=next(folder.glob('*.srt'));cues={}
  for b in re.split(r'\n\s*\n',path.read_text(encoding='utf-8-sig')):
   lines=b.strip().splitlines()
   if len(lines)>2 and lines[0].isdigit():cues[int(lines[0])]={'cue':int(lines[0]),'time':lines[1],'text':'\n'.join(lines[2:])}
  ev=[{'id':f'EP{ep}:T{i+1}','cue_range':[lo,hi],'cues':[cues[k] for k in range(lo,hi+1)]} for i,(lo,hi) in enumerate(ranges)]
  observations.append({'id':f'O{ep}','episode':ep,'observation_date':day,'date_basis':'title','date_precision':'day','title_date_is_verified_publication_time':False,'title':title,'subtitle':str(path.relative_to(ROOT)),'judgment_target':'2024美国总统选举候选人胜算','state':state,'judgment':judgment,'confidence_description':confidence,'premise_or_mechanism':reason,'caution':caution,'evidence':ev,'attribution':'model_reconstruction_with_verbatim_author_evidence','external_fact_validation':'not_performed','retrospective_part':ep==912})
 transitions=[
 {'id':'T1','from':'O520','to':'O731','type':'reinforcement_or_explicit_condition','description':'观察到早期拜登优势论；3月把身体条件和特朗普政治污点更明确地连到强判断。不能证明中间从未变化。','evidence':['EP520:T2','EP731:T1']},
 {'id':'T2','from':'O731','to':'O843','type':'negative_signal_absorbed','description':'辩论表现差没有在所读片段中推翻原框架，作者将它解释为可利用的弱势叙事。','reported_event':'拜登辩论表现不佳','event_time_exact':None,'event_known_by_author_no_later_than':'2024-06-29','evidence':['EP843:T1','EP843:T2','EP843:T3']},
 {'id':'T3','from':'O843','to':'O859','type':'confidence_softening_without_direction_flip','description':'枪击后仍偏拜登；胜负难料与早期毫无胜算存在强度差别，但不是已经转向特朗普。','reported_event':'特朗普被枪击','event_time_exact':None,'event_known_by_author_no_later_than':'2024-07-15','evidence':['EP859:T1','EP912:T3']},
 {'id':'T4','from':'O859','to':'O867','type':'candidate_replacement_and_premise_change','description':'对手从拜登换为哈里斯，作者重新判断候选人能力和党内组织关系。首次改判时刻未知。','reported_event':'拜登退选、哈里斯接替竞选','event_time_exact':None,'event_known_by_author_no_later_than':'2024-07-23','evidence':['EP867:T1','EP867:T2','EP882:T2','EP912:T3']},
 {'id':'T5','from':'O867','to':'O882','type':'partial_recovery_not_reversal','description':'选择沃尔兹提高哈里斯胜算，但作者仍不认为局势已扭转。','reported_event':'哈里斯选择沃尔兹为竞选搭档','event_time_exact':None,'event_known_by_author_no_later_than':'2024-08-07','evidence':['EP882:T3']},
 {'id':'T6','from':'O882','to':'O912','type':'retrospective_explanation_and_current_trend','description':'9月回顾将枪击与退选区分；可支持改判机制，不能回填7月某日的结论。当前对焦灼及特朗普势头上升的判断须同时保留。','evidence':['EP912:T1','EP912:T2','EP912:T3']}
 ]
 gaps=[]
 for ep in [862,973]:
  folder=folders.get(ep)
  gaps.append({'episode':ep,'status':'subtitle_missing' if folder and not list(folder.glob('*.srt')) else 'not_used','restriction':'简介标题不能替代作者正文判断；973属结果揭晓阶段，不能计为事前预测。'})
 result={'topic':'2024美国大选：作者判断随时间的变化','status':'first_evidence_linked_timeline','observations':observations,'transitions':transitions,'main_finding':'原判断对候选人身份、身体条件和组织支持有依赖；重大事件不必立即翻转，候选人替换可能使旧前提失效。','observed_switch_bracket':{'last_sampled_explicit_biden_advantage':'2024-07-15','first_sampled_explicit_harris_low_win_chance':'2024-08-07','intermediate_negative_harris_assessment':'2024-07-23','exact_first_switch':'unknown','warning':'抽样区间，不等于完整语料确认的首次转折；不可据此虚构当日改判。'},'gaps':gaps,'probability_policy':'保留口述与转写原文，不把十拿九稳或歧义数值转换成校准概率。','time_policy':{'observation_date':'标题日期优先；本轮无日内时间','event_time':'与论述时间分离；尚未外部核实的事件不填精确发生/公开时间','retrospective':'回顾语句只能从回顾发表时可见，不向过去补写','database_separation':'本文件是作者判断层，不把字幕中的事件叙述写入外部新闻事实库'},'exposure':{'selected_training_episodes':sorted(wanted),'other_subtitle_windows_scanned':[854,892,935],'reserved_not_read':sorted(RESERVED)},'limitations':['仅相关窗口抽样，不是全量逐日追踪','作者回顾可能存在事后重构；保留当时原话独立对照','本轮没有外部验证选举新闻、健康说法或法律事件','首次转折确切位置及中间缺失字幕待补，不用后来结果填空']}
 refs={e['id'] for o in observations for e in o['evidence']}
 assert all(set(t['evidence'])<=refs for t in transitions)
 assert observations==sorted(observations,key=lambda o:o['observation_date'])
 (OUT/'timeline.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
 print(f'{len(observations)} dated observations, {len(transitions)} transitions; source references and chronology passed')

if __name__=='__main__':main()
