import json,hashlib,html
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
for n,h in read(P/"answer_lock.json")["files"].items():assert sha(P/n)==h
cues=read(P/"target_transcript.json")["cues"]
assert [x["cue"] for x in cues]==list(range(655))
rows=json.loads('[{"id": "C01", "result": "PARTIAL_ALIGNMENT_POLICY_DIFFERENCE", "system": "区分数据、市场加息定价、联储决定和援助执行。", "blogger": "认为市场担忧短暂，既定停止加息节奏不会被几份数据轻易改变，但油价暴涨可能改变决定。", "difference": "层次区分落实，但没有复现政策惯性、特定触发条件及其明确倾向。", "ranges": [[367, 431]]}, {"id": "C02", "result": "TIMING_CONFLICT_MISSED", "system": "列经济资源、外交信誉和安全约束。", "blogger": "美国希望等国内经济与选举压力缓解，以色列担心等到那时美方不再帮助，于是双方时间偏好冲突。", "difference": "静态成本比较不足，遗漏行动窗口和等待成本；这些动机解释不自动成为事实。", "ranges": [[533, 648]]}, {"id": "C03", "result": "HIDDEN_CHANNEL_INFERENCE_MISSED", "system": "把数据来源与角色分开，不直接补写政策动机。", "blogger": "从收紧后消费仍超预期反推政府通过不显眼渠道注入资金，并联系选民利益。", "difference": "遗漏以结果推断隐藏机制的思路；博主说“证实”，系统仍须单独记录证据与其他解释，不能用消费数据独立证明具体渠道。", "ranges": [[432, 495]]}, {"id": "C04", "result": "PARTIAL_CHAIN_SUBSTANTIVE_CONCLUSION_GAP", "system": "紧缩预期可能增加投入约束，但不从数据直接推断抛弃盟友。", "blogger": "不再加息但维持高息→国内调整未完→以方此时迫使介入会消耗资源→美方不愿被绑定，并作很强的判断。", "difference": "宏观约束方向有交集，但政策路径、时间结构和结论确信度不同；不能标为同一预测。", "ranges": [[496, 648]]}, {"id": "C05", "result": "HYPOTHESIS_PROTOCOL_IMPLEMENTED_NOT_EQUIVALENT", "system": "H01/H02/H03均有依据、假设、后续观察及更新方向。", "blogger": "对同一数据同时提出通胀压力与资金托底解释，并给出自己的政策倾向；本期还更新医院责任判断。", "difference": "多情景流程落实，但不等于已还原作者排序；医院更新依赖本输入未取得的素材，事实另行核验。", "ranges": [[0, 13], [432, 532]]}, {"id": "C06", "result": "PATH_DEPENDENCE_AND_CONFIDENCE_GAP", "system": "保留不同援助路径及退出阈值未明。", "blogger": "强调以方等待会失去窗口、既有行为使回头更难，同时强断言美方不会被绑上战车。", "difference": "系统保持路径开放，未复现作者时间与不可逆成本论证；应保留差异，不把修辞性的切割等同全部援助终止。", "ranges": [[533, 648]]}]')
review=json.loads('[{"id": "R01", "title": "是否区分市场的加息担忧、政策惯性与真正触发条件？", "finding": "博主认为零售数据引发的市场恐慌会消退，既定停止加息节奏不易被几份国内数据改变；他把油价突然大涨列为可能迫使继续加息的因素。原答案虽然区分市场定价与正式政策，却没有还原这套排序及明确倾向。", "question": "这样归纳是否准确？保留博主的政策与收益率判断，但不把它当成已验证结果，也不将“不再加息”误写为马上降息。", "ranges": [[367, 431], [496, 532]]}, {"id": "R02", "title": "是否保留了从消费结果反推资金渠道的推理？", "finding": "博主对同一数据给出两层解释：通胀压力仍在，同时消费韧性显示政府通过不显眼渠道投放资金、照顾核心选民。他承认具体管道看不到，却将消费上涨视为此前判断获证实。系统没有还原这种由结果反推机制的思路。", "question": "是否忠实保留了可见结果、作者推断的机制和其确信程度？核验时仍需与收入、信贷、价格等其他解释比较，不能由单组名义零售数据独立确认具体资金渠道。", "ranges": [[432, 495]]}, {"id": "R03", "title": "是否漏掉美以双方不同的时间窗口与等待成本？", "finding": "博主认为美国想等国内经济和选举压力缓解再处理地区投入，以色列却担心等待会失去美方支持，因而必须在此时施压。他据此强烈判断美国不会被绑上战车。系统只列一般资源约束和多个分支，没有充分表达双方等待成本不一致的冲突。", "question": "是否准确保留“谁能等、谁不能等、为何此时行动”的机制及作者的强判断？这里的切割/不被绑定不能未经界定就等同于全部军援停止。", "ranges": [[533, 648]]}]')
for card in review:
 card["evidence"]=[{"from":lo,"to":hi,"cues":[x for x in cues if lo<=x["cue"]<=hi],"context_url":"CONTEXT.html#cue-"+str(lo)} for lo,hi in card.pop("ranges")]
