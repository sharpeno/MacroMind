import hashlib
import json
import re

from .models import DetectionResult


def serialized(value):
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def digest(value):
    return hashlib.sha256(serialized(value).encode("utf8")).hexdigest()


def key_name(key):
    return re.sub(r"^\d+_", "", key).lower()


def shape(value):
    if isinstance(value, dict):
        return {
            k: shape(v)
            for k, v in sorted(value.items())
            if k not in ("filename", "directory", "sample_label", "golden_id", "sample_id")
        }
    if isinstance(value, list):
        return sorted({serialized(shape(v)) for v in value})
    return type(value).__name__


def detect_legacy_format(document):
    matches, versions = [], {}
    if isinstance(document, str):
        matches.append("SUMMARY_ONLY_LEGACY")
    elif isinstance(document, dict):
        keys = {key_name(k) for k in document}
        migration = document.get("ma1_migration")
        if isinstance(migration, dict) and "schema_version" in migration:
            versions["ma1_migration.schema_version"] = migration["schema_version"]
        for k in ("schema_version", "ontology_version"):
            if k in document:
                versions[k] = document[k]
        pre = {"claims", "sources", "actors_events_indicators_observations_policies"} <= keys
        numbered = {"claims", "sources", "structural_processes", "arguments"} <= keys
        ma1 = versions.get("ma1_migration.schema_version") == "V0.3.1-MA.1"
        # MA.1 extends the numbered V0.3 envelope. The parent signature is not
        # a conflicting alternative. A separate pre-MA envelope IS a conflict.
        if pre:
            matches.append("LEGACY_PRE_MA")
        if ma1 and numbered:
            matches.append("MA1_COMPAT")
        elif numbered:
            matches.append("V0_3_LEGACY")
        if keys >= {"objects"} and isinstance(document.get("objects"), list):
            objects = document["objects"]
            if objects and all(
                isinstance(o, dict)
                and o.get("schema_version") == "0.1.0"
                and o.get("ontology_version") == "0.3"
                for o in objects
            ):
                matches.append("CANONICAL_0_1")
    conflicts = []
    if len(matches) > 1:
        status, family = "AMBIGUOUS", "UNKNOWN_LEGACY"
        conflicts = sorted(matches)
    elif matches:
        family = matches[0]
        status = "EXACT" if family in ("MA1_COMPAT", "CANONICAL_0_1") else "STRONG"
        if versions.get("ma1_migration.schema_version") not in (None, "V0.3.1-MA.1"):
            status, family = "UNKNOWN", "UNKNOWN_LEGACY"
            conflicts = ["unrecognized_explicit_legacy_schema_version"]
    else:
        status, family = "UNKNOWN", "UNKNOWN_LEGACY"
    return DetectionResult(
        family=family,
        status=status,
        evidence=sorted(matches) + conflicts,
        matched_signatures=sorted(matches),
        conflicting_signatures=conflicts,
        explicit_version=versions,
        shape_hash=digest(shape(document)),
    )
