from macromind.compatibility import CompatibilityAdapterRegistry, detect_legacy_format

from .helpers import legacy


def test_registry_deterministic_selection():
    registry = CompatibilityAdapterRegistry()
    assert registry.catalog() == CompatibilityAdapterRegistry().catalog()
    assert len({s.adapter_id for s in registry.specs}) == len(registry.specs)
    detection = detect_legacy_format(legacy(ma1=True))
    selected = registry.select(detection)
    assert selected.source_family == "MA1_COMPAT" and selected.target_schema_version == "0.1.0"
    assert registry.select(detection, "9.9.9") is None
    assert registry.select(detect_legacy_format({"unknown": True})) is None
