"""Freeze a task-contract comparison on exposed rice case 1134."""
import json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'phase1/topic_mining';OUT=BASE/'author_contract_experiment_001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 if OUT.exists():raise SystemExit('Preserve existing run')
 (OUT/'inputs').mkdir(parents=True);(OUT/'outputs').mkdir()
 news=read(BASE/'title_aligned_001/A_input.json');evidence={e['id']:e for e in read(BASE/'rice_lineage_001/evidence.json')}
 memory=[]
 for mid,eid in [('H1','E904c'),('H2','E907b'),('H3','E907g')]:
  e=evidence[eid];memory.append({'id':mid,'episode':e['episode'],'observed_on':e['date'],'source':'rice_lineage_001/evidence.json#'+eid,'cue_range':e['cue_range'],'cues':e['cues'],'attribution':'历史作者原文；不等于外部事实核验。'})
 old=read(BASE/'memory_connection_001/inputs/C1.json')['instruction']
 new=(BASE/'author_perspective_audit_001/candidate_task_contract.txt').read_text(encoding='utf-8')
 # Same length budget for both; changed schema is part of the contract treatment.
 old=old.replace('正文约600—900汉字。','正文约1000—1400汉字。')
 new+='\n正文约1000—1400汉字。'
 for arm,instruction in [('A',old),('B',new)]:
  for rep in [1,2]:write(OUT/'inputs'/f'{arm}{rep}.json',{'title':'日本米荒究竟是天灾还是人祸？小泉进次郎再次开仓放粮能否抑制米价？20250527','cutoff':news['cutoff'],'questions':news['questions'],'news':news['news'],'historical_memory':memory,'instruction':instruction})
 protocol={'status':'frozen_awaiting_authorization','target':1134,'design':'2 arms x 2 independent fresh contexts; inherited model, no override','treatment':'仅更换任务契约，含归属说明及输出字段；不是单句提示效应','arms':{'A':'旧预测作者任务与逐题结构','B':'作者信念/预测把握/外部事实分离，按待解释对象排序'},'common_budget':'1000—1400汉字；与先前实验不作分数直比','rubric':{'P1_historical_confidence':'H1须保留自称猜测与强倾向并存，H2为支持者获益的强动机归因；不能因外部未核实自动变成作者无明确看法，也不能变成已证实事实。语义达成即可，不以字段出现评分。','P2_attribution':'分别表达作者当时相信、当前预测的把握和输入证据状态；不以更多字段直接判优。','P3_update':'当前投放/渠道变化不能写成当年仍拒绝投放；延续或修正历史条件要指出当期依据，不能以缺外部核验代替作者改判证据。','P4_comparable_ranking':'每组竞争解释回答同一对象；成因、政策动机与降价效果不得互相排先后。','secondary':'标题两问是否都有明确判断，是否因格式负担只做归属登记、不回答问题。'},'primary_reference_scope':'历史原文和固定新闻；本轮不要求猜中1134新增的海外债券损失链','no_target_answer_in_inputs':True,'no_preference_cards':True,'no_cross_question_prompt':True,'new_news':0,'new_subtitles':0,'sealed_groups':0,'active_framework_changed':False,'stop_rule':'完成4份即评价；不追加生成或用本例改提示后重算成绩','limits':['已暴露旧案例，准备者知晓作者材料','每组两次，非可靠统计效应','父代理评分知晓组别','输出结构是处理的一部分，需按语义比较，不能按字段打分','历史记忆为同一长期话题，非未见迁移','较大时间间隔不能假定旧信念无条件延续','本轮验证任务归属与排序可比性，不证明主判断忠实度整体提升']}
 write(OUT/'protocol.json',protocol)
 checks={'history_before_cutoff':all(m['observed_on']<'2025-05-27' for m in memory),'target_not_in_memory':all(m['episode']!=1134 for m in memory)}
 for rep in [1,2]:
  a=read(OUT/'inputs'/f'A{rep}.json');b=read(OUT/'inputs'/f'B{rep}.json');a.pop('instruction');b.pop('instruction');checks[f'common_input_{rep}']=a==b
 assert all(checks.values());write(OUT/'input_checks.json',checks);print('4 inputs frozen; shared evidence and historical dates checked.')
if __name__=='__main__':main()