comparison={"case":"conflict_475","created_at":datetime.now(timezone.utc).isoformat(),"answer_sha256":sha(P/"answer_before_subtitle.json"),"exposure_sha256":sha(P/"exposure.json"),"reading":{"whole_episode":True,"cue_count":655,"ranges_read":[[0,229],[230,459],[460,654]],"not_audio_verified":True},"rows":rows,"review_cards":review,"uncovered_theme":{"range":[0,276],"theme":"医院责任、弹药技术与舆论代价推理未匹配；输入缺失对应新证据，不做技术归责验收","status":"not covered by frozen answer; not automatically a new rule"},"conclusion":"PARTIAL_METHOD_TRANSFER_WITH_CORE_REASONING_GAP","human_comparison_approval":"PENDING","fact_accuracy":"NOT_INDEPENDENTLY_TESTED","forecast_accuracy":"NOT_SCORED","remaining_unread_episodes":["476","478","479","480","482","484","493","495","496","509","601"],"limits":["one qualitative case, no accuracy percentage","source input mismatch and search contamination","cannot infer framework incapable from one application miss","do not revise v0.3 or frozen answer with this comparison"]}
write("comparison.json",comparison)
css="body{margin:0;background:#f3f7f6;color:#183e42;font:18px/1.7 system-ui}main{max-width:1040px;margin:auto;padding:28px}section,article{background:white;border:1px solid #ccdbd7;border-radius:12px;padding:24px;margin:20px 0}h1,h2{line-height:1.4}a{color:#126859}button,select,textarea{font:inherit;box-sizing:border-box;max-width:100%}button{padding:10px 16px;margin:5px;border:1px solid #156658;border-radius:7px;background:#156658;color:white;cursor:pointer}textarea{width:100%;min-height:110px;padding:10px}label{display:block;margin-top:15px}select{padding:10px}blockquote{margin:12px 0;border-left:4px solid #87a99b;padding:14px;background:#f2f6f4}small{display:block;color:#526c6b}summary{cursor:pointer;color:#126859;font-weight:bold}.notice{background:#fff4d9;padding:15px}.finding{background:#eaf3f9;padding:15px}table{border-collapse:collapse;width:100%;font-size:16px}td,th{border-bottom:1px solid #ccd9d5;padding:10px;text-align:left;vertical-align:top}p,td{overflow-wrap:anywhere}:target{outline:2px solid #cfaa41} @media(max-width:600px){main{padding:12px}article,section{padding:16px}h1{font-size:26px}table{font-size:14px}}"
esc=html.escape
full='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>475期完整字幕上下文</title><style>'+css+'</style><main><h1>第475期完整字幕</h1><p>原字幕保留，未核听。<a href="TRACE.html">返回对照与审阅</a></p>'
for c in cues:full+=f'<p id="cue-{c["cue"]}"><small>cue {c["cue"]} · {esc(c["time"])}</small>{esc(c["text"])}</p>'
(P/"CONTEXT.html").write_text(full+"</main></html>",encoding="utf-8")
answer=read(P/"answer_before_subtitle.json")
page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MacroMind · 第475期留出对照</title><style>'+css+'</style><main><h1>第475期 · 第四例留出对照</h1><p>先封存新闻分析，再阅读博主字幕。v0.3保持不变。</p><p class="notice">初步结果：方法部分迁移，但漏掉关键原因链。以下是助手对照，尚待你审阅。不是事实或预测准确率验收；承接前三期反馈调整运用方式，且已接触历史后续信息，本轮不称严格盲测。</p><section><h2>先看结果，再审三个差异</h2><p>请只判断我们的对照是否忠实。若不同意，在意见框说明；完成后下载 JSON 给我。</p><p id="progress"></p><button id="next">下一项待审</button><button id="download">下载审阅 JSON</button><button id="import">导入本页审阅</button><input id="file" type="file" accept=".json" hidden><p id="status" aria-live="polite">填写会暂存当前浏览器，导出后再提交。</p></section>'
page+='<section><h2>阅读字幕前已封存的答案</h2><p>'+esc(answer["overall"])+'</p><details><summary>展开六项方法的原始分析</summary>'
for r in answer["rules"]:page+='<h3>'+r["id"]+'</h3><p>'+esc(r["analysis"])+'</p><p>基础判断：'+esc(r["base"])+'</p><p>更新条件：'+esc(r["trigger"])+'</p>'
page+='<h3>封存的候选解释与更新条件</h3>'
for h in answer["hypotheses"]:page+='<h4>'+esc(h["id"]+' '+h["claim"])+'</h4><p>依据：'+esc('、'.join(h["basis"]))+'；假设：'+esc(h["assumptions"])+'</p><p>后续观察：'+esc(h["discriminating_observations"])+'</p><p>更新方向：'+esc(h["update"])+'</p>'
page+='<h3>封存的身份与态度记录</h3>'
for actor in answer["speaker_ledger"]:page+='<p>'+esc(actor["speaker"]+'｜'+actor["role"]+'｜'+actor["observed"]+'｜公开态度：'+actor["stance"]+'｜动机假说：'+actor["motive_hypothesis"])+'</p>'
page+='</details><p><a href="answer_before_subtitle.json">原始答案</a> · <a href="answer_lock.json">封存哈希</a> · <a href="news_input.json">输入来源及限制</a></p></section><section><h2>逐项对照</h2><table><tr><th>规则</th><th>实际发现</th></tr>'
for r in rows:page+='<tr><td>'+r["id"]+'</td><td>'+esc(r["difference"])+'</td></tr>'
page+='</table></section>'
for c in review:
 page+='<article id="'+c["id"]+'"><h2>'+c["id"]+' · '+esc(c["title"])+'</h2><p class="finding">'+esc(c["finding"])+'</p><p>'+esc(c["question"])+'</p><details><summary>展开连续原话上下文</summary>'
 for e in c["evidence"]:
  page+=f'<h3>cue {e["from"]}—{e["to"]}</h3><blockquote>'
  for cue in e["cues"]:page+=f'<p><small>{cue["cue"]} · {esc(cue["time"])}</small>{esc(cue["text"])}</p>'
  page+='</blockquote><a href="'+e["context_url"]+'" target="_blank" rel="noopener">查看整期前后文</a>'
 page+='</details><label>对照归纳是否忠实 <select data-id="'+c["id"]+'"><option value="pending">待审</option><option value="accept">准确，无需修改</option><option value="revise">需要修改</option><option value="uncertain">暂不确定</option></select></label><label>意见或补充（需修改时请填写）<textarea data-id="'+c["id"]+'"></textarea></label></article>'
