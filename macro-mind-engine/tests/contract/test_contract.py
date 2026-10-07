import json

import pytest
from macromind.contract.loader import load_frozen_contract
from macromind.contract.semantic_hash import calculate_file_sha256
from macromind.errors import ContractIntegrityError


def mutate(root, filename, fn, rehash=False):
    path = root / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    fn(data)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    if rehash:
        mutate(
            root,
            "freeze_manifest.json",
            lambda m: [
                r.update(sha256=calculate_file_sha256(path))
                for r in m["canonical_output_hashes"]
                if r["path"].endswith("/" + filename)
            ],
        )


def test_C001_valid(contract_root):
    c = load_frozen_contract(contract_root)
    assert c.integrity_report.status == "PASS"
    assert len(c.core_objects) == 14 and len(c.core_boundaries) == 15


@pytest.mark.parametrize(
    "field,value",
    [
        ("version", "0.4"),
        ("status", "DRAFT"),
        ("formal_freeze_executed", False),
        ("core_blockers", ["blocker"]),
        ("semantic_hash", "0" * 64),
        ("freeze_readiness_decision", "READY"),
        ("core_principle_count", 15),
        ("formal_freeze_executed", "true"),
        ("production_import_ready", True),
    ],
    ids=[
        "C002",
        "C003",
        "C004",
        "C009",
        "C010",
        "readiness",
        "principles",
        "strict_boolean",
        "readiness_guard",
    ],
)
def test_invalid_manifest(contract_copy, field, value):
    mutate(contract_copy, "freeze_manifest.json", lambda m: m.update({field: value}))
    with pytest.raises(ContractIntegrityError):
        load_frozen_contract(contract_copy)


@pytest.mark.parametrize(
    "file,key,extra",
    [
        ("core_objects.json", "objects", False),
        ("core_objects.json", "objects", True),
        ("core_boundaries.json", "boundaries", False),
        ("core_principles.json", "principles", False),
    ],
    ids=["C005", "C006", "C007", "principle_missing"],
)
def test_wrong_membership_with_updated_file_hash(contract_copy, file, key, extra):
    mutate(contract_copy, file, lambda d: d[key].append(d[key][0]) if extra else d[key].pop(), True)
    with pytest.raises(ContractIntegrityError):
        load_frozen_contract(contract_copy)


def test_C008_bytes_changed(contract_copy):
    path = contract_copy / "core_objects.json"
    path.write_bytes(path.read_bytes() + b"\n")
    with pytest.raises(ContractIntegrityError, match="sha256"):
        load_frozen_contract(contract_copy)


def test_C011_original_unchanged(contract_root):
    before = {p.name: p.read_bytes() for p in contract_root.iterdir() if p.is_file()}
    load_frozen_contract(contract_root)
    assert before == {p.name: p.read_bytes() for p in contract_root.iterdir() if p.is_file()}


@pytest.mark.parametrize(
    "mode", ["missing", "bad_json", "missing_hash", "duplicate_key", "projection_drift"]
)
def test_fail_closed(contract_copy, mode):
    if mode == "missing":
        (contract_copy / "core_objects.json").unlink()
    elif mode == "bad_json":
        (contract_copy / "core_objects.json").write_text("{", encoding="utf-8")
    elif mode == "missing_hash":
        mutate(contract_copy, "freeze_manifest.json", lambda m: m["canonical_output_hashes"].pop())
    elif mode == "duplicate_key":
        (contract_copy / "core_objects.json").write_text(
            '{"objects":[],"objects":[]}', encoding="utf-8"
        )
    else:
        mutate(
            contract_copy,
            "core_objects.json",
            lambda m: m["objects"][0].update(core_definition="changed"),
            True,
        )
    with pytest.raises(ContractIntegrityError):
        load_frozen_contract(contract_copy)
