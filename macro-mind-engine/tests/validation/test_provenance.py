from .helpers import has, obj


def test_occurrence_version_source_conflict(engine):
    values = [
        obj("Source", "s1"),
        obj("Source", "s2"),
        obj("Claim", "c", source_refs=["s1"]),
        obj("SourceVersion", "v", source_ref="s2"),
        obj("SourceSegment", "seg", source_ref="s1", source_version_ref="v"),
        obj("ClaimOccurrence", claim_ref="c", source_segment_ref="seg", source_version_ref="v"),
    ]
    assert has(engine.validate(values), "V-PROV002", "ERROR")
    values[3]["source_ref"] = "s1"
    assert not engine.validate(values).errors


def test_source_family_never_counts_independent_support(engine):
    values = [
        obj("Source", "s1", family_ref="family"),
        obj("Source", "s2", family_ref="family"),
        obj("SourceFamily", "family", source_refs=["s1", "s2"]),
        obj("Claim", source_refs=["s1", "s2"]),
    ]
    report = engine.validate(values)
    assert has(report, "V-PROV003", "INDETERMINATE") and not report.errors
    assert "truth" not in values[-1] and "independent_support_count" not in values[-1]


def test_unknown_segment_version_and_incomplete_claim_sources(engine):
    values = [
        obj("Source", "s1"),
        obj("Source", "s2"),
        obj("Claim", "c", source_refs=["s2"]),
        obj("SourceVersion", "v", source_ref="s1"),
        obj("SourceSegment", "seg", source_ref="s1", source_version_ref=None),
        obj("ClaimOccurrence", claim_ref="c", source_segment_ref="seg", source_version_ref="v"),
    ]
    report = engine.validate(values)
    assert not report.errors and has(report, "V-PROV002", "INDETERMINATE")
