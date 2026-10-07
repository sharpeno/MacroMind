import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from macromind.cli.main import app
from typer.testing import CliRunner

ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def test_contract_verify_exit_codes_and_logging(contract_root, tmp_path):
    result = runner.invoke(app, ["contract", "verify", "--contract-root", str(contract_root)])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["ERROR"] == 0
    log = json.loads(result.stderr)
    assert {
        "run_id",
        "operation",
        "version",
        "input_paths",
        "output_paths",
        "errors",
        "warnings",
        "duration",
    } <= log.keys()
    result = runner.invoke(
        app, ["contract", "verify", "--contract-root", str(tmp_path / "missing")]
    )
    assert result.exit_code == 1
    assert json.loads(result.stdout)["ERROR"] > 0


def test_registry_cli():
    result = runner.invoke(
        app, ["registry", "verify", "--registry-root", str(ROOT / "registries/v0_3")]
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["core_count"] == 14


def test_schema_export_cli(contract_root, tmp_path):
    result = runner.invoke(
        app,
        [
            "schema",
            "export",
            "--contract-root",
            str(contract_root),
            "--registry-root",
            str(ROOT / "registries/v0_3"),
            "--output-root",
            str(tmp_path / "schemas"),
        ],
    )
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["schema_count"] == 26


def test_export_refuses_protected_destination(contract_root):
    result = runner.invoke(
        app,
        [
            "schema",
            "export",
            "--contract-root",
            str(contract_root),
            "--registry-root",
            str(ROOT / "registries/v0_3"),
            "--output-root",
            str(contract_root),
        ],
    )
    assert result.exit_code == 1


def test_no_validate_command():
    assert runner.invoke(app, ["validate"]).exit_code == 2


def test_json_logs_survive_windows_legacy_codepage(tmp_path):
    registry = Path(shutil.copytree(ROOT / "registries/v0_3", tmp_path / "注册表"))
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "macromind.cli.main",
            "registry",
            "verify",
            "--registry-root",
            str(registry),
        ],
        capture_output=True,
        env=os.environ | {"PYTHONIOENCODING": "gbk"},
        check=False,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout.decode("ascii"))["status"] == "PASS"
    assert json.loads(result.stderr.decode("ascii"))["input_paths"] == [str(registry)]
