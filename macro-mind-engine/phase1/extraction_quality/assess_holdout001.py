import json,hashlib
from pathlib import Path
ROOT=Path('G:/youhegaojian/macro-mind-engine');B=ROOT/'phase1/batch_pilot';O=ROOT/'phase1/extraction_quality/holdout_001'
def rd(p):return json.loads(p.read_bytes())
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
frozen=rd(O/'frozen_sample.json');assert hashlib.sha256((O/'frozen_sample.json').read_bytes()).hexdigest()==rd(O/'precheck_manifest.json')['sample_sha256']
judgments={
'EP001/C02':('NO_CLEAR_MISMATCH_FOUND','当前表述保留了美国加息的条件、宽松转收紧及短暂/持续两种路径。本次未发现明确失真；并非证明完整或正确。',None),
'EP002/C05':('POTENTIAL_STRENGTH_AND_ATTRIBUTION_LOSS','原话128是“全世界其他国家库存基本快见底”，原提取变成“可能不足”，强度有所降低。127提及官方测算，但片段未给可核验出处；应区分博主说法和已证实官方数据。','博主把中国开始补充库存解读为其他国家石油库存已接近见底的信号；原话提到“官方测算”，但本片段未提供可定位来源，该判断及测算归属尚未独立核实。'),
'EP003/C18':('POTENTIAL_CAUSAL_SCOPE_DRIFT','原话351–353强调政治人物不能主宰市场趋势，面对市场交易压力其立场受限；现有“制度与利益条件”引入了这段未明确说明的概括，遗漏具体约束机制。','博主认为，政治人物不能凭个人意愿主宰市场趋势；面对市场交易压力，他们的立场和政策选择会受到约束。他用“冲浪者而非浪潮制造者”来说明这一判断。'),
'EP004/C08':('POTENTIAL_CONDITION_LOSS','原话132–135是检查药效是否符合预期，不符合才修改候选物；“筛选→实验→修改”的线性概括可能让修改看起来是必经步骤。','博主描述先筛选潜在有用的化合物，再通过实验检验作用是否符合预期；若结果不符，则修改候选物并观察新效果，之后再筛出稳定方向。'),
'EP005/C21':('NO_CLEAR_MISMATCH_FOUND','原话402–410支持人口密度将小众需求累积成可维生职业；现有主张保留了这一机制。412的大城市吸引人口优势属进一步展开，本次不强制扩写。',None)
}
results=[];items=[]
for x in frozen['items']:
 rid=x['id'];ep,cid=rid.split('/');status,reason,proposed=judgments[rid];guard=rd(O/(ep+'.guard.json'))
 results.append({'id':rid,'guard_status':guard['status'],'guard_review_required':guard['review_required'],'claim_marked_unreviewed':cid in guard['unreviewed_ids'],'assistant_status':status,'reason':reason,'proposed_text':proposed,'human_status':'PENDING','truth_verified':False})
 summary=['冻结的原提取：'+x['claim'][2],'助手复核意见：'+reason]
 if proposed:summary.append('候选修订（尚未采用）：'+proposed)
 items.append({'id':'H01/'+rid,'episode':ep,'kind':'留出校准','title':rid+' · '+('请核对疑似偏差' if proposed else '请核对是否确实无须修改'),'review_summary':summary,'prompt':'请对照原字幕判断；可以保留原提取，也可以采用候选修订或提出不同修改。助手意见可能有误，不是标准答案。只审转述是否忠实，不要求核实观点在现实中正确。','evidence':x['quotes'],'related':[rid],'priority':True,'has_proposal':bool(proposed),'detail':{'取样边界':'未进入前两轮审核片段，也没有对应的专门措辞规则；基线指纹已知，非模型从未见过的材料。','上下文':x['context'],'规则检查':guard['status'],'独立性':'同一助手再次核对，未做盲评；等待用户校准。'}})
wr(O/'assistant_assessment.json',results)
wr(O/'comparison.json',{'sample_size':5,'episode_count':5,'prior_review_cue_overlap':0,'specific_rule_facet_overlap':0,'guard_baseline_passes':5,'assistant_no_clear_mismatch':2,'assistant_potential_mismatch':3,'human_confirmed_errors':None,'precision_recall':'NOT_MEASURED; no human ground truth and no paired extraction experiment','improvement_proven':False,'conclusion':'Known-error guards do not diagnose fresh semantic mismatch in unchanged baseline statements. All five remain unreviewed by guard; no false semantic acceptance emitted.'})
d={'version':1,'dataset':hashlib.sha256(json.dumps(items,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'items':items,'original_run':str(B/'run_003'),'videos':rd(B/'run_003/../review_round_002/review_data.json')['videos']};wr(O/'review_data.json',d)
t=(B/'review_round_002_delta/template.html').read_text(encoding='utf-8').replace('第二轮修订确认','留出样本校准').replace('第二轮修订 / 2项','未审片段检验 / 5项').replace('本轮2项','本轮5项').replace('这里只确认第二轮意见落实后的2组新增或拆分内容。','这里是5条未参与前两轮审核的样本。助手发现3处疑似偏差，另2条暂未发现明确问题，请你校准这些判断。').replace('review_round_002_delta/exports','holdout_001/exports').replace('MacroMind_round002delta_','MacroMind_holdout001_').replace("const optionSets={","const optionSets={\n'留出校准':[['keep_original','原提取可保留'],['adopt_proposal','采用展示的候选修订'],['change','需要另作修改（请填写）'],['unsure','无法确认']],")
# No proposed text means the adopt option must not be offered.
t=t.replace("function options(item){return [['pending','尚未判定'],...(optionSets[item.kind]||defaultOptions)];}", "function options(item){return [['pending','尚未判定'],...(optionSets[item.kind]||defaultOptions).filter(x=>x[0]!=='adopt_proposal'||item.has_proposal)];}")
# Inspect options implementation before rendering replacement below.
(O/'template.html').write_text(t,encoding='utf-8');(O/'HUMAN_REVIEW.html').write_text(t.replace('__DATA__',json.dumps(d,ensure_ascii=False).replace('<','\\u003c')),encoding='utf-8')
(B/'human_reviews/holdout_001/exports').mkdir(parents=True,exist_ok=True)
wr(O/'progress.json',{'stage':'GUARD_COMPARISON_AND_ASSISTANT_ASSESSMENT_COMPLETE','completed':['Five samples frozen before detailed inspection','Five real guard CLI runs saved','Assistant second-pass findings saved without rewriting canonical data'],'unfinished':['UI validation','Human calibration of five assistant assessments','No improvement or population accuracy conclusion yet'],'next_step':'Validate calibration UI, then obtain human ground truth'})
print('5 frozen checks; 3 potential semantic mismatches, 2 no-clear-mismatch; human labels pending.')
