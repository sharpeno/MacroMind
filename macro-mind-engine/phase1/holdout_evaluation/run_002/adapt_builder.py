import json
from pathlib import Path
P=Path("G:/youhegaojian/macro-mind-engine/phase1/holdout_evaluation/run_002")
rows=[
{"id":"C01","result":"PARTIAL_ALIGNMENT","system":"分开到访、合同、未来执行与效果。","blogger":"从到访姿态和接待安排推断俄方认可合作格局；从合同推演示范与制度吸引。","difference":"阶段区分保留，但遗漏行动本身的信号及示范作用；不能只等执行收益才分析。","ranges":[[11,82],[489,544]]},
{"id":"C02","result":"PARTIAL_ALIGNMENT","system":"俄罗斯可能获外交机会，但资源转移未知。","blogger":"把普京亲自到访与姿态联系到巴以冲突后俄方压力降低；并分析美国收缩与以色列挽留的矛盾。","difference":"方向部分接近，系统没有形成行动→压力/约束变化的明确推断。博主的事实前提和解释未独立核验。","ranges":[[11,82],[139,184]]},
{"id":"C03","result":"ROLE_LEDGER_IMPLEMENTED_SIGNAL_INFERENCE_GAP","system":"记录普京代表身份和到访，明确没有讲话；动机仅列合作。","blogger":"利用亲自来访、动作和接待规格识别国家态度与压力；并非必须找到一段讲话才分析。","difference":"身份记录已落实，但从行动反推隐含状态仍较弱；消息缺失与推演停止之间需区分。","ranges":[[11,82]]},
{"id":"C04","result":"KEY_TRANSMISSION_CHAIN_MISSED","system":"等待油气协议或供给资料，暂不单向调整油价判断。","blogger":"以会议凝聚发展合作力量→争斗需求减弱→中东失序及供应风险预期下降解释油价，并判断因中东崩盘而暴涨的剧本不太可能。","difference":"系统把预期变化过多绑定实体供应协议，遗漏外交合作本身可能影响风险预期的渠道。不能因此认定博主的因果解释已被证实。","ranges":[[83,113],[391,442]]},
{"id":"C05","result":"PARTIAL_UPDATE_REPRESENTATION","system":"维持472基线，追加论坛及合同信息。","blogger":"将到访、论坛与其描述的市场变化结合，强化合作稳定局势的判断。","difference":"原答案没有生成这种更新路径；输入缺少油价数据，不能按方向准确率评分。","ranges":[[391,442]]},
{"id":"C06","result":"INSUFFICIENT_MATCHED_EXIT_EVIDENCE","system":"提醒缺少战略完成和退出条件。","blogger":"重点在路径吸引力、资源取舍和未来预期，并非明确退出契约。","difference":"本例不能证明退出规则有效；另有合同→示范→技术回流→市场整合的长链未覆盖。","ranges":[[269,390],[471,544]]}
]
review=[
{"id":"R01","title":"行动本身是否也要作为角色与态度的信号？","finding":"原答案已登记普京的国家领导人身份，却主要停在“来访、寻求合作”。博主进一步从亲自来访、姿态与接待安排推断俄罗斯压力减轻及认可合作格局。我们记为身份记录落实，但行动信号的推断仍不充分。","question":"是否准确归纳了遗漏？这里保留的是博主的解释，不把动作或接待规格直接当作确定的内心证明。原话中的“俄乌冲突以来第一次出国”等事实前提未独立核实。","ranges":[[11,82]]},
{"id":"R02","title":"影响油价预期，是否不必等到具体供给协议？","finding":"博主提出会议凝聚合作与发展预期→各方争斗需求下降→中东失序及供应风险担忧缓和的链条。系统主要等油气协议和供给数据，漏掉了外交合作影响风险预期的渠道。该推演可以先作为基础假说，不等于已经证明会议导致价格变化。","question":"这条链是否忠实？是否准确区分“少了预期传导推演”与“没有事实证实因果”？","ranges":[[83,113],[391,442]]},
{"id":"R03","title":"铁路合同的意义是否还包括示范和吸引力？","finding":"原答案只强调签约与执行不同。博主则从向欧洲出口，推到技术回流、市场整合和合作示范；又把各国交流成功经验解释为增强对未来发展的向往与凝聚力。我们记为遗漏较长的制度吸引链，而不是合同已经证明所有远期结果。","question":"是否准确保留了案例→示范→合作吸引的层次？两段证据展示的是本期相互关联的论述，不能把中间所有假设写成已实现。","ranges":[[269,390],[489,544]]}
]
s=(P.parent/"run_001/build_comparison.py").read_text(encoding="utf-8")
start=s.index("rows=[");end=s.index("for card in review:")
s=s[:start]+"rows=json.loads("+repr(json.dumps(rows,ensure_ascii=False))+")\nreview=json.loads("+repr(json.dumps(review,ensure_ascii=False))+")\n"+s[end:]
s=s.replace("472","473").replace("643","551").replace("642","550")
s=s.replace('[[0,229],[230,459],[460,550]]','[[0,229],[230,550]]')
s=s.replace('"remaining_unread_episodes":["473","474"','"remaining_unread_episodes":["474"')
s=s.replace('"range":[446,531],"theme":"历史行动效果依赖当时环境，不能机械复制旧成功"','"range":[139,184],"theme":"美国收缩与以色列挽留的结构矛盾未充分展开"')
s=s.replace("历史材料上的","历史材料上的")
s=s.replace("原新闻失效","原新闻无法获取")
s=s.replace("其余14份","其余13份").replace("14 reserved","13 reserved")
s=s.replace("action","action")
s=s.replace('esc(r["trigger"])','esc(r["trigger"])')
s=s.replace('系统识别','系统识别')
# Surface the actual pre-registered speaker ledger alongside the answer.
s=s.replace("page+='</details><p><a href=\"answer_before_subtitle.json\">", """page+='<h3>封存的身份与态度记录</h3>'
for actor in answer["speaker_ledger"]:page+='<p>'+esc(actor["speaker"]+'｜'+actor["role"]+'｜'+actor["observed"]+'｜公开态度：'+actor["stance"]+'｜动机假说：'+actor["motive_hypothesis"])+'</p>'
page+='</details><p><a href="answer_before_subtitle.json">""")
(P/"build_comparison.py").write_text(s,encoding="utf-8")