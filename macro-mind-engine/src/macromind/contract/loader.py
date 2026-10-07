import json
from pathlib import Path

from pydantic import ValidationError

from macromind.errors import ContractIntegrityError

from .integrity import verify_manifest_hashes
from .models import ContractIntegrityReport, FrozenContract, FrozenManifest
from .semantic_hash import verify_semantic_hash
from .version import ARTIFACTS, CORE_NAMES


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def load_frozen_contract(contract_root: Path) -> FrozenContract:
    root = Path(contract_root)
    report = ContractIntegrityReport()
    try:
        for name in ARTIFACTS:
            report.check(f"present:{name}", (root / name).is_file())
        if report.errors:
            raise ContractIntegrityError(report)
        data = {
            name: json.loads(
                (root / name).read_text(encoding="utf-8-sig"), object_pairs_hook=_unique_pairs
            )
            for name in ARTIFACTS
            if name.endswith(".json")
        }
        manifest = FrozenManifest.model_validate(data["freeze_manifest.json"])
        for name, expected in {
            "version": "0.3",
            "status": "FROZEN",
            "formal_freeze_executed": True,
            "core_object_count": 14,
            "core_boundary_count": 15,
            "core_principle_count": 16,
            "core_blockers": [],
            "freeze_readiness_decision": "READY_TO_FREEZE_WITH_NONBLOCKING_DEBTS",
            "production_import_ready": False,
            "analyst_skill_status": "NOT_READY",
            "macromind_core_skill_status": "NOT_READY",
        }.items():
            report.check(f"manifest:{name}", getattr(manifest, name) == expected)
        verify_manifest_hashes(root, manifest, report)
        objects = data["core_objects.json"]["objects"]
        boundaries = data["core_boundaries.json"]["boundaries"]
        principles = data["core_principles.json"]["principles"]
        names = [o["object_name"] for o in objects]
        report.check("exact_14_objects", len(names) == 14 and set(names) == set(CORE_NAMES))
        report.check("manifest_object_list", names == manifest.core_objects)
        report.check(
            "exact_15_boundaries",
            [b["boundary_id"] for b in boundaries] == [f"B{i:02}" for i in range(1, 16)],
        )
        report.check(
            "exact_16_principles",
            [p["principle_id"] for p in principles] == [f"P{i:02}" for i in range(1, 17)],
        )
        projection = data["semantic_contract_projection.json"]
        report.check("semantic_hash", verify_semantic_hash(projection, manifest.semantic_hash))
        report.check("projection_version", projection["version"] == "0.3")
        for key, records, fields in [
            ("objects", objects, ("object_name", "core_definition", "semantic_invariants")),
            ("boundaries", boundaries, ("boundary_id", "boundary", "frozen_semantic_rule")),
            ("principles", principles, ("principle_id", "title", "frozen_rule")),
        ]:
            report.check(
                f"projection:{key}", projection[key] == [{k: r[k] for k in fields} for r in records]
            )
        policy = (root / "CHANGE_POLICY.md").read_text(encoding="utf-8-sig")
        report.check("projection:change_policy", projection["change_policy"] == policy)
        report.check(
            "projection:rule_details",
            projection["accepted_audit_rule_details"]
            == data["core_principles.json"]["accepted_audit_rule_details"],
        )
        mapping = data["source_mapping.json"]
        report.check(
            "source_mapping:objects", [r["object_name"] for r in mapping["objects"]] == names
        )
        report.check(
            "source_mapping:boundaries",
            [r["boundary_id"] for r in mapping["boundaries"]]
            == [b["boundary_id"] for b in boundaries],
        )
        if report.errors:
            raise ContractIntegrityError(report)
        return FrozenContract(
            ontology_name=manifest.ontology_name,
            version=manifest.version,
            status=manifest.status,
            formal_freeze_executed=manifest.formal_freeze_executed,
            core_objects=objects,
            core_boundaries=boundaries,
            core_principles=principles,
            freeze_manifest=manifest,
            semantic_contract_projection=projection,
            semantic_hash=manifest.semantic_hash,
            change_policy=policy,
            source_mapping=mapping,
            freeze_debt_ledger=data["freeze_debt_ledger.json"],
            freeze_debt_status_overlay=data["freeze_debt_status_overlay.json"],
            integrity_report=report,
        )
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, ValidationError) as exc:
        report.check("parse_or_structure", False, str(exc))
        raise ContractIntegrityError(report) from exc
