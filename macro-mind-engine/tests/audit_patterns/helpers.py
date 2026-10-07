from collections import Counter

from macromind.audit.ids import semantic_hash
from macromind.audit.models import AuditRecord, NormalizedAuditBundle, RecordType


def record(number=0, kind=RecordType.ADAPTATION_LOSS, **changes):
    fields = dict(
        record_id=f"record:{number:06}",
        record_type=kind,
        phase="1.4",
        component="compatibility",
        category="missing_field",
        source_artifact_id="artifact:a",
        source_artifact_hash="a" * 64,
        source_pointer=f"/losses/{number}",
        source_path=f"/claims/{number}/detail",
        metadata={"source_record": {}},
        severity="WARNING",
    )
    fields.update(changes)
    return AuditRecord(**fields)


def bundle(records):
    value = NormalizedAuditBundle(
        input_manifest=[],
        records=records,
        unsupported_inputs=[],
        normalization_warnings=[],
        record_counts=dict(Counter(r.record_type.value for r in records)),
        deterministic_hash="",
    )
    return value.model_copy(update={"deterministic_hash": semantic_hash(value.semantic_payload())})
