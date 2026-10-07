import json,hashlib,re,html
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ROOT=P.parents[2];read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
now=lambda:datetime.now(timezone.utc).isoformat()
sources=[]
for n in ["1486755","1486209"]:
 a=read(P/"sources"/(n+".json"))["props"]["pageProps"]["articleDetail"]
 sources.append({"id":"N"+n,"url":"https://www.cls.cn/detail/"+n,"title":a["title"],"ctime_utc":datetime.fromtimestamp(a["ctime"],timezone.utc).isoformat(),"retrieved_snapshot":f"sources/{n}.html","sha256":sha(P/"sources"/(n+".html")),"epistemic_status":"MEDIA_REPORT_NOT_INDEPENDENTLY_VERIFIED"})
sources.append({"id":"NWH","url":"https://www.presidency.ucsb.edu/documents/statement-press-secretary-karine-jean-pierre-president-bidens-travel-israel-and-jordan","title":"Statement by Press Secretary on President Biden's Travel to Israel and Jordan","display_date":"2023-10-16","source_type":"archived official statement; no precise publication time shown","observed_summary":"宣布10月18日访问以色列，表达支持并磋商后续安排；随后计划到约旦与约旦、埃及、巴勒斯坦权力机构领导人讨论加沙平民人道需求。仅为访问计划，不是实际行程结果。","retrieval":"web tool opened page; lines 59-65"})
write("news_input.json",{"frozen_at":now(),"sources":sources,"unavailable":[{"url":"https://www.cls.cn/detail/1487000","result":"articleDetail empty; errno404; not used as evidence"}],"cutoff":"2023-10-17 day-level upper boundary; video exact time unknown","leakage":["Episode title and metadata exposed","Model historical knowledge not blinded","Search snippets exposed Oct18 visit and later Jordan cancellation/hospital explosion; excluded from admitted facts but knowledge exposure cannot be undone"],"scope":"Retrospective method transfer comparison, not valid as clean historical predictive backtest"})
facts=[
{"id":"F01","source":"N1486755","text":"耶伦公开宣称美国能同时支持以色列与乌克兰，并呼吁选出众议院议长以推进追加资金立法。","level":"报道中的表态与制度条件；不是拨款已通过"},
{"id":"F02","source":"N1486209","text":"报道所述时点拉法口岸仍关闭；以方否认相关停火协议，有部长反对让物资进入。","level":"单一报道及被引述官方立场；后续状态未知"},
{"id":"F03","source":"N1486209","text":"以方宣布疏散黎巴嫩边境村民，同时称若真主党克制则愿维持现状。","level":"宣布的安排与条件性表态，不等于全面战争"},
{"id":"F04","source":"NWH","text":"白宫宣布拜登访问以色列及约旦的计划，包括支持以色列、磋商下一步及讨论人道需求。","level":"官方行程声明，不能算访问已经完成"}
]
rules=[
{"id":"C01","applicability":"APPLICABLE","facts":["F01","F04"],"analysis":"支持的政治信号明显，但公开承诺、拨款立法和直接参战须分开。议长空缺影响追加资金推进，并不证明所有既有军援停止。访问计划不等于美军作战命令。","base":"更倾向美国继续支持盟友并进行外交干预，而非仅凭这些表态认定直接参战。","trigger":"新增拨款通过、武器交付、军事命令与实际行动分别更新；不以拨款作为所有介入的唯一标准。"},
{"id":"C02","applicability":"APPLICABLE","facts":["F01","F02","F03","F04"],"analysis":"美国支持以色列且寻求地区协调，但追加资金受立法进程约束；口岸安排需要以色列、埃及等配合，以方内部分歧可能阻碍。不同层级的合作不能视为统一控制。","base":"外交安排可能推进，也可能受参与方否决与安全条件阻碍；优先观察实际通行与执行。","trigger":"各方一致安排及现场通行支持改善；反对或继续关闭削弱安排已落实的判断。"},
{"id":"C03","applicability":"LIMITED","facts":["F01","F03","F04"],"analysis":"支持、访问和降温话语可形成美国同时安抚盟友与约束升级的动机假说。但缺少持续配合与责任撇清的完整线索，不能据受益或声援认定幕后指挥方。","base":"保留盟友安抚、威慑外部参与和外交协调多种解释；本例不足以排序具体隐秘操盘者。","trigger":"后续配合行为及具体关系证据出现后，再更新幕后作用假说。"},
{"id":"C04","applicability":"APPLICABLE_WITH_LIMITS","facts":["F01","F03","F04"],"analysis":"财力和支持承诺可以产生威慑，但能力不等于愿意直接作战。直接参战将带来扩大冲突和双线资源压力，外交、援助及防御姿态是可用替代路径；这些代价比较是助手运用规则的推演，不是新闻证明了决策动机。","base":"将支持并管控升级列为较优先分支；直接作战留作条件分支，不断言绝不会发生。","trigger":"美国人员或资产遇袭、明确作战授权、部署用途与交战行动改变时重估；没有这些信息时不提前算已参战。"},
{"id":"C05","applicability":"PARTIAL_NO_LOCKED_PRIOR_CASE","facts":["F01","F02","F03","F04"],"analysis":"新增信息提高对美国公开支持力度和高层协调投入的判断；口岸否认消息反对把传闻当成落实。没有本案例此前独立封存答案，不能虚构一次前后预测修订。","base":"本次答案作为后续更新起点；局部升级、全面战争和市场价格分别记录。","trigger":"新信息到来时另存版本并写明是哪一环改变，不回填本答案。"},
{"id":"C06","applicability":"APPLICABLE_WITH_LIMITS","facts":["F03","F04"],"analysis":"支持以色列和磋商后续步骤不构成可检验的战争退出条件。边境克制表态保留调整空间，访问多方也保留外交路径，不能把承诺压力推成必然无限投入。","base":"短期仍有路径调整余地，但目标、期限与可接受结果不够具体，不能认定存在已执行的退出安排。","trigger":"明确目标、期限、停火执行或外交条件落地后再调整。"}
]
answer={"schema":"macromind.holdout-answer.v1","case":"conflict_472","created_at":now(),"framework_sha256":sha(ROOT/"phase1/framework_review/v03_frozen_001/framework.json"),"news_input_sha256":sha(P/"news_input.json"),"subtitle_semantically_read":False,"fact_ledger":facts,"rules":rules,"overall":"在封存新闻范围内，基础判断是美国加强支持与外交协调，同时保留管控扩散的动机假说；不能从财力表态和访问计划跳到已经直接参战。直接作战是需要额外触发条件的分支。","alternatives":["访问可能主要传递支持，约束升级未必奏效","追加资金受阻不等于所有支持无效","地区行动可能突破各方原有控制意图"],"unresolved":["缺失原始第三篇滚动报道，输入与博主未必等量","不知视频与同日新闻先后","无独立财政能力、军力与因果核验","没有市场方向或精确时限预测"],"evaluation_limit":"Historical source contamination disclosed; do not score as predictive accuracy"}
write("answer_before_subtitle.json",answer)
write("answer_lock.json",{"locked_at":now(),"files":{n:sha(P/n) for n in ["protocol.json","target_metadata.json","news_input.json","answer_before_subtitle.json"]},"framework_sha256":answer["framework_sha256"],"subtitle_status":"UNREAD_AT_LOCK"})
write("progress.json",{"status":"ANSWER_LOCKED_TARGET_UNREAD","completed":["framework manifest checked","first holdout selected before content read","sources acquired; one unavailable","answer frozen"],"pending":["record exposure then read only 472 fully","compare with continuous evidence","validate and render review"],"remaining_unread":15})
print(json.dumps(read(P/"answer_lock.json"),ensure_ascii=False,indent=2))