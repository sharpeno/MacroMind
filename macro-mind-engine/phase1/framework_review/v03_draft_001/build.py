import copy, hashlib, json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path("G:/youhegaojian/macro-mind-engine")
P=Path(__file__).resolve().parent
source=ROOT/"phase1/conflict_study/run_002/analysis.json"
analysis=json.loads(source.read_text(encoding="utf-8"))
units={u["id"]:u for u in analysis["units"]}
base=ROOT/"phase1/method_application/run_002/framework.json"
framework=json.loads(base.read_text(encoding="utf-8"))
spec=[
("C01","承诺与支持到了哪一步？",
"把表态、承诺范围、资金或物资、组织安排、实际执行和效果分开，再判断是否真正加大支持。",
["谁对谁支持，公开说了什么","新增资源、执行迹象、观察截止日"],
["先说明本次下场或升级具体指什么，不能事后换口径","比较既有支持与新增投入；同一行动可以有多个作用","给出当前已到哪一步，以及对下一步的倾向"],
"有明确承诺可先视为约束；尚无执行证据时，不提前计入执行收益，也不断言不会执行。",
"新增拨款、部署、撤回承诺或可观察执行出现时更新；表态与执行冲突时保留冲突。",
"教学例：某机构承诺援助但未见交付，可判断存在援助意向和政治约束；交付能力与实际作用仍未知。",
"把新增拨款作为博主该例的观察指标，不能规定所有介入都必须有新增拨款；威慑与约束盟友可并存。",
[("U01",14,28),("U22",65,87)]),
("C02","谁想做、谁能做、谁能阻止？",
"分析各方的利益、能力和依赖，也看同一主体内部的分歧，以及能阻碍安排的参与者。",
["参与者、内部决策者与执行方","已知收益、代价、资源、外部依赖和替代选择"],
["分别列出动机与能力，不把国家或机构当成完全一致的一个人","找出维持现状、升级、缓和各自的推动者和阻碍者","比较约束强弱，形成有条件的倾向，注明未知环节"],
"已有行为与约束足以支持排序时给出暂时倾向；其余环节列为假说，不因信息不全停止所有推演。",
"关键参与者改变态度、约束减弱、资源变化或出现新阻挠者时调整排序。",
"教学例：两方有合作意愿，但负责执行的部门会受损；先判断落实阻力较大，并观察补偿或协调安排。",
"不能凭制度标签或民族性格代替证据；有破坏能力不等于能完全控制事件方向。",
[("U15",499,510),("U35",120,132)]),
("C03","如何从行为与多种线索推断？",
"用公开行为、不同指标和文本对照形成解释，并检查同样现象还能由什么原因造成。",
["可追溯的行为、文本或指标","历史基准、来源关系、至少一种竞争解释"],
["说明观察与常态的差异，比较哪些解释更能说明差异","允许从决策反推动机或信息优势，但标明这是推断","检查反证；区分资源支持、事前知情和直接指挥"],
"可以给出最值得优先考虑的解释，不要求先找到内部文件；证据薄弱时降低确信程度并保留替代解释。",
"出现能区分解释的新证据时重新排序；若反证也被解释成支持，先检查是否形成无法证伪的循环。",
"教学例：某方提前准备多个方案，可暂推断其较早意识到风险；也可能是常规预案，后续需比较准备时间与日常标准。",
"多条同源措辞不等于多份独立证据；拟合现象不证明唯一因果。该限制是系统的证据要求，不声称博主始终遵守。",
[("U14",76,95),("U13",35,43)]),
("C04","新闻如何传到实际影响？",
"分别推演短期情绪、实际供需、对冲措施及后续反馈，允许条件改变后影响反向。",
["受影响对象、时间范围与计量口径","供应需求、替代方案、执行时滞和传导环节"],
["列出事件到结果之间的必要环节","区分公告、可执行能力与已实现效果","给出基础情景、替代分支和方向反转条件"],
"继续使用已有供需约束作基础判断；未出现的新措施收益不提前计入，已公开但未执行的措施作为条件分支。",
"实际供应或需求变化、替代措施落实或失效、关键传导环节中断时更新。",
"教学例：运输风险增加可先提高短期扰动判断；只有实际停运或持续成本上升，才加强长期供应受损判断。",
"公告不是可交付产能；价格目标缺标的、单位或期限时，仅记录观点，不生成精确预测评分。",
[("U29",180,193),("U24",525,548)]),
("C05","新信息如何改变旧判断？",
"保留原判断，再登记新增信息、遗漏因素和改变后的倾向；区分补充、修订与明确撤回。",
["带时间和对象的原判断","新证据及其日期、影响环节、比较口径"],
["先确认比较的是同一对象、尺度与时间范围","明确哪些依据增加或减弱，写出旧判断到新判断的变化","不能把后来的观点倒填成早先已经知道"],
"没有足以改变约束的新证据时，沿用原基础判断并注明仍待观察；不把未知写成不存在。",
"新证据触及原条件、关键主体改变立场，或发现遗漏时，保留旧版并新增判断版本。",
"开发例：469期倾向缓和，470期加入伊朗因素后重新提高风险；471期转向局部持续。需要保留这条变化链。",
"局部升级、全面战争与市场价格分开评分；博主自称准确率高不作为验证结果。",
[("U31",16,40),("U34",541,553)]),
("C06","目标怎样算完成，能否改变路径？",
"检查目标定义、解释权、退出条件和可逆性，区分承诺造成的压力与绝对没有选择。",
["公开目标与完成标准","谁解释结果、失败或暂停条件、内外部退出成本"],
["问顺利和不顺利时各怎样结束","比较宣布目标与实际可实现范围","检查是否存在暂停、换目标或重新解释的空间"],
"目标含糊或缺退出方案时，先判断持续投入与承诺压力较大；不直接判定行动必然永久持续。",
"目标缩小、完成口径明确、可执行退出安排或承担转向成本的人出现时更新。",
"教学例：项目宣称彻底解决问题却无完成指标，可判断退出困难；后续明确分阶段交付标准，可能降低该困难。",
"知道代价不代表总能理性选择；政治上困难不等于逻辑上绝无退路。",
[("U02",210,230),("U20",316,341)])
]
cards=[]
for cid,title,rule,inputs,steps,default,update,example,boundary,evs in spec:
 candidate=next(c for c in analysis["candidate_rules"] if c["id"]==cid)
 evidence=[]
 for uid,lo,hi in evs:
  u=units[uid];selected=[e for e in u["evidence"] if lo<=e["cue"]<=hi]
  assert len(selected)==hi-lo+1,(uid,lo,hi)
  evidence.append({"unit":uid,"episode":u["episode"],"cues":selected})
 cards.append({"id":cid,"target":candidate["target"],"title":title,"rule":rule,"inputs":inputs,"steps":steps,"default":default,"update":update,"example":example,"boundary":boundary,"evidence":evidence,"attribution":{"rule":"ASSISTANT_OPERATIONALIZATION_BASED_ON_BLOGGER","boundary":"ASSISTANT_EVIDENCE_SAFEGUARD","approval":"PENDING"}})
