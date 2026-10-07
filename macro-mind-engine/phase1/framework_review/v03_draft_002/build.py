import json,hashlib,copy,html
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path("G:/youhegaojian/macro-mind-engine");P=Path(__file__).resolve().parent;OLD=P.parent/"v03_draft_001"
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
src=Path("C:/Users/无语/Downloads/MacroMind_v03draft001_2026-10-05T17-32-00-452Z_6of6.json")
r=read(src);oldpacket=read(OLD/"review_packet.json")
assert r["schema"]==oldpacket["schema"] and r["review_id"]==oldpacket["review_id"] and r["draft_sha256"]==sha(OLD/"framework_draft.json")
assert len(r["records"])==6 and {x["id"] for x in r["records"]}=={c["id"] for c in oldpacket["cards"]}
for x in r["records"]:
 assert x["fidelity"] in ["accept","revise","reject","uncertain"] and x["boundary"] in ["accept","revise","reject","uncertain"]
 assert all(isinstance(x[k],str) for k in ["notes","suggestion","evidence_notes"])
 if "revise" in [x["fidelity"],x["boundary"]]:assert (x["notes"]+x["suggestion"]).strip()
(P/"submitted_review.json").write_bytes(src.read_bytes())
(P/"exports"/src.name).write_bytes(src.read_bytes())
receipt={x["id"]:x for x in r["records"]}
assert [x["id"] for x in r["records"] if x["fidelity"]=="revise"]==["C03","C04"]
d=read(OLD/"framework_draft.json");cards=copy.deepcopy(d["review_cards"])
c=next(x for x in cards if x["id"]=="C03")
c.update(target="M01",related_methods=["M02"],title="如何从多方言行的配合中识别潜在作用方？",rule=receipt["C03"]["suggestion"],
 inputs=["各方关联表述、支持态度、否认知情及其上下文","公开行为与关系线索；作者对其配合方式的解释"],
 steps=["分开记录可观察线索、作者解释、作用方推断与目的推断","保留作者原有确信程度，同时标明其为个人分析判断","只有上下文支持时才写具体战略目的；历史基准、竞争解释和反证属于系统核验，不冒充本段已展示的方法"],
 default="线索不全时可形成潜在作用方的基础判断，标明推断链与尚未确定的环节；作者的强断言不自动升级为事实。",
 update="新的关联、否认、公开行为或独立证据出现时更新；支持、知情、指挥分别更新。",
 example="本例：9527从哈马斯与伊朗反复强调联系、支持及否认知情的配合中，强烈推断伊朗的幕后作用。系统保留“个人观点”和“百分之百”，不将其改写为独立证实。",
 boundary="本段证明的是作者如何判断，不独立证明伊朗参与。关联、支持、事前知情和直接指挥不能替代。没有新增上下文证明时，不加入“逐渐把自己端上台面”的具体目的。")
c=next(x for x in cards if x["id"]=="C04")
c.update(title="宣称的后招会影响预期，但会真正兑现吗？",rule=receipt["C04"]["suggestion"],
 inputs=["公开后招、其当下威慑或预期作用","作者设想的触发局面、战略得失及更优替代选择"],
 steps=["先独立记录第465期对表态影响油价预期的解释","再记录第468期对兑现条件、战略代价和替代选择的分析","分别判断能力、兑现意愿和已经执行，不用其中一项代替另一项"],
 default="即使认为兑现意愿较低，也保留表态可能影响市场预期的判断；不因此认定没有实施能力。",
 update="触发条件、战略代价、替代选择或实际投入改变时，分别更新预期作用与兑现判断。",
 example="本例：465期解释页岩油后招如何制衡市场预期；468期认为真正动用时大局已受损，且此前存在更优选择，因此倾向认为停留于威慑。这两层分别呈现。",
 boundary="“大局已输”和替代方案更优均为作者判断。本例针对特定后招的兑现意愿，不证明美国没有增产能力，也不泛化为不会因其他目的增产。兑现可信度低不等于没有市场影响。")
trans={x["episode"]:x for x in read(ROOT/"phase1/conflict_study/run_002/transcripts.json")}
ranges={"C01":[("456",0,95),("465",62,128)],"C02":[("460",390,549),("470",72,145)],"C03":[("460",35,106)],"C04":[("465",390,579),("468",110,229)],"C05":[("469",0,42),("470",541,689)],"C06":[("456",198,241),("464",316,382)]}
audit=[]
for c in cards:
 oldc=next(x for x in oldpacket["cards"] if x["id"]==c["id"])
 c["inherited"]=c["id"] not in ["C03","C04"]
 c["review_receipt"]=receipt[c["id"]]
 c["attribution"]["approval"]="INHERITED_RULE_AND_BOUNDARY_APPROVAL" if c["inherited"] else "PENDING_DELTA_REVIEW"
 c["evidence"]=[]
 for ep,lo,hi in ranges[c["id"]]:
  cues=[x for x in trans[ep]["cues"] if lo<=x["cue"]<=hi]
  assert len(cues)==hi-lo+1
  c["evidence"].append({"unit":"连续上下文","episode":ep,"cues":cues,"context_url":"contexts/"+ep+".html#cue-"+str(lo),"selection_policy":"人工按论证/话题边界扩展；可打开整期上下文，未自动宣称逻辑完整"})
 audit.append({"id":c["id"],"old_ranges":[{"episode":e["episode"],"from":e["cues"][0]["cue"],"to":e["cues"][-1]["cue"]} for e in oldc["evidence"]],"new_ranges":ranges[c["id"]],"rule_changed":not c["inherited"]})
