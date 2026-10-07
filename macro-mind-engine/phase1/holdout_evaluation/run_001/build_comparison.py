import json,hashlib,html
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
for n,h in read(P/"answer_lock.json")["files"].items():assert sha(P/n)==h
cues=read(P/"target_transcript.json")["cues"]
assert [x["cue"] for x in cues]==list(range(643))
rows=[
{"id":"C01","result":"PARTIAL_ALIGNMENT","system":"区分支持表态、拨款与直接参战。","blogger":"把双线支持表态解释为身份约束下不得不作的强硬回答，并进一步推断心虚；没有在本期展开议长与拨款链。","difference":"共有表态不等于实质的区分，但动机与语用解释不同，不能算完整复现。","ranges":[[237,289]]},
{"id":"C02","result":"KEY_CAUSAL_CHAIN_MISSED","system":"识别以方分歧可能阻碍通行与外交执行。","blogger":"从停火传闻与否认、撤离迹象推断以色列管理层可能脱节，进而解释拜登突然到访；另分以方极端与温和力量。","difference":"只说存在多方约束，漏掉内部控制失灵→盟友被迫亲自介入这条核心因果链。该链是博主推断，非已核实事实。","ranges":[[290,375],[446,550],[586,610]]},
{"id":"C03","result":"INFERENCE_STYLE_UNDERUSED","system":"允许安抚与约束升级的动机假说，但认为幕后操盘线索不足，不排序。","blogger":"从访问安排、消息矛盾、撤离与后续表态反推动机和未公开局面；并明确部分因果说不清。","difference":"系统较少使用可观察异常反推隐含状态。本例并非简单证明同一幕后主体；与C03相关但不能未经审阅扩大已批准规则。","ranges":[[3,35],[290,375],[611,637]]},
{"id":"C04","result":"PARTIAL_ALIGNMENT_WITH_CONFIDENCE_GAP","system":"支持并管控升级优先；直接参战仅作条件分支。","blogger":"把双线能力宣示解读为特定身份下唯一可说的答案，进一步判为壮胆；对拜登解决问题的能力明显更悲观。","difference":"系统分开能力与意愿，但没有复现讲话者角色约束和博主强确信；没有足够证据把这归为预测方向命中。","ranges":[[203,211],[237,289],[547,610]]},
{"id":"C05","result":"UPDATE_PROCESS_ALIGNED_FORECAST_NOT_TESTED","system":"设立后续行为触发器；无此前案例封存答案，不虚构修订史。","blogger":"等待访问后的说辞判断后续，同时提出起码3—5天和平的时间判断，又保留具体因果不明及后续观察。","difference":"共享后续验证思路；系统没有提出这项短期判断。和平范围与起算点未清楚界定，暂不评分，不能记为系统命中或失败。","ranges":[[586,637]]},
{"id":"C06","result":"INSUFFICIENT_MATCHED_EVIDENCE","system":"讨论退出条件不明确、承诺不等于无限投入。","blogger":"本期重点在管理控制与地区力量变化，没有找到完整对应的目标完成或退出条件论证。","difference":"不强行把失控隐喻认成C06得到验证；此项跨例效果未验证。","ranges":[[586,610]]}
]
review=[
{"id":"R01","title":"系统是否漏掉了本期最关键的原因链？","finding":"系统只判断内部意见不一可能妨碍执行。博主则把访问变化、停火消息与否认、撤离迹象串成：以方内部控制可能失灵→美国不得不亲自介入处理。我们将它记为核心推理遗漏，而非完整对齐。","question":"这样的差异归纳是否忠实？特别是“可能失控”与“被迫介入”的联系，是否保留了原话的语气和理由？这里只核对博主的分析，不要求认定其推断在现实中为真。","ranges":[[290,375],[586,610]]},
{"id":"R02","title":"“必须这样说”与“真的有能力”是否分开了？","finding":"博主认为财长在该角色下只能给出能支持双线的回答，再从此时强调能力推断心虚。系统只做了能力、意愿、行动的区分，未复现这段讲话动机判断。不能替博主删掉强判断，也不能将其升级为客观事实。","question":"将此记为部分对齐、但漏掉角色约束与讲话动机，是否合适？","ranges":[[237,289]]},
{"id":"R03","title":"保留“3—5天和平”，但暂不评分是否合适？","finding":"博主既说要等访问后的说辞再判断，又提出起码3—5天和平；随后表示相关因果说不清楚。系统提前封存的答案没有这项短期判断。我们完整保留时间表述，因和平的范围与起算点不清而暂不评分，不把有保留误写成完全没有判断。","question":"是否准确保留了明确判断与不确定性的各自范围？若你认为“和平”有上下文限定，请指出，不用在这里判定历史成败。","ranges":[[586,637]]}
]
for card in review:
 card["evidence"]=[{"from":lo,"to":hi,"cues":[x for x in cues if lo<=x["cue"]<=hi],"context_url":"CONTEXT.html#cue-"+str(lo)} for lo,hi in card.pop("ranges")]