draft=copy.deepcopy(framework)
draft["id"]="9527-methods-v0.3-draft-001";draft["state"]="DRAFT_PENDING_HUMAN_REVIEW_NOT_ACTIVE"
draft.pop("frozen_on",None)
draft["created_at"]=datetime.now(timezone.utc).isoformat()
draft["parent"]={"path":str(base),"sha256":hashlib.sha256(base.read_bytes()).hexdigest()}
draft["development_source"]={"path":str(source),"sha256":hashlib.sha256(source.read_bytes()).hexdigest()}
draft["review_cards"]=cards
for m in draft["methods"]:
 m["status"]="DRAFT_PENDING_HUMAN_REVIEW";m["semantic_approval"]="NOT_GRANTED"
 m["v03_proposed_extensions"]=[c["id"] for c in cards if c["target"]==m["id"]]
draft["activation_policy"]="No automatic activation from browser choices; validate exported review and resolve changes before separate freeze."
raw=json.dumps(draft,ensure_ascii=False,indent=2).encode()
(P/"framework_draft.json").write_bytes(raw)
packet={"schema":"macromind.framework-review.v1","review_id":"v03_draft_001","draft_sha256":hashlib.sha256(raw).hexdigest(),"cards":cards}
(P/"review_packet.json").write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding="utf-8")
template=(P/"template.html").read_text(encoding="utf-8-sig")
(P/"REVIEW.html").write_text(template.replace("__DATA__",json.dumps(packet,ensure_ascii=False).replace("<","\\u003c")),encoding="utf-8")
md=["# 9527 方法 v0.3 草案","", "状态：待人工审阅，未替代v0.2。继承v0.2五项方法，增加六组操作规则；C01与C06均扩展M02。规则是助手操作化，证据边界是系统建议，分别审阅。",""]
for c in cards:
 md += [f'## {c["id"]} {c["title"]}',"",c["rule"],"","所需信息："+"；".join(c["inputs"]),""]+[f'{i+1}. {s}' for i,s in enumerate(c["steps"])]+["","基础判断："+c["default"],"","更新条件："+c["update"],"","例子："+c["example"],"","证据边界："+c["boundary"],""]
(P/"DRAFT.md").write_text("\n".join(md),encoding="utf-8")
print(json.dumps({"cards":len(cards),"sha256":packet["draft_sha256"],"status":draft["state"]}))