d["id"]="9527-methods-v0.3-draft-002";d["created_at"]=datetime.now(timezone.utc).isoformat()
for method in d["methods"]:
 method["v03_proposed_extensions"]=[c["id"] for c in cards if c["target"]==method["id"]]
d["review_cards"]=cards;d["review_revision"]={"prior_draft_sha256":sha(OLD/"framework_draft.json"),"submission_sha256":sha(src),"approved_rule_ids":["C01","C02","C05","C06"],"pending_rule_ids":["C03","C04"]}
raw=json.dumps(d,ensure_ascii=False,indent=2).encode();(P/"framework_draft.json").write_bytes(raw)
packet={"schema":oldpacket["schema"],"review_id":"v03_draft_002","draft_sha256":hashlib.sha256(raw).hexdigest(),"cards":cards}
(P/"review_packet.json").write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding="utf-8")
(P/"evidence_boundary_audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding="utf-8")
template=(OLD/"template.html").read_text(encoding="utf-8-sig")
template=template.replace("v0.3 六项规则审阅","v0.3 两项修订复审").replace("v0.3 · 六项规则审阅","v0.3 · 两项修订复审")
template=template.replace("每项有两个选择：","C01、C02、C05、C06 已认可并锁定，本次只需复审 C03、C04。上下文补充不代表你已经审阅过新展示的片段。每项有两个选择：")
template=template.replace("v03_draft_001","v03_draft_002").replace("v03draft001","v03draft002")
template=template.replace("fidelity:'pending',boundary:'pending'","fidelity:c.inherited?'accept':'pending',boundary:c.inherited?'accept':'pending'")
template=template.replace("6项均待审。可先展开原话证据，再选择意见。","已继承4项认可；请复审C03、C04。原文件与旧审阅均保留。")
template=template.replace("const seen=new Set();","const seen=new Set();")
template=template.replace("seen.add(r.id);","seen.add(r.id); if(data.cards.find(c=>c.id===r.id).inherited&&(r.fidelity!=='accept'||r.boundary!=='accept'))throw Error('不能通过复审文件改写已继承的认可');")
template=template.replace("c.id+' → '+c.target+' · 待审草案'","c.id+' → '+c.target+(c.inherited?' · 原规则已认可（上下文补充）':' · 本次待复审')")
template=template.replace("article.append(audit);","if(c.inherited){audit.querySelectorAll('select,textarea').forEach(el=>el.disabled=true);audit.prepend(node('p','此前规则及边界已认可，本次未改变文字。如新增上下文使你改变看法，可在对话中提出。'))} article.append(audit);")
template=template.replace("details.append(quote)}","details.append(quote);const full=node('a','打开整期字幕，从本段定位（可看前后文）');full.href=e.context_url;full.target='_blank';full.rel='noopener';details.append(full)}")
template=template.replace("展开原话证据（","展开连续原话上下文（")
template=template.replace("article.append(details);const audit=", "article.append(details);const prior=node('details');prior.append(node('summary','查看上次审阅意见（只读）'));for(const k of ['notes','suggestion','evidence_notes'])if(c.review_receipt[k])prior.append(node('p',c.review_receipt[k]));article.append(prior);const audit=")
(P/"template.html").write_text(template,encoding="utf-8")
(P/"REVIEW.html").write_text(template.replace("__DATA__",json.dumps(packet,ensure_ascii=False).replace("<","\\u003c")),encoding="utf-8")
ctx=P/"contexts";ctx.mkdir(exist_ok=True)
for ep in {e["episode"] for c in cards for e in c["evidence"]}:
 body=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第'+ep+'期 · 完整字幕上下文</title><style>body{max-width:900px;margin:auto;padding:20px;font:18px/1.7 system-ui;color:#173d41}p{padding:10px;border-bottom:1px solid #ddd;overflow-wrap:anywhere}p:target{background:#fff0b9}small{display:block;color:#667}</style><h1>第'+ep+'期 · 完整字幕上下文</h1><p>原字幕未改字、未核听。完整上下文用于核对推理，不代表内容已经核实。<a href="../REVIEW.html">返回复审</a></p>']
 for cue in trans[ep]["cues"]:body.append(f'<p id="cue-{cue["cue"]}"><small>cue {cue["cue"]} · {html.escape(cue["time"])}</small>{html.escape(cue["text"])}</p>')
 (ctx/(ep+".html")).write_text("\n".join(body),encoding="utf-8")
(P/"DRAFT.md").write_text("# v0.3 第二版待审草案\n\nC01/C02/C05/C06原规则及边界已认可，文字未改；C03/C04根据审阅改写，待复审。上下文为新增展示，不能把旧认可当成对新增片段的验收。\n\n"+"\n\n".join("## "+c["id"]+" "+c["title"]+"\n\n"+c["rule"]+"\n\n证据边界："+c["boundary"] for c in cards),encoding="utf-8")
print("archived review; 4 inherited / 2 pending; continuous contexts and full transcript pages generated")
