import json,hashlib,html
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
for n,h in read(P/"answer_lock.json")["files"].items():assert sha(P/n)==h
cues=read(P/"target_transcript.json")["cues"]
assert [x["cue"] for x in cues]==list(range(684))
rows=json.loads('[{"id": "C01", "result": "PARTIAL_ALIGNMENT", "system": "区分谴责、取消会晤与执行建议。", "blogger": "进一步把美方支持承诺与交付能力、时点和责任解释分开，将强硬支持话语解释为潜在甩责。", "difference": "阶段区分一致，但具体话语功能未复现；两者资料范围不同。", "ranges": [[497, 534]]}, {"id": "C02", "result": "MECHANISM_GAP", "system": "分析会晤取消、公众压力与协调依赖。", "blogger": "提出多环节参与导致责任分散、难以停机排查，失误后仍可能持续升级；另指出高层协调不能控制基层触发。", "difference": "系统主要分析外部政治约束，内部执行与控制机制不足。不能把博主机制解释直接视为已证实原因。", "ranges": [[23, 56], [345, 392], [601, 662]]}, {"id": "C03", "result": "CONDITIONAL_HYPOTHESES_MISSED", "system": "不定责任，列施压等动机但没有具体区分计划。", "blogger": "倾向不信以方解释，却对是否有意保留问号；分为有意给拜登谈判施压和非预期打击后失控升级，并以后续是否继续攻击民用设施判断。", "difference": "保留不确定性不应省略假说、观察指标和更新方向；博主以技术/概率作判断的前提未独立验证，后续行为也不能唯一证明先前意图。", "ranges": [[134, 303], [328, 392], [429, 496]]}, {"id": "C04", "result": "PARTIAL_TRANSMISSION_DIFFERENT_BRANCHES", "system": "公众反应→取消会晤→协调受阻→风险预期上升。", "blogger": "在有意施压分支中，进一步推演以色列以失控升级威胁迫使美国上桌；另把伊朗的停止行动要求解读为介入铺垫。", "difference": "系统有条件链，但没有复现对手选择受限→表态的策略用途；未采用博主更强的行动断言。", "ranges": [[429, 534], [535, 600]]}, {"id": "C05", "result": "UPDATE_PROCESS_PARTIAL", "system": "明确相对472/474调整协调可执行性。", "blogger": "给出后续行为用来辨别两个动机分支，同时在后文重申给拜登下马威只是猜测之一。", "difference": "系统有更新意识，欠缺区分性观察设计；不能将同一指标当作排他的因果检验。", "ranges": [[274, 303], [328, 392], [567, 600]]}, {"id": "C06", "result": "SUBSTANTIVE_DIVERGENCE", "system": "不把未达成写成绝无退出，讨论替代外交路径。", "blogger": "以追责压力和战时无法停止排查解释以方为何难退出，部分措辞更绝对。", "difference": "系统边界与博主强判断存在差异，应同时保留，不能把弱化后的表述冒充原话。", "ranges": [[51, 113], [345, 392]]}]')
review=json.loads('[{"id": "R01", "title": "是否保留了两种情景和用来区分它们的后续观察？", "finding": "博主倾向不信以方解释，但对是否有意打击另留问号：一支是借事件向拜登施压、增加谈判筹码，另一支是非预期打击后在责任分散中持续升级。他用后续是否继续攻击民用设施作为区分线索。系统只保留动机未定，没有把假说与观察计划展开。", "question": "这是否忠实保留责任倾向、意图不确定性和分支？技术/概率说法未独立验证，后续停止或继续也不能单独证明此前意图；这些是系统核验边界，不替换博主原判断。", "ranges": [[134, 303], [328, 392], [429, 496]]}, {"id": "R02", "title": "是否分析了公开表态怎样约束对方、为后续行动铺垫？", "finding": "系统记录了身份和公开态度；博主还将美方支持话语解释为可用交付限制甩责，将伊朗要求停止行动解释为在对方难以满足要求时为介入铺垫。他对伊朗说出强断言，但对以方给拜登设局仍明确称为一种猜测。", "question": "是否准确分开讲话内容、角色与策略解释，以及不同命题的确信程度？保留博主的断言不等于我们已经证实伊朗必然采取何种行动。", "ranges": [[497, 600]]}, {"id": "R03", "title": "是否漏掉了内部责任链与高层控制的局限？", "finding": "博主解释多环节参与会分散责任，战时难以停下排查，可能使越线反复发生；又指出高层关系安排无法确保基层事件不改变全局。系统主要分析外部外交受阻，没有充分展开内部执行与控制机制。", "question": "这样归纳是否合适？应保留“多环节—责任分散—难以纠偏—持续升级”的机制及场景，不将它泛化为任何多人决策都必然失控。", "ranges": [[23, 56], [345, 392], [601, 662]]}]')
for card in review:
 card["evidence"]=[{"from":lo,"to":hi,"cues":[x for x in cues if lo<=x["cue"]<=hi],"context_url":"CONTEXT.html#cue-"+str(lo)} for lo,hi in card.pop("ranges")]
