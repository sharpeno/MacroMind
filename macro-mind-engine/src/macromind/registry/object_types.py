from macromind.contract.version import CORE_NAMES
from macromind.errors import RegistryError


def check_object_types(entries) -> None:
    core = {entry.name for entry in entries if entry.kind == "core"}
    if core != set(CORE_NAMES):
        raise RegistryError(
            f"Core set differs from Frozen 14: {sorted(core.symmetric_difference(CORE_NAMES))}"
        )
    expected = {
        "Scenario": "auxiliary",
        "AnalystMethodSignal": "analyst_auxiliary",
        "ReviewQueueItem": "governance",
    }
    by_name = {e.name: e.kind for e in entries}
    if any(by_name.get(name) != kind for name, kind in expected.items()):
        raise RegistryError("Required non-Core classification missing or invalid")
