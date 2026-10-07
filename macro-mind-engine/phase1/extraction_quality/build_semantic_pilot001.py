import sys,json,hashlib
from pathlib import Path
ROOT=Path('G:/youhegaojian/macro-mind-engine');sys.path.insert(0,str(ROOT/'src'))
from macromind.quality.annotations import digest
from macromind.quality.semantic_review import validate_packet
O=ROOT/'phase1/extraction_quality/semantic_pilot_001';B=ROOT/'phase1/batch_pilot'
def rd(p):return json.loads(p.read_bytes())
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
f=rd(O/'frozen_sample.json');assert hashlib.sha256((O/'frozen_sample.json').read_bytes()).hexdigest()==rd(O/'freeze_manifest.json')['frozen_sample_sha256']
def dim(text,cues,status='addressed'):return {'status':status,'assessment':text,'cue_ids':cues}
analyses={
'EP002/C16':{
 'speaker_role':dim('博主假设央行负责人接下来可能如何讲话，不是已发表的央行声明。',[396,397,399,400]),
 'modality':dim('有可能、如果出现；是条件性推演，非确定政策。',[399,400]),
 'conditions':dim('须提前准备plan B；可能通过证明独立性后在合适节点调整解释与政策组合。',[392,396]),
 'time_scope':dim('接下来可能宣布，具体时间节点未确定。',[396,399,400]),
 'objects':dim('假想讲话针对美联储及美国通胀、增长与信用问题，不泛化为所有央行。',[395,397]),
 'assumptions':dim('博主假定政策制定者可能准备纠错手段；没有证明现实中已形成该方案。',[390,392,396]),
 'reasoning_relation':dim('先用领导纠错的类比讲备用方案，再展开一段假想政策表述。',[389,390,396,397,398,399]),
 'alternatives':dim('有准备的引导纠错，对比没有plan B时随市场被动行动；货币加财政是其假想方案内容。',[392,393,397]),
 'external_evidence':dim('片段转述人名和讲话但未给可定位文件，不能作为实际政策发布证据。',[393,394,399,400],'unresolved')},
'EP003/C16':{
 'speaker_role':dim('博主强调是自己的看法，并声明不作市场预测；不等于说法没有预测性内容。',[318,319,320]),
 'modality':dim('可能出现、个人看法，保留猜想性质。',[320,321,322]),
 'conditions':dim('原市场题材破裂，但支撑题材的期待未变，且美国市场不再相信该叙事时，新市场可能承接。',[327,328,330,331,332,333]),
 'time_scope':dim('本段未给具体兑现时点。',[],'not_in_excerpt'),
 'objects':dim('谈AI/AGI题材、美国市场和新的承接市场；没有在本片段给出确定目标市场。',[328,331,332,333]),
 'assumptions':dim('AI相关期待仍存在，是博主提出承接猜想的前提。',[327,328,330,331]),
 'reasoning_relation':dim('以平衡效应和民谣类比引出不同市场间承接的猜想，并非证实的因果规律。',[324,325,326,332,333]),
 'alternatives':dim('本段没有系统列出承接失败或其他情景。',[],'not_in_excerpt'),
 'external_evidence':dim('本段未提供资金实际转移或新市场承接的数据。',[],'not_in_excerpt')},
'EP005/C20':{
 'speaker_role':dim('博主对城市发展机制的解释。',[369,370,388]),
 'modality':dim('前段说可能，末段强调配套的重要性；当前摘要没有将其写成客观定律。',[370,388]),
 'conditions':dim('如果有需求可以修路改善交通，基础设施投入降低物流成本是解释背景。',[380,383,384]),
 'time_scope':dim('过去形成机制与现在、未来发展潜力比较，不存在精确时间承诺。',[369,370,385,386]),
 'objects':dim('比较城市硬件配套和交通条件，未涉及具体城市价格或投资回报预测。',[382,385,386,387,388]),
 'assumptions':dim('博主认为追加道路的费用相对可承受；这不是独立验证的工程成本结论。',[383]),
 'reasoning_relation':dim('对比自然形成的交通优势与可建设的配套条件，解释竞争优势变化。',[369,370,380,383,388]),
 'alternatives':dim('原交通位置与新建配套是比较维度，不是二者完全互斥；当前降低依赖的表述没有写成不需要交通。',[369,380,382,384]),
 'external_evidence':dim('片段没有具体成本表、独立比较数据或外部来源。',[],'not_in_excerpt')}
}
proposals={
'EP002/C16':'博主用假想的央行讲话说明提前准备纠错方案的重要性：他设想在适当时点提出货币与财政共同应对通胀、低增长和信用压力，并可能接受较长时间或更强的加息。这是其对可能政策路径的推演，并非央行已发表的讲话。',
'EP003/C16':'博主提出一种猜想：如果美国市场的AI题材受挫，但相关期待仍未消失，新市场可能承接这部分热情；本段未明确承接市场及时间，也不代表资金转移已经发生。'}
items=[];results=[]
for x in f['items']:
 rid=x['id'];ep,cid=rid.split('/');a=rd(Path(x['annotation_path']));s=rd(Path(x['segments_path']));proposal=proposals.get(rid,x['claim'][2]);packet={'version':'1','episode':ep,'source_digest':digest(s),'annotation_digest':digest(a),'observer':'current_assistant; same-author nonblind self-review','items':[{'claim_id':cid,'original_statement':x['claim'][2],'proposed_statement':proposal,'action':'revise' if rid in proposals else 'retain','evidence_cues':x['claim'][1],'dimensions':analyses[rid],'forecast_use':'background_only' if ep in ['EP002','EP003'] else 'not_forecast','human_status':'PENDING'}]}
 wr(O/(ep+'.packet.json'),packet);result=validate_packet(packet,a,s);wr(O/(ep+'.validation.json'),result);assert not result['errors'],result;results.append({'id':rid,'action':packet['items'][0]['action'],'packet_status':result['status'],'semantic_acceptance':False})
 summary=['原提取：'+x['claim'][2],('自检后的候选（待确认）：'+proposal if rid in proposals else '自检建议：保留原提取，不为增加细节而强制改写。')]
 items.append({'id':'S01/'+rid,'episode':ep,'kind':'语义自检校准','title':rid+' · '+('候选补充，不预设原文错误' if rid in proposals else '建议保留原提取'),'prompt':'请判断新增细节是否必要且忠实。可以保留原提取，不必因为助手写得更长就采用；这些判断尚未获得独立验证。','review_summary':summary,'has_proposal':rid in proposals,'evidence':x['quotes'],'priority':True,'related':[rid],'detail':{'九项自检':analyses[rid],'用途':'提出可追溯候选，不自动写入正式数据','上下文':x['context']}})
