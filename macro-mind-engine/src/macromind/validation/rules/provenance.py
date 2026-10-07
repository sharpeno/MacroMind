from .common import finding


def claim_sources(s):
    for obj in s.index.of_type("Claim"):
        yield finding(
            obj,
            "PASS" if obj.source_refs else "WARNING",
            "/source_refs",
            "Provenance presence does not establish truth.",
            evidence=obj.source_refs,
        )


def consistency(s):
    for obj in s.index.of_type("SourceSegment", "ClaimOccurrence"):
        version = s.index.get(obj.source_version_ref)
        segment = (
            s.index.get(obj.source_segment_ref) if obj.object_type == "ClaimOccurrence" else obj
        )
        conflicts, incomplete = [], []
        if (
            segment
            and segment.object_type == "SourceSegment"
            and version
            and version.object_type == "SourceVersion"
        ):
            if segment.source_ref != version.source_ref:
                conflicts.append("segment_source_differs_from_version_source")
            if segment.source_version_ref and segment.source_version_ref != version.id:
                conflicts.append("occurrence_version_differs_from_segment_version")
        if (
            obj.object_type == "ClaimOccurrence"
            and segment
            and segment.object_type == "SourceSegment"
        ):
            source = s.index.get(segment.source_ref)
            if (
                source
                and source.object_type == "Source"
                and source.family_ref
                and obj.origin_family_ref
                and source.family_ref != obj.origin_family_ref
            ):
                conflicts.append("occurrence_family_differs_from_source_family")
            claim = s.index.get(obj.claim_ref)
            if (
                claim
                and claim.object_type == "Claim"
                and claim.source_refs
                and segment.source_ref not in claim.source_refs
            ):
                incomplete.append("occurrence_source_not_in_claim_sources")
        yield finding(
            obj,
            "ERROR"
            if conflicts
            else ("PASS" if segment and version and not incomplete else "INDETERMINATE"),
            message="Occurrence/segment/version provenance consistency.",
            conflicts=conflicts,
            incomplete=incomplete,
        )
    for obj in s.index.of_type("Source"):
        for ref in obj.version_refs + obj.segment_refs:
            target = s.index.get(ref)
            if target and target.object_type in ("SourceVersion", "SourceSegment"):
                yield finding(
                    obj,
                    "PASS" if target.source_ref == obj.id else "ERROR",
                    message="Source back-reference consistency.",
                    related=[ref],
                )


def independence(s):
    for obj in s.index.of_type("SourceFamily"):
        yield finding(
            obj,
            "INDETERMINATE",
            "/source_refs",
            "Source multiplicity is not independent support; independence scoring is outside this validator.",
            evidence=obj.source_refs,
        )
