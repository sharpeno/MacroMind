"""Audit attribution and ranking task boundaries without another generation round."""
import json,html
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'phase1/topic_mining';OUT=BASE/'author_perspective_audit_001'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 if OUT.exists():raise SystemExit('Preserve recorded audit; use new version')
 OUT.mkdir()
 original=read(BASE/'memory_connection_002/inputs/B1.json')
 output=read(BASE/'memory_connection_002/outputs/B2.json')
 a1=read(BASE/'memory_connection_002/outputs/A1.json')
 cases=read(BASE/'explanation_selection_001/cases.json')
 findings=[
 {'id':'F1','finding':'作者信念与外部事实状态在输出中混用','evidence':[{'source':'memory_connection_002/inputs/B1.json#/historical_memory/2','quote':'他来救市的话 / 弹药是充足的','cue_range':[450,451]},{'source':'memory_connection_002/outputs/B2.json#/answers/1/main_judgment','quote':output['answers'][1]['main_judgment']}],'interpretation':'历史原文对资源持明确看法；输出将当前是否具备资源降为待验证条件，却未单独记录作者当时的信念及是否存在更新证据。','causal_status':'观察到表达混用，不证明由某一句提示单独造成；历史信念也不能无条件永久沿用'},
 {'id':'F2','finding':'部分排序混合了不同待解释对象','evidence':[{'source':'memory_connection_002/outputs/A1.json#/answers/0/ranked_explanations','quote':a1['answers'][0]['ranked_explanations']}],'interpretation':'统计修订原因和解雇动机不能在同一解释竞赛中直接排先后。应先指定解释对象，再在对象内部比较。','causal_status':'输出结构问题可直接观察；对忠实度影响尚未单独验证'},
 {'id':'F3','finding':'当前任务未分别要求作者确信、预测把握和事实核验状态','evidence':[{'source':'memory_connection_002/inputs/B1.json#/instruction','quote':original['instruction']}],'interpretation':'主判断容易混合作者可能相信什么、模型预测得是否可靠以及现实是否成立；谨慎地标注事实，不应自动把作者强判断改弱。','causal_status':'字段与措辞存在歧义；候选契约修复尚未经过生成对照'},
 {'id':'F4','finding':'历史选择偏好有边界，不能改成政治解释总优先','evidence':[{'source':'explanation_selection_001/cases.json','episodes':[520,798,989,911,1016,1056]}],'interpretation':'作者既比较可归功收益，也允许职责解释妥协、承认真实失败及现实约束。缺的是带条件的解释比较，不是固定政治立场。','causal_status':'对六个目的抽样旧案例的归纳，非总体规律'}]
 write(OUT/'findings.json',findings)
 cards=[]
 for c in cases:
  cards.append({'episode':c['episode'],'observed_on':c['analysis_date'],'trigger':c['cue'],'premise':c['premise'],'preferred_explanation':c['mechanism'],'competing_explanation':c['alternative'],'selection_reason':c['ranking'],'boundary':c['boundary'],'author_confidence':c['confidence'],'source':'explanation_selection_001/cases.json','evidence_ids':[e['id'] for e in c['evidence']],'status':'historical_case_specific_not_universal_rule'})
 write(OUT/'preference_evidence.json',cards)
 prompt='''任务是预测该作者在目标时点会如何分析，不是把模型自己的最佳判断署到作者名下。
先区分三个层次：
1. 历史作者信念：记录原文日期、对象、适用条件及作者当时的确信程度。未获外部核实不等于作者没有相信；过往相信也不等于当前必然继续相信。
2. 当前作者判断的模型预测：依据历史信念与当期材料，说明哪些可能延续、哪些应更新、哪些无法判断。预测须标为模型重建，不能伪称作者已经说过。
3. 外部事实状态：单独记录输入直接支持、仅为作者主张或模型推断、仍未知等状态。本任务不联网，不把未核验写成已验证，也不把外部未知直接改写为作者低确信。
排序时先写明待解释对象。行为动机、数据形成原因、政策后果等不同对象分别比较；只有回答同一问题的解释才直接竞争。若材料不足以复原作者偏好，说明不足，不用模型自身偏好填补。既往解释不得固定压过新信息；如提出更新，引用造成更新的材料或明确写无直接更新证据。
允许作者预测持强烈倾向或包含错误，但须准确标注来源和条件。作者确信程度、模型对复现准确性的把握、世界事实可信程度分开表达。不得为表现大胆而编造立场。
仍仅使用给定标题、日期、新闻和历史记忆。不要读取目标字幕或其他答案。
输出JSON：author_state数组（belief、source_refs、observed_on、conditions、author_confidence、current_use及理由）；answers数组（question_id、predicted_author_judgment、predicted_author_confidence、reconstruction_confidence、reasoning_chain、explanation_comparisons）；每个explanation_comparisons含explanandum与ranked_paths，每条路径含claim、support_refs、preference_reason、boundary；另列external_evidence_notes与missing_materials。没有依据的作者确信标unknown。'''
 (OUT/'candidate_task_contract.txt').write_text(prompt,encoding='utf-8')
 schema={'status':'candidate_not_active','independent_confidence_fields':['author_confidence','predicted_author_confidence','reconstruction_confidence'],'evidence_status_location':'external_evidence_notes','ranking_unit':'explanandum','historical_belief_update':'current_use: retained_conditionally / revised_with_evidence / unresolved','do_not':'把事实未知直接当成作者无判断；把没有新信息当成历史观点永远正确；把不同解释对象混排'}
 write(OUT/'contract.json',schema)
 plan={'status':'prepared_not_executed','stop_rule_respected':'不再对1183追加生成，也不改写旧成绩','next_test':'从已暴露的其他案例选择有明确历史信念与确信程度的材料，固定同一记忆和新闻，只比较旧任务契约与新契约；暂不同时注入偏好卡或新增跨题提示。','primary_endpoints':['能否保留作者有出处的确信程度，同时将外部未核验单列','有更新判断时是否指出新证据或明确标记为重建不确定','是否只在同一待解释对象内比较路径'],'separate_later_question':'任务契约修复与偏好卡效应不能混在同轮归因；先测归属表达，再决定是否测试偏好卡。','human_review':'只提交严重归属冲突与框架方向问题，不扩大逐条全量审阅','generated_answers':0,'new_subtitles':0,'active_framework_changed':False}
 write(OUT/'next_test.json',plan)
 checks={'six_historical_cards':len(cards)==6,'every_card_has_evidence_and_boundary':all(c['evidence_ids'] and c['boundary'] for c in cards),'contract_separates_confidence_and_external_notes':all(k in prompt for k in ['author_confidence','reconstruction_confidence','external_evidence_notes','explanandum']),'contract_contains_no_target_specific_answer':all(x not in prompt for x in ['1183','撤职','救市','特朗普']),'no_generation_claim':plan['generated_answers']==0}
 assert all(checks.values());write(OUT/'checks.json',checks)
 def block(x):return '<pre>'+html.escape(json.dumps(x,ensure_ascii=False,indent=2))+'</pre>'
 page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>作者视角与解释排序审查</title><style>body{max-width:1100px;margin:30px auto;padding:0 20px;font:16px/1.7 system-ui,"Microsoft YaHei",sans-serif;color:#183d3d;background:#f5f8f7}section,details{padding:18px;background:white;border:1px solid #d5e2df;border-radius:10px;margin:16px 0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px/1.7 system-ui}summary{cursor:pointer;font-weight:bold}.note{padding:14px;background:#fff2d7}</style><h1>作者视角与解释排序审查</h1><p class="note">本轮仅审查已有记录并准备候选契约，没有运行新生成实验，未证明修订能提升效果。</p>'''
 for f in findings:page+='<section><h2>'+html.escape(f['finding'])+'</h2>'+block(f)+'</section>'
 page+='<details><summary>六个历史选择依据与边界</summary>'+block(cards)+'</details><details><summary>候选任务契约</summary><pre>'+html.escape(prompt)+'</pre></details><section>'+block(plan)+'</section></html>'
 (OUT/'REVIEW.html').write_text(page,encoding='utf-8');print('Audit saved: 4 findings, 6 historical cards, candidate contract; 5 checks passed.')
if __name__=='__main__':main()
