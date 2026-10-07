"""Separate inference permission from confirmation; never certify hidden motives."""

import json
from html import escape
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from macromind.methods.prototype import Anchor, Model, Source, digest


class Observation(Model):
    id: str
    statement: str = Field(min_length=1)
    layer: Literal["blogger_report", "official_statement"]
    anchors: list[Anchor] = Field(min_length=1)
    world_fact_verified: Literal[False] = False


class Hypothesis(Model):
    id: str
    statement: str = Field(min_length=1)
    attribution: Literal["blogger_explicit", "assistant_transfer"]
    original_force: str = Field(min_length=1)
    observation_refs: list[str] = Field(min_length=1)
    attribution_anchors: list[Anchor]
    assumptions: list[str] = Field(min_length=1)
    alternatives: list[str] = Field(min_length=1)
    strengthen_with: list[str] = Field(min_length=1)
    weaken_with: list[str] = Field(min_length=1)
    epistemic_status: Literal["HYPOTHESIS_FROM_INDIRECT_EVIDENCE"]
    confirmation: Literal["NOT_CONFIRMED"]

    @model_validator(mode="after")
    def explicit_attribution_needs_quote(self):
        if self.attribution == "blogger_explicit" and not self.attribution_anchors:
            raise ValueError("Blogger attribution requires original statement anchors")
        return self


class InferenceCase(Model):
    id: str
    title: str
    scope: str
    observations: list[Observation] = Field(min_length=1)
    hypotheses: list[Hypothesis] = Field(min_length=1)

    @model_validator(mode="after")
    def connected(self):
        ids = [x.id for x in self.observations + self.hypotheses]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate observation/hypothesis IDs")
        known = {x.id for x in self.observations}
        for h in self.hypotheses:
            if not set(h.observation_refs) <= known:
                raise ValueError("Unresolved observation reference")
        return self


class Dossier(Model):
    version: Literal["indirect-inference-1"]
    correction: str
    method_distinction: str
    attribution_limit: str
    sources: dict[str, Source]
    cases: list[InferenceCase] = Field(min_length=1)
    semantic_acceptance: Literal[False] = False
    skill_ready: Literal[False] = False

    @model_validator(mode="after")
    def unique_cases(self):
        if len({c.id for c in self.cases}) != len(self.cases):
            raise ValueError("Duplicate case IDs")
        return self


def validate(data, root):
    dossier = Dossier.model_validate(data)
    root = Path(root).resolve()
    records = {}
    for sid, source in dossier.sources.items():
        path = (root / source.path).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("Missing/outside source")
        if digest(path) != source.sha256:
            raise ValueError("Source hash mismatch")
        content = json.loads(path.read_text(encoding="utf-8-sig"))
        if source.format == "segments":
            rows = [(str(x["cue_id"]), x["quote"], x["time_range"]) for x in content]
        else:
            rows = [(x["id"], x["text"], x["locator"]) for x in content["records"]]
        if len({r[0] for r in rows}) != len(rows):
            raise ValueError("Duplicate source record IDs")
        records[sid] = {rid: (text, locator) for rid, text, locator in rows}
    for case in dossier.cases:
        for ob in case.observations:
            expected_role = "method" if ob.layer == "blogger_report" else "case"
            if any(
                dossier.sources.get(a.source) is None
                or dossier.sources[a.source].role != expected_role
                for a in ob.anchors
            ):
                raise ValueError("Observation source layer mismatch")
        for h in case.hypotheses:
            if h.attribution == "blogger_explicit" and any(
                dossier.sources.get(a.source) is None or dossier.sources[a.source].role != "method"
                for a in h.attribution_anchors
            ):
                raise ValueError("Blogger attribution source mismatch")
        anchors = [a for ob in case.observations for a in ob.anchors]
        anchors += [a for h in case.hypotheses for a in h.attribution_anchors]
        for a in anchors:
            row = records.get(a.source, {}).get(a.record)
            if row is None or a.quote not in row[0]:
                raise ValueError("Quote/record mismatch")
    return dossier.model_dump(mode="json"), records


