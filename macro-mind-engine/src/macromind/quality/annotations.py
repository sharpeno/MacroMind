"""Pinned review policies guard annotation compilation without claiming semantic truth."""

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, TypeAdapter


class Facet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    claim: str
    name: str
    required_text: list[str] = Field(min_length=1)


class Edge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    argument: str
    premises: list[str]
    conclusion: str


class Policy(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: Literal["1"]
    episode: str
    source_sha256: str
    baseline: dict[str, str]
    reviewed_ids: list[str]
    facets: list[Facet] = []
    edges: list[Edge] = []
    background_claims: list[str] = []
    context_only_cues: list[int] = []
    review_evidence: list[str]


def digest(value):
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def records(annotation):
    result = {}
    types = {
        "claims": tuple[StrictStr, list[StrictInt], StrictStr, Literal["active", "deferred"]],
        "arguments": tuple[StrictStr, list[StrictStr], StrictStr, StrictStr],
        "scenarios": tuple[StrictStr, StrictStr, StrictStr, StrictStr],
        "methods": tuple[StrictStr, list[StrictInt], StrictStr],
    }
    for key, row_type in types.items():
        rows = TypeAdapter(list[row_type]).validate_python(annotation[key])
        for row in rows:
            if row[0] in result:
                raise ValueError("Duplicate annotation ID: " + row[0])
            result[row[0]] = list(row)
    TypeAdapter(list[StrictStr]).validate_python(annotation["forecast_candidates"])
    result["@forecast_candidates"] = annotation["forecast_candidates"]
    return result


def assess(annotation, segments, policy):
    """Return findings; deterministic guards do not certify semantic correctness."""
    errors, review = [], []

    def fail(rule, ref, message):
        errors.append({"rule": rule, "ref": ref, "message": message})

    try:
        p = Policy.model_validate(policy)
        recs = records(annotation)
        if annotation["episode"] != p.episode:
            raise ValueError("Episode does not match pinned policy")
        cue_ids = [s["cue_id"] for s in segments]
        if any(type(n) is not int or n < 1 for n in cue_ids):
            raise ValueError("Cue IDs must be positive integers")
        if len(set(cue_ids)) != len(cue_ids):
            raise ValueError("Duplicate source cue IDs")
        if any(not isinstance(s["quote"], str) for s in segments):
            raise ValueError("Source quotes must be strings")
    except (ValueError, KeyError, TypeError) as exc:
        return {
            "status": "BLOCKED",
            "compile_allowed": False,
            "errors": [{"rule": "Q-INPUT", "message": str(exc)}],
            "review_required": [],
            "semantic_acceptance": False,
        }
    if digest(segments) != p.source_sha256:
        fail("Q-SOURCE", p.episode, "Source differs from pinned evidence; never rewrite raw cues")
    claims = {r[0]: r for r in annotation["claims"]}
    arguments = {r[0]: r for r in annotation["arguments"]}
    cues = set(cue_ids)
    for key in ["claims", "methods"]:
        for row in annotation[key]:
            if not row[1] or len(set(row[1])) != len(row[1]) or not set(row[1]) <= cues:
                fail("Q-EVIDENCE", row[0], "Evidence cues missing, duplicate or unresolvable")
    for row in annotation["arguments"]:
        if not row[1] or any(cid not in claims for cid in row[1] + [row[2]]):
            fail("Q-REFERENCE", row[0], "Argument references missing claims")
    for row in annotation["scenarios"]:
        if row[1] not in claims:
            fail("Q-REFERENCE", row[0], "Scenario claim missing")
    for cid in annotation["forecast_candidates"]:
        if cid not in claims:
            fail("Q-REFERENCE", cid, "Forecast candidate claim missing")
    for facet in p.facets:
        statement = claims.get(facet.claim, [None, None, ""])[2]
        if any(text not in statement for text in facet.required_text):
            fail("Q-FACET", facet.claim, "Reviewed wording changed: " + facet.name)
    for edge in p.edges:
        actual = arguments.get(edge.argument)
        if not actual or actual[1] != edge.premises or actual[2] != edge.conclusion:
            fail("Q-EDGE-SCOPE", edge.argument, "Reason must only support the reviewed scope")
    for cid in p.background_claims:
        if cid not in claims:
            fail("Q-BACKGROUND", cid, "Preserve attributed background, do not silently delete it")
        if cid in annotation["forecast_candidates"]:
            fail("Q-FORECAST", cid, "Background outlook cannot enter forecast accuracy candidates")
    for cid, row in claims.items():
        if set(row[1]) & set(p.context_only_cues):
            fail("Q-CONTEXT", cid, "User retained these cues as context, not new claims")
    for rid in sorted(set(recs) | set(p.baseline)):
        if rid not in recs or digest(recs[rid]) != p.baseline.get(rid):
            review.append(
                {
                    "rule": "Q-CHANGED",
                    "ref": rid,
                    "message": "New, changed or removed content requires review",
                }
            )
    unreviewed = sorted(set(recs) - set(p.reviewed_ids) - {"@forecast_candidates"})
    return {
        "policy_version": p.version,
        "episode": p.episode,
        "status": "BLOCKED" if errors else "REVIEW_REQUIRED" if review else "GUARDS_PASSED",
        "compile_allowed": not errors and not review,
        "errors": errors,
        "review_required": review,
        "unreviewed_ids": unreviewed,
        "semantic_acceptance": False,
        "meaning": "Guard checks only; no factual, forecast or whole-corpus acceptance",
    }


def review_disposition(record):
    """A positive dropdown never suppresses free-text requests."""
    decision = record.get("decision")
    if decision not in {"faithful", "accept_revision", "context", "change", "reject", "extract"}:
        return "MANUAL_REVIEW"
    if decision in {"change", "reject", "extract"}:
        return "ACTION_REQUIRED"
    if any(str(record.get(key, "")).strip() for key in ("note", "correction", "evidence")):
        return "INSPECT_TEXT_BEFORE_CLOSING"
    return "KEEP_CONTEXT" if decision == "context" else "ACCEPT_WITHIN_REVIEW_SCOPE"
