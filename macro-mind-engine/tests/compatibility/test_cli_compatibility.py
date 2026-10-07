import json

import pytest
from macromind.cli.main import app
from typer.testing import CliRunner

from .conftest import CONTRACT, REGISTRY
from .helpers import legacy


@pytest.mark.parametrize("value,code", [(legacy(), 0), ({"unknown": True}, 1)])
def test_detect_cli(tmp_path, value, code):
    source = tmp_path / "input.any"
    source.write_text(json.dumps(value), encoding="utf8")
    result = CliRunner().invoke(app, ["compatibility", "detect", "--input", str(source)])
    assert result.exit_code == code
    assert "shape_hash" in json.loads(result.stdout)


def test_adapt_cli_codes_and_no_inplace(tmp_path):
    source = tmp_path / "input.json"
    output = tmp_path / "result.json"
    source.write_text(json.dumps(legacy()), encoding="utf8")
    args = [
        "compatibility",
        "adapt",
        "--input",
        str(source),
        "--contract-root",
        str(CONTRACT),
        "--registry-root",
        str(REGISTRY),
    ]
    result = CliRunner().invoke(app, args + ["--output", str(output)])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["status"] in ("LOSSY_BUT_SAFE", "PARTIAL")
    assert CliRunner().invoke(app, args + ["--output", str(source)]).exit_code == 2
    assert CliRunner().invoke(app, args + ["--in-place"]).exit_code == 2
    source.write_text("{broken", encoding="utf8")
    assert CliRunner().invoke(app, args).exit_code == 2
    source.write_text('{"random":true}', encoding="utf8")
    assert CliRunner().invoke(app, args).exit_code == 1
