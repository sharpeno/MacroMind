from pathlib import Path
import json
P=Path("G:/youhegaojian/macro-mind-engine/phase1/holdout_evaluation/run_003")
rows=[
{"id":"C01","result":"PARTIAL_ALIGNMENT","system":"区分谴责、取消会晤与执行建议。","blogger":"进一步把美方支持承诺与交付能力、时点和责任解释分开，将强硬支持话语解释为潜在甩责。","difference":"阶段区分一致，但具体话语功能未复现；两者资料范围不同。","ranges":[[497,534]]},
{"id":"C02","result":"MECHANISM_GAP","system":"分析会晤取消、公众压力与协调依赖。","blogger":"提出多环节参与导致责任分散、难以停机排查，失误后仍可能持续升级；另指出高层协调不能控制基层触发。","difference":"系统主要分析外部政治约束，内部执行与控制机制不足。不能把博主机制解释直接视为已证实原因。","ranges":[[23,56],[345,392],[601,662]]},
{"id":"C03","result":"CONDITIONAL_HYPOTHESES_MISSED","system":"不定责任，列施压等动机但没有具体区分计划。","blogger":"倾向不信以方解释，却对是否有意保留问号；分为有意给拜登谈判施压和非预期打击后失控升级，并以后续是否继续攻击民用设施判断。","difference":"保留不确定性不应省略假说、观察指标和更新方向；博主以技术/概率作判断的前提未独立验证，后续行为也不能唯一证明先前意图。","ranges":[[134,303],[328,392],[429,459]]},
{"id":"C04","result":"PARTIAL_TRANSMISSION_DIFFERENT_BRANCHES","system":"公众反应→取消会晤→协调受阻→风险预期上升。","blogger":"在有意施压分支中，进一步推演以色列以失控升级威胁迫使美国上桌；另把伊朗的停止行动要求解读为介入铺垫。","difference":"系统有条件链，但没有复现对手选择受限→表态的策略用途；未采用博主更强的行动断言。","ranges":[[429,534],[535,598]]},
{"id":"C05","result":"UPDATE_PROCESS_PARTIAL","system":"明确相对472/473调整协调可执行性。","blogger":"给出后续行为用来辨别两个动机分支，同时在后文重申给拜登下马威只是猜测之一。","difference":"系统有更新意识，欠缺区分性观察设计；不能将同一指标当作排他的因果检验。","ranges":[[274,303],[328,392],[567,598]]},
{"id":"C06","result":"SUBSTANTIVE_DIVERGENCE","system":"不把未达成写成绝无退出，讨论替代外交路径。","blogger":"以追责压力和战时无法停止排查解释以方为何难退出，部分措辞更绝对。","difference":"系统边界与博主强判断存在差异，应同时保留，不能把弱化后的表述冒充原话。","ranges":[[51,113],[345,392]]}
]
review=[
{"id":"R01","title":"是否保留了两种情景和用来区分它们的后续观察？","finding":"博主倾向不信以方解释，但对是否有意打击另留问号：一支是借事件向拜登施压、增加谈判筹码，另一支是非预期打击后在责任分散中持续升级。他用后续是否继续攻击民用设施作为区分线索。系统只保留动机未定，没有把假说与观察计划展开。","question":"这是否忠实保留责任倾向、意图不确定性和分支？技术/概率说法未独立验证，后续停止或继续也不能单独证明此前意图；这些是系统核验边界，不替换博主原判断。","ranges":[[134,303],[328,392],[429,459]]},
{"id":"R02","title":"是否分析了公开表态怎样约束对方、为后续行动铺垫？","finding":"系统记录了身份和公开态度；博主还将美方支持话语解释为可用交付限制甩责，将伊朗要求停止行动解释为在对方难以满足要求时为介入铺垫。他对伊朗说出强断言，但对以方给拜登设局仍明确称为一种猜测。","question":"是否准确分开讲话内容、角色与策略解释，以及不同命题的确信程度？保留博主的断言不等于我们已经证实伊朗必然采取何种行动。","ranges":[[497,598]]},
{"id":"R03","title":"是否漏掉了内部责任链与高层控制的局限？","finding":"博主解释多环节参与会分散责任，战时难以停下排查，可能使越线反复发生；又指出高层关系安排无法确保基层事件不改变全局。系统主要分析外部外交受阻，没有充分展开内部执行与控制机制。","question":"这样归纳是否合适？应保留“多环节—责任分散—难以纠偏—持续升级”的机制及场景，不将它泛化为任何多人决策都必然失控。","ranges":[[23,56],[345,392],[601,662]]}
]
s=(P.parent/"run_002/build_comparison.py").read_text(encoding="utf-8")
start=s.index("rows=");end=s.index("for card in review:")
s=s[:start]+"rows=json.loads("+repr(json.dumps(rows,ensure_ascii=False))+")\nreview=json.loads("+repr(json.dumps(review,ensure_ascii=False))+")\n"+s[end:]
s=s.replace("473","474").replace("551","684").replace("550","683").replace("第二例","第三例")
s=s.replace('[[0,229],[230,683]]','[[0,229],[230,459],[460,683]]')
s=s.replace('"remaining_unread_episodes":["474","475"','"remaining_unread_episodes":["475"')
s=s.replace("其余13份","其余12份").replace("13 reserved","12 reserved")
s=s.replace("一篇原新闻无法获取、输入与博主未必等量","新闻输入与博主未必等量")
s=s.replace("承接第472期反馈","承接前两期反馈")
s=s.replace('"range":[139,184],"theme":"美国收缩与以色列挽留的结构矛盾未充分展开"','"range":[460,496],"theme":"美国低成本维持地区秩序的战略解释未充分展开"')
(P/"build_comparison.py").write_text(s,encoding="utf-8")