def render(data, root):
    d, records = validate(data, root)

    def e(x):
        return escape(str(x), quote=True)

    def bullets(items):
        return "<ul>" + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>"

    def evidence(anchors):
        parts = []
        for a in anchors:
            loc = records[a["source"]][a["record"]][1]
            url = d["sources"][a["source"]]["url"]
            link = f'<a href="{e(url)}">来源页面</a>' if url else ""
            parts.append(
                f"<blockquote><small>{e(a['source'])} / {e(a['record'])} · {e(loc)} {link}</small><p>{e(a['quote'])}</p></blockquote>"
            )
        return "".join(parts)

    cases = []
    for c in d["cases"]:
        observations = "".join(
            f'<article id="{e(c["id"])}-{e(o["id"])}"><h3>{e(o["id"])} · 观察依据</h3><p>{e(o["statement"])}</p><small>{"博主所述动作，未独立核实现实事实" if o["layer"] == "blogger_report" else "公开讲话选段，不等于完整决策记录"}</small><details><summary>展开观察依据原文</summary>{evidence(o["anchors"])}</details></article>'
            for o in c["observations"]
        )
        hypotheses = []
        for h in c["hypotheses"]:
            refs = "、".join(
                f'<a href="#{e(c["id"])}-{e(ref)}">{e(ref)}</a>' for ref in h["observation_refs"]
            )
            attribution = (
                "博主明确提出的解释"
                if h["attribution"] == "blogger_explicit"
                else "助手按这一分析方式提出的迁移假设"
            )
            hypotheses.append(
                f'<article id="{e(c["id"])}-{e(h["id"])}"><h3>{e(h["statement"])}</h3><p class="tag">可据间接线索提出推断 · 尚未确证</p><p>{attribution}。原表达强度：{e(h["original_force"])}</p><p>从这些观察出发：{refs}</p><details><summary>展开推断前提、竞争解释与验证线索</summary><h4>推断依赖什么前提</h4>{bullets(h["assumptions"])}<h4>还有哪些解释</h4>{bullets(h["alternatives"])}<h4>什么材料会增强这一解释</h4>{bullets(h["strengthen_with"])}<h4>什么材料会削弱这一解释</h4>{bullets(h["weaken_with"])}<h4>归属依据</h4>{evidence(h["attribution_anchors"]) or "<p>这是助手提出的假设，不是博主对这个案例的已知评价。</p>"}</details></article>'
            )
        cases.append(
            f'<section id="{e(c["id"])}"><h2>{e(c["title"])}</h2><p>{e(c["scope"])}</p>{observations}{"".join(hypotheses)}</section>'
        )
    return f"""<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>MacroMind · 从决策推导动机</title><style>
body{{background:#f3f7f5;color:#173e36;font:17px/1.75 system-ui,sans-serif;margin:0}}main{{max-width:1000px;margin:auto;padding:28px 20px}}h1{{font-size:30px}}article,.intro{{background:white;border:1px solid #cbdcd4;border-radius:12px;padding:22px;margin:18px 0}}.tag{{background:#e6f2ec;padding:12px;border-left:4px solid #47816a}}blockquote{{margin:12px 0;background:#f4f7f5;padding:14px;border-left:4px solid #76a18e}}summary{{cursor:pointer;color:#116553}}a{{color:#116553}}small{{color:#587168}}nav{{display:flex;flex-wrap:wrap;gap:20px}}p,li,a{{overflow-wrap:anywhere}}@media(max-width:600px){{main{{padding:16px 12px}}article{{padding:16px}}h1{{font-size:25px}}}}
</style><main><small>修订版 · 只读方法示例 · 不要求重复填写审核意见</small><h1>从公开表态和决策动作，推导可能的动机与信息</h1><div class="intro"><p>{e(d["correction"])}</p><p>{e(d["method_distinction"])}</p><p class="tag">观察动作 → 考察准备时间与约束 → 提出动机/信息假设 → 比较解释 → 寻找后续验证</p><p>缺少事前直接记录，不会禁止推断。存在公开动作，也不会自动确定具体动机或非公开信息。</p><p>{e(d["attribution_limit"])}</p></div><nav>{"".join(f'<a href="#{e(c["id"])}">{e(c["title"])}</a>' for c in d["cases"])}</nav>{"".join(cases)}<p><a href="inference.json">查看结构化推断记录</a> · <a href="REPORT.md">修订说明</a></p><p>程序检查引用和记录结构，具体推断由助手整理；没有自动完成语义验收或方法有效性认证。</p></main></html>"""
