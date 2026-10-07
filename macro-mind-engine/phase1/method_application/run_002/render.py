import html
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def read(n):
    return json.loads((OUT / n).read_text(encoding="utf-8"))


f, c, s = read("framework.json"), read("case.json"), read("source.json")
e = html.escape
style = (
    (ROOT / "phase1/method_application/run_001/TRACE.html")
    .read_text(encoding="utf-8")
    .split("<style>")[1]
    .split("</style>")[0]
)
p = [
    '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>MacroMind｜v0.2方法与新案例</title><style>'
    + style
    + '</style><main><div class="muted">研究候选 v0.2 · 2026-10-05</div><h1>分析利益和动机，也保留其他解释</h1><div class="note">三项补强已落实，v0.1和原答案保留。新案例是欧洲央行2025年6月5日利率决定。本页由助手使用候选框架分析，不代表9527对该事件的看法。历史应用，非盲测，非当前投资建议。</div><nav><a href="#changes">方法改了什么</a><a href="#case">新案例判断</a><a href="#actors">参与者与依赖</a><a href="#steps">五项方法应用</a><a href="#sources">官方依据</a></nav><section id="changes"><h2>三项补强</h2>'
]
lines = [
    "# 方法v0.2与新材料应用",
    "",
    "已将P01/P02/P03落实到M01/M02/M04；M03/M05保留原规则。v0.1和首轮答案不改。冻结规则在新案例读取前完成。",
    "",
    "## 方法规则",
    "",
]
for m in f["methods"]:
    p.append(
        '<article id="'
        + m["id"]
        + '"><h3>'
        + e(m["id"] + " " + m["title"])
        + "</h3><details><summary>查看执行规则、输入与边界</summary><p>输入："
        + e("；".join(m["required_inputs"]))
        + "</p><ol>"
        + "".join("<li>" + e(x) + "</li>" for x in m["procedure"])
        + "</ol><p>"
        + e(m["default_judgment"])
        + "</p><p>"
        + e(m["not_applicable_or_limited"])
        + "</p><p>"
        + e(m["update_rule"])
        + "</p></details></article>"
    )
    lines += (
        ["### " + m["id"] + " " + m["title"], "", "输入：" + "；".join(m["required_inputs"]), ""]
        + [str(i) + ". " + x for i, x in enumerate(m["procedure"], 1)]
        + [
            "",
            "基础判断：" + m["default_judgment"],
            "",
            "边界：" + m["not_applicable_or_limited"],
            "",
            "更新：" + m["update_rule"],
            "",
        ]
    )
p.append(
    '</section><section id="case"><h2>新案例的基础判断</h2><article><h3>'
    + e(c["baseline"]["text"])
    + "</h3><p>公开目标与措施部分匹配，没有材料迫使我们采用“隐藏目的”解释；这也不证明不存在未公开因素。</p><details><summary>什么证据会改变判断？</summary><p>加强："
    + e(c["baseline"]["strengthen"])
    + "</p><p>削弱："
    + e(c["baseline"]["weaken"])
    + "</p><p>撤回："
    + e(c["baseline"]["withdraw"])
    + '</p></details></article></section><section id="actors"><h2>谁受影响，依赖谁</h2>'
)
for a in c["actors"]:
    p.append(
        "<article><h3>"
        + e(a["id"] + " · " + a["role"])
        + "</h3><p>"
        + e(a["gain_or_cost"])
        + "</p><p>"
        + e(a["dependency"])
        + '</p><span class="tag">'
        + ("公开目标" if a["status"] == "PUBLIC_GOAL" else "助手机制假说，待验证")
        + "</span></article>"
    )
p.append('</section><section id="steps"><h2>五项方法如何使用</h2>')
for a in c["applications"]:
    p.append(
        "<article><h3>"
        + a["id"]
        + "</h3><p>"
        + e(a["result"])
        + "</p><details><summary>更新条件与依据</summary><p>"
        + e(a["next"])
        + "</p>"
        + "".join('<a href="#' + v + '">' + v + "</a> " for v in a["refs"])
        + "</details></article>"
    )
p.append("<h3>条件传导与阻断</h3>")
for x in c["causal_links"]:
    p.append(
        "<article><strong>"
        + e(x["from"] + " → " + x["to"])
        + "</strong><p>条件："
        + e(x["condition"])
        + "</p><p>可能阻断："
        + e(x["break"])
        + '</p><p class="muted">助手假说；不是已观察到的结果。</p></article>'
    )
p.append(
    '</section><section id="sources"><h2>官方依据与限制</h2><a target="_blank" rel="noopener" href="'
    + s["url"]
    + '">欧洲央行原始发布 · 2025-06-05</a>'
)
for n in s["notes"]:
    p.append(
        '<article id="'
        + n["id"]
        + '"><strong>'
        + n["id"]
        + " "
        + e(n["text"])
        + "</strong><p>"
        + e(n["locator"])
        + "</p></article>"
    )
p.append(
    "<blockquote>"
    + e(s["excerpt"])
    + "</blockquote><p>"
    + e(s["limits"])
    + "</p><ul>"
    + "".join("<li>" + e(x) + "</li>" for x in c["limits"])
    + '</ul><p>这里是阅读页，无需填审核表。可以根据M编号指出规则问题。</p><a href="REPORT.md">报告与未完成项</a> · <a href="../../method_comparison/run_001/TRACE.html">EP006诊断依据</a></section></main></html>'
)
(OUT / "TRACE.html").write_text("".join(p), encoding="utf-8")
(OUT / "FRAMEWORK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Rendered v0.2 rules, 5 applications, 4 actors, 3 conditional links.")
