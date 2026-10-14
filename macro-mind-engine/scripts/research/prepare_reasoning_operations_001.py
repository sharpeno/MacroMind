"""Prepare and record an exposed-case diagnostic; never promote it to blind evaluation."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'phase1/topic_mining'
OUT=BASE/'reasoning_operations_001'
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 if OUT.exists(): raise SystemExit('Recorded diagnostic exists; create a new version instead')
 OUT.mkdir()
 operations=[
  {'id':'O1','name':'先拆问题，再寻找异常','action':'把标题中的政策、被点名者及结果分开；分别问为什么此时、为什么此对象、为什么采用这个动作。记录已知与未知，不用一个新闻自动解释所有问题。','sources':['retrieval_experiment_002:J01','retrieval_experiment_002:J06'],'status':'target_derived_candidate','boundary':'旧事重提本身不能证明恶意；新证据或一致执法可能解释时间和对象。'},
  {'id':'O2','name':'分开行动者、受益者和承担代价者','action':'至少区分个人、派别、机构、行业与国家；逐项说明谁能获得什么收益、谁有行动能力、谁承担成本。个人合理性不自动等于整体合理性。','sources':['mechanism_transfer_002:M7','retrieval_experiment_001:J02','retrieval_experiment_002:J03'],'status':'historical_structure_with_target_diagnostic','boundary':'受益不证明策划；主体和控制能力未知时保留为假说。'},
  {'id':'O3','name':'沿短期行动推到下一轮约束','action':'写明短期收益如何改变信用、对手组织、资源或责任归属，再判断这个变化是否反过来削弱最初收益。比较可行替代动作，不把一切强硬都叫反噬。','sources':['mechanism_transfer_002:M8','mechanism_transfer_002:M10','retrieval_experiment_001:J03','retrieval_experiment_001:J05','retrieval_experiment_001:J09'],'status':'historical_structure_with_target_diagnostic','boundary':'对手凝聚、资源存在和可用替代都需条件；不能由压力直接断言反噬已经发生。'},
  {'id':'O4','name':'让解释竞争，而非让检索顺序决定结论','action':'列出两到三条能回答同一个问题的解释，比较各自能解释哪些异常、额外假设和区分性证据；相关但回答不同问题的链并列保留。允许大胆动机假说，说明为何倾向它以及什么会改变倾向。','sources':['retrieval_experiment_001:J03','retrieval_experiment_002:J01','retrieval_experiment_002:J04','retrieval_experiment_002:J05'],'status':'model_reconstruction','boundary':'材料缺失不等于反证；没有观察到选择性时，不能自动把排外或派系斗争排首位。'},
  {'id':'O5','name':'区分事实、桥接假设和待查材料','action':'每条链列新闻编号、桥接假设与待查材料。未知前提可作条件分支，不能从作者答案补进事实栏；输出明确倾向，同时保留置信程度和适用范围。','sources':['retrieval_experiment_002:J02','retrieval_experiment_001:J10'],'status':'model_reconstruction','boundary':'没有直接动机证据不禁止推理；但不补造日期、具体数值、指控成立或作者原话。'}
 ]
 write(OUT/'operations.json',operations)
 prompt='尝试复现作者选择线索和形成判断的过程。\n'+'\n'.join(f"{o['id']} {o['name']}：{o['action']} 边界：{o['boundary']}" for o in operations)+'\n逐题输出：主判断；新闻依据；桥接假说；机制链；解释排序及理由；替代动作；改变判断的条件；材料缺口。不强制每题使用所有操作。'
 (OUT/'candidate_prompt.txt').write_text(prompt,encoding='utf-8')
 for episode,run in [(1183,'retrieval_experiment_001'),(1187,'retrieval_experiment_002')]:
  original=read(BASE/run/'A_input.json')
  write(OUT/f'input_{episode}.json',{'frozen_original_input':original,'candidate_operations':prompt,'usage':'exposed_diagnostic_only; not independent generation'})
 protocol={'status':'completed_exposed_diagnostic','date':'2026-10-10','objective':'检验问题拆分、利益层级及解释排序的候选操作；优先框架，不批量补日期','date_policy':{'priority':['video_title','corresponding_folder_details'],'missing':'按个案查看文件夹详细信息；仍缺时记录未知，不推定、不启动批量补齐','precision':'只有日期时不虚构发布时间；日内新闻边界另记'},'source_runs':['retrieval_experiment_001','retrieval_experiment_002'],'new_subtitles_read':0,'new_news_added':0,'sealed_groups_consumed':0,'generation':'主代理在看过作者判断后人工构造诊断输出；非独立子代理、非盲测、非随机重复实验','candidate_derived_from_targets':True,'active_catalog_changed':False,'knowledge_promotion':False,'rollback':'停用本目录候选提示即可；旧输入、答案、目录均保留。已暴露状态不能回退。','claim_limit':'以下是候选操作的可执行示范及边界诊断，不能据此宣称作者贴近度或泛化能力提高。'}
 write(OUT/'protocol.json',protocol)
 write(ROOT/'phase1/material_partition/workflow_policy.json',{'priority':'framework_extraction_and_testing','bulk_publication_date_backfill':False,'video_date_precedence':['title','corresponding_folder_details'],'date_missing_action':'仅当前选中案例按需查看详细信息；未知不推定','development_materials':'优先已有内容处理记录与回归案例','effective_date':'2026-10-10'})
 print(OUT)
if __name__=='__main__':main()
