import html
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
p = json.loads((OUT / "comparison.json").read_text(encoding="utf-8"))
base = json.loads((ROOT / p["baseline_path"]).read_text(encoding="utf-8"))
e = html.escape
style = (
    (ROOT / "phase1/method_application/run_001/TRACE.html")
    .read_text(encoding="utf-8")
    .split("<style>")[1]
    .split("</style>")[0]
)
parts = [
    '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>MacroMind｜EP006方法忠实度对照</title><style>'
    + style
    + '</style><main><div class="muted">EP006 · 对照已封存答案 · 2026-10-05</div><h1>有方法对应，也发现了分析重点的遗漏</h1><div class="note"><strong>结论：部分方法对应，尚不足以验收完整忠实度。</strong><p>'
    + e(p["finding"])
    + "</p><p>"
    + e(p["comparability_note"])
    + '</p>原答案和v0.1规则未改。这里是定性对照，不提供相似率、预测分数或事实认证。</div><nav><a href="#methods">逐方法对照</a><a href="#judgments">原判断能否检验</a><a href="#proposals">改进建议</a><a href="#quotes">博主原话</a><a href="../../method_application/run_001/TRACE.html">查看封存原答案</a></nav><section id="methods"><h2>五项方法逐项对照</h2>'
]
lines = [
    "# EP006与封存应用的定性对照",
    "",
    "2026-10-05。范围：用户授权进行上一轮建议的EP006对照；不改写原应用，不实施v0.2。",
    "",
    "## 结论",
    "",
    p["finding"],
    "",
    p["comparability_note"],
    "",
    "不能验收完整方法忠实度；也不能因同题同材料条件不成立而直接判框架无效。结果是诊断，不是准确率测量。",
    "",
]
for m in p["method_comparisons"]:
    original = next(a for a in base["applications"] if a["method_id"] == m["method_id"])
    verdict = "部分对应" if m["verdict"] == "PARTIAL" else "本轮不可直接检验"
    parts.append(
        '<article id="'
        + m["method_id"]
        + '"><span class="tag">'
        + verdict
        + "</span><h3>"
        + m["method_id"]
        + "</h3><p><strong>原应用：</strong>"
        + e(original["working_judgment"])
        + "</p><p><strong>相同处：</strong>"
        + e(m["same"])
        + "</p><p><strong>差距：</strong>"
        + e(m["gap"])
        + "</p><details><summary>差异原因与判断依据</summary><p>"
        + e(m["assessment"])
        + "</p><p>原推理编号："
        + e("、".join(m["baseline_refs"]))
        + "</p><p>博主证据："
        + " ".join('<a href="#' + x + '">' + x + "</a>" for x in m["blogger_refs"])
        + "</p></details></article>"
    )
    lines += [
        "## " + m["method_id"] + "：" + verdict,
        "",
        "原应用：" + original["working_judgment"],
        "",
        "相同：" + m["same"],
        "",
        "差距：" + m["gap"],
        "",
        "判断：" + m["assessment"],
        "",
        "依据：" + "、".join(m["blogger_refs"]) + "；原应用步骤：" + "、".join(m["baseline_refs"]),
        "",
    ]
parts.append('</section><section id="judgments"><h2>两个原判断能否检验</h2>')
lines += ["## 两项原判断", ""]
for j in p["judgment_comparisons"]:
    parts.append(
        "<article><h3>"
        + j["id"]
        + "</h3><p>"
        + e(j["baseline_statement"])
        + "</p><p>"
        + e(j["reason"])
        + "</p></article>"
    )
    lines += ["- " + j["id"] + "：" + j["reason"]]
parts.append('</section><section id="proposals"><h2>三项改进建议：尚未写入规则</h2>')
lines += ["", "## 改进建议（未实施）", ""]
for s in p["improvement_proposals"]:
    parts.append(
        "<article><h3>"
        + e(s["title"])
        + "</h3><p>"
        + e(s["suggestion"])
        + "</p><p><strong>反向检查：</strong>"
        + e(s["countercheck"])
        + "</p>"
        + " ".join('<a href="#' + x + '">' + x + "</a>" for x in s["source_refs"])
        + "</article>"
    )
    lines += ["- " + s["title"] + "：" + s["suggestion"] + " 反向检查：" + s["countercheck"]]
parts.append(
    '</section><section id="quotes"><h2>博主原话与边界</h2><p>完整读取363条自动字幕，选取8组相关单元；未逐句核听。以下内容是博主的陈述、归因或推测，不自动升级为事实。</p>'
)
for u in p["blogger_units"]:
    time = u["quotes"][0]["time_range"].split(" --> ")[0].replace(",", ".").split(":")
    sec = int(float(time[0]) * 3600 + float(time[1]) * 60 + float(time[2]))
    parts.append(
        '<article id="'
        + u["id"]
        + '"><h3>'
        + e(u["id"] + " " + u["title"])
        + "</h3><p>"
        + e(u["statement"])
        + '</p><p class="note">'
        + e(u["boundary"])
        + '</p><a target="_blank" rel="noopener" href="https://www.bilibili.com/video/BV1qNtG6vE32/?t='
        + str(sec)
        + '">打开原视频核听</a><details><summary>展开原话（'
        + str(len(u["quotes"]))
        + "个片段）</summary>"
    )
    for q in u["quotes"]:
        parts.append(
            '<blockquote><span class="muted">cue '
            + str(q["cue_id"])
            + " · "
            + e(q["time_range"])
            + "</span><br>"
            + e(q["quote"])
            + "</blockquote>"
        )
    parts.append("</details></article>")
parts.append(
    "</section><section><h2>下一步</h2><p>"
    + e(p["next_step"])
    + '</p><p>本页是对照报告，不需要填写审核表。若认为某条对照不忠实，可直接告诉我M编号或B编号。</p><a href="REPORT.md">完整报告和验证记录</a></section></main></html>'
)
(OUT / "TRACE.html").write_text("".join(parts), encoding="utf-8")
lines += [
    "",
    "## 范围与限制",
    "",
    "基线已封存于读取EP006讲解之前；本轮核验原包92项产物哈希。原始材料及既有数据保持不变。先前不是严格盲测，本轮也不补写成盲测。",
    "",
    "完整读取363条自动字幕，选8组方法相关单元；不声称穷尽提取。原话、时间与归属在comparison.json及segments.json。原始字幕与信息说明复制到sources，疑似错字和专名未擅自修订。没有外部事实核验；本期的高强度动机归因与极端情景保留为博主解释，不采纳为事实。",
    "",
    "制裁参与者、政治人事等材料不在原应用的单篇新闻底座内。把这些缺失记为输入/问题范围差异，同时记录规则对行为反推、多主体关系的不足；两类原因不能相互替代。",
    "",
    "## 下一步",
    "",
    p["next_step"],
    "",
    "工程验证与未决项见PROGRESS.md、validation.json及同名command/stdout/stderr/result文件。",
]
(OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Rendered 5 method comparisons, 2 original judgments, 3 proposals, 8 evidence groups.")