comparison={"case":"conflict_474","created_at":datetime.now(timezone.utc).isoformat(),"answer_sha256":sha(P/"answer_before_subtitle.json"),"exposure_sha256":sha(P/"exposure.json"),"reading":{"whole_episode":True,"cue_count":684,"ranges_read":[[0,229],[230,459],[460,683]],"not_audio_verified":True},"rows":rows,"review_cards":review,"uncovered_theme":{"range":[460,496],"theme":"美国低成本维持地区秩序的战略解释未充分展开","status":"not covered by frozen answer; not automatically a new rule"},"conclusion":"PARTIAL_METHOD_TRANSFER_WITH_CORE_REASONING_GAP","human_comparison_approval":"PENDING","fact_accuracy":"NOT_INDEPENDENTLY_TESTED","forecast_accuracy":"NOT_SCORED","remaining_unread_episodes":["475","476","478","479","480","482","484","493","495","496","509","601"],"limits":["one qualitative case, no accuracy percentage","source input mismatch and search contamination","cannot infer framework incapable from one application miss","do not revise v0.3 or frozen answer with this comparison"]}
write("comparison.json",comparison)
css="body{margin:0;background:#f3f7f6;color:#183e42;font:18px/1.7 system-ui}main{max-width:1040px;margin:auto;padding:28px}section,article{background:white;border:1px solid #ccdbd7;border-radius:12px;padding:24px;margin:20px 0}h1,h2{line-height:1.4}a{color:#126859}button,select,textarea{font:inherit;box-sizing:border-box;max-width:100%}button{padding:10px 16px;margin:5px;border:1px solid #156658;border-radius:7px;background:#156658;color:white;cursor:pointer}textarea{width:100%;min-height:110px;padding:10px}label{display:block;margin-top:15px}select{padding:10px}blockquote{margin:12px 0;border-left:4px solid #87a99b;padding:14px;background:#f2f6f4}small{display:block;color:#526c6b}summary{cursor:pointer;color:#126859;font-weight:bold}.notice{background:#fff4d9;padding:15px}.finding{background:#eaf3f9;padding:15px}table{border-collapse:collapse;width:100%;font-size:16px}td,th{border-bottom:1px solid #ccd9d5;padding:10px;text-align:left;vertical-align:top}p,td{overflow-wrap:anywhere}:target{outline:2px solid #cfaa41} @media(max-width:600px){main{padding:12px}article,section{padding:16px}h1{font-size:26px}table{font-size:14px}}"
esc=html.escape
full='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>474期完整字幕上下文</title><style>'+css+'</style><main><h1>第474期完整字幕</h1><p>原字幕保留，未核听。<a href="TRACE.html">返回对照与审阅</a></p>'
for c in cues:full+=f'<p id="cue-{c["cue"]}"><small>cue {c["cue"]} · {esc(c["time"])}</small>{esc(c["text"])}</p>'
(P/"CONTEXT.html").write_text(full+"</main></html>",encoding="utf-8")
answer=read(P/"answer_before_subtitle.json")
page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MacroMind · 第474期留出对照</title><style>'+css+'</style><main><h1>第474期 · 第三例留出对照</h1><p>先封存新闻分析，再阅读博主字幕。v0.3保持不变。</p><p class="notice">初步结果：方法部分迁移，但漏掉关键原因链。以下是助手对照，尚待你审阅。不是事实或预测准确率验收；承接前两期反馈调整运用方式，且已接触历史后续信息，本轮不称严格盲测。</p><section><h2>先看结果，再审三个差异</h2><p>请只判断我们的对照是否忠实。若不同意，在意见框说明；完成后下载 JSON 给我。</p><p id="progress"></p><button id="next">下一项待审</button><button id="download">下载审阅 JSON</button><button id="import">导入本页审阅</button><input id="file" type="file" accept=".json" hidden><p id="status" aria-live="polite">填写会暂存当前浏览器，导出后再提交。</p></section>'
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
seed={"schema":"macromind.holdout-comparison-review.v1","review_id":"holdout474_001","comparison_sha256":sha(P/"comparison.json"),"ids":[c["id"] for c in review]}
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
document.getElementById('download').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(pack(),null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='MacroMind_holdout474001_'+new Date().toISOString().replace(/[:.]/g,'-')+'_'+records.filter(complete).length+'of3.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status('已发起下载，请确认完成后提交。')};
document.getElementById('import').onclick=()=>document.getElementById('file').click();
document.getElementById('file').onchange=async e=>{try{const f=e.target.files[0];if(!f)return;if(f.size>1000000)throw Error('文件过大');const incoming=valid(JSON.parse(await f.text()));if(!confirm('将覆盖当前填写，建议先下载备份。继续？'))return;records=incoming;restore();save();status('已导入')}catch(e){status('导入失败，原填写保留：'+e.message)}finally{document.getElementById('file').value=''}};
"""
page+='<section><h2>检验边界</h2><p>已完整读取第474期684条字幕，未核听；其余12份保留未读。新闻输入与博主未必等量；同日发布时间先后未知。本页判断须人工复核，不用单例计算准确率。</p><p>测试与记录见同目录 REPORT.md、validation.json；已冻结答案不会随审阅修改。</p></section></main><script id="seed" type="application/json">'+json.dumps(seed,ensure_ascii=False).replace("<","\\u003c")+'</script><script>'+js+'</script></html>'
(P/"TRACE.html").write_text(page,encoding="utf-8")
write("progress.json",{"status":"COMPARISON_READY_PENDING_QA_AND_HUMAN_REVIEW","completed":["answer frozen before exposure","474 fully read 684 cues","six rule comparison recorded","three human review questions prepared"],"pending":["UI and integrity validation","human comparison review","subsequent holdouts not started"],"remaining_unread":comparison["remaining_unread_episodes"]})
print("comparison and review built; full episode read; 12 reserved remain unread")