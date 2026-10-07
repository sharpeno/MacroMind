"""Opt-in, reversible activation policy 1.0; historical adapters stay unchanged.

Unavailable means not usable now, never a false factual proposition. No pool entry
can be reactivated by changing a status label; rerun against supplemented evidence.
"""

import argparse
import hashlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

from .adapters.numbered import entries
from .detector import digest, serialized
from .engine import CompatibilityEngine, load_document, pointer
from .ids import build_ids

POLICY_VERSION = "1.0"
TIME_FIELDS = {
    "reference_time",
    "asserted_at",
    "published_at",
    "content_time",
    "captured_at",
    "period",
    "baseline_period",
    "knowledge_cutoff",
    "prediction_window",
}
RAW_EVIDENCE_FIELDS = {
    "source_segment",
    "source_segments",
    "source_segment_refs",
    "evidence_refs",
    "source_refs",
    "claim_refs",
    "argument_refs",
    "observed_in_arguments",
}


def prepare(document):
    """Only representation-preserving conversions; never infer a timestamp."""
    output, conversions = deepcopy(document), []

    def visit(value, path=""):
        if isinstance(value, list):
            for i, item in enumerate(value):
                visit(item, path + "/" + str(i))
        elif isinstance(value, dict):
            for key, item in list(value.items()):
                location = path + "/" + key.replace("~", "~0").replace("/", "~1")
                if (
                    key in TIME_FIELDS
                    and isinstance(item, dict)
                    and "text" not in item
                    and set(item) <= {"start", "end"}
                    and item
                    and all(
                        isinstance(v, str) and len(v) == 4 and v.isascii() and v.isdigit()
                        for v in item.values()
                    )
                ):
                    replacement = {
                        "text": serialized(item),
                        "start": None,
                        "end": None,
                        "source_ref": None,
                    }
                    value[key] = replacement
                    conversions.append(
                        {
                            "operation": "OPAQUE_YEAR_RANGE",
                            "path": location,
                            "before": item,
                            "after": replacement,
                            "reason": "Preserve recorded endpoints as opaque text; do not invent day, timezone, or instant.",
                        }
                    )
                else:
                    visit(item, location)

    visit(output)
    return output, conversions


def set_pointer(obj, path, value):
    parts = [p.replace("~1", "/").replace("~0", "~") for p in path.strip("/").split("/")]
    target = obj
    for part in parts[:-1]:
        target = target[int(part)] if isinstance(target, list) else target[part]
    last = parts[-1]
    target[int(last) if isinstance(target, list) else last] = value


