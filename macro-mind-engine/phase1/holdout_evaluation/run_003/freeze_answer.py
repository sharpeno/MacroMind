import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
P=Path(__file__).resolve().parent;ROOT=P.parents[2];read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):(P/n).write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
now=lambda:datetime.now(timezone.utc).isoformat()
facts=[
{"id":"F01","text":"报道提及医院爆炸与重大伤亡，并同时记载巴方指责以军、以军否认并指责杰哈德。","status":"伤亡报道与各方责任指控分开；责任和确切伤亡未独立确定"},
{"id":"F02","text":"报道引述阿巴斯称，他与约旦、埃及领导人决定取消在安曼与拜登的会晤。","status":"报道中的宣布；会晤渠道受阻，不等于全部外交终止"},
{"id":"F03","text":"多国及国际组织公开谴责，呼吁制止暴力、保护医疗与平民。","status":"不同主体和角色的公开态度，不能合并为同一实施安排"},
{"id":"F04","text":"报道记载土耳其外长提出未来协议可由其他国家担保执行，以及德国总理表达防止外溢的意向。","status":"方案与立场，不等于协议存在或执行"},
]
write("news_input.json",{"source":read(P/"retrieval_log.json"),"display_date":"2023-10-18 08:38","facts":facts,"inherited_context":"472/473 already exposed; prior analyst explanations are context, not independently verified news","limits":["single composite report, multiple attributed statements","responsibility disputed","exact target publication time unknown","no market time series","historical event and earlier future snippets known; not strict blind backtest"]})
rules=[
{"id":"C01","analysis":"谴责、取消会面、提出担保机制应分别记为立场、安排变更与政策建议。会晤取消已是明确的新限制，不能等到全局结果确认才更新；也不能从谴责推成军事介入。","base":"拜登通过原安曼会晤协调的空间已受损，其他渠道仍可能存在。","trigger":"会晤恢复、替代沟通、实际援助/停火安排分别更新。"},
{"id":"C02","analysis":"医院事件及舆论压力与美国支持以色列的姿态相撞；阿拉伯领导人参加会面的政治成本可能上升。会晤取消提示美国协调依赖对方合作，不能独自决定外交成效。","base":"降温协调难度上升，公开切割与私下沟通可并存。","trigger":"替代会晤、共同声明或现场执行支持协调恢复；继续拒绝和升级削弱它。"},
{"id":"C03","analysis":"结合访问前夕、公开指责及取消会晤，事件客观上使美国更难同时维持盟友支持与地区协调。可列各方借机施压或表达立场的动机假说；仅凭时间与受益，不能认定谁策划爆炸或给拜登制造下马威。","base":"先判断约束与博弈后果，再保留动机分支；责任归属不填定论。","trigger":"独立取证、可核查决策信息和后续互动分别改变责任或动机判断。"},
{"id":"C04","analysis":"伤亡报道→公众愤怒/参与成本→会晤取消→协调路径收窄→冲突外溢风险预期可能上升，是可先提出的条件链。若影响供应或运输担忧，可能传导市场；输入没有价格数据，不能声称油价已涨或实际供给已下降。","base":"相较此前协调基线，提高短期外交受阻与扩散担忧的权重，保留替代沟通缓和分支。","trigger":"实际地区介入、供应/运输变化和市场数据到来后逐环核对，考虑同时期其他驱动。"},
{"id":"C05","analysis":"新取消会晤信息使第472期“支持并协调”的基础分支受挫，第473期合作可能稳定预期的推演也不能当作自动奏效。调整的是协调可执行性，不据此宣称美国必然全面参战或永久退出。","base":"降低原定高层会晤近期促成协调的判断，维持后续更新。","trigger":"按新事实另存变化，不回写472/473答案；短期挫折不自动等于长期战略失效。"},
{"id":"C06","analysis":"未来协议担保是潜在实施机制，但无具体协议、权限、履约与退出标准。可以分析替代路径，不把建议写成已解决冲突。","base":"维持外交与执行安排尚待形成的判断；不把未达成写成逻辑上无出路。","trigger":"明确条款、参与方、执行约束和验证条件出现后评估。"}
]
speakers=[
{"speaker":"阿巴斯","role":"巴勒斯坦总统","event":"医院事件及安曼会晤","observed":"谴责并宣布与其他领导人取消会晤","stance":"反对事件所涉暴力，拒绝原会晤安排","motive_hypothesis":"表达政治抗议、回应社会压力、施加外交约束","scope":"假说；不能由取消会晤推出策划事件"},
{"speaker":"以色列国防军","role":"以方军事机构","event":"医院爆炸责任争议","observed":"否认责任并提出另一归责","stance":"否定自身责任","motive_hypothesis":"公开解释与维护合法性，真实与否须另行取证","scope":"机构表态不是独立调查结论"},
{"speaker":"土耳其外长","role":"土耳其政府外交代表","event":"未来和平安排","observed":"提出第三方担保","stance":"支持通过协议与担保促成长期和平","motive_hypothesis":"争取调解参与、推动稳定","scope":"建议与实施分开"}
]
answer={"case":"conflict_474","created_at":now(),"framework_sha256":sha(ROOT/"phase1/framework_review/v03_frozen_001/framework.json"),"news_input_sha256":sha(P/"news_input.json"),"subtitle_semantically_read":False,"speaker_ledger":speakers,"rules":rules,"overall":"医院事件及取消安曼会晤，已使美国按原计划协调地区关系的空间收窄。先形成外交受阻与短期风险预期上升的基础判断；仍保留替代沟通。事件责任与具体策划动机维持未定，不从政治后果倒推确定实施者。","unresolved":["责任归属与伤亡规模未经独立核验","未来对军事部署和长期秩序的影响未确定","无价格数据，不给方向准确率"]}
write("answer_before_subtitle.json",answer)
write("answer_lock.json",{"locked_at":now(),"files":{n:sha(P/n) for n in ["protocol.json","target_metadata.json","news_input.json","answer_before_subtitle.json"]},"subtitle_status":"UNREAD_AT_LOCK"})
write("progress.json",{"status":"ANSWER_LOCKED_TARGET_UNREAD","completed":["sources and adaptive protocol saved","answer frozen"],"pending":["record exposure and read474","comparison and QA"]})
print(json.dumps(read(P/"answer_lock.json"),ensure_ascii=False,indent=2))