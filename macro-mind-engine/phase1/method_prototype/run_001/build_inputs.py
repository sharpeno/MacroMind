import copy,hashlib,json
from pathlib import Path
r=Path.cwd();o=r/'phase1/method_prototype/run_001';o.mkdir(exist_ok=True)
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
segments=r/'phase1/batch_pilot/run_005/EP002/segments.json'
quotes={str(x['cue_id']):x['quote'] for x in rd(segments)}
side=rd(r/'phase1/batch_pilot/run_005/method_evidence.json')
def anchor(cue):return {'source':'ep002','record':str(cue),'quote':quotes[str(cue)]}
method={'id':'9527.leadership_correction','version':'0.1-experimental','analyst':'有何高见9527','title':'提前准备、同行引导与择机纠错','attribution':side['attribution'],'originator':'unknown','available_on':'2026-10-04','summary':next(c[2] for c in rd(r/'phase1/batch_pilot/run_005/EP002/annotation.json')['claims'] if c[0]=='C23'),'summary_review':'user_wording_adopted','representation_review':'not_separately_human_reviewed','ordering':side['ordering'],'conditions':[
 {'id':'G1','label':'存在能推动调整的行动主体','question':'案例中是否存在能够提出方案并推动调整的行动主体？','anchors':[anchor(389)]},
 {'id':'G2','label':'正在讨论认识问题与调整既有做法','question':'案例是否涉及对既有判断或做法的认识与调整，而非只有价格变化？','anchors':[anchor(388)]}],
 'steps':[{'id':f'S{i+1}','label':step['step'],'question':q,'anchors':[anchor(x['cue_id']) for x in step['quotes']]} for i,(step,q) in enumerate(zip(side['steps'],[
 '是否有当时材料表明，行动主体在问题被普遍认识前已识别问题？',
 '是否有在行动前准备替代方案、并控制错误程度的证据？',
 '是否有与相关群体同行并引导其认识问题的具体过程证据？',
 '是否有在相关群体认识问题后择机提出预案、并带领纠错的证据？']))],
 'limitations':['方法文字来自用户已确认的提取；条件与检查问题是助手操作化，尚未单独人工确认。','这是一种被转述并认同的做法，原始作者未知，不代表9527原创。','不能从事后调整倒推事前计划，也不能从宣布政策调整推定完整方法成立。','解释领导与纠错过程，不直接生成资产价格预测、交易建议或政策效果结论。','当前原型仅检查来源锚点和显式映射；不自动提取新新闻，也不自动验证语义。']}
wr(o/'method.json',method)
url='https://www.federalreserve.gov/newsevents/speech/powell20240823a.htm'
fed={'title':'Review and Outlook','speaker':'Jerome H. Powell','published':'2024-08-23','retrieved_on':'2026-10-04','url':url,'capture_scope':'Selected short excerpts verified against official page; not a full-text archive. Missing evidence means absent from this packet, not proved absent in reality.','records':[
 {'id':'pivot','text':'We recognized that and pivoted beginning in November.','locator':'The Rise and Fall of Inflation，紧接判断通胀并非暂时性的段落'},
 {'id':'adjust','text':'The time has come for policy to adjust.','locator':'Near-Term Outlook for Policy，政策展望段落'}]}
wr(o/'public_case_excerpts.json',fed)
sources={'ep002':{'path':segments.relative_to(r).as_posix(),'sha256':sha(segments),'role':'method','format':'segments','published':'2026-09-15','url':'https://www.bilibili.com/video/BV12Cej62Exm/'},'fed2024':{'path':(o/'public_case_excerpts.json').relative_to(r).as_posix(),'sha256':sha(o/'public_case_excerpts.json'),'role':'case','format':'records','published':'2024-08-23','url':url}}
def fedanchor(key):return [{'source':'fed2024','record':key,'quote':next(x['text'] for x in fed['records'] if x['id']==key)}]
def judgment(status,reason,anchors):return {'status':status,'reason':reason,'anchors':anchors,'author':'assistant'}
case={'id':'powell2024.public_transfer','title':'新加入的历史案例：2024年鲍威尔杰克逊霍尔讲话','kind':'historical_public','mode':'retrospective_transfer','as_of':'2024-08-23','question':'仅凭这份讲话选段，能否把政策转向解释成上述“提前准备并择机纠错”的完整方法？','judgments':{
 'G1':judgment('supported','官方讲话由鲍威尔讨论政策调整，足以进入行动主体这一提问；不证明其能单独决定全部政策。',fedanchor('adjust')),
 'G2':judgment('supported','选段明确说认识到问题后转向，属于对既有判断的调整。',fedanchor('pivot')),
 'S1':judgment('unknown','回顾认识与转向不能证明在公众之前预先识别；需要当时带日期的判断记录。',fedanchor('pivot')),
 'S2':judgment('unknown','选段没有可核验的预先替代方案或错误控制过程；不能据此断言没有计划。',[]),
 'S3':judgment('unknown','公开发言不等于与群体同行并引导其认识错误，需要具体交流和反应材料。',[]),
 'S4':judgment('unknown','表达调整意向只支持局部观察，尚不支持“待群体认识后提出预案并带领纠错”的完整步骤。',fedanchor('adjust'))},'alternatives':['可能是随新增数据作出调整，而不是事先准备好一套同行纠错方案。','也可能存在本材料未收录的预案或沟通过程，需要额外资料，不能凭选段排除。']}
