"""Deterministic trace builder over explicitly authored judgments, not an extractor."""

import hashlib
import json
from datetime import date
from html import escape
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Anchor(Model):
    source: str = Field(min_length=1)
    record: str = Field(min_length=1)
    quote: str = Field(min_length=1)


class Source(Model):
    path: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    role: Literal["method", "case"]
    format: Literal["segments", "records"]
    published: date
    url: str | None = None

    @model_validator(mode="after")
    def safe_url(self):
        if self.url and not self.url.startswith(("https://", "http://")):
            raise ValueError("Only http(s) source URLs allowed")
        return self


class Node(Model):
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    question: str = Field(min_length=1)
    basis: Literal["assistant_operationalization"] = "assistant_operationalization"
    anchors: list[Anchor] = Field(min_length=1)


class Method(Model):
    id: str
    version: str
    analyst: str
    title: str
    attribution: str
    originator: Literal["unknown"]
    available_on: date
    summary: str
    summary_review: Literal["user_wording_adopted"]
    representation_review: Literal["not_separately_human_reviewed"]
    ordering: str
    conditions: list[Node] = Field(min_length=1)
    steps: list[Node] = Field(min_length=1)
    limitations: list[str] = Field(min_length=1)
    effectiveness_verified: Literal[False] = False
    skill_ready: Literal[False] = False

    @model_validator(mode="after")
    def unique_nodes(self):
        ids = [n.id for n in self.conditions + self.steps]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate method node IDs")
        return self


class Judgment(Model):
    status: Literal["supported", "contradicted", "unknown"]
    reason: str = Field(min_length=1)
    anchors: list[Anchor]
    author: Literal["assistant", "synthetic_fixture"]

    @model_validator(mode="after")
    def evidence_required(self):
        if self.status != "unknown" and not self.anchors:
            raise ValueError("Non-unknown judgments require case evidence")
        return self


class Case(Model):
    id: str
    title: str
    kind: Literal["historical_public", "synthetic"]
    mode: Literal["retrospective_transfer", "as_of_analysis"]
    as_of: date
    question: str
    judgments: dict[str, Judgment]
    alternatives: list[str] = Field(min_length=1)
    mapping_review: Literal["not_human_reviewed"] = "not_human_reviewed"


class Packet(Model):
    version: Literal["method-prototype-1"]
    method: Method
    case: Case
    sources: dict[str, Source]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def analyze(data, root):
    packet = Packet.model_validate(data)
    method, case = packet.method, packet.case
    root = Path(root).resolve()
    if case.mode == "as_of_analysis" and method.available_on > case.as_of:
        raise ValueError("Method unavailable at case cutoff; use explicit retrospective transfer")
    expected = {n.id for n in method.conditions + method.steps}
    if set(case.judgments) != expected:
        raise ValueError("Exactly one judgment required for each condition and step")
    records = {}
    for sid, source in packet.sources.items():
        path = (root / source.path).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"Missing or outside-root source: {sid}")
        if digest(path) != source.sha256:
            raise ValueError(f"Source hash mismatch: {sid}")
        if source.role == "case" and source.published > case.as_of:
            raise ValueError(f"Case evidence beyond cutoff: {sid}")
        if source.role == "method" and source.published > method.available_on:
            raise ValueError(f"Method evidence beyond availability: {sid}")
        content = json.loads(path.read_text(encoding="utf-8-sig"))
        if source.format == "segments":
            rows = [(str(x["cue_id"]), x["quote"], x["time_range"]) for x in content]
        else:
            rows = [(x["id"], x["text"], x["locator"]) for x in content["records"]]
        if len({x[0] for x in rows}) != len(rows):
            raise ValueError(f"Duplicate source record IDs: {sid}")
        records[sid] = {rid: (text, locator) for rid, text, locator in rows}

    def resolve(anchors, role):
        result = []
        for anchor in anchors:
            source = packet.sources.get(anchor.source)
            if source is None or source.role != role:
                raise ValueError("Method and case evidence must remain separate")
            record = records[anchor.source].get(anchor.record)
            if record is None or anchor.quote not in record[0]:
                raise ValueError(f"Quote/record mismatch: {anchor.source}/{anchor.record}")
            result.append({**anchor.model_dump(), "locator": record[1], "url": source.url})
        return result

    rows = []
    for group, nodes in [("condition", method.conditions), ("step", method.steps)]:
        for node in nodes:
            judgment = case.judgments[node.id]
            if case.kind != "synthetic" and judgment.author == "synthetic_fixture":
                raise ValueError("Synthetic judgment cannot be used in a public case")
            rows.append(
                {
                    "group": group,
                    "id": node.id,
                    "label": node.label,
                    "question": node.question,
                    "status": judgment.status,
                    "reason": judgment.reason,
                    "author": judgment.author,
                    "method_evidence": resolve(node.anchors, "method"),
                    "case_evidence": resolve(judgment.anchors, "case"),
                }
            )
    conditions = [case.judgments[n.id].status for n in method.conditions]
    steps = [case.judgments[n.id].status for n in method.steps]
    if "contradicted" in conditions:
        status = "NOT_APPLICABLE"
    elif "unknown" in conditions:
        status = "INSUFFICIENT_SCOPE_EVIDENCE"
    elif "contradicted" in steps:
        status = "COUNTEREVIDENCE"
    elif "unknown" in steps:
        status = "INCOMPLETE_METHOD_EVIDENCE"
    else:
        status = "TRACE_COMPLETE_NOT_VALIDATED"
    return {
        "format": packet.version,
        "method": method.model_dump(mode="json"),
        "case": case.model_dump(mode="json", exclude={"judgments"}),
        "sources": {k: v.model_dump(mode="json") for k, v in packet.sources.items()},
        "status": status,
        "rows": rows,
        "open_questions": [r["question"] for r in rows if r["status"] == "unknown"],
        "counterevidence": [r["id"] for r in rows if r["status"] == "contradicted"],
        "semantic_acceptance": False,
        "effectiveness_verified": False,
        "skill_ready": False,
        "engine_role": "Validates anchors and derives status from authored mappings; no semantic inference",
    }