wr(O/'comparison.json',{'samples':3,'same_assistant_nonblind':True,'baseline_frozen':True,'actions':results,'candidate_revisions':2,'retained':1,'human_labels':'PENDING','semantic_improvement_proven':False,'canonical_changes':0})
data={'version':1,'dataset':digest(items),'items':items,'original_run':str(B/'run_004'),'videos':rd(ROOT/'phase1/extraction_quality/holdout_001/review_data.json')['videos']};wr(O/'review_data.json',data)
t=(ROOT/'phase1/extraction_quality/holdout_001/template.html').read_text(encoding='utf-8').replace('留出样本校准','语义自检试用').replace('未审片段检验 / 5项','语义自检试用 / 3项').replace('本轮5项','本轮3项').replace('这里是5条未参与前两轮审核的样本。助手发现3处疑似偏差，另2条暂未发现明确问题，请你校准这些判断。','这次对3条新样本执行九项语义自检，形成2条候选补充和1条保留建议。重点看自检是否有用，不是默认要求你接受更长的摘要。').replace('MacroMind_holdout001_','MacroMind_semantic001_').replace('holdout_001/exports','semantic_pilot_001/exports').replace("'留出校准':", "'语义自检校准':").replace('封存的 run_003','封存的 run_004')
(O/'template.html').write_text(t,encoding='utf-8');(O/'HUMAN_REVIEW.html').write_text(t.replace('__DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c')),encoding='utf-8')
(B/'human_reviews/semantic_pilot_001/exports').mkdir(parents=True,exist_ok=True)
print('Three nine-axis packets validated structurally. Semantic acceptance remains false.')
