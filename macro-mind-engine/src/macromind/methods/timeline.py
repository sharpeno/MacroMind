"""Append-only historical evidence snapshots; authored judgments, not forecasting."""

import hashlib
import json
from datetime import date
from html import escape
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from macromind.methods.prototype import Model, digest


class Evidence(Model):
    id: str
    published: date
    event_date: date
    path: str
    sha256: str = Field(pattern=r"^[a-f0-9]{64}$")
    kind: Literal["signal", "announcement", "instruction", "execution", "outcome"]


class Judgment(Model):
    id: str
    dimension: Literal["policy", "execution", "broad_effect", "hidden_plan"]
    statement: str = Field(min_length=1)
    state: Literal["provisional", "announced", "scheduled", "observed", "withdrawn", "unknown"]
    evidence_refs: list[str] = Field(min_length=1)
    reason: str = Field(min_length=1)
    next_trigger: str = Field(min_length=1)
    attribution: Literal["assistant_reconstruction"] = "assistant_reconstruction"
    teaching_branch: bool = False


class Snapshot(Model):
    version: Literal["timeline-1"]
    id: str
    as_of: date
    mode: Literal["retrospective_reconstruction"]
    method_available_on: date
    previous_sha256: str | None
    coverage: str = Field(min_length=1)
    sources: list[Evidence] = Field(min_length=1)
    judgments: list[Judgment] = Field(min_length=1)
    semantic_acceptance: Literal[False] = False
    forecast_score_eligible: Literal[False] = False

    @model_validator(mode="after")
    def ids_unique(self):
        for values in [[s.id for s in self.sources], [j.id for j in self.judgments]]:
            if len(values) != len(set(values)):
                raise ValueError("Duplicate IDs")
        return self


