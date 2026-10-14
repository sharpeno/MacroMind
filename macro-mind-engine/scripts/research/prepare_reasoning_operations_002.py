"""Freeze paired inputs before independent execution; no answer keys in generation packets."""
import copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'phase1/topic_mining'; OLD=BASE/'reasoning_operations_001'; OUT=BASE/'reasoning_operations_002'
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 if OUT.exists():raise SystemExit('Run exists; do not overwrite')
 (OUT/'inputs').mkdir(parents=True);(OUT/'outputs').mkdir()
 originals={ep:read(OLD/f'input_{ep}.json')['frozen_original_input'] for ep in (1183,1187)}
 candidate=(OLD/'candidate_prompt.txt').read_text(encoding='utf-8')
 variants={f'base_{ep}':copy.deepcopy(d) for ep,d in originals.items()}
 replacements={
 'CF1':(1183,'N2','【合成反事实，非历史新闻】就业报告后局长被撤职。撤职依据是一份早于报告完成的独立审查，发现明确违规，同类负责人一律追责。违规的具体性质未给出，不能自动当作已证实蓄意伪造就业数据。'),
 'CF2':(1183,'N2',originals[1183]['news'][1]['summary']+'【合成反事实补充，非历史事实】公众能独立复核统计流程，后续数据可信度没有下降。此项作为本情境给定前提。'),
 'CF3':(1187,'N2','【合成反事实，非历史新闻】特朗普要求英特尔CEO陈立武辞职；当前利益冲突指控有新的独立证据，同类人一致受到追责。英特尔仍处于经营困难中，没有CEO已辞职的事实。'),
 'CF4':(1187,'N2','【合成反事实，非历史新闻】特朗普要求英特尔CEO陈立武辞职。指控只涉及多年前普遍存在的行为，只有少数对象在没有新证据时被追究；追究对象的完整分布与选择标准未知。英特尔仍处于经营困难中，没有CEO已辞职的事实。'),
 'CF5':(1187,'N1','【合成反事实，非历史新闻】特朗普称拟对进口半导体征收约100%关税；在美国投资或制造也不获得任何豁免。讲话尚不是正式公告，适用范围仍不清楚，与苹果新增1000亿美元美国投入的宣布同时进行。')}
 for name,(ep,nid,summary) in replacements.items():
  d=copy.deepcopy(originals[ep]);d['scenario']='synthetic_counterfactual_not_historical';d['news']=[{'id':n['id'],'summary':summary,'classification':'synthetic_counterfactual'} if n['id']==nid else n for n in d['news']];variants[name]=d
 d=copy.deepcopy(originals[1187]);d['news']=list(reversed(d['news']));variants['CF6']=d
 common='只读取本输入，不读取其他文件、字幕或作者答案，不联网。仅按给定材料逐题分析，允许大胆但明确标注的动机假说。输出中文 JSON：answers 数组，每项含 question_id、main_judgment、news_refs、reasoning_chain、ranked_explanations（每项 explanation 与 reason）、revision_conditions、missing_materials。总正文约900—1200汉字。不输出评分或自评。合成反事实覆盖被替换的新闻前提，不是实际历史，也不要用历史记忆纠正它。'
 for name,d in variants.items():
  for arm in ('A','B'):
   packet={'title':d['title'],'questions':d['questions'],'cutoff':d['cutoff'],'news':d['news'],'scenario':d.get('scenario','historical_input'),'instruction':common,'analysis_guidance':d['instruction']+(('\n'+candidate) if arm=='B' else '')}
   write(OUT/'inputs'/f'{name}_{arm}.json',packet)
 protocol={'status':'inputs_frozen_awaiting_agent_authorization','design':'2 historical cases + 6 probes, paired A/B, 16 separate no-history generation contexts; one sample each','arms':{'A':'original ordinary instruction, no mechanism package','B':'same instruction plus candidate operations'},'only_arm_difference':'analysis_guidance candidate addition','common_output_format':True,'candidate_target_derived':True,'evaluation':'exposed regression and synthetic premise sensitivity; not unseen generalization','new_news':0,'new_subtitles':0,'within_run_updates':False,'candidate_promotion':False,'counterfactual_expectations':read(OLD/'counterfactual_probes.json'),'grading':'按预定探针检查方向与边界；原案例比较问题拆分、主判断和解释排序，缺材料另列；不合成准确率。评分者已知组别。','limits':['single_generation_per_cell','parent_evaluator_unblinded','candidate_developed_on_these_cases','counterfactuals_are_synthetic'],'date_policy':'标题优先，否则查看对应文件夹详细信息；本轮使用原冻结日期，不批量补齐'}
 write(OUT/'protocol.json',protocol)
 checks={}
 for name in variants:
  a=read(OUT/'inputs'/f'{name}_A.json');b=read(OUT/'inputs'/f'{name}_B.json');a.pop('analysis_guidance');b.pop('analysis_guidance');checks[name+'_paired_inputs_equal']=a==b
 checks['CF6_only_order_changed']=sorted(read(OUT/'inputs/CF6_A.json')['news'],key=lambda n:n['id'])==sorted(read(OUT/'inputs/base_1187_A.json')['news'],key=lambda n:n['id'])
 assert all(checks.values());write(OUT/'input_checks.json',checks)
 print('Frozen 16 inputs; 9 paired/order checks passed.')
if __name__=='__main__':main()
