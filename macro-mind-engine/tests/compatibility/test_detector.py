from copy import deepcopy

import pytest
from macromind.compatibility import detect_legacy_format

from .helpers import legacy


@pytest.mark.parametrize(
    "ma1,status,family", [(False, "STRONG", "V0_3_LEGACY"), (True, "EXACT", "MA1_COMPAT")]
)
def test_markers_and_shape(ma1, status, family):
    value = legacy(ma1=ma1)
    result = detect_legacy_format(value)
    assert result.status == status and result.family == family
    assert result == detect_legacy_format(deepcopy(value))


def test_ambiguous_not_selected(compatibility):
    value = legacy(ma1=True)
    value["07_actors_events_indicators_observations_policies"] = {}
    detection = detect_legacy_format(value)
    assert detection.status == "AMBIGUOUS" and detection.conflicting_signatures
    result = compatibility.adapt(value)
    assert (
        result.status == "UNSUPPORTED"
        and result.adapter_id is None
        and not result.canonical_bundle["objects"]
    )


@pytest.mark.parametrize(
    "value",
    [{"unrecognized": [1, 2]}, 42, [], {"ma1_migration": {"schema_version": "V0.3.1-MA.1"}}],
)
def test_unknown_is_unsupported(compatibility, value):
    assert detect_legacy_format(value).status == "UNKNOWN"
    assert compatibility.adapt(value).status == "UNSUPPORTED"


def test_labels_not_format():
    value = legacy(ma1=True)
    value.update(filename="GS002.json", directory="GS003", sample_label="GS004", golden_id="GS001")
    first = detect_legacy_format(value)
    value.update(filename="banana", directory="random", sample_label="GS001", golden_id="GS005")
    assert first == detect_legacy_format(value)


def test_unknown_explicit_version():
    value = legacy(ma1=True)
    value["ma1_migration"]["schema_version"] = "V999"
    assert detect_legacy_format(value).status == "UNKNOWN"
