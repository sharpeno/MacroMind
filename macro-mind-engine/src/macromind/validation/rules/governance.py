from .common import finding


def review(s):
    for obj in s.index.of_type("ReviewQueueItem"):
        yield finding(
            obj,
            message="Review status is workflow metadata; every registered rule still runs.",
            review_status=obj.status,
        )


def immutable(s):
    # Actual before/after assertion is performed by the engine after all rules.
    yield finding(
        None, message="Validator operates on an isolated snapshot and verifies it after execution."
    )


def promotion(s):
    for obj in s.index.of_type("Heuristic"):
        yield finding(
            obj,
            "INDETERMINATE",
            "/status",
            "Candidate/unknown is not validated Skill; no promotion operation or structured Skill evidence contract exists.",
            schema_gap="skill_promotion_evidence",
        )