seed={"schema":"macromind.holdout-comparison-review.v1","review_id":"holdout475_001","comparison_sha256":sha(P/"comparison.json"),"ids":[c["id"] for c in review]}
write("review_packet.json",seed)
js=r"""
const seed=JSON.parse(document.getElementById('seed').textContent),key='macromind.holdoutReview.'+seed.comparison_sha256;
let records=seed.ids.map(id=>({id,decision:'pending',notes:''}));
const status=s=>document.getElementById('status').textContent=s;
function valid(p){
 if(!p||p.schema!==seed.schema||p.review_id!==seed.review_id||p.comparison_sha256!==seed.comparison_sha256)throw Error('版本不匹配');
 if(!Array.isArray(p.records)||p.records.length!==3)throw Error('需包含三项');
 const seen=new Set();for(const r of p.records){if(!seed.ids.includes(r.id)||seen.has(r.id)||!['pending','accept','revise','uncertain'].includes(r.decision)||typeof r.notes!=='string'||r.notes.length>100000)throw Error('编号、选项或意见无效');seen.add(r.id)}
 return seed.ids.map(id=>{const r=p.records.find(x=>x.id===id);return {id,decision:r.decision,notes:r.notes}});
}
const complete=r=>r.decision!=='pending'&&(r.decision!=='revise'||r.notes.trim());
function pack(){return {...seed,records,completed:records.filter(complete).length,exported_at:new Date().toISOString(),framework_change:'NONE'}}
function progress(){document.getElementById('progress').textContent='已填写 '+records.filter(complete).length+' / 3 项；填写完成不等于全部同意。'}
function restore(){for(const r of records){document.querySelector('select[data-id='+r.id+']').value=r.decision;document.querySelector('textarea[data-id='+r.id+']').value=r.notes}progress()}
function save(){try{localStorage.setItem(key,JSON.stringify(pack()));status('已暂存；请下载 JSON 后提交。')}catch(e){status('浏览器暂存不可用，请下载备份。')}progress()}
try{const old=localStorage.getItem(key);if(old)records=valid(JSON.parse(old))}catch(e){status('原草稿未载入：'+e.message)}
restore();
for(const el of document.querySelectorAll('select,textarea'))el.addEventListener(el.tagName==='SELECT'?'change':'input',()=>{const r=records.find(r=>r.id===el.dataset.id);r[el.tagName==='SELECT'?'decision':'notes']=el.value;save()});
document.getElementById('next').onclick=()=>{const r=records.find(r=>!complete(r));if(r){location.hash=r.id;document.querySelector('select[data-id='+r.id+']').focus()}else status('已填写，请下载提交；框架未自动修改。')};
document.getElementById('download').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(pack(),null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='MacroMind_holdout475001_'+new Date().toISOString().replace(/[:.]/g,'-')+'_'+records.filter(complete).length+'of3.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status('已发起下载，请确认完成后提交。')};
document.getElementById('import').onclick=()=>document.getElementById('file').click();
document.getElementById('file').onchange=async e=>{try{const f=e.target.files[0];if(!f)return;if(f.size>1000000)throw Error('文件过大');const incoming=valid(JSON.parse(await f.text()));if(!confirm('将覆盖当前填写，建议先下载备份。继续？'))return;records=incoming;restore();save();status('已导入')}catch(e){status('导入失败，原填写保留：'+e.message)}finally{document.getElementById('file').value=''}};
"""
page+='<section><h2>检验边界</h2><p>已完整读取第475期655条字幕，未核听；其余11份保留未读。一篇访问新闻未获取，新闻输入与博主未必等量；同日发布时间先后未知。本页判断须人工复核，不用单例计算准确率。</p><p>测试与记录见同目录 REPORT.md、validation.json；已冻结答案不会随审阅修改。</p></section></main><script id="seed" type="application/json">'+json.dumps(seed,ensure_ascii=False).replace("<","\\u003c")+'</script><script>'+js+'</script></html>'
(P/"TRACE.html").write_text(page,encoding="utf-8")
write("progress.json",{"status":"COMPARISON_READY_PENDING_QA_AND_HUMAN_REVIEW","completed":["answer frozen before exposure","475 fully read 655 cues","six rule comparison recorded","three human review questions prepared"],"pending":["UI and integrity validation","human comparison review","subsequent holdouts not started"],"remaining_unread":comparison["remaining_unread_episodes"]})
print("comparison and review built; full episode read; 11 reserved remain unread")