wr(o/'public_case.packet.json',{'version':'method-prototype-1','method':method,'case':case,'sources':sources})
synthetic={'notice':'全部为虚构的流程测试材料，不是现实新闻或用户审核。','records':[{'id':key,'text':text,'locator':'合成案例测试记录'} for key,text in {
 'G1':'虚构项目组负责人有权提议并组织更换流程。','G2':'虚构团队正在重新认识既有流程的问题并讨论调整。',
 'S1':'虚构记录：负责人提前一周发现问题，此时团队尚未意识到问题。','S2':'虚构记录：负责人事前准备替代流程，并设置影响范围上限。',
 'S3':'虚构记录：负责人参与团队使用流程并引导大家识别问题。','S4':'虚构记录：团队确认问题后，负责人提出预案并组织改正。',
 'outside':'虚构记录：材料仅列昨日资产价格，没有行动主体、问题认识或调整过程。','counter':'虚构记录：负责人确认直到问题发生后才首次准备方案。'}.items()]}
wr(o/'synthetic_records.json',synthetic)
ss={'ep002':sources['ep002'],'fixture':{'path':(o/'synthetic_records.json').relative_to(r).as_posix(),'sha256':sha(o/'synthetic_records.json'),'role':'case','format':'records','published':'2026-10-04'}}
def syn(key):return [{'source':'fixture','record':key,'quote':next(x['text'] for x in synthetic['records'] if x['id']==key)}]
base={'id':'synthetic.complete','title':'虚构完整映射：仅验证程序','kind':'synthetic','mode':'as_of_analysis','as_of':'2026-10-04','question':'程序是否保留全部映射与证据，同时仍拒绝宣称方法有效？','judgments':{k:{'status':'supported','reason':'虚构材料明确写出该条件或步骤，仅作测试。','anchors':syn(k),'author':'synthetic_fixture'} for k in ['G1','G2','S1','S2','S3','S4']},'alternatives':['即使流程描述完整，也不表示它导致成功；本例没有现实有效性含义。']}
for name in ['complete','missing','outside','counter']:
 c=copy.deepcopy(base);c['id']='synthetic.'+name
 if name=='missing':c['judgments']['G2']={'status':'unknown','reason':'此测试刻意不提供适用范围证据。','anchors':[],'author':'synthetic_fixture'}
 if name=='outside':c['judgments']['G2']={'status':'contradicted','reason':'此测试材料明确仅为价格列表。','anchors':syn('outside'),'author':'synthetic_fixture'}
 if name=='counter':c['judgments']['S2']={'status':'contradicted','reason':'此测试有反证：方案是在事后准备。','anchors':syn('counter'),'author':'synthetic_fixture'}
 wr(o/(name+'.packet.json'),{'version':'method-prototype-1','method':method,'case':c,'sources':ss})
wr(o/'lineage.json',{'canonical_data':'phase1/batch_pilot/run_005','method_source':'EP002/C23','existing_application':'EP002/C16 is hypothetical, not a real central bank speech','source_sidecar_sha256':sha(r/'phase1/batch_pilot/run_005/method_evidence.json'),'human_receipt':'phase1/batch_pilot/human_reviews/semantic_pilot_001/batch_001/receipt.json','public_case_mode':'Retrospective transfer using a later extracted method, not a point-in-time forecast','newspaper_or_full_text_downloaded':False})
print('Method, public transfer and four synthetic cases saved')
