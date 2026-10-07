import hashlib
import json
import os
from copy import deepcopy
from pathlib import Path

from pydantic import ValidationError

from macromind.schema.auxiliary import AUXILIARY_MODELS
from macromind.schema.core import CORE_MODELS
from macromind.validation import ValidatorEngine
from macromind.validation.reference_contracts import REFERENCE_CONTRACTS

from .adapters.numbered import entries, escape
from .detector import detect_legacy_format, digest, serialized
from .ids import build_ids
from .mapping import convert_model
from .models import AdaptationLoss, AdaptationResult, CompatibilityQuarantineItem, MappingEntry
from .registry import CompatibilityAdapterRegistry

MODELS = {**CORE_MODELS, **AUXILIARY_MODELS}


def pointer(value, path):
    if not path:
        return value
    for part in path.split("/")[1:]:
        key = part.replace("~1", "/").replace("~0", "~")
        value = value[int(key)] if isinstance(value, list) else value[key]
    return value


def leaves(value, path=""):
    if isinstance(value, dict) and value:
        for key, item in sorted(value.items()):
            yield from leaves(item, path + "/" + escape(key))
    elif isinstance(value, list) and value:
        for i, item in enumerate(value):
            yield from leaves(item, path + "/" + str(i))
    else:
        yield path, value


def load_document(data):
    text = data.decode("utf-8-sig")
    if text.lstrip().startswith(("{", "[")):

        def unique(pairs):
            result = {}
            for key, value in pairs:
                if key in result:
                    raise ValueError("Duplicate JSON key: " + key)
                result[key] = value
            return result

        return json.loads(
            text,
            object_pairs_hook=unique,
            parse_constant=lambda v: (_ for _ in ()).throw(ValueError("Nonfinite JSON value " + v)),
        )
    # Arbitrary text is only a summary carrier. No filename/extension detection.
    return text


