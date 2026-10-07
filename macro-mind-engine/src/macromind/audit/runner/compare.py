"""Exact engineering comparison: disappearance is not resolution."""

from pathlib import Path

from ..continuity_index.resolution import strict_json
from ..ids import canonical_bytes, digest_bytes, semantic_hash
from .models import VERSION
from .storage import atomic_bytes, complete, new_directory, read_package, require, write_json


def difference(left, right):
    common = set(left) & set(right)
    return {
        "added": sorted(set(right) - set(left)),
        "removed": sorted(set(left) - set(right)),
        "common": sorted(common),
        "changed": sorted(key for key in common if left[key] != right[key]),
    }


def compare_runs(left, left_hash, right, right_hash, output_root):
    left, right = Path(left).resolve(), Path(right).resolve()
    lm, rm = read_package(left, left_hash), read_package(right, right_hash)
    require(lm["package_type"] == rm["package_type"] == "AUDIT_RUN", "NOT_AUDIT_RUN")

    def read(root, name):
        return strict_json((root / (name + ".json")).read_bytes())

    ls, rs = read(left, "semantic_summary"), read(right, "semantic_summary")
    require(ls["data_kind"] == rs["data_kind"], "MIXED_COMPARISON_KIND")
    lv, rv = ls["versions"], rs["versions"]
    context_same = ls["validation_context"] == rs["validation_context"]
    foundation_same = ls["foundation_hashes"] == rs["foundation_hashes"]
    scope_same = ls["source_hashes"] == rs["source_hashes"] and ls["input_mode"] == rs["input_mode"]
    base_compatible = all(
        lv[k] == rv[k] for k in ("runner", "projection", "normalization", "ontology", "schema")
    )
    pattern_ok = (
        base_compatible and lv["patterns"] == rv["patterns"] and foundation_same and context_same
    )
    continuity_ok = (
        base_compatible
        and lv["continuity"] == rv["continuity"]
        and ls["resolution_context_hash"] == rs["resolution_context_hash"]
    )
    compatibility = {
        "pattern": "COMPARABLE" if pattern_ok else "NOT_COMPARABLE",
        "continuity": "COMPARABLE" if continuity_ok else "NOT_COMPARABLE",
        "same_validation_context": context_same,
        "same_foundation": foundation_same,
        "same_input_scope": scope_same,
        "same_conditions": context_same and foundation_same and scope_same and lv == rv,
        "versions_left": lv,
        "versions_right": rv,
        "removed_means": "NOT_PRESENT_IN_SELECTED_RUN_NOT_RESOLVED",
        "continuity_coverage": [
            read(root, "run_summary")["coverage"]["continuity_business_coverage"]
            for root in (left, right)
        ],
    }
    lp, rp = read(left, "pattern_aggregation"), read(right, "pattern_aggregation")
    lc, rc = read(left, "continuity_result"), read(right, "continuity_result")
    patterns_left = {p["pattern_id"]: p for p in lp["patterns"]}
    patterns_right = {p["pattern_id"]: p for p in rp["patterns"]}
    pattern_diff = (
        difference(patterns_left, patterns_right) if pattern_ok else {"status": "NOT_COMPARABLE"}
    )
    if pattern_ok:
        pattern_diff["occurrences"] = {
            pid: {
                "left": [
                    {"run_content_identity": ls["deterministic_hash"], "record_id": rid}
                    for rid in patterns_left.get(pid, {}).get("occurrence_record_ids", [])
                ],
                "right": [
                    {"run_content_identity": rs["deterministic_hash"], "record_id": rid}
                    for rid in patterns_right.get(pid, {}).get("occurrence_record_ids", [])
                ],
                "count_delta": patterns_right.get(pid, {}).get("occurrence_count", 0)
                - patterns_left.get(pid, {}).get("occurrence_count", 0),
            }
            for pid in sorted(set(patterns_left) | set(patterns_right))
        }
    diff = {
        "comparison_version": VERSION,
        "data_kind": ls["data_kind"],
        "inputs": difference(
            {h: h for h in ls["source_hashes"]}, {h: h for h in rs["source_hashes"]}
        ),
        "configuration": {
            "left": {k: ls[k] for k in ("input_mode", "validation_context", "foundation_hashes")},
            "right": {k: rs[k] for k in ("input_mode", "validation_context", "foundation_hashes")},
        },
        "disposition_count_delta": {
            k: rp["disposition_counts"].get(k, 0) - lp["disposition_counts"].get(k, 0)
            for k in sorted(set(lp["disposition_counts"]) | set(rp["disposition_counts"]))
        },
        "patterns": pattern_diff,
        "relations": difference(
            lc["relation_index"]["relations_by_key"], rc["relation_index"]["relations_by_key"]
        )
        if continuity_ok
        else {"status": "NOT_COMPARABLE"},
        "memberships": difference(
            lc["membership_index"]["memberships_by_id"], rc["membership_index"]["memberships_by_id"]
        )
        if continuity_ok
        else {"status": "NOT_COMPARABLE"},
        "resolution_context": {
            "left": ls["resolution_context_hash"],
            "right": rs["resolution_context_hash"],
        },
        "compatibility": compatibility,
    }
    run = new_directory(output_root, [left, right])
    try:
        write_json(
            run,
            "request.json",
            {
                "left": str(left),
                "left_manifest_sha256": left_hash,
                "right": str(right),
                "right_manifest_sha256": right_hash,
            },
        )
        write_json(run, "input_manifests.json", {"left": lm, "right": rm})
        write_json(run, "compatibility.json", compatibility)
        write_json(run, "diff.json", diff)
        atomic_bytes(
            run,
            "report.md",
            (
                "# 工程运行比较\n\n移除仅表示本次输入范围内未出现，不表示问题已修复。重跑同一来源不算独立证据。\n\n"
                + canonical_bytes(compatibility).decode()
                + "\n完整增减及来源见 diff.json；不作观点变化或方法推断。\n"
            ).encode("utf-8"),
        )
        require(
            digest_bytes((left / "manifest.json").read_bytes()) == left_hash
            and digest_bytes((right / "manifest.json").read_bytes()) == right_hash,
            "COMPARE_INPUT_CHANGED",
            exit_code=3,
        )
        # Re-read every left/right artifact, not just the manifests.
        read_package(left, left_hash)
        read_package(right, right_hash)
        sha = complete(run, "COMPARISON", {"comparison": semantic_hash(diff)})
        read_package(run, sha)
        return {
            "comparison_dir": str(run),
            "manifest_sha256": sha,
            "exit_code": 0,
            "compatibility": compatibility,
        }
    except BaseException:
        marker = run / "manifest.json"
        if marker.exists():
            marker.unlink()
        raise
