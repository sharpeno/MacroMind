from macromind.validation import ValidationInputError

from .helpers import legacy


def test_transport_only_integration(compatibility, real_results):
    for result in real_results.values():
        report = compatibility.validator.validate(
            result.canonical_bundle, {"validation_mode": "partial_bundle"}
        )
        assert not any(i.rule_id in ("V-SCH001", "V-SCH002") for i in report.errors)
        assert report.outcome_counts == result.validator_report_summary["outcome_counts"]
    try:
        compatibility.validator.validate(legacy())
    except ValidationInputError:
        pass
    else:
        raise AssertionError("Raw legacy transport must still be rejected")


def test_validator_errors_not_repaired(compatibility):
    value = legacy([{"claim_id": "c", "statement": "C", "source_refs": ["c"]}])
    result = compatibility.adapt(value)
    assert result.status == "PARTIAL"
    assert any(i["rule_id"] == "V-REF003" for i in result.validator_report_summary["errors"])
    assert result.canonical_bundle["objects"][0]["source_refs"] == ["c"]