class CompatibilityEngine:
    def __init__(self, contract_root, registry_root):
        self.validator = ValidatorEngine(contract_root, registry_root)
        self.adapters = CompatibilityAdapterRegistry()

    def detect(self, document):
        return detect_legacy_format(document)

    def adapt(self, document, target_schema_version="0.1.0", *, source_sha256=None):
        raw = deepcopy(document)
        before = serialized(raw)
        detection = self.detect(raw)
        spec = self.adapters.select(detection, target_schema_version)
        source_hash = source_sha256 or hashlib.sha256(before.encode("utf8")).hexdigest()
        losses = []
        quarantine = []
        unknowns = []
        unsupported = []
        candidates = []
        ledger = []

        def loss(path, category, severity, description, effect):
            item = dict(
                source_path=path,
                category=category,
                severity=severity,
                description=description,
                canonical_effect=effect,
            )
            losses.append(AdaptationLoss(loss_id="loss:" + digest(item)[:24], **item))

        def isolate(path, kind, payload, reason, missing, category="REQUIRED_FIELD_UNAVAILABLE"):
            quarantine.append(
                CompatibilityQuarantineItem(
                    source_path=path,
                    source_object_type=kind,
                    raw_payload_hash=digest(payload),
                    raw_payload=payload,
                    reason_code=reason,
                    message="No canonical object invented for unsupported semantics.",
                    missing_semantics=sorted(set(missing)),
                    candidate_target_type=kind,
                )
            )
            loss(
                path,
                category,
                "BLOCKING",
                reason,
                "Object quarantined, raw retained.",
            )

        records = entries(raw) if spec else []
        assignments, refs, duplicate_targets = build_ids(records)
        migration = raw.get("ma1_migration", {}) if isinstance(raw, dict) else {}
        policy = migration.get("machine_use_policy", {}) if isinstance(migration, dict) else {}
        policy = policy if isinstance(policy, dict) else {}
        excluded_occurrences = policy.get("excluded_occurrence_evidence", [])
        quarantined_ids = policy.get("immutable_object_quarantine", [])
        excluded_occurrences = (
            {v for v in excluded_occurrences if isinstance(v, str)}
            if isinstance(excluded_occurrences, list)
            else set()
        )
        quarantined_ids = (
            {v for v in quarantined_ids if isinstance(v, str)}
            if isinstance(quarantined_ids, list)
            else set()
        )
        if spec and detection.family == "SUMMARY_ONLY_LEGACY":
            loss(
                "",
                "SUMMARY_ONLY_LIMITATION",
                "WARNING",
                "Unstructured carrier cannot reconstruct semantic objects.",
                "Raw text only; canonical_reconstruction_forbidden.",
            )
        elif spec:
            for path, kind, payload in records:
                if kind not in MODELS or not isinstance(payload, dict):
                    isolate(path, kind, payload, "unsupported_object_shape", [])
                    continue
                target, id_key, old_id = assignments[path]
                if old_id in quarantined_ids or (
                    kind == "ClaimOccurrence" and old_id in excluded_occurrences
                ):
                    isolate(
                        path, kind, payload, "explicit_historical_exclusion", [], "STRUCTURAL_LOSS"
                    )
                    quarantine[
                        -1
                    ].message = "Preserved explicit historical exclusion; no new adjudication."
                    quarantine[
                        -1
                    ].suggested_future_action = "Keep excluded; compatibility must not overturn the recorded historical decision."
                    continue
                if target in duplicate_targets:
                    isolate(
                        path,
                        kind,
                        payload,
                        "indistinguishable_duplicate_identity",
                        ["unique_identity"],
                    )
                    continue
                state = {
                    "loss": loss,
                    "unknowns": unknowns,
                    "unsupported": unsupported,
                    "blocking": [],
                }
                forced = {
                    "id": (
                        target,
                        path + "/" + escape(id_key) if old_id else None,
                        "COPY"
                        if old_id == target and id_key == "id"
                        else "RENAME"
                        if old_id == target
                        else "REF_MAP"
                        if old_id
                        else "EXPAND_STRUCTURAL",
                        "Stable preserved or content-namespaced identity.",
                    ),
                    "object_type": (
                        kind,
                        path,
                        "EXPAND_STRUCTURAL",
                        "Explicit object section; never classify text.",
                    ),
                    "schema_version": (
                        "0.1.0",
                        None,
                        "EXPAND_STRUCTURAL",
                        "Target representation version, not a historical assertion.",
                    ),
                    "ontology_version": (
                        "0.3",
                        None,
                        "EXPAND_STRUCTURAL",
                        "Target frozen contract version.",
                    ),
                }
                # A legacy Scenario record describes an explicit branch. Preserve
                # that branch structurally without endorsing its condition.
                if (
                    kind == "Scenario"
                    and "branches" not in payload
                    and any(k in payload for k in ("condition", "condition_expression"))
                ):
                    condition = payload.get("condition", payload.get("condition_expression"))
                    outcome = payload.get("result", payload.get("outcome"))
                    if (isinstance(condition, str) or condition is None) and (
                        isinstance(outcome, str) or outcome is None
                    ):
                        forced["branches"] = (
                            [
                                dict(
                                    id=target + "/branch/0",
                                    condition=condition,
                                    outcome=outcome,
                                    child_branch_refs=[],
                                )
                            ],
                            path,
                            "EXPAND_STRUCTURAL",
                            "Recorded Scenario condition/outcome wrapped as one branch; no Forecast admission.",
                        )
                output, origins = convert_model(MODELS[kind], payload, path, state, forced)
                if state["blocking"]:
                    isolate(
                        path, kind, payload, "required_semantics_unavailable", state["blocking"]
                    )
                    continue
                try:
                    MODELS[kind].model_validate(output)
                except ValidationError as exc:
                    isolate(
                        path,
                        kind,
                        payload,
                        "unrepresentable_canonical_shape",
                        ["/".join(map(str, e["loc"])) for e in exc.errors()],
                    )
                    continue
                candidates.append((path, kind, output, origins))
            # All identities are allocated BEFORE mapping references. Never guess
            # an ambiguous reference. Retain its literal spelling for partial validation.
            live = {o["id"] for _, _, o, _ in candidates}
            for path, kind, output, origins in candidates:
                for contract in REFERENCE_CONTRACTS[kind]:
                    if contract.resolution in ("external", "local_step"):
                        continue

                    def visit(value, parts, contract=contract, origins=origins, path=path):
                        field, *rest = parts
                        many = field.endswith("[]")
                        key = field[:-2] if many else field
                        if not isinstance(value, dict) or key not in value:
                            return
                        items = (
                            value[key] if many and isinstance(value[key], list) else [value[key]]
                        )
                        for i, item in enumerate(items):
                            if rest:
                                visit(item, rest)
                            elif isinstance(item, str):
                                matches = refs.get(item, [])
                                allowed = [
                                    identity
                                    for typ, identity in matches
                                    if contract.target_types is None or typ in contract.target_types
                                ]
                                if len(allowed) == 1 and allowed[0] in live:
                                    if many:
                                        value[key][i] = allowed[0]
                                    else:
                                        value[key] = allowed[0]
                                    if allowed[0] != item:
                                        top = contract.field.split(".")[0].removesuffix("[]")
                                        source, _, _ = origins[top]
                                        origins[top] = (
                                            source,
                                            "REF_MAP",
                                            "Unique declared target-type identity mapping.",
                                        )
                                elif item not in live:
                                    loss(
                                        path + "/" + escape(contract.field),
                                        "REFERENCE_UNRESOLVED",
                                        "WARNING",
                                        "Reference missing, quarantined or ambiguous; retained without guessing.",
                                        "Partial-bundle reference remains unresolved.",
                                    )

                    visit(output, contract.field.split("."))
            candidates.sort(key=lambda item: (item[2]["object_type"], item[2]["id"]))
            for i, (path, _kind, output, origins) in enumerate(candidates):
                for field, value in output.items():
                    source, operation, reason = origins[field]
                    source_value = pointer(raw, source) if source is not None else None
                    for suffix, leaf in leaves(value):
                        ledger.append(
                            MappingEntry(
                                source_path=source,
                                target_path=f"/canonical_bundle/objects/{i}/"
                                + escape(field)
                                + suffix,
                                operation=operation,
                                source_value_hash=digest(source_value)
                                if source is not None
                                else None,
                                target_value_hash=digest(leaf),
                                reason=reason,
                                evidence=[path],
                            )
                        )
        else:
            isolate("", None, raw, "unsupported_or_ambiguous_family_or_target", [])
        if isinstance(raw, dict):
            # Preserve ALL top-level sections, including accepted decisions, fields
            # outside canonical objects and historical quarantined future priors.
            for key in sorted(raw):
                if not (detection.family == "CANONICAL_0_1" and key == "objects"):
                    unsupported.append(
                        dict(
                            source_path="/" + escape(key),
                            value=raw[key],
                            classification="historical_section_snapshot",
                            operation="PRESERVE_RAW",
                        )
                    )
                    loss(
                        "/" + escape(key),
                        "STRUCTURAL_LOSS",
                        "WARNING",
                        "Original section layout and unsupported nested history retained separately.",
                        "Canonical mappings are explicit; raw remainder is not activated as evidence.",
                    )
        for item in unsupported:
            ledger.append(
                MappingEntry(
                    source_path=item["source_path"],
                    target_path="/raw_document" + item["source_path"],
                    operation="PRESERVE_RAW",
                    source_value_hash=digest(item["value"]),
                    target_value_hash=digest(item["value"]),
                    reason="Unrepresented historical value retained verbatim.",
                )
            )
        for i, item in enumerate(quarantine):
            ledger.append(
                MappingEntry(
                    source_path=item.source_path,
                    target_path=f"/quarantined_items/{i}/raw_payload",
                    operation="QUARANTINE",
                    source_value_hash=item.raw_payload_hash,
                    target_value_hash=item.raw_payload_hash,
                    reason=item.reason_code,
                )
            )
        bundle = {"objects": [o for _, _, o, _ in candidates]}
        report = self.validator.validate(bundle, {"validation_mode": "partial_bundle"})
        summary = dict(
            validator_version=report.validator_version,
            mode=report.mode,
            object_count=report.object_count,
            outcome_counts=report.outcome_counts,
            errors=[i.model_dump(mode="json") for i in report.errors],
            deterministic_hash=report.deterministic_hash,
        )
        status = (
            "UNSUPPORTED"
            if spec is None or (quarantine and not candidates)
            else "PARTIAL"
            if quarantine or detection.family == "SUMMARY_ONLY_LEGACY" or report.errors
            else "LOSSY_BUT_SAFE"
            if losses or unknowns or unsupported
            else "LOSSLESS"
        )
        result = AdaptationResult(
            source_sha256=source_hash,
            source_family=detection.family,
            detection_status=detection.status,
            adapter_id=spec.adapter_id if spec else None,
            target_schema_version=target_schema_version,
            status=status,
            canonical_bundle=bundle,
            quarantined_items=quarantine,
            mapping_ledger=sorted(ledger, key=lambda m: m.target_path),
            losses=sorted(
                {item.loss_id: item for item in losses}.values(), key=lambda item: item.loss_id
            ),
            unknowns=sorted(unknowns, key=serialized),
            warnings=["Raw historical sections are preserved, not active canonical evidence."]
            if unsupported
            else [],
            unsupported_fields=sorted(unsupported, key=lambda v: v["source_path"]),
            source_object_count=len(records),
            canonical_object_count=len(candidates),
            quarantined_object_count=len(quarantine),
            deterministic_hash="",
            validator_report_summary=summary,
            raw_document=raw,
            canonical_reconstruction_forbidden=detection.family == "SUMMARY_ONLY_LEGACY",
        )
        manifest = {
            k: getattr(result, k)
            for k in (
                "source_sha256",
                "source_family",
                "detection_status",
                "adapter_id",
                "adapter_version",
                "target_ontology_version",
                "target_schema_version",
                "status",
                "source_object_count",
                "canonical_object_count",
                "quarantined_object_count",
            )
        }
        manifest.update(
            unknown_count=len(unknowns),
            loss_count=len(result.losses),
            mapping_ledger_hash=digest([m.model_dump(mode="json") for m in result.mapping_ledger]),
            canonical_bundle_hash=digest(bundle),
            validator_summary=summary,
            source_unchanged=True,
        )
        result.adaptation_manifest = manifest
        result.deterministic_hash = digest(
            result.model_dump(mode="json", exclude={"deterministic_hash"})
        )
        if serialized(raw) != before:
            raise RuntimeError("Adapter mutated its input snapshot")
        return result

    def adapt_file(self, input_path, output_path=None):
        source = Path(input_path).resolve()
        destination = Path(output_path).resolve() if output_path is not None else None
        manifest = (
            destination.with_name(destination.stem + ".adaptation_manifest.json")
            if destination
            else None
        )
        for target in (destination, manifest):
            if target and (
                target == source or (target.exists() and os.path.samefile(source, target))
            ):
                raise ValueError("INPUT_ERROR: input and output refer to the same file")
            if target and target.exists():
                raise ValueError("INPUT_ERROR: refusing to overwrite an existing artifact")
        data = source.read_bytes()
        before = hashlib.sha256(data).hexdigest()
        result = self.adapt(load_document(data), source_sha256=before)
        if hashlib.sha256(source.read_bytes()).hexdigest() != before:
            raise RuntimeError("Source changed during adaptation; output not written")
        if destination:
            destination.parent.mkdir(parents=True, exist_ok=True)
            for target, value in (
                (destination, result.model_dump(mode="json")),
                (manifest, result.adaptation_manifest),
            ):
                with target.open("x", encoding="utf8", newline="\n") as stream:
                    stream.write(
                        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
                    )
        return result
