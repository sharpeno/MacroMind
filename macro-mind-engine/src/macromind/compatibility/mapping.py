"""Explicit representation aliases and conservative field conversion."""

import types
from enum import Enum
from typing import Annotated, Union, get_args, get_origin

from pydantic import BaseModel, TypeAdapter, ValidationError

from macromind.schema.common import TimeReference, UnknownValue

from .adapters.numbered import escape
from .detector import digest

MISSING = object()
ALIASES = {
    "Source": {"locator": ["location", "path"], "family_ref": ["source_family_id"]},
    "SourceVersion": {"source_ref": ["source_id"], "content_sha256": ["content_hash"]},
    "SourceSegment": {"source_ref": ["source_id"], "text": ["raw_text"]},
    "Claim": {"claimant": ["claimant_id"], "modal_strength": ["certainty_expressed"]},
    "ClaimOccurrence": {"claim_ref": ["claim_id"], "origin_family_ref": ["origin_family_id"]},
    "Actor": {"display_name": ["name"]},
    "Event": {"decided_at": ["decision_at"], "occurrence_status": ["event_status", "status"]},
    "Forecast": {
        "claim_ref": ["claim_id"],
        "claimant": ["forecaster_id"],
        "resolution_status": ["evaluation_status"],
    },
    "Assessment": {
        "target_ref": ["claim_ref", "claim_id"],
        "assessment_time": ["assessed_at"],
        "verification_status": ["veracity"],
    },
    "Argument": {
        "final_conclusion": ["conclusion"],
        "creator_shortcuts": ["creator_explicit_shortcuts"],
    },
    "IndicatorObservation": {"indicator_ref": ["indicator_id"]},
    "Heuristic": {"statement": ["rule"]},
    "ReasoningStep": {
        "id": ["step_id"],
        "premises": ["from_claim_refs", "from_claim"],
        "conclusion_ref": ["to_claim_ref", "to_claim"],
    },
    "ReviewQueueItem": {"reason": ["issue", "question"]},
}
# Only representation-equivalent enum aliases. Unknown legacy vocabulary is NOT
# mapped to a guessed current meaning.
ENUM_ALIASES = {
    "HeuristicStatus": {
        "candidate_not_stable_skill": "candidate",
        "observed_candidate_only": "candidate",
    }
}


def options(annotation):
    if get_origin(annotation) is Annotated:
        return options(get_args(annotation)[0])
    if get_origin(annotation) in (Union, types.UnionType):
        return list(get_args(annotation))
    return [annotation]


def unknown_for(annotation):
    members = options(annotation)
    for item in members:
        if item is UnknownValue:
            return {"state": "unknown"}
        if (
            isinstance(item, type)
            and issubclass(item, Enum)
            and "unknown" in {e.value for e in item}
        ):
            return "unknown"
    if type(None) in members:
        return None
    if any(get_origin(item) is list for item in members):
        return []
    return MISSING


def convert_model(model, raw, path, state, forced=None):
    output, origins = {}, {}
    used = set()
    for name, field in model.model_fields.items():
        if forced and name in forced:
            value, source, operation, reason = forced[name]
            if source and source.startswith(path + "/") and "/" not in source[len(path) + 1 :]:
                used.add(source[len(path) + 1 :].replace("~1", "/").replace("~0", "~"))
        else:
            keys = [name] + ALIASES.get(model.__name__, {}).get(name, [])
            present = [k for k in keys if k in raw]
            key = present[0] if present else None
            value = raw[key] if key else MISSING
            if (
                name not in raw
                and len(present) > 1
                and any(raw[k] != raw[present[0]] for k in present[1:])
            ):
                # Both versions remain raw; choosing a conflicting attribution would
                # silently adjudicate it. Quarantine the object instead.
                state["blocking"].append(name + ":conflicting_aliases")
            if key:
                used.add(key)
            source = path + "/" + escape(key) if key else None
            operation = "COPY" if key == name else "RENAME"
            reason = "recorded_canonical_field" if key == name else "explicit_representation_alias"
            value, operation, reason = convert_value(
                value, field.annotation, source or path, state, name, operation, reason
            )
            if value is MISSING and not field.is_required():
                value = field.get_default(call_default_factory=True)
                operation, reason = "EXPAND_STRUCTURAL", "canonical_nonsemantic_default"
            elif value is MISSING:
                state["blocking"].append(name)
                continue
        output[name] = value
        origins[name] = (source, operation, reason)
    # Unrecognized fields are never discarded; raw_document plus precise pointer
    # provides lossless historical retrieval even when canonical cannot express them.
    for key in sorted(set(raw) - used - set(forced or {})):
        if key not in model.model_fields:
            pointer = path + "/" + escape(key)
            state["unsupported"].append(
                dict(
                    source_path=pointer,
                    value=raw[key],
                    classification="unknown_meaningful_or_historical",
                    operation="PRESERVE_RAW",
                )
            )
            state["loss"](
                pointer,
                "UNKNOWN_LEGACY_FIELD",
                "WARNING",
                "Canonical field unavailable; original value preserved.",
                "Not active canonical semantics.",
            )
    return output, origins