comparison={"case":"conflict_472","created_at":datetime.now(timezone.utc).isoformat(),"answer_sha256":sha(P/"answer_before_subtitle.json"),"exposure_sha256":sha(P/"exposure.json"),"reading":{"whole_episode":True,"cue_count":643,"ranges_read":[[0,229],[230,459],[460,642]],"not_audio_verified":True},"rows":rows,"review_cards":review,"uncovered_theme":{"range":[446,531],"theme":"历史行动效果依赖当时环境，不能机械复制旧成功","status":"not covered by frozen answer; not automatically a new rule"},"conclusion":"PARTIAL_METHOD_TRANSFER_WITH_CORE_REASONING_GAP","human_comparison_approval":"PENDING","fact_accuracy":"NOT_INDEPENDENTLY_TESTED","forecast_accuracy":"NOT_SCORED","remaining_unread_episodes":["473","474","475","476","478","479","480","482","484","493","495","496","509","601"],"limits":["one qualitative case, no accuracy percentage","source input mismatch and search contamination","cannot infer framework incapable from one application miss","do not revise v0.3 or frozen answer with this comparison"]}
write("comparison.json",comparison)
css="body{margin:0;background:#f3f7f6;color:#183e42;font:18px/1.7 system-ui}main{max-width:1040px;margin:auto;padding:28px}section,article{background:white;border:1px solid #ccdbd7;border-radius:12px;padding:24px;margin:20px 0}h1,h2{line-height:1.4}a{color:#126859}button,select,textarea{font:inherit;box-sizing:border-box;max-width:100%}button{padding:10px 16px;margin:5px;border:1px solid #156658;border-radius:7px;background:#156658;color:white;cursor:pointer}textarea{width:100%;min-height:110px;padding:10px}label{display:block;margin-top:15px}select{padding:10px}blockquote{margin:12px 0;border-left:4px solid #87a99b;padding:14px;background:#f2f6f4}small{display:block;color:#526c6b}summary{cursor:pointer;color:#126859;font-weight:bold}.notice{background:#fff4d9;padding:15px}.finding{background:#eaf3f9;padding:15px}table{border-collapse:collapse;width:100%;font-size:16px}td,th{border-bottom:1px solid #ccd9d5;padding:10px;text-align:left;vertical-align:top}p,td{overflow-wrap:anywhere}:target{outline:2px solid #cfaa41} @media(max-width:600px){main{padding:12px}article,section{padding:16px}h1{font-size:26px}table{font-size:14px}}"
esc=html.escape
full='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>472期完整字幕上下文</title><style>'+css+'</style><main><h1>第472期完整字幕</h1><p>原字幕保留，未核听。<a href="TRACE.html">返回对照与审阅</a></p>'
for c in cues:full+=f'<p id="cue-{c["cue"]}"><small>cue {c["cue"]} · {esc(c["time"])}</small>{esc(c["text"])}</p>'
(P/"CONTEXT.html").write_text(full+"</main></html>",encoding="utf-8")
answer=read(P/"answer_before_subtitle.json")
page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MacroMind · 第472期留出对照</title><style>'+css+'</style><main><h1>第472期 · 首例留出对照</h1><p>先封存新闻分析，再阅读博主字幕。v0.3保持不变。</p><p class="notice">初步结果：方法部分迁移，但漏掉关键原因链。以下是助手对照，尚待你审阅。不是事实或预测准确率验收；检索见到较晚消息摘要，本轮不称严格盲测。</p><section><h2>先看结果，再审三个差异</h2><p>请只判断我们的对照是否忠实。若不同意，在意见框说明；完成后下载 JSON 给我。</p><p id="progress"></p><button id="next">下一项待审</button><button id="download">下载审阅 JSON</button><button id="import">导入本页审阅</button><input id="file" type="file" accept=".json" hidden><p id="status" aria-live="polite">填写会暂存当前浏览器，导出后再提交。</p></section>'
page+='<section><h2>阅读字幕前已封存的答案</h2><p>'+esc(answer["overall"])+'</p><details><summary>展开六项方法的原始分析</summary>'
for r in answer["rules"]:page+='<h3>'+r["id"]+'</h3><p>'+esc(r["analysis"])+'</p><p>基础判断：'+esc(r["base"])+'</p><p>更新条件：'+esc(r["trigger"])+'</p>'
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
seed={"schema":"macromind.holdout-comparison-review.v1","review_id":"holdout472_001","comparison_sha256":sha(P/"comparison.json"),"ids":[c["id"] for c in review]}
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
document.getElementById('download').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(pack(),null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='MacroMind_holdout472001_'+new Date().toISOString().replace(/[:.]/g,'-')+'_'+records.filter(complete).length+'of3.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status('已发起下载，请确认完成后提交。')};
document.getElementById('import').onclick=()=>document.getElementById('file').click();
document.getElementById('file').onchange=async e=>{try{const f=e.target.files[0];if(!f)return;if(f.size>1000000)throw Error('文件过大');const incoming=valid(JSON.parse(await f.text()));if(!confirm('将覆盖当前填写，建议先下载备份。继续？'))return;records=incoming;restore();save();status('已导入')}catch(e){status('导入失败，原填写保留：'+e.message)}finally{document.getElementById('file').value=''}};
"""
page+='<section><h2>检验边界</h2><p>已完整读取第472期643条字幕，未核听；其余14份保留未读。一篇原新闻失效、输入与博主未必等量；同日发布时间先后未知。本页判断须人工复核，不用单例计算准确率。</p><p>测试与记录见同目录 REPORT.md、validation.json；已冻结答案不会随审阅修改。</p></section></main><script id="seed" type="application/json">'+json.dumps(seed,ensure_ascii=False).replace("<","\\u003c")+'</script><script>'+js+'</script></html>'
(P/"TRACE.html").write_text(page,encoding="utf-8")
write("progress.json",{"status":"COMPARISON_READY_PENDING_QA_AND_HUMAN_REVIEW","completed":["answer frozen before exposure","472 fully read 643 cues","six rule comparison recorded","three human review questions prepared"],"pending":["UI and integrity validation","human comparison review","subsequent holdouts not started"],"remaining_unread":comparison["remaining_unread_episodes"]})
print("comparison and review built; full episode read; 14 reserved remain unread")