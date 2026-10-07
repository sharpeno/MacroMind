import json
import shutil
from pathlib import Path

import pytest
import yaml
from macromind.contract.version import CORE_NAMES
from macromind.errors import RegistryError, VersionError
from macromind.registry._enums import ENUM_TYPES
from macromind.registry.enums import generate_python_enums, read_yaml, render_python_enums
from macromind.registry.loader import load_registry
from macromind.registry.models import RegistryBundle
from macromind.schema.auxiliary import AUXILIARY_MODELS
from macromind.schema.core import CORE_MODELS

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "registries/v0_3"


@pytest.fixture
def registry_copy(tmp_path):
    return Path(shutil.copytree(REGISTRY, tmp_path / "registry"))


def mutate(root, file, fn):
    path = root / f"{file}.yaml"
    data = read_yaml(path)
    fn(data)
    path.write_text(yaml.safe_dump(data, sort_keys=True, allow_unicode=True), encoding="utf-8")


def test_R001_R002_R003_R004_R009():
    bundle = load_registry(REGISTRY)
    assert {n for n, o in bundle.object_types.items() if o.kind == "core"} == set(CORE_NAMES)
    assert bundle.object_types["Scenario"].kind == "auxiliary"
    assert bundle.object_types["AnalystMethodSignal"].kind == "analyst_auxiliary"
    assert "0.1.0" in bundle.schema_versions.schema_versions
    assert set(CORE_MODELS) | set(AUXILIARY_MODELS) <= set(bundle.object_types)


def test_R005_duplicate_value_rejected(registry_copy):
    mutate(registry_copy, "semantic_roles", lambda d: d["entries"].append(d["entries"][0]))
    with pytest.raises(RegistryError, match="duplicate"):
        load_registry(registry_copy)


def test_R006_unknown_required(registry_copy):
    mutate(
        registry_copy,
        "semantic_roles",
        lambda d: d.update(entries=[e for e in d["entries"] if e["value"] != "unknown"]),
    )
    with pytest.raises(RegistryError, match="unknown"):
        load_registry(registry_copy)


def test_R007_unknown_relation_endpoint(registry_copy):
    mutate(registry_copy, "relations", lambda d: d["entries"][0].update(target_types=["NewCore"]))
    with pytest.raises(RegistryError, match="endpoint"):
        load_registry(registry_copy)


def test_R008_schema_enum_coverage():
    bundle = load_registry(REGISTRY)
    assert set(bundle.enums) == set(ENUM_TYPES)
    for name, enum in ENUM_TYPES.items():
        assert [e.value for e in enum] == [e.value for e in bundle.enums[name].entries]
    for model in [*CORE_MODELS.values(), *AUXILIARY_MODELS.values()]:
        for name, definition in model.model_json_schema().get("$defs", {}).items():
            if "enum" in definition:
                assert definition["enum"] == [e.value for e in bundle.enums[name].entries]


def test_R010_frozen_unchanged(contract_root):
    from macromind.contract.loader import load_frozen_contract

    before = {p.name: p.read_bytes() for p in contract_root.iterdir() if p.is_file()}
    load_registry(REGISTRY)
    assert load_frozen_contract(contract_root).integrity_report.status == "PASS"
    assert before == {p.name: p.read_bytes() for p in contract_root.iterdir() if p.is_file()}


def test_R011_generated_deterministic(tmp_path):
    generate_python_enums(REGISTRY, tmp_path / "one.py")
    generate_python_enums(REGISTRY, tmp_path / "two.py")
    assert (tmp_path / "one.py").read_bytes() == (tmp_path / "two.py").read_bytes()
    assert (tmp_path / "one.py").read_bytes() == (
        ROOT / "src/macromind/registry/_enums.py"
    ).read_bytes()
    assert render_python_enums(REGISTRY).encode() == (tmp_path / "one.py").read_bytes()


def test_R012_roundtrip_deterministic(registry_copy):
    before = load_registry(registry_copy)
    for path in registry_copy.glob("*.yaml"):
        path.write_text(
            yaml.safe_dump(read_yaml(path), sort_keys=True, allow_unicode=True), encoding="utf-8"
        )
    after = load_registry(registry_copy)
    assert before.model_dump() == after.model_dump()
    assert (
        RegistryBundle.model_validate_json(before.model_dump_json()).model_dump()
        == after.model_dump()
    )
    assert json.dumps(before.model_dump(), sort_keys=True) == json.dumps(
        after.model_dump(), sort_keys=True
    )


@pytest.mark.parametrize(
    "case",
    [
        "core_missing",
        "extra_core",
        "duplicate_object",
        "replacement",
        "schema_version",
        "auto_merge",
        "stale_enums",
        "duplicate_yaml_key",
        "missing_file",
        "yaml_code",
    ],
)
def test_registry_fail_closed(registry_copy, case):
    if case == "core_missing":
        mutate(registry_copy, "object_types", lambda d: d["entries"].pop(0))
    elif case == "extra_core":
        mutate(registry_copy, "object_types", lambda d: d["entries"][-1].update(kind="core"))
    elif case == "duplicate_object":
        mutate(registry_copy, "object_types", lambda d: d["entries"].append(d["entries"][0]))
    elif case == "replacement":
        mutate(
            registry_copy,
            "semantic_roles",
            lambda d: d["entries"][0].update(
                deprecated=True, status="deprecated", replacement="bad"
            ),
        )
    elif case == "schema_version":
        mutate(
            registry_copy, "schema_versions", lambda d: d.update(schema_versions=["not-a-version"])
        )
    elif case == "auto_merge":
        mutate(
            registry_copy,
            "identity_policies",
            lambda d: d["entries"][0].update(automatic_merge=True),
        )
    elif case == "stale_enums":
        mutate(registry_copy, "semantic_roles", lambda d: d["entries"][0].update(value="new_role"))
    elif case == "duplicate_yaml_key":
        (registry_copy / "relations.yaml").write_text(
            "entries: []\nentries: []\n", encoding="utf-8"
        )
    elif case == "missing_file":
        (registry_copy / "failure_types.yaml").unlink()
    else:
        (registry_copy / "relations.yaml").write_text(
            "!!python/object/apply:builtins.print ['unsafe']", encoding="utf-8"
        )
    with pytest.raises(RegistryError):
        load_registry(registry_copy)


def test_wrong_ontology_version():
    with pytest.raises(VersionError):
        load_registry(REGISTRY, "0.4")
