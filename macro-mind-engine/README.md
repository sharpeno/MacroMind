# MacroMind Engine

新增独立的[任务运行框架与模型接入](docs/current/RUNTIME.md)：在隔离任务快照上执行，不改变正式数据或方法验收状态。


当前入口：[项目进度](docs/current/STATUS.md) · [目录地图](docs/current/STRUCTURE.md) · [操作与续接](docs/current/OPERATIONS.md)。

当前首五期数据为 run_005，最新人工反馈已落实；尚未完成新新闻分析与可调用分析师框架。执行 `.\.venv\Scripts\python.exe scripts/operations/project_status.py` 只读核对最新指针、封存产物与计数。历史阶段报告保留当时结论，不代表当前全部能力。

Python 3.12+, Pydantic v2, Draft 2020-12 JSON Schema, PyYAML, Typer and pytest.
Ontology 0.3 remains frozen; executable schema and registry version are 0.1.0.
Production import and Analyst/Core Skills remain NOT_READY. Validator, legacy compatibility, audit and the five-episode pilot now have implementations and evidence; see the current status page for scope and limitations.

Frozen Contract is authoritative. Schema does not redefine Ontology. Validator does
not repair facts. Migration does not re-extract semantics. Review does not waive
schema validity. Unknown is valid data. Model inference is attributed. Original
artifacts are immutable. All transformations must be diffable and runs auditable.

## Setup

From this directory, with Python 3.12+ available:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test]"
```

`requirements-lock.txt` records the tested environment. The package includes the
generated enums; registry YAML and authoritative frozen inputs are external paths,
so always pass explicit paths for CLI operations. No contract is embedded/copied.

## Commands

```powershell
.\.venv\Scripts\macromind.exe contract verify --contract-root ../golden_sample_test/core_ontology/v0.3
.\.venv\Scripts\macromind.exe registry verify --registry-root registries/v0_3
.\.venv\Scripts\macromind.exe schema export --contract-root ../golden_sample_test/core_ontology/v0.3 --registry-root registries/v0_3 --output-root schemas/v0_3
.\.venv\Scripts\python.exe -m pytest
```

All three commands output deterministic result JSON to stdout and per-run structured
JSON metadata to stderr. Contract verification returns 0 for PASS/warnings and 1
for errors. The CLI now includes validation, compatibility and audit commands; run `macromind --help` for the exact command names. Analyst Skill and production readiness are not implied.
CLI JSON uses lossless Unicode escapes for Windows code-page independence; exported
schema files remain UTF-8.

## Developer builds

```powershell
.\.venv\Scripts\python.exe scripts/generate_enums.py
.\.venv\Scripts\python.exe scripts/build_schema_docs.py
.\.venv\Scripts\python.exe scripts/run_gate.py
```

Registry YAML is authoritative; generated Python enums and JSON Schemas are checked
for drift. Do not hand-edit generated files. A schema's structural acceptance does
not establish forecast admission, truth, sufficient evidence or causal validity.

See `docs/SCHEMA_MAPPING.md` for field origins, requiredness and unknown semantics;
`docs/REGISTRY_POLICY.md` for vocabulary and identity policy; and
`docs/PHASE1_0_1_2_GATE.md` plus `phase1/gate_result.json` for actual acceptance results.
Only D02/D07/D16/D18 receive partial-progress overlays. No historical debt is resolved
by declaration. Git collaboration instructions are in [COLLABORATING.md](../COLLABORATING.md).

