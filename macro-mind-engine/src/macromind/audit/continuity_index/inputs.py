"""Loading requires bytes and external trust; there is no ambient resolver."""

from dataclasses import dataclass

from pydantic import ValidationError

from ..continuity import ContinuityAnnotation
from ..ids import canonical_bytes, semantic_hash
from .identity import annotation_projection
from .models import ContinuityIndexError, ContinuityIndexInputBundle, TrustedContextDescriptor
from .resolution import locate, require, strict_json, verify_snapshot


@dataclass(frozen=True)
class VerifiedInput:
    bundle_bytes: bytes
    artifact_bytes: tuple[tuple[str, bytes], ...]
    trusted_context_bytes: bytes


def decode(verified, check_semantic=True):
    try:
        bundle = ContinuityIndexInputBundle.model_validate(strict_json(verified.bundle_bytes))
        trusted = TrustedContextDescriptor.model_validate(
            strict_json(verified.trusted_context_bytes)
        )
        artifacts = dict(verified.artifact_bytes)
        require(len(artifacts) == len(verified.artifact_bytes), "DUPLICATE_ARTIFACT")
        require(bundle.data_kind == trusted.data_kind, "DATA_KIND_MISMATCH")
        manifest = {x.artifact_id: x.sha256 for x in bundle.input_manifest}
        require(len(manifest) == len(bundle.input_manifest), "DUPLICATE_ARTIFACT")
        require(
            set(manifest) == set(artifacts) and manifest == bundle.source_artifact_hashes,
            "MANIFEST_MISMATCH",
        )
        for entry in bundle.input_manifest:
            require(entry.data_kind == bundle.data_kind, "MIXED_DATA_KIND", entry.artifact_id)
            locate(artifacts, entry.artifact_id, "", entry.sha256)
        require(bundle.resolution_snapshot in artifacts, "MISSING_SNAPSHOT")
        snapshot = verify_snapshot(artifacts[bundle.resolution_snapshot], artifacts, trusted)
        known = frozenset(x.ref for x in snapshot.references)
        sources = {x.annotation_index: x for x in bundle.annotation_sources}
        require(
            len(sources) == len(bundle.annotation_sources)
            and set(sources) == set(range(len(bundle.annotation_payloads))),
            "ANNOTATION_SOURCE_COVERAGE",
        )
        annotations, provenance = {}, {}
        for index, payload in enumerate(bundle.annotation_payloads):
            source = sources[index]
            require("known_refs" not in payload, "PAYLOAD_KNOWN_REFS_FORBIDDEN", str(index))
            original = locate(
                artifacts,
                source.source_artifact_id,
                source.source_pointer,
                source.source_artifact_hash,
            )
            require(
                canonical_bytes(original) == canonical_bytes(payload)
                and canonical_bytes(source.raw_payload) == canonical_bytes(payload)
                and semantic_hash(payload) == source.payload_hash,
                "PAYLOAD_MISMATCH",
                str(index),
            )
            annotation = ContinuityAnnotation.model_validate({**payload, "known_refs": known})
            aid = annotation.annotation_id
            if aid in annotations:
                same = canonical_bytes(provenance[aid]["raw_payload"]) == canonical_bytes(payload)
                raise ContinuityIndexError(
                    "DUPLICATE_ANNOTATION_ID" if same else "ANNOTATION_ID_CONTENT_CONFLICT", aid
                )
            annotations[aid] = annotation.model_dump(mode="json")
            provenance[aid] = {
                **source.model_dump(mode="json"),
                "raw_payload": payload,
                "claimed_resolution_status": payload.get("resolution_status"),
                "computed_resolution_status": annotation.resolution_status,
            }
        annotations = dict(sorted(annotations.items()))
        semantic = {
            "contract_version": bundle.contract_version,
            "data_kind": bundle.data_kind,
            "resolution_context_hash": snapshot.semantic_hash,
            "annotations": [annotation_projection(a) for a in annotations.values()],
        }
        if check_semantic:
            require(
                bundle.deterministic_hash == semantic_hash(semantic), "BUNDLE_SEMANTIC_MISMATCH"
            )
        return bundle, snapshot, annotations, provenance, semantic
    except ValidationError as error:
        raise ContinuityIndexError("CONTRACT_VALIDATION_ERROR", str(error)) from error


def load_input_bundle(bundle_bytes, explicitly_supplied_artifact_bytes, trusted_context_descriptor):
    try:
        trusted = TrustedContextDescriptor.model_validate(trusted_context_descriptor)
    except ValidationError as error:
        raise ContinuityIndexError("TRUST_DESCRIPTOR_ERROR", str(error)) from error
    verified = VerifiedInput(
        bytes(bundle_bytes),
        tuple(
            sorted((key, bytes(value)) for key, value in explicitly_supplied_artifact_bytes.items())
        ),
        canonical_bytes(trusted.model_dump(mode="json")),
    )
    decode(verified)
    return verified


def serialize_input_bundle(bundle, artifacts, trusted):
    value = (
        bundle.model_dump(mode="json")
        if isinstance(bundle, ContinuityIndexInputBundle)
        else dict(bundle)
    )
    value["deterministic_hash"] = ""
    verified = VerifiedInput(
        canonical_bytes(value),
        tuple(sorted(artifacts.items())),
        canonical_bytes(
            trusted.model_dump(mode="json")
            if isinstance(trusted, TrustedContextDescriptor)
            else trusted
        ),
    )
    value["deterministic_hash"] = semantic_hash(decode(verified, check_semantic=False)[4])
    return canonical_bytes(value)
