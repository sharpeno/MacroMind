import json,hashlib,html
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
for n,h in read(P/"answer_lock.json")["files"].items():assert sha(P/n)==h
cues=read(P/"target_transcript.json")["cues"]
assert [x["cue"] for x in cues]==list(range(551))
rows=json.loads('[{"id": "C01", "result": "PARTIAL_ALIGNMENT", "system": "分开到访、合同、未来执行与效果。", "blogger": "从到访姿态和接待安排推断俄方认可合作格局；从合同推演示范与制度吸引。", "difference": "阶段区分保留，但遗漏行动本身的信号及示范作用；不能只等执行收益才分析。", "ranges": [[11, 82], [489, 544]]}, {"id": "C02", "result": "PARTIAL_ALIGNMENT", "system": "俄罗斯可能获外交机会，但资源转移未知。", "blogger": "把普京亲自到访与姿态联系到巴以冲突后俄方压力降低；并分析美国收缩与以色列挽留的矛盾。", "difference": "方向部分接近，系统没有形成行动→压力/约束变化的明确推断。博主的事实前提和解释未独立核验。", "ranges": [[11, 82], [139, 184]]}, {"id": "C03", "result": "ROLE_LEDGER_IMPLEMENTED_SIGNAL_INFERENCE_GAP", "system": "记录普京代表身份和到访，明确没有讲话；动机仅列合作。", "blogger": "利用亲自来访、动作和接待规格识别国家态度与压力；并非必须找到一段讲话才分析。", "difference": "身份记录已落实，但从行动反推隐含状态仍较弱；消息缺失与推演停止之间需区分。", "ranges": [[11, 82]]}, {"id": "C04", "result": "KEY_TRANSMISSION_CHAIN_MISSED", "system": "等待油气协议或供给资料，暂不单向调整油价判断。", "blogger": "以会议凝聚发展合作力量→争斗需求减弱→中东失序及供应风险预期下降解释油价，并判断因中东崩盘而暴涨的剧本不太可能。", "difference": "系统把预期变化过多绑定实体供应协议，遗漏外交合作本身可能影响风险预期的渠道。不能因此认定博主的因果解释已被证实。", "ranges": [[83, 113], [391, 442]]}, {"id": "C05", "result": "PARTIAL_UPDATE_REPRESENTATION", "system": "维持473基线，追加论坛及合同信息。", "blogger": "将到访、论坛与其描述的市场变化结合，强化合作稳定局势的判断。", "difference": "原答案没有生成这种更新路径；输入缺少油价数据，不能按方向准确率评分。", "ranges": [[391, 442]]}, {"id": "C06", "result": "INSUFFICIENT_MATCHED_EXIT_EVIDENCE", "system": "提醒缺少战略完成和退出条件。", "blogger": "重点在路径吸引力、资源取舍和未来预期，并非明确退出契约。", "difference": "本例不能证明退出规则有效；另有合同→示范→技术回流→市场整合的长链未覆盖。", "ranges": [[269, 390], [471, 544]]}]')
review=json.loads('[{"id": "R01", "title": "行动本身是否也要作为角色与态度的信号？", "finding": "原答案已登记普京的国家领导人身份，却主要停在“来访、寻求合作”。博主进一步从亲自来访、姿态与接待安排推断俄罗斯压力减轻及认可合作格局。我们记为身份记录落实，但行动信号的推断仍不充分。", "question": "是否准确归纳了遗漏？这里保留的是博主的解释，不把动作或接待规格直接当作确定的内心证明。原话中的“俄乌冲突以来第一次出国”等事实前提未独立核实。", "ranges": [[11, 82]]}, {"id": "R02", "title": "影响油价预期，是否不必等到具体供给协议？", "finding": "博主提出会议凝聚合作与发展预期→各方争斗需求下降→中东失序及供应风险担忧缓和的链条。系统主要等油气协议和供给数据，漏掉了外交合作影响风险预期的渠道。该推演可以先作为基础假说，不等于已经证明会议导致价格变化。", "question": "这条链是否忠实？是否准确区分“少了预期传导推演”与“没有事实证实因果”？", "ranges": [[83, 113], [391, 442]]}, {"id": "R03", "title": "铁路合同的意义是否还包括示范和吸引力？", "finding": "原答案只强调签约与执行不同。博主则从向欧洲出口，推到技术回流、市场整合和合作示范；又把各国交流成功经验解释为增强对未来发展的向往与凝聚力。我们记为遗漏较长的制度吸引链，而不是合同已经证明所有远期结果。", "question": "是否准确保留了案例→示范→合作吸引的层次？两段证据展示的是本期相互关联的论述，不能把中间所有假设写成已实现。", "ranges": [[269, 390], [489, 544]]}]')
for card in review:
 card["evidence"]=[{"from":lo,"to":hi,"cues":[x for x in cues if lo<=x["cue"]<=hi],"context_url":"CONTEXT.html#cue-"+str(lo)} for lo,hi in card.pop("ranges")]