def convert_value(value, annotation, path, state, name, operation, reason):
    members = options(annotation)
    if value is MISSING:
        result = unknown_for(annotation)
        if result is not MISSING:
            state["unknowns"].append(
                dict(source_path=path, field=name, reason="legacy_field_absent", value=result)
            )
            state["loss"](
                path,
                "SEMANTIC_UNKNOWN",
                "WARNING",
                "Legacy field absent; canonical unknown/null/empty records no invented fact.",
                "Unknown or unrecorded.",
            )
        return result, "DEFAULT_UNKNOWN", "legacy_field_absent"
    if value is None and type(None) in members:
        return None, operation, reason
    if TimeReference in members and isinstance(value, str):
        return (
            {"text": value, "start": None, "end": None, "source_ref": None},
            "WRAP",
            "Opaque time expression; no parsing or timezone inference.",
        )
    for item in members:
        if isinstance(item, type) and issubclass(item, Enum) and isinstance(value, str):
            aliases = ENUM_ALIASES.get(item.__name__, {})
            if value in aliases:
                return (
                    aliases[value],
                    "ENUM_MAP",
                    "Reviewed representation-equivalent lifecycle spelling; no promotion.",
                )
    nested = next(
        (
            t
            for t in members
            if isinstance(t, type) and issubclass(t, BaseModel) and t is not UnknownValue
        ),
        None,
    )
    if nested and isinstance(value, dict) and value.get("state") != "unknown":
        result, _ = convert_model(nested, value, path, state)
        return result, "WRAP", "Nested structure mapped field-by-field; unknowns logged."
    list_type = next((t for t in members if get_origin(t) is list), None)
    if list_type is not None and isinstance(value, list):
        element = get_args(list_type)[0]
        element_model = next(
            (t for t in options(element) if isinstance(t, type) and issubclass(t, BaseModel)), None
        )
        if element_model:
            results = []
            for i, item in enumerate(value):
                if not isinstance(item, dict):
                    state["blocking"].append(name + ":unrepresentable_nested_item")
                    continue
                forced = None
                if element_model.__name__ == "ReasoningStep":
                    raw = dict(item)
                    if (
                        "from_claim" in raw
                        and "from_claim_refs" not in raw
                        and isinstance(raw["from_claim"], str)
                    ):
                        raw["from_claim_refs"] = [raw["from_claim"]]
                        del raw["from_claim"]
                    item = raw
                    if "id" not in item and "step_id" not in item:
                        forced = {
                            "id": (
                                "compat:step:" + digest(item)[:24],
                                None,
                                "EXPAND_STRUCTURAL",
                                "Content-derived local step id; no inferred statement.",
                            )
                        }
                result, _ = convert_model(element_model, item, path + "/" + str(i), state, forced)
                results.append(result)
            return (
                results,
                "EXPAND_STRUCTURAL",
                "Explicit nested records; no semantic reconstruction.",
            )
    try:
        # Pydantic is a shape check, not permission to coerce semantic numbers.
        adapted = TypeAdapter(annotation).validate_python(value)
        result = TypeAdapter(annotation).dump_python(adapted, mode="json")
        if type(result) is not type(value) and not isinstance(adapted, Enum):
            raise ValueError("Semantic scalar coercion is not an allowed adapter operation")
        return result, operation, reason
    except (ValueError, TypeError, ValidationError):
        result = unknown_for(annotation)
        category = (
            "ENUM_UNMAPPED"
            if any(isinstance(t, type) and issubclass(t, Enum) for t in members)
            else "FIELD_UNREPRESENTABLE"
        )
        state["loss"](
            path,
            category,
            "BLOCKING" if result is MISSING else "WARNING",
            "Legacy value cannot be represented without interpretation.",
            "Quarantine or explicit unknown; original retained.",
        )
        state["unsupported"].append(
            dict(source_path=path, value=value, classification=category, operation="PRESERVE_RAW")
        )
        if result is not MISSING:
            state["unknowns"].append(
                dict(
                    source_path=path,
                    field=name,
                    reason="legacy_semantics_unavailable",
                    value=result,
                )
            )
        return result, "DEFAULT_UNKNOWN", "legacy_semantics_unavailable"
