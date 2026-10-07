"""Synthetic canonical fixtures; no Golden input or legacy conversion."""

from copy import deepcopy

from macromind.schema.common import ReasoningStep, ResolutionCriteria
from macromind.validation.index import MODEL_TYPES


def sample(model):
    schema = model.model_json_schema()

    def fill(node):
        if "$ref" in node:
            return fill(schema["$defs"][node["$ref"].split("/")[-1]])
        if "default" in node:
            return deepcopy(node["default"])
        if "const" in node:
            return node["const"]
        if "enum" in node:
            return "unknown" if "unknown" in node["enum"] else node["enum"][0]
        if "anyOf" in node:
            if any(part.get("type") == "null" for part in node["anyOf"]):
                return None
            return fill(node["anyOf"][0])
        kind = node.get("type")
        if kind == "object":
            return {key: fill(value) for key, value in node.get("properties", {}).items()}
        return {
            "array": [],
            "string": "synthetic",
            "number": 0.0,
            "integer": 0,
            "boolean": False,
            "null": None,
        }[kind]

    return fill(schema)


def obj(kind, identity=None, **fields):
    value = sample(MODEL_TYPES[kind])
    value.update(id=identity or kind.lower(), **fields)
    MODEL_TYPES[kind].model_validate(value)  # Fixtures must be canonical before testing mutations.
    return value


def step(identity="edge", premises=None, conclusion="b", **fields):
    value = sample(ReasoningStep)
    value.update(
        id=identity,
        premises=["a"] if premises is None else premises,
        conclusion_ref=conclusion,
        reasoner_id="analyst",
        expression_level="explicit",
        analysis_context="historical_reconstruction",
    )
    value.update(fields)
    return value


def time(date):
    return {
        "text": "opaque temporal expression",
        "start": date + "T00:00:00Z",
        "end": date + "T00:00:00Z",
    }


def criteria(**fields):
    value = sample(ResolutionCriteria)
    value.update(
        description="Recorded criterion",
        reasoner_id="analyst",
        analysis_context="historical_reconstruction",
        set_at=time("2026-01-01"),
        approved_at=time("2026-01-02"),
        evaluation_time=time("2026-12-31"),
        scoring_permitted=True,
    )
    value.update(fields)
    return value


def forecast(**fields):
    defaults = dict(
        claim_ref="claim",
        claimant="analyst",
        modal_strength="likely",
        knowledge_cutoff=time("2026-01-01"),
        prediction_window=time("2026-12-01"),
        resolution_criteria=criteria(),
    )
    defaults.update(fields)
    return obj("Forecast", **defaults)


def issues(report, rule):
    return [i for i in report.issues if i.rule_id == rule]


def has(report, rule, outcome):
    return any(i.outcome == outcome for i in issues(report, rule))