comparison={"case":"conflict_473","created_at":datetime.now(timezone.utc).isoformat(),"answer_sha256":sha(P/"answer_before_subtitle.json"),"exposure_sha256":sha(P/"exposure.json"),"reading":{"whole_episode":True,"cue_count":551,"ranges_read":[[0,229],[230,550]],"not_audio_verified":True},"rows":rows,"review_cards":review,"uncovered_theme":{"range":[139,184],"theme":"美国收缩与以色列挽留的结构矛盾未充分展开","status":"not covered by frozen answer; not automatically a new rule"},"conclusion":"PARTIAL_METHOD_TRANSFER_WITH_CORE_REASONING_GAP","human_comparison_approval":"PENDING","fact_accuracy":"NOT_INDEPENDENTLY_TESTED","forecast_accuracy":"NOT_SCORED","remaining_unread_episodes":["474","475","476","478","479","480","482","484","493","495","496","509","601"],"limits":["one qualitative case, no accuracy percentage","source input mismatch and search contamination","cannot infer framework incapable from one application miss","do not revise v0.3 or frozen answer with this comparison"]}
write("comparison.json",comparison)
css="body{margin:0;background:#f3f7f6;color:#183e42;font:18px/1.7 system-ui}main{max-width:1040px;margin:auto;padding:28px}section,article{background:white;border:1px solid #ccdbd7;border-radius:12px;padding:24px;margin:20px 0}h1,h2{line-height:1.4}a{color:#126859}button,select,textarea{font:inherit;box-sizing:border-box;max-width:100%}button{padding:10px 16px;margin:5px;border:1px solid #156658;border-radius:7px;background:#156658;color:white;cursor:pointer}textarea{width:100%;min-height:110px;padding:10px}label{display:block;margin-top:15px}select{padding:10px}blockquote{margin:12px 0;border-left:4px solid #87a99b;padding:14px;background:#f2f6f4}small{display:block;color:#526c6b}summary{cursor:pointer;color:#126859;font-weight:bold}.notice{background:#fff4d9;padding:15px}.finding{background:#eaf3f9;padding:15px}table{border-collapse:collapse;width:100%;font-size:16px}td,th{border-bottom:1px solid #ccd9d5;padding:10px;text-align:left;vertical-align:top}p,td{overflow-wrap:anywhere}:target{outline:2px solid #cfaa41} @media(max-width:600px){main{padding:12px}article,section{padding:16px}h1{font-size:26px}table{font-size:14px}}"
esc=html.escape
full='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>473期完整字幕上下文</title><style>'+css+'</style><main><h1>第473期完整字幕</h1><p>原字幕保留，未核听。<a href="TRACE.html">返回对照与审阅</a></p>'
for c in cues:full+=f'<p id="cue-{c["cue"]}"><small>cue {c["cue"]} · {esc(c["time"])}</small>{esc(c["text"])}</p>'
(P/"CONTEXT.html").write_text(full+"</main></html>",encoding="utf-8")
answer=read(P/"answer_before_subtitle.json")
page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MacroMind · 第473期留出对照</title><style>'+css+'</style><main><h1>第473期 · 第二例留出对照</h1><p>先封存新闻分析，再阅读博主字幕。v0.3保持不变。</p><p class="notice">初步结果：方法部分迁移，但漏掉关键原因链。以下是助手对照，尚待你审阅。不是事实或预测准确率验收；承接第472期反馈调整运用方式，且已接触历史后续信息，本轮不称严格盲测。</p><section><h2>先看结果，再审三个差异</h2><p>请只判断我们的对照是否忠实。若不同意，在意见框说明；完成后下载 JSON 给我。</p><p id="progress"></p><button id="next">下一项待审</button><button id="download">下载审阅 JSON</button><button id="import">导入本页审阅</button><input id="file" type="file" accept=".json" hidden><p id="status" aria-live="polite">填写会暂存当前浏览器，导出后再提交。</p></section>'
page+='<section><h2>阅读字幕前已封存的答案</h2><p>'+esc(answer["overall"])+'</p><details><summary>展开六项方法的原始分析</summary>'
for r in answer["rules"]:page+='<h3>'+r["id"]+'</h3><p>'+esc(r["analysis"])+'</p><p>基础判断：'+esc(r["base"])+'</p><p>更新条件：'+esc(r["trigger"])+'</p>'
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
seed={"schema":"macromind.holdout-comparison-review.v1","review_id":"holdout473_001","comparison_sha256":sha(P/"comparison.json"),"ids":[c["id"] for c in review]}
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
document.getElementById('download').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(pack(),null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='MacroMind_holdout473001_'+new Date().toISOString().replace(/[:.]/g,'-')+'_'+records.filter(complete).length+'of3.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status('已发起下载，请确认完成后提交。')};
document.getElementById('import').onclick=()=>document.getElementById('file').click();
document.getElementById('file').onchange=async e=>{try{const f=e.target.files[0];if(!f)return;if(f.size>1000000)throw Error('文件过大');const incoming=valid(JSON.parse(await f.text()));if(!confirm('将覆盖当前填写，建议先下载备份。继续？'))return;records=incoming;restore();save();status('已导入')}catch(e){status('导入失败，原填写保留：'+e.message)}finally{document.getElementById('file').value=''}};
"""
page+='<section><h2>检验边界</h2><p>已完整读取第473期551条字幕，未核听；其余13份保留未读。一篇原新闻无法获取、输入与博主未必等量；同日发布时间先后未知。本页判断须人工复核，不用单例计算准确率。</p><p>测试与记录见同目录 REPORT.md、validation.json；已冻结答案不会随审阅修改。</p></section></main><script id="seed" type="application/json">'+json.dumps(seed,ensure_ascii=False).replace("<","\\u003c")+'</script><script>'+js+'</script></html>'
(P/"TRACE.html").write_text(page,encoding="utf-8")
write("progress.json",{"status":"COMPARISON_READY_PENDING_QA_AND_HUMAN_REVIEW","completed":["answer frozen before exposure","473 fully read 551 cues","six rule comparison recorded","three human review questions prepared"],"pending":["UI and integrity validation","human comparison review","subsequent holdouts not started"],"remaining_unread":comparison["remaining_unread_episodes"]})
print("comparison and review built; full episode read; 13 reserved remain unread")