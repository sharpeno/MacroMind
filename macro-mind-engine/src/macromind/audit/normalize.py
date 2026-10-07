"""One source item -> one audit record. No aggregation or analytical inference."""

from collections import Counter
from copy import deepcopy

from .ids import record_id, semantic_hash
from .inputs import AuditInputArtifact, AuditInputBundle, InputIntegrityError
from .models import AuditRecord, NormalizedAuditBundle, RecordType
from .provenance import escape_token, resolve_pointer


class UnsupportedShape(ValueError):
    pass


def _items(content: dict, key: str, kind: RecordType):
    items = content.get(key, [])
    if not isinstance(items, list):
        raise UnsupportedShape(f"{key} must be an array")
    for index, item in enumerate(items):
        yield f"/{escape_token(key)}/{index}", kind, item


def _source_items(artifact: AuditInputArtifact):
    c, t, R = artifact.content, artifact.artifact_type, RecordType
    if not isinstance(c, dict):
        raise UnsupportedShape("Engineering report must be a JSON object")
    if t == "validation_report" and "issues" in c:
        yield from _items(c, "issues", R.VALIDATION_FINDING)
    elif t == "adaptation_result" and "losses" in c and "quarantined_items" in c:
        for key, kind in [
            ("losses", R.ADAPTATION_LOSS),
            ("quarantined_items", R.QUARANTINE),
            ("mapping_ledger", R.MAPPING_EVENT),
            ("unknowns", R.UNKNOWN_ENGINEERING_RECORD),
            ("warnings", R.UNKNOWN_ENGINEERING_RECORD),
            ("unsupported_fields", R.UNKNOWN_ENGINEERING_RECORD),
        ]:
            yield from _items(c, key, kind)
    elif t in {"schema_gap_report", "registry_gap_report"} and "gaps" in c:
        kind = R.SCHEMA_GAP if t == "schema_gap_report" else R.REGISTRY_GAP
        yield from _items(c, "gaps", kind)
        yield from _items(c, "inherited_phase1_3_gaps", kind)
    elif t == "gate_result" and "gates" in c:
        yield from _items(c, "gates", R.GATE_RESULT)
        if "status" in c:
            yield "/status", R.GATE_RESULT, c["status"]
    elif t == "test_report" and "cases" in c:
        yield from _items(c, "cases", R.TEST_RESULT)
        for key in ("existing_before_phase1_4", "phase1_4_new", "total"):
            if key in c:
                yield f"/{key}", R.TEST_RESULT, c[key]
    elif t == "debt_overlay" and isinstance(c.get("debts"), dict):
        for key in sorted(c["debts"]):
            yield f"/debts/{escape_token(key)}", R.DEBT_STATUS, c["debts"][key]
    elif t == "immutability_report" and "checked_files" in c:
        for key in sorted(c):
            # Empty change arrays are evidence too, not inferred PASS findings.
            yield f"/{escape_token(key)}", R.IMMUTABILITY_EVENT, c[key]
    else:
        raise UnsupportedShape(f"Unsupported artifact type or shape: {t}")


def _record(a: AuditInputArtifact, pointer: str, kind: RecordType, item: object) -> AuditRecord:
    d = item if isinstance(item, dict) else {}
    if kind == RecordType.UNKNOWN_ENGINEERING_RECORD:
        # Opaque payloads can have arbitrary keys named severity/category/etc.
        # Never interpret those keys as the supported engineering contract.
        d = {}
    severity = d.get("severity")
    outcome = d.get("outcome", d.get("status", d.get("current_outcome")))
    if kind == RecordType.GATE_RESULT and isinstance(item, str):
        outcome = item
    message = next(
        (
            d[k]
            for k in ("message", "description", "reason", "remaining", "impact")
            if isinstance(d.get(k), str)
        ),
        item if isinstance(item, str) else None,
    )
    evidence = d.get("evidence_refs", d.get("evidence", []))
    if not isinstance(evidence, list):
        evidence = [evidence]
    return AuditRecord(
        record_id=record_id(a.sha256, pointer, kind.value),
        record_type=kind,
        phase=a.phase,
        component=a.component,
        category=d.get("category"),
        severity=severity,
        source_severity=severity,
        normalized_severity_class=severity,
        source_outcome=deepcopy(outcome),
        message=message,
        source_artifact_id=a.artifact_id,
        source_artifact_hash=a.sha256,
        source_pointer=pointer,
        object_ref=deepcopy(d.get("object_ref")),
        source_path=d.get("source_path", d.get("field_path")),
        target_path=d.get("target_path"),
        rule_id=d.get("rule_id"),
        reason_code=d.get("reason_code"),
        evidence_refs=deepcopy(evidence),
        review_required=d.get("review_required"),
        metadata={"source_record": deepcopy(item)},
    )


class AuditNormalizer:
    def normalize_artifact(self, artifact: AuditInputArtifact) -> NormalizedAuditBundle:
        return self._normalize([artifact])

    def normalize_bundle(self, bundle: AuditInputBundle) -> NormalizedAuditBundle:
        return self._normalize(bundle.artifacts())

    def _normalize(self, artifacts: list[AuditInputArtifact]) -> NormalizedAuditBundle:
        # Verify every envelope before interpreting any source records.
        for a in artifacts:
            a.verify()
        if len({a.artifact_id for a in artifacts}) != len(artifacts):
            raise InputIntegrityError("Duplicate artifact identity; provide each artifact once")
        records, unsupported, manifest = [], [], []
        for a in sorted(artifacts, key=lambda x: (x.artifact_type, x.sha256, x.artifact_id)):
            manifest.append(
                {
                    "artifact_id": a.artifact_id,
                    "artifact_type": a.artifact_type,
                    "sha256": a.sha256,
                    "phase": a.phase,
                    "component": a.component,
                    "format": a.format,
                    "path_or_label": a.path_or_label,
                    "source_metadata": deepcopy(a.source_metadata),
                    "hash_basis": "source_bytes" if a.raw_bytes is not None else "canonical_json",
                    "hash_verified": True,
                }
            )
            try:
                if a.format != "json":
                    raise UnsupportedShape(f"Unsupported format: {a.format}")
                items = list(_source_items(a))
                candidate = [_record(a, p, t, i) for p, t, i in items]
            except (UnsupportedShape, ValueError, TypeError) as exc:
                unsupported.append(
                    {
                        "artifact_id": a.artifact_id,
                        "artifact_type": a.artifact_type,
                        "sha256": a.sha256,
                        "reason": str(exc),
                        "source_pointer": "",
                    }
                )
                candidate = [_record(a, "", RecordType.UNKNOWN_ENGINEERING_RECORD, a.content)]
            for record in candidate:
                assert (
                    resolve_pointer(a.content, record.source_pointer)
                    == record.metadata["source_record"]
                )
            records.extend(candidate)
        if len({r.record_id for r in records}) != len(records):
            raise InputIntegrityError("Overlapping source record identities")
        result = NormalizedAuditBundle(
            input_manifest=manifest,
            records=records,
            unsupported_inputs=unsupported,
            normalization_warnings=[],
            record_counts=dict(sorted(Counter(r.record_type.value for r in records).items())),
            deterministic_hash="",
        )
        return result.model_copy(
            update={"deterministic_hash": semantic_hash(result.semantic_payload())}
        )