def object_hash(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()


def evaluate(data, root, previous=None):
    snapshot = Snapshot.model_validate(data)
    root = Path(root).resolve()
    if previous is None and snapshot.previous_sha256 is not None:
        raise ValueError("Initial snapshot cannot claim predecessor")
    if previous is not None:
        if snapshot.previous_sha256 != object_hash(previous):
            raise ValueError("Predecessor hash mismatch")
        if snapshot.as_of <= date.fromisoformat(previous["as_of"]):
            raise ValueError("Snapshot cutoffs must increase")
        if snapshot.method_available_on.isoformat() != previous["method_available_on"]:
            raise ValueError("Method availability changed within replay")
    documents = {}
    sources = {s.id: s for s in snapshot.sources}
    for s in snapshot.sources:
        if s.published > snapshot.as_of:
            raise ValueError("Future publication in snapshot, even if unreferenced")
        path = (root / s.path).resolve()
        if not path.is_relative_to(root) or not path.is_file() or digest(path) != s.sha256:
            raise ValueError("Source path/hash mismatch")
        doc = json.loads(path.read_text(encoding="utf-8-sig"))
        if (
            doc["id"] != s.id
            or doc["published"] != s.published.isoformat()
            or doc["kind"] != s.kind
            or doc["event_date"] != s.event_date.isoformat()
        ):
            raise ValueError("Source metadata mismatch")
        if not doc["url"].startswith("https://") or not doc["excerpt"] or not doc["locator"]:
            raise ValueError("Source needs URL, excerpt and locator")
        documents[s.id] = doc
    if previous:
        old_sources = {s["id"]: s for s in previous["sources"]}
        for s in snapshot.sources:
            if s.id in old_sources and s.model_dump(mode="json") != old_sources[s.id]:
                raise ValueError("Existing source identity changed; use a new revision ID")
    for j in snapshot.judgments:
        if not set(j.evidence_refs) <= set(sources):
            raise ValueError("Unknown source reference")
        kinds = {sources[k].kind for k in j.evidence_refs}
        if j.dimension == "execution" and j.state == "observed" and "execution" not in kinds:
            raise ValueError("Announcement/instruction cannot prove observed execution")
        if (
            j.dimension == "broad_effect"
            and j.state in {"observed", "withdrawn"}
            and "outcome" not in kinds
        ):
            raise ValueError("Broad effects need outcome evidence")
        if j.dimension == "hidden_plan" and j.state != "unknown":
            raise ValueError("This public-record pilot does not certify hidden plans")
    old = {j["id"]: j for j in previous["judgments"]} if previous else {}
    new = {j.id: j.model_dump(mode="json") for j in snapshot.judgments}
    if previous and old.keys() != new.keys():
        raise ValueError("Stable judgment IDs required; no silent dropped branches")
    changes = []
    for key, item in new.items():
        before = old.get(key)
        action = (
            "INITIAL"
            if before is None
            else (
                "WITHDRAW"
                if item["state"] == "withdrawn" and before["state"] != "withdrawn"
                else ("HOLD" if before["state"] == item["state"] else "UPDATE")
            )
        )
        changes.append({"id": key, "action": action, "before": before, "after": item})
    return {
        **snapshot.model_dump(mode="json"),
        "documents": documents,
        "changes": changes,
        "engine_role": "Checks time/provenance and records authored updates; not semantic or predictive validation",
    }


def save_new(result, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / "snapshot.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "snapshot_sha256": digest(output / "snapshot.json"),
                "object_sha256": object_hash(result),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def render_timeline(results):
    def e(value):
        return escape(str(value), quote=True)

    labels = {"INITIAL": "建立判断", "UPDATE": "更新", "HOLD": "维持状态", "WITHDRAW": "撤回分支"}
    states = {
        "provisional": "暂定判断",
        "announced": "措施已公布",
        "scheduled": "已安排执行",
        "observed": "已有执行观察",
        "withdrawn": "已撤回",
        "unknown": "未知，保留边界",
    }
    cards = []
    for r in results:
        rows = []
        for change in r["changes"]:
            j = change["after"]
            refs = "".join(
                f'<details><summary>{e(sid)} · {e(r["documents"][sid]["title"])}</summary><p>公开日期：{e(r["documents"][sid]["published"])}；材料涉及日期：{e(r["documents"][sid]["event_date"])}</p><blockquote>{e(r["documents"][sid]["excerpt"])}</blockquote><p>{e(r["documents"][sid]["summary"])}</p><a href="{e(r["documents"][sid]["url"])}">官方原文</a><p>定位：{e(r["documents"][sid]["locator"])}</p></details>'
                for sid in j["evidence_refs"]
            )
            prior = f"<p>此前：{e(change['before']['statement'])}</p>" if change["before"] else ""
            teaching = (
                '<p class="note">用于检验撤回机制的过宽分支，不是9527观点或真实事前预测。</p>'
                if j["teaching_branch"]
                else ""
            )
            rows.append(
                f"<article><small>{e(j['id'])} · {labels[change['action']]} · {states[j['state']]}</small><h3>{e(j['statement'])}</h3>{teaching}{prior}<p>理由：{e(j['reason'])}</p><p>下一观察条件：{e(j['next_trigger'])}</p>{refs}</article>"
            )
        cards.append(
            f'<section id="{e(r["id"])}"><h2>{e(r["as_of"])} · {e(r["id"])}</h2><p>{e(r["coverage"])}</p>{"".join(rows)}</section>'
        )
    nav = "".join(f'<a href="#{e(r["id"])}">{e(r["as_of"])}</a>' for r in results)
    return f"""<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>MacroMind · 判断更新时间线</title><style>body{{margin:0;background:#f3f7f5;color:#173e36;font:17px/1.75 system-ui}}main{{max-width:1050px;margin:auto;padding:28px 18px}}article,.intro{{background:white;border:1px solid #cadcd3;padding:22px;border-radius:12px;margin:18px 0}}nav{{display:flex;flex-wrap:wrap;gap:18px}}a,summary{{color:#126752}}summary{{cursor:pointer;padding:10px 0}}blockquote,.note{{background:#edf3e9;padding:12px;margin:10px 0}}small{{color:#547266}}p,li{{overflow-wrap:anywhere}}@media(max-width:600px){{h1{{font-size:25px}}article{{padding:15px}}}}</style><main><h1>新证据如何改变判断</h1><div class="intro"><p>2024年降息案例：方向信号 → 具体措施 → 执行与效果分开观察。</p><p>本页是事后重建，作者已知后续结果，不是盲测或真实预测成绩。使用后来整理的方法回看历史；日期限制只约束输入引用，不能消除人工判断的后见影响。</p><p>每一时点保留独立输入、判断和前后差异；会议日期与公开日期分开。具体判断由助手编写，程序检查时间和引用，不自动理解新闻。</p><p>关键检验：执行得到支持，也允许撤回过宽的效果推断；不据此确证内部计划。</p></div><nav>{nav}</nav>{"".join(cards)}<p><a href="REPORT.md">范围与验证报告</a> · <a href="timeline.json">完整结构化时间线</a></p></main></html>"""
