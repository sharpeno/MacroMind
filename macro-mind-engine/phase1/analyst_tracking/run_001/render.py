import html
import json
from pathlib import Path

out = Path(__file__).resolve().parent
p = json.loads((out / "analysis.json").read_text(encoding="utf-8"))
e = html.escape
parts = [
    '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><link rel="icon" href="data:,"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MacroMind｜五期美联储判断追踪</title><style>body{margin:0;background:#f3f6f4;color:#183b35;font:18px/1.75 system-ui,"Microsoft YaHei",sans-serif}main{max-width:1080px;margin:auto;padding:30px 22px 70px}h1{font-size:32px;line-height:1.35}h2{margin-top:40px}h3{line-height:1.4}a{color:#006e61;overflow-wrap:anywhere}article,.note{background:white;border:1px solid #ccdcd5;border-radius:12px;padding:22px;margin:18px 0}.note{background:#fff6df}nav{display:flex;gap:16px;flex-wrap:wrap}summary{cursor:pointer;font-weight:600}blockquote{margin:14px 0;padding:14px;border-left:4px solid #88a99b;background:#f3f7f5;white-space:pre-wrap;overflow-wrap:anywhere}.muted{font-size:15px;color:#4e655e}.tag{font-size:14px;padding:4px 9px;border-radius:4px;background:#dfede5}.timeline{border-left:3px solid #69998a;padding-left:22px}.refs{display:flex;gap:10px;flex-wrap:wrap}section,article{scroll-margin-top:20px}@media(max-width:600px){main{padding:18px 14px}h1{font-size:25px}article{padding:16px}body{font-size:17px}}</style><main><div class="muted">9527 · 跨期方法提炼 · 2026-10-05</div><h1>从讲话到数据，再到决策后的新问题</h1><p>EP007、EP008 补入较早的时间段，与 EP001—EP003 连成一条可追溯的讨论线。</p><div class="note"><strong>这是分析阅读页，无需重复审核首五期。</strong><br>点击证据编号可跳到对应主张，展开查看原话和时间；视频链接定位到首个片段。新增内容由助手提取，尚未经人工审核。发布日期来自用户材料，外部新闻与政策结果未独立核验。以下为事后重建，不是预测成绩单。</div><nav><a href="#timeline">五期时间线</a><a href="#connections">跨期连接</a><a href="#methods">方法候选</a><a href="#issues">待补证</a><a href="#evidence">原话证据</a><a href="REPORT.md">完整报告</a></nav>'
]


def refs(ids):
    return '<div class="refs">' + "".join(f'<a href="#{e(x)}">{e(x)}</a>' for x in ids) + "</div>"


parts.append('<section id="timeline"><h2>判断如何变化</h2><div class="timeline">')
for n in p["chronology"]:
    ep = p["episodes"][n["episode"]]
    parts.append(
        f'<article><span class="tag">{e(ep["published_at"])} · {e(n["episode"])}</span><h3>{e(n["phase"])}</h3><p>{e(n["text"])}</p>{refs(n["refs"])}</article>'
    )
parts.append(
    '</div></section><section id="connections"><h2>六条跨期连接</h2><p>连接由助手重建；重复出现证明方法被反复使用，不证明解释真实或有效。</p>'
)
for c in p["connections"]:
    parts.append(
        f'<article id="{c["id"]}"><h3>{e(c["title"])}</h3><p>{e(c["explanation"])}</p>{refs(c["refs"])}</article>'
    )
parts.append(
    '</section><section id="methods"><h2>五项方法候选</h2><p>操作步骤和更新触发由助手整理，尚未成为已验证的 Skill。</p>'
)
for m in p["method_candidates"]:
    parts.append(
        f"<article><h3>{e(m['title'])}</h3><p>{e(m['steps'])}</p><details><summary>替代解释与更新触发</summary><p>{e(m['alternative'])}</p><p>{e(m['trigger'])}</p>{refs(m['refs'])}</details></article>"
    )
parts.append('</section><section id="issues"><h2>仍需补证的边界</h2>')
for q in p["issues"]:
    parts.append(
        f"<article><strong>{e(q['id'])} · {e(q['issue'])}</strong><p>{e(q['handling'])}</p>{refs(q['refs'])}</article>"
    )
parts.append(
    '</section><section id="evidence"><h2>原话证据</h2><p>新增主张使用 T 编号，与原先 C 编号区分；旧主张直接引用 run_005。引用中的错字、数字冲突原样保留。</p>'
)
for c in p["new_claims"] + p["inherited_claims"]:
    ep = p["episodes"][c["episode"]]
    first = c["quotes"][0]
    clock = first["time_range"].split(" --> ")[0].replace(",", ".").split(":")
    sec = int(float(clock[0]) * 3600 + float(clock[1]) * 60 + float(clock[2]))
    url = ep["url"].split("?")[0] + "?t=" + str(sec)
    note = c.get("constraint", "沿用旧版原话与适用边界；本次不新增人工批准。")
    parts.append(
        f'<article id="{e(c["id"])}"><span class="tag">{e(c["id"])}</span><h3>{e(c["statement"])}</h3><p>{e(note)}</p><a href="{e(url)}" target="_blank" rel="noopener">打开原视频，从首个片段核听</a><details><summary>展开原话证据（{len(c["quotes"])} 个片段）</summary>'
    )
    for q in c["quotes"]:
        parts.append(
            f'<blockquote><div class="muted">cue {q["cue_id"]} · {e(q["time_range"])}</div>{e(q["quote"])}</blockquote>'
        )
    parts.append("</details></article>")
parts.append(
    "</section><section><h2>下一步</h2><p>" + e(p["next_step"]) + "</p></section></main></html>"
)
(out / "TRACE.html").write_text("".join(parts), encoding="utf-8")
print("Rendered 5 timepoints, 6 links, 5 methods, 31 evidence cards.")
