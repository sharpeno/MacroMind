import html
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def read(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))


c, f, s = read("case.json"), read("framework.json"), read("news_source.json")
e = html.escape
# Reuse only presentation style, not prior claims or analysis.
old = (OUT.parents[2] / "phase1/analyst_tracking/run_001/TRACE.html").read_text(encoding="utf-8")
style = old.split("<style>")[1].split("</style>")[0]
p = [
    '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>MacroMind｜冻结方法的首次应用</title><style>'
    + style
    + '</style><main><div class="muted">方法 v0.1 · 初始应用 · 2026-10-05</div><h1>证据不完整，仍然给出可修正的判断</h1><div class="note">五项方法已在案例读取前冻结。这里是助手使用候选框架的历史应用，不是博主对本案的观点，也不是预测成绩单。可以展开方法、查看原话、追溯新闻依据；本页无需填写审核表。</div><nav><a href="#baseline">基础判断</a><a href="#application">分析过程</a><a href="#news">新闻依据</a><a href="#rules">固定方法</a><a href="#limits">缺口与下一步</a></nav><section id="baseline"><h2>现在按什么来分析？</h2>'
]
for j in c["judgments"]:
    p.append(
        '<article id="'
        + j["id"]
        + '"><span class="tag">'
        + ("基础判断，可撤回" if j["status"] == "PROVISIONAL" else "事实状态，仍未知")
        + "</span><h3>"
        + e(j["statement"])
        + "</h3><p>"
        + e(j["scope"])
        + "</p><details><summary>什么证据会改变它？</summary><p>加强："
        + e(j["strengthen"])
        + "</p><p>削弱："
        + e(j["weaken"])
        + "</p><p>撤回/替换："
        + e(j["withdraw"])
        + "</p></details><p>推理依据："
        + " ".join('<a href="#' + x + '">' + x + "</a>" for x in j["supports"])
        + "</p></article>"
    )
p.append(
    "<p>"
    + e(c["operating_consequence"])
    + '</p></section><section id="application"><h2>五项方法如何使用</h2>'
)
labels = {
    "LIMITED": "证据有限",
    "APPLICABLE": "适用",
    "PARTIAL": "部分适用",
    "TRANSFER_LIMITED": "跨领域迁移，受限",
    "INITIAL_ONLY": "仅初始登记",
}
for a in c["applications"]:
    m = next(v for v in f["methods"] if v["id"] == a["method_id"])
    p.append(
        '<article id="app-'
        + m["id"]
        + '"><span class="tag">'
        + labels[a["applicability"]]
        + "</span><h3>"
        + m["id"]
        + " "
        + e(m["title"])
        + "</h3><p>"
        + e(a["working_judgment"])
        + "</p><details><summary>展开推理、替代解释与更新条件</summary><p>适用理由："
        + e(a["reason"])
        + "</p>"
    )
    for step in a["steps"]:
        p.append(
            '<div id="'
            + step["id"]
            + '"><strong>'
            + step["id"]
            + " · "
            + e(step["operation"])
            + "</strong><p>"
            + e(step["result"])
            + "</p><p>新闻依据："
            + " ".join('<a href="#' + v + '">' + v + "</a>" for v in step["evidence_refs"])
            + "</p></div>"
        )
    p.append(
        "<p>替代解释："
        + e(a["alternative"])
        + "</p><p>更新条件："
        + e(a["update_trigger"])
        + '</p><p class="muted">'
        + e(a["transfer_note"])
        + '</p></details><a href="#rule-'
        + m["id"]
        + '">查看冻结规则及博主原话</a></article>'
    )
p.append(
    '</section><section id="news"><h2>这次用了什么新闻</h2><p><a href="'
    + s["url"]
    + '" target="_blank" rel="noopener">'
    + e(s["title"])
    + "</a></p><p>报道时间：2026-08-31 23:51（北京时间）；案例截止：当日23:59:59。当前页面读取于2026-10-05，未取得当日网页存档。只核对报道内容，未独立核实战况。</p>"
)
for n in s["notes"]:
    p.append(
        '<article id="'
        + n["id"]
        + '"><strong>'
        + n["id"]
        + " · "
        + e(n["statement"])
        + '</strong><p class="muted">'
        + e(n["locator"])
        + "；报道归属保留。</p></article>"
    )
p.append(
    "<details><summary>关键原文选段</summary><blockquote>"
    + e(s["excerpt"])
    + '</blockquote><p>这句只能说明报道所述证据状态，不能推出事件未发生。</p></details></section><section id="rules"><h2>五项固定规则 v0.1</h2><p>冻结的是本轮应用规则。不是认证有效；后续修改须另起版本，保留此版。</p>'
)
records = {v["id"]: v for v in read("framework_evidence.json")}
for m in f["methods"]:
    p.append(
        '<article id="rule-'
        + m["id"]
        + '"><h3>'
        + e(m["id"] + " " + m["title"])
        + "</h3><p>适用："
        + e("；".join(m["applicability"]))
        + "</p><p>基础判断："
        + e(m["default_judgment"])
        + "</p><details><summary>执行步骤与不适用边界</summary><ol>"
        + "".join("<li>" + e(x) + "</li>" for x in m["procedure"])
        + "</ol><p>"
        + e(m["not_applicable_or_limited"])
        + "</p><p>"
        + e(m["update_rule"])
        + "</p></details><details><summary>支持本方法的博主原话</summary>"
    )
    for ref in m["refs"]:
        v = records[ref]
        p.append("<h4>" + e(ref + " · " + v["statement"]) + "</h4>")
        for q in v["quotes"]:
            p.append(
                '<blockquote><span class="muted">cue '
                + str(q["cue_id"])
                + " · "
                + e(q["time_range"])
                + "</span><br>"
                + e(q["quote"])
                + "</blockquote>"
            )
    p.append("</details></article>")
p.append(
    '</section><section id="limits"><h2>缺口与下一步</h2><ul>'
    + "".join("<li>" + e(x) + "</li>" for x in c["unresolved"])
    + '</ul><p>本轮完成的是“规则固定＋有依据的应用”。后续可补独立事实来源，或另行对照EP006讲解；不需要你先寻找更多后期视频。</p><a href="REPORT.md">本轮报告</a> · <a href="FRAMEWORK.md">方法文档</a></section></main><script>function reveal(){const id=decodeURIComponent(location.hash.slice(1));const el=document.getElementById(id);if(!el)return;let p=el.parentElement;while(p){if(p.tagName==="DETAILS")p.open=true;p=p.parentElement}el.scrollIntoView()}addEventListener("hashchange",reveal);if(location.hash)reveal();</script></html>'
)
(OUT / "TRACE.html").write_text("".join(p), encoding="utf-8")
print("Rendered application trace: 5 applications, 9 reasoning steps, 2 judgments, 5 news notes.")
