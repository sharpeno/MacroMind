from copy import deepcopy

import pytest

from .helpers import has, issues, obj, step


def argument(**fields):
    defaults = dict(
        premises=["a"],
        steps=[step()],
        final_conclusion="b",
        most_fragile_step=["edge"],
        reasoner_id="analyst",
    )
    defaults.update(fields)
    return [obj("Claim", "a"), obj("Claim", "b"), obj("Argument", "arg", **defaults)]


def test_dag_attribution_preserved(engine):
    values = argument(steps=[step(reasoner_id="model", expression_level="model_reconstruction")])
    before = deepcopy(values)
    report = engine.validate(values)
    assert not report.errors and has(report, "V-ARG003", "PASS")
    assert values == before
    detail = issues(report, "V-ARG005")[0].details
    assert detail["overall_reasoner"] == "analyst" and detail["edge_reasoner"] == "model"


def test_graph_cycle_and_self_cycle(engine):
    values = argument(steps=[step("one"), step("two", ["b"], "a")], most_fragile_step=["one"])
    assert has(engine.validate(values), "V-ARG003", "ERROR")
    values = argument(steps=[step("edge", ["a"], "a")])
    assert has(engine.validate(values), "V-ARG003", "ERROR")


def test_step_alias_cycle(engine):
    values = argument(
        steps=[step("one", ["two"], "b"), step("two", ["one"], "a")], most_fragile_step=["one"]
    )
    assert has(engine.validate(values), "V-ARG003", "ERROR")


def test_duplicate_orphan_and_bad_node_refs(engine):
    assert has(engine.validate(argument(steps=[step(), step()])), "V-ARG001", "ERROR")
    assert has(engine.validate(argument(steps=[step(premises=[])])), "V-ARG004", "WARNING")
    values = argument(intermediate_conclusions=["absent"])
    assert has(engine.validate(values), "V-REF004", "ERROR")
    assert has(engine.validate(argument(final_conclusion="a")), "V-ARG004", "WARNING")


@pytest.mark.parametrize(
    "fragile,outcome",
    [
        (["missing"], "ERROR"),
        (None, "INDETERMINATE"),
        ({"state": "unknown"}, "INDETERMINATE"),
        (["/steps/0"], "PASS"),
        (["edge"], "PASS"),
    ],
)
def test_fragile_reference(engine, fragile, outcome):
    assert has(engine.validate(argument(most_fragile_step=fragile)), "V-ARG002", outcome)


def test_argument_gaps_are_explicit(engine):
    report = engine.validate(argument())
    assert has(report, "V-ARG006", "INDETERMINATE") and not report.errors


def test_local_global_collision_is_not_an_invented_cycle(engine):
    values = argument(steps=[step("a", ["a"], "b")], most_fragile_step=["a"])
    report = engine.validate(values)
    assert has(report, "V-ARG003", "INDETERMINATE") and not report.errors
