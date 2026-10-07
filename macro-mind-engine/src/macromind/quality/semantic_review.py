"""Validate semantic self-review documentation, never the truth of its judgments."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from macromind.quality.annotations import digest

AXES = {
    "speaker_role",
    "modality",
    "conditions",
    "time_scope",
    "objects",
    "assumptions",
    "reasoning_relation",
    "alternatives",
    "external_evidence",
}


class Dimension(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["addressed", "not_in_excerpt", "unresolved"]
    assessment: str = Field(min_length=1)
    cue_ids: list[StrictInt]

    @model_validator(mode="after")
    def evidence_required(self):
        if not self.assessment.strip():
            raise ValueError("Empty assessment")
        if self.status == "addressed" and not self.cue_ids:
            raise ValueError("Addressed dimensions require source anchors")
        return self


class Item(BaseModel):
    model_config = ConfigDict(extra="forbid")
    claim_id: str
    original_statement: str
    proposed_statement: str = Field(min_length=1)
    action: Literal["retain", "revise", "hold"]
    evidence_cues: list[StrictInt] = Field(min_length=1)
    dimensions: dict[str, Dimension]
    forecast_use: Literal["not_forecast", "background_only", "candidate_needs_contract"]
    human_status: Literal["PENDING"] = "PENDING"

    @model_validator(mode="after")
    def complete_axes(self):
        if set(self.dimensions) != AXES:
            raise ValueError("Exactly nine semantic dimensions required")
        if self.action == "retain" and self.original_statement != self.proposed_statement:
            raise ValueError("Retain cannot change wording")
        if len(set(self.evidence_cues)) != len(self.evidence_cues):
            raise ValueError("Duplicate evidence cues")
        return self


class Packet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: Literal["1"]
    episode: str
    source_digest: str
    annotation_digest: str
    observer: str = Field(min_length=1)
    items: list[Item] = Field(min_length=1)


def validate_packet(packet, annotation, segments):
    """Bind a nine-axis self-check to its exact input; return review-ready, not approved."""
    errors = []
    try:
        p = Packet.model_validate(packet)
        if p.episode != annotation["episode"]:
            raise ValueError("Episode mismatch")
        if p.source_digest != digest(segments) or p.annotation_digest != digest(annotation):
            raise ValueError("Stale or altered input fingerprint")
        claims = {c[0]: c for c in annotation["claims"]}
        cues = {s["cue_id"] for s in segments}
        if len(cues) != len(segments):
            raise ValueError("Duplicate source cues")
        ids = [i.claim_id for i in p.items]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate review items")
        for item in p.items:
            cid = item.claim_id
            if cid not in claims or item.original_statement != claims[cid][2]:
                raise ValueError("Original claim missing or changed: " + cid)
            if not set(item.evidence_cues) <= cues:
                raise ValueError("Evidence cue unavailable: " + cid)
            for dim in item.dimensions.values():
                if not set(dim.cue_ids) <= set(item.evidence_cues):
                    raise ValueError("Dimension evidence outside declared review scope")
    except (ValueError, TypeError, KeyError, IndexError) as exc:
        errors.append(str(exc))
    return {
        "status": "INVALID_PACKET" if errors else "READY_FOR_HUMAN_REVIEW",
        "errors": errors,
        "semantic_acceptance": False,
        "compile_authorization": False,
        "meaning": "Checks documentation completeness and source binding only; assessments may be wrong",
    }
