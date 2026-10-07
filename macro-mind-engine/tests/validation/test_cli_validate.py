import json

import pytest
from macromind.cli.main import app
from typer.testing import CliRunner

from .conftest import CONTRACT, REGISTRY
from .helpers import obj


@pytest.mark.parametrize(
    "payload,code",
    [
        ({"objects": []}, 0),
        ({"objects": [obj("Claim")]}, 0),
        ({"objects": [obj("Claim", source_refs=["absent"])]}, 1),
        ({"wrong": []}, 2),
    ],
)
def test_cli_codes(tmp_path, payload, code):
    path = tmp_path / "input.json"
    path.write_text(json.dumps(payload), encoding="utf8")
    result = CliRunner().invoke(
        app,
        [
            "validate",
            "--input",
            str(path),
            "--contract-root",
            str(CONTRACT),
            "--registry-root",
            str(REGISTRY),
        ],
    )
    assert result.exit_code == code, result.output
    data = json.loads(result.stdout)
    assert json.loads(result.stderr)["operation"] == "validate"
    if code != 2:
        assert data["executed_rule_count"] == data["rule_count"]


def test_cli_context_mode_override_and_bad_json(tmp_path):
    path, context = tmp_path / "bundle.json", tmp_path / "context.json"
    path.write_text(
        json.dumps({"objects": [obj("Claim", source_refs=["absent"])]}), encoding="utf8"
    )
    context.write_text(
        json.dumps({"validation_mode": "partial_bundle", "sample_label": "opaque"}), encoding="utf8"
    )
    args = [
        "validate",
        "--input",
        str(path),
        "--contract-root",
        str(CONTRACT),
        "--registry-root",
        str(REGISTRY),
        "--context",
        str(context),
    ]
    result = CliRunner().invoke(app, args)
    assert result.exit_code == 0
    assert json.loads(result.stdout)["indeterminate"]
    assert CliRunner().invoke(app, args + ["--mode", "complete_bundle"]).exit_code == 1
    assert CliRunner().invoke(app, args + ["--mode", "guess"]).exit_code == 2
    path.write_text("{bad", encoding="utf8")
    assert CliRunner().invoke(app, args).exit_code == 2
