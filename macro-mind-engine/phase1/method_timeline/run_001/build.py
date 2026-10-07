import json
from pathlib import Path
from macromind.methods.timeline import evaluate,save_new,object_hash
from macromind.methods.prototype import digest
r=Path.cwd();o=r/'phase1/method_timeline/run_001';sdir=o/'sources';sdir.mkdir(exist_ok=True)
def wr(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
base='https://www.federalreserve.gov/'
specs=[
 ('signal','2024-08-23','2024-08-23','signal','鲍威尔：Review and Outlook','newsevents/speech/powell20240823a.htm','The time has come for policy to adjust.','Near-Term Outlook for Policy，调整方向与后续数据的段落','讲话表达调整方向，但时间和节奏取决于新数据。此时本包没有9月具体决定。'),
 ('decision','2024-09-18','2024-09-18','announcement','9月FOMC决定','newsevents/pressreleases/monetary20240918a.htm','by 1/2 percentage point to 4-3/4 to 5 percent','决定目标区间的段落','公布下调50基点至4.75%–5%；是9月的决定，不把这个区间当作11月仍然不变。'),
 ('instruction','2024-09-18','2024-09-19','instruction','9月实施说明','newsevents/pressreleases/monetary20240918a1.htm','Effective September 19, 2024','国内政策操作指令开头及目标利率条款','实施指令自9月19日起生效；指令存在不等于已经观察到执行效果。'),
 ('nov_decision','2024-11-07','2024-11-07','announcement','11月FOMC决定','newsevents/pressreleases/monetary20241107a.htm','by 1/4 percentage point to 4-1/2 to 4-3/4 percent','目标区间决定的段落','11月再下调25基点至4.50%–4.75%，更新政策状态。'),
 ('transmission','2024-11-26','2024-11-07','execution','11月会议纪要：短端传导','monetarypolicy/fomcminutes20241107.htm','fully passing through to both secured and unsecured reference rates','Staff Review of the Financial Situation，短期融资市场段落','纪要回顾两次会议间的情况：9月调整传导到短期市场参考利率；不是截至11月26日每一天的实时观测。'),
 ('borrowing','2024-11-26','2024-11-07','outcome','11月会议纪要：借贷成本','monetarypolicy/fomcminutes20241107.htm','borrowing costs for households and most businesses rose','Staff Review of the Financial Situation，国内信贷市场段落','纪要称家庭与多数企业的借贷成本同期上升，主要与长期国债收益率上升有关。')]
sources={}
for sid,pub,event,kind,title,url,excerpt,locator,summary in specs:
 doc={'id':sid,'published':pub,'event_date':event,'kind':kind,'title':title,'url':base+url,'excerpt':excerpt,'locator':locator,'summary':summary,'retrieved_on':'2026-10-05','capture_scope':'Selected excerpt and assistant paraphrase checked against official current page; not a full historical-vintage archive','published_date_evidence':base+'newsevents/pressreleases/monetary20241126a.htm' if pub=='2024-11-26' else base+url}
 path=sdir/(sid+'.json');wr(path,doc);sources[sid]={'id':sid,'published':pub,'event_date':event,'kind':kind,'path':path.relative_to(r).as_posix(),'sha256':digest(path)}
wr(o/'publication_check.json',{'release_url':base+'newsevents/pressreleases/monetary20241126a.htm','meeting':'2024-11-06/07','public_release':'2024-11-26','note':'发布页确认纪要公开日期；会议日期不能代替公众可获知日期。按日截止，未模拟日内精确交易信息。'})
def j(id,dim,state,text,refs,reason,trigger,teaching=False):return {'id':id,'dimension':dim,'state':state,'statement':text,'evidence_refs':refs,'reason':reason,'next_trigger':trigger,'teaching_branch':teaching}
plans=[('T0','2024-08-23',['signal'],[
 j('policy','policy','provisional','将政策朝放松方向调整作为工作判断，幅度和时点不预设。',['signal'],'公开讲话提供方向信号；不能提前填入9月决定。','等待具体决定与执行安排；若方向改变，应撤回或修订。'),
 j('execution','execution','unknown','暂不计入尚未出现的具体措施所带来的实际改善。',['signal'],'允许推测内部已有准备，但本包尚无执行安排或执行观察。','出现工具、实施日及执行迹象后逐层更新。'),
 j('broad_relief','broad_effect','provisional','待检验的过宽分支：一旦降息，多数借贷成本会同步下降。',['signal'],'为检验反证和撤回机制而事后设置的教学分支，未计入主判断，也不是博主观点。','检查后续借贷成本；相反结果将撤回此分支。',True),
 j('hidden_plan','hidden_plan','unknown','可考虑内部准备的解释，不把具体预案或非公开信息计为事实。',['signal'],'表态可以提供间接线索，不能唯一确定内部动机或信息内容。','寻找同时期决策过程材料，并比较其他解释。')]),
 ('T1','2024-09-18',['signal','decision','instruction'],[
 j('policy','policy','announced','方向信号已变成具体措施：9月宣布下调50基点至4.75%–5%。',['decision'],'主判断从可能调整更新为已公布政策。','后续新决定会更新区间；不默认路径固定。'),
 j('execution','execution','scheduled','9月19日实施安排已明确，预期影响短端；尚不写成已经观察到效果。',['instruction'],'相比T0已有可执行工具与日期，因此不再维持“没有具体安排”的基线。','后续运行记录是否显示传导。'),
 j('broad_relief','broad_effect','provisional','过宽效果分支仍待检验，不将宣布降息当作多数借贷成本已经下降。',['decision'],'措施已公布，但未新增足够的广泛效果观察。','寻找不同期限与借款主体的成本结果。',True),
 j('hidden_plan','hidden_plan','unknown','工具和实施安排支持存在准备，但仍不能确定内部提前量与非公开信息。',['instruction'],'间接解释得到一些结构性支持，具体内部判断仍未知。','需要决策过程与当时信息；不从措施存在倒推完整预案。')]),
 ('T2','2024-11-26',list(sources),[
 j('policy','policy','announced','11月已再宣布降息25基点至4.50%–4.75%，更新政策状态。',['nov_decision'],'仍为已公布政策这一状态，但具体幅度和区间更新，不复制过时参数。','继续观察后续决定及其条件。'),
 j('execution','execution','observed','公开纪要提供了9月调整传导至短端参考利率的事后观察。',['transmission'],'从实施指令推进到执行观察；观察覆盖此前会议间时段，公开时间为11月26日。','继续区分执行、不同市场传导和更广泛经济效果。'),
 j('broad_relief','broad_effect','withdrawn','撤回“多数借贷成本会随降息同步下降”的过宽分支。',['borrowing'],'公开记录给出相反现象。短端传导不等于广泛融资成本同步下降，应分期限和传导渠道重新分析。','新判断应考虑长期利率、期限溢价等因素；本例不建立新的因果效果估计。',True),
 j('hidden_plan','hidden_plan','unknown','执行得到支持，但内部动机、事前掌握的信息和完整纠错方案仍未确证。',['transmission','borrowing'],'有执行及反例不等于识别了唯一内部原因；既不默认全知，也不因不明而停止其他分析。','只有新的过程证据才调整内部计划解释。')])]
previous=None;results=[]
for sid,cutoff,keys,judgments in plans:
 packet={'version':'timeline-1','id':sid,'as_of':cutoff,'mode':'retrospective_reconstruction','method_available_on':'2026-10-05','previous_sha256':object_hash(previous) if previous else None,'coverage':'按日截止的公开材料选样，不是全新闻库或完整实时信息集；判断由已知后续结果的助手回看编写。','sources':[sources[k] for k in keys],'judgments':judgments}
 wr(o/(sid+'.input.json'),packet)
 result=evaluate(packet,r,previous);save_new(result,o/sid);results.append(result);previous=result
wr(o/'timeline.json',results)
wr(o/'lineage.json',{'method_prototype':'phase1/method_prototype/run_003','approval_preserved':'phase1/method_prototype/run_003/approval.json','canonical_unchanged':'run_005','case_selection':'Public records supply signal, announced tools, transmission and a contrary broad-effect observation','judgments':'Assistant authored after reading later evidence; NOT blind backtest','scope':'Only evidence input timing is mechanically constrained; no claim of eliminating hindsight bias'})
print(json.dumps({'snapshots':len(results),'sources':len(sources),'changes':[{x['id']:[c['action'] for c in x['changes']]} for x in results]}))