class ActivationEngine:
    def __init__(self, contract_root, registry_root):
        self.compatibility = CompatibilityEngine(contract_root, registry_root)
        self.validator = self.compatibility.validator

    def activate(self, document, *, source_sha256=None):
        raw = deepcopy(document)
        prepared, conversions = prepare(raw)
        adaptation = self.compatibility.adapt(prepared)
        candidates = deepcopy(adaptation.canonical_bundle["objects"])
        records = entries(prepared)
        assignments, aliases, _ = build_ids(records)
        origins = {
            assignments[path][0]: path for path, _, item in records if isinstance(item, dict)
        }
        originals = {path: item for path, _, item in entries(raw)}
        index = {o["id"]: o for o in candidates}
        dependencies = {o["id"]: [] for o in candidates}
        repairs = []
        for obj in candidates:
            identity = obj["id"]
            # Only these two field meanings were authorized for source identity projection.
            paths = []
            if obj["object_type"] == "MechanismUsage":
                paths = ["/source_refs/" + str(i) for i in range(len(obj["source_refs"]))]
            elif obj["object_type"] == "IndicatorObservation" and obj["comparison_basis"]:
                paths = ["/comparison_basis/baseline_source_ref"]
            for path in paths:
                old = pointer(obj, path)
                segment = index.get(old) if isinstance(old, str) else None
                source = (
                    index.get(segment.get("source_ref"))
                    if segment and segment["object_type"] == "SourceSegment"
                    else None
                )
                if source and source["object_type"] == "Source":
                    set_pointer(obj, path, source["id"])
                    dependencies[identity].append(
                        {"field": path, "target": old, "kind": "PRESERVED_SEGMENT"}
                    )
                    repairs.append(
                        {
                            "object_ref": identity,
                            "field": path,
                            "before": old,
                            "after": source["id"],
                            "segment": deepcopy(segment),
                            "segment_hash": digest(segment),
                            "operation": "SEGMENT_PARENT_SOURCE",
                            "reason": "Source identity field projected via explicit parent; original segment remains a required evidence dependency.",
                        }
                    )
            original = originals.get(origins.get(identity), {})
            for key in sorted(RAW_EVIDENCE_FIELDS):
                value = original.get(key)
                values = value if isinstance(value, list) else [value]
                for ref in values:
                    if not isinstance(ref, str):
                        continue
                    targets = aliases.get(ref, [])
                    target = targets[0][1] if len(targets) == 1 else ref
                    dependencies[identity].append(
                        {"field": "/" + key, "target": target, "kind": "ORIGINAL_EVIDENCE"}
                    )
        # A suspended inference cannot leave its conclusions independently enabled.
        # Conservatively defer the recorded conclusions too; no alternative support
        # is assumed. Raw attributed statements remain retrievable in the repair pool.
        for obj in candidates:
            if obj["object_type"] == "Argument":
                conclusions = [
                    obj.get("final_conclusion"),
                    *obj.get("intermediate_conclusions", []),
                    *[step.get("conclusion_ref") for step in obj["steps"]],
                ]
                for conclusion in conclusions:
                    if conclusion in index and conclusion != obj["id"]:
                        dependencies[conclusion].append(
                            {
                                "field": "/inference_support",
                                "target": obj["id"],
                                "kind": "RECORDED_ARGUMENT_SUPPORT",
                            }
                        )
        active = {o["id"]: o for o in candidates}
        inactive, rounds = {}, []
        while True:
            report = self.validator.validate(
                {"objects": list(active.values())}, {"validation_mode": "complete_bundle"}
            )
            reasons = {}
            # Indeterminate references cannot establish closure. Other uncertainty remains
            # visible and must not be interpreted as verified truth or validated method.
            for issue in report.errors + [
                x for x in report.indeterminate if x.rule_id.startswith("V-REF")
            ]:
                if issue.object_ref not in active:
                    raise ValueError(
                        "Unattributed validation failure; cannot silently drop the bundle"
                    )
                reasons.setdefault(issue.object_ref, []).append(issue.model_dump(mode="json"))
            for identity in active:
                for edge in dependencies[identity]:
                    if edge["target"] not in active:
                        reasons.setdefault(identity, []).append(
                            {
                                "rule_id": "ACT-DEPENDENCY",
                                "field_path": edge["field"],
                                "related_refs": [edge["target"]],
                                "reason": "Evidence dependency unavailable; entire dependent object deferred.",
                                "dependency_kind": edge["kind"],
                            }
                        )
            if not reasons:
                break
            rounds.append({"round": len(rounds) + 1, "removed": sorted(reasons)})
            for identity, why in sorted(reasons.items()):
                obj = active.pop(identity)
                path = origins[identity]
                inactive[identity] = {
                    "object_ref": identity,
                    "object_type": obj["object_type"],
                    "source_path": path,
                    "raw_payload": originals[path],
                    "projected_payload": obj,
                    "reasons": why,
                    "status": "DEFERRED_NOT_USABLE",
                    "round": len(rounds),
                    "activation_condition": "Supplement evidence or an unambiguous versioned conversion, then recompute dependency closure and validation.",
                }
        pool = [
            {
                "status": "DEFERRED_NOT_USABLE",
                "source_path": q.source_path,
                "raw_payload": pointer(raw, q.source_path),
                "reasons": [q.model_dump(mode="json")],
                "activation_condition": "Preserve historical exclusions; otherwise supplement evidence or versioned conversion and rerun.",
            }
            for q in adaptation.quarantined_items
        ]
        pool.extend(inactive[k] for k in sorted(inactive))
        if isinstance(raw, str):
            pool.append(
                {
                    "status": "SUMMARY_ONLY_NOT_USABLE",
                    "source_path": "",
                    "raw_payload": raw,
                    "reasons": ["No canonical objects may be reconstructed from a summary."],
                    "activation_condition": "Obtain the actual underlying evidence; do not manufacture historical objects.",
                }
            )
        active_bundle = {"objects": sorted(active.values(), key=lambda o: o["id"])}
        report = self.validator.validate(active_bundle, {"validation_mode": "complete_bundle"})
        result = {
            "policy_version": POLICY_VERSION,
            "availability_semantics": "NOT_USABLE_NOW_IS_NOT_FALSE_OR_PROVEN_ABSENT",
            "source_sha256": source_sha256 or digest(raw),
            "raw_document": raw,
            "prepared_document": prepared,
            "adaptation": adaptation.model_dump(mode="json"),
            "conversions": conversions,
            "source_repairs": repairs,
            "evidence_dependencies": dependencies,
            "closure_rounds": rounds,
            "active_bundle": active_bundle,
            "repair_pool": pool,
            "validation": report.model_dump(mode="json"),
            "counts": {
                "historical_objects": adaptation.source_object_count,
                "adapted_candidates": len(candidates),
                "active": len(active),
                "initial_quarantine": len(adaptation.quarantined_items),
                "dependency_or_validation_deferred": len(inactive),
                "repair_pool": len(pool),
                "conversions": len(conversions),
                "source_repairs": len(repairs),
                "active_types": dict(
                    sorted(Counter(o["object_type"] for o in active.values()).items())
                ),
            },
            "status": "ACTIVE_CHAIN_CLOSED" if active else "NO_USABLE_OBJECTS",
            "limitations": [
                "Reference closure does not establish truth, full provenance completeness, chronology, or a validated analyst method.",
                "All remaining validator uncertainty and warnings are retained.",
                "No historical repair-pool object is automatically reactivated.",
            ],
        }
        result["deterministic_hash"] = digest(result)
        assert raw == document
        return result


def main():
    parser = argparse.ArgumentParser(
        description="Explicit opt-in activation policy 1.0; preserve originals and deferred evidence."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--contract-root", type=Path, required=True)
    parser.add_argument("--registry-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError("Refusing to overwrite an existing artifact")
        data = args.input.read_bytes()
        result = ActivationEngine(args.contract_root, args.registry_root).activate(
            load_document(data), source_sha256=hashlib.sha256(data).hexdigest()
        )
        if args.input.read_bytes() != data:
            raise ValueError("Input changed during activation")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(serialized(result) + "\n")
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "counts": result["counts"],
                    "deterministic_hash": result["deterministic_hash"],
                    "output": str(args.output),
                },
                ensure_ascii=True,
            )
        )
        return 0 if result["status"] == "ACTIVE_CHAIN_CLOSED" else 1
    except (ValueError, OSError) as error:
        print(json.dumps({"status": "FAILED", "error": str(error)}, ensure_ascii=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
