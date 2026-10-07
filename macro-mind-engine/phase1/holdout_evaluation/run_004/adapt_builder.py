from pathlib import Path
import json
P=Path("G:/youhegaojian/macro-mind-engine/phase1/holdout_evaluation/run_004")
rows=[
{"id":"C01","result":"PARTIAL_ALIGNMENT_POLICY_DIFFERENCE","system":"区分数据、市场加息定价、联储决定和援助执行。","blogger":"认为市场担忧短暂，既定停止加息节奏不会被几份数据轻易改变，但油价暴涨可能改变决定。","difference":"层次区分落实，但没有复现政策惯性、特定触发条件及其明确倾向。","ranges":[[367,431]]},
{"id":"C02","result":"TIMING_CONFLICT_MISSED","system":"列经济资源、外交信誉和安全约束。","blogger":"美国希望等国内经济与选举压力缓解，以色列担心等到那时美方不再帮助，于是双方时间偏好冲突。","difference":"静态成本比较不足，遗漏行动窗口和等待成本；这些动机解释不自动成为事实。","ranges":[[533,648]]},
{"id":"C03","result":"HIDDEN_CHANNEL_INFERENCE_MISSED","system":"把数据来源与角色分开，不直接补写政策动机。","blogger":"从收紧后消费仍超预期反推政府通过不显眼渠道注入资金，并联系选民利益。","difference":"遗漏以结果推断隐藏机制的思路；博主说“证实”，系统仍须单独记录证据与其他解释，不能用消费数据独立证明具体渠道。","ranges":[[432,495]]},
{"id":"C04","result":"PARTIAL_CHAIN_SUBSTANTIVE_CONCLUSION_GAP","system":"紧缩预期可能增加投入约束，但不从数据直接推断抛弃盟友。","blogger":"不再加息但维持高息→国内调整未完→以方此时迫使介入会消耗资源→美方不愿被绑定，并作很强的判断。","difference":"宏观约束方向有交集，但政策路径、时间结构和结论确信度不同；不能标为同一预测。","ranges":[[496,648]]},
{"id":"C05","result":"HYPOTHESIS_PROTOCOL_IMPLEMENTED_NOT_EQUIVALENT","system":"H01/H02/H03均有依据、假设、后续观察及更新方向。","blogger":"对同一数据同时提出通胀压力与资金托底解释，并给出自己的政策倾向；本期还更新医院责任判断。","difference":"多情景流程落实，但不等于已还原作者排序；医院更新依赖本输入未取得的素材，事实另行核验。","ranges":[[0,13],[432,532]]},
{"id":"C06","result":"PATH_DEPENDENCE_AND_CONFIDENCE_GAP","system":"保留不同援助路径及退出阈值未明。","blogger":"强调以方等待会失去窗口、既有行为使回头更难，同时强断言美方不会被绑上战车。","difference":"系统保持路径开放，未复现作者时间与不可逆成本论证；应保留差异，不把修辞性的切割等同全部援助终止。","ranges":[[533,648]]}
]
review=[
{"id":"R01","title":"是否区分市场的加息担忧、政策惯性与真正触发条件？","finding":"博主认为零售数据引发的市场恐慌会消退，既定停止加息节奏不易被几份国内数据改变；他把油价突然大涨列为可能迫使继续加息的因素。原答案虽然区分市场定价与正式政策，却没有还原这套排序及明确倾向。","question":"这样归纳是否准确？保留博主的政策与收益率判断，但不把它当成已验证结果，也不将“不再加息”误写为马上降息。","ranges":[[367,431],[496,532]]},
{"id":"R02","title":"是否保留了从消费结果反推资金渠道的推理？","finding":"博主对同一数据给出两层解释：通胀压力仍在，同时消费韧性显示政府通过不显眼渠道投放资金、照顾核心选民。他承认具体管道看不到，却将消费上涨视为此前判断获证实。系统没有还原这种由结果反推机制的思路。","question":"是否忠实保留了可见结果、作者推断的机制和其确信程度？核验时仍需与收入、信贷、价格等其他解释比较，不能由单组名义零售数据独立确认具体资金渠道。","ranges":[[432,495]]},
{"id":"R03","title":"是否漏掉美以双方不同的时间窗口与等待成本？","finding":"博主认为美国想等国内经济和选举压力缓解再处理地区投入，以色列却担心等待会失去美方支持，因而必须在此时施压。他据此强烈判断美国不会被绑上战车。系统只列一般资源约束和多个分支，没有充分表达双方等待成本不一致的冲突。","question":"是否准确保留“谁能等、谁不能等、为何此时行动”的机制及作者的强判断？这里的切割/不被绑定不能未经界定就等同于全部军援停止。","ranges":[[533,648]]}
]
s=(P.parent/"run_003/build_comparison.py").read_text(encoding="utf-8")
start=s.index("rows=");end=s.index("for card in review:")
s=s[:start]+"rows=json.loads("+repr(json.dumps(rows,ensure_ascii=False))+")\nreview=json.loads("+repr(json.dumps(review,ensure_ascii=False))+")\n"+s[end:]
s=s.replace("474","475").replace("684","655").replace("683","654").replace("第三例","第四例")
s=s.replace('"remaining_unread_episodes":["475","476"','"remaining_unread_episodes":["476"')
s=s.replace("其余12份","其余11份").replace("12 reserved","11 reserved").replace("前两期反馈","前三期反馈")
s=s.replace('"range":[460,496],"theme":"美国低成本维持地区秩序的战略解释未充分展开"','"range":[0,276],"theme":"医院责任、弹药技术与舆论代价推理未匹配；输入缺失对应新证据，不做技术归责验收"')
# Make precommitted hypothesis details visible, not just recorded in JSON.
anchor="page+='<h3>封存的身份与态度记录</h3>'"
insert="""page+='<h3>封存的候选解释与更新条件</h3>'
for h in answer["hypotheses"]:page+='<h4>'+esc(h["id"]+' '+h["claim"])+'</h4><p>依据：'+esc('、'.join(h["basis"]))+'；假设：'+esc(h["assumptions"])+'</p><p>后续观察：'+esc(h["discriminating_observations"])+'</p><p>更新方向：'+esc(h["update"])+'</p>'
"""
s=s.replace(anchor,insert+anchor)
s=s.replace("新闻输入与博主未必等量","一篇访问新闻未获取，新闻输入与博主未必等量")
(P/"build_comparison.py").write_text(s,encoding="utf-8")