STATUS = {
    "NOT_APPLICABLE": "不适用：适用条件有反证",
    "INSUFFICIENT_SCOPE_EVIDENCE": "证据不足：尚不能确认适用条件",
    "COUNTEREVIDENCE": "存在反证：不能视为完整方法实例",
    "INCOMPLETE_METHOD_EVIDENCE": "部分可对照，但方法证据不完整",
    "TRACE_COMPLETE_NOT_VALIDATED": "映射完整；方法有效性仍未验证",
}


def render(result):
    def esc(value):
        return escape(str(value), quote=True)

    def evidence(items):
        if not items:
            return "<p>暂无证据。不能把缺失写成不存在。</p>"
        parts = []
        for a in items:
            link = f'<a href="{esc(a["url"])}">外部来源</a>' if a["url"] else "本地字幕"
            parts.append(
                f"<blockquote><small>{esc(a['source'])} / {esc(a['record'])} · "
                f"{esc(a['locator'])} · {link}</small><p>{esc(a['quote'])}</p></blockquote>"
            )
        return "".join(parts)

    cards = []
    labels = {
        "supported": "映射者判断：有支持",
        "contradicted": "映射者判断：有反证",
        "unknown": "证据不足",
    }
    for row in result["rows"]:
        cards.append(
            f'<article id="{esc(row["id"])}"><small>{"适用条件" if row["group"] == "condition" else "分析步骤"}</small>'
            f"<h3>{esc(row['label'])}</h3><p>{esc(row['question'])}</p>"
            f"<strong>{labels[row['status']]}</strong><p>{esc(row['reason'])}</p>"
            f"<details><summary>展开原话与案例证据</summary><h4>方法原话</h4>{evidence(row['method_evidence'])}"
            f"<h4>案例证据</h4>{evidence(row['case_evidence'])}</details></article>"
        )
    method, case = result["method"], result["case"]
    questions = "".join(f"<li>{esc(q)}</li>" for q in result["open_questions"])
    alternatives = "".join(f"<li>{esc(q)}</li>" for q in case["alternatives"])
    limitations = "".join(f"<li>{esc(q)}</li>" for q in method["limitations"])
    nav = "".join(f'<a href="#{esc(r["id"])}">{esc(r["label"])}</a>' for r in result["rows"])
    return f"""<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:,"><title>MacroMind 方法追溯原型</title><style>
body{{margin:0;background:#f4f7f6;color:#163934;font:17px/1.7 system-ui,sans-serif}}main{{max-width:1080px;margin:auto;padding:32px 20px}}h1{{font-size:32px}}h2{{margin-top:32px}}article,.intro{{background:white;border:1px solid #c7d9d2;border-radius:12px;padding:22px;margin:16px 0}}.badge{{background:#fff2cb;padding:16px;border-left:5px solid #ae8422}}nav{{display:flex;gap:12px;flex-wrap:wrap}}a{{color:#11665a;overflow-wrap:anywhere}}nav a{{background:#e1eee8;padding:8px 12px;border-radius:6px}}blockquote{{margin:12px 0;padding:14px;border-left:4px solid #6b9e8a;background:#f1f6f3}}summary{{cursor:pointer;color:#11665a;padding:12px 0}}small{{color:#50655f}}p,li{{overflow-wrap:anywhere}}@media(max-width:600px){{main{{padding:16px 12px}}h1{{font-size:26px}}article{{padding:16px}}}}
</style><main><small>实验原型 · 只读追溯 · 不写入既有审核结果</small>
<h1>{esc(method["title"])}</h1><div class="intro"><p>{esc(method["summary"])}</p>
<p>来源归属：{esc(method["attribution"])}</p><p>步骤顺序：{esc(method["ordering"])}</p>
<p>用户已确认方法文字；本页适用条件、问题设计与案例映射由助手整理，尚未单独人工审核。</p></div>
<h2>{esc(case["title"])}</h2><p>{esc(case["question"])}</p>
<p>案例类型：{esc(case["kind"])} · 分析方式：{esc(case["mode"])} · 材料截止：{esc(case["as_of"])}</p>
<p class="badge">{esc(STATUS[result["status"]])}。这不是事实认证、收益预测或方法有效性结论。</p>
<p>阅读路径：方法 → 适用条件 → 分析步骤 → 案例材料 → 待补证据。程序校验引用并汇总人工编写的映射，不会自动理解新闻。</p>
<nav>{nav}</nav>{"".join(cards)}<h2>仍需补充什么</h2><ul>{questions or "<li>形式映射无缺项，仍需独立语义与有效性验证。</li>"}</ul>
<h2>其他可能解释</h2><ul>{alternatives}</ul><h2>方法边界</h2><ul>{limitations}</ul>
<p><a href="analysis.json">查看完整分析JSON</a> · <a href="packet.json">查看输入与来源指纹</a></p></main></html>"""
