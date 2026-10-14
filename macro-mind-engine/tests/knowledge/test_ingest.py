import json
from copy import deepcopy
from pathlib import Path

import pytest

from macromind.knowledge.ingest import ingest
from macromind.knowledge.store import KnowledgeStore

BATCH = Path(__file__).resolve().parents[2] / "knowledge_base/batches/historical_001/batch.json"


def test_real_batch_cutoffs_and_idempotence(tmp_path):
    db = tmp_path / "facts.sqlite3"
    first = ingest(BATCH, db)
    assert first["new_observations"] == 20
    assert ingest(BATCH, db)["new_observations"] == 0
    s = KnowledgeStore(db)
    try:
        assert not s.observations("US_CPI_ALL_MOM_SA", "2023-10-12T12:29:59Z", "release_value")
        assert (
            s.observations(
                "US_CPI_ALL_MOM_SA", "2023-10-12T12:30:00Z", "release_value", strict_version=True
            )[0]["value"]
            == "0.4"
        )
        assert len(s.observations("US_SP500_PRESS_CLOSE", "2023-10-19T20:21:46Z")) == 1
        assert len(s.observations("US_SP500_PRESS_CLOSE", "2023-10-19T20:21:47Z")) == 2
        assert not s.observations("CN_SSE_PRESS_CLOSE", "2023-10-19T20:35:30+08:00")
        assert len(s.observations("CN_SSE_PRESS_CLOSE", "2023-10-19T20:36:00+08:00")) == 1
        assert not s.observations(
            "US_SP500_PRESS_CLOSE", "2023-10-21T00:00:00Z", strict_version=True
        )
    finally:
        s.close()


def test_invalid_batch_does_not_partially_commit(tmp_path):
    batch = deepcopy(json.loads(BATCH.read_text(encoding="utf-8-sig")))
    for source in batch["sources"]:
        source["version"]["provenance"]["raw_file"] = None
    batch["sources"][-1]["observations"][-1]["value"] = "nan"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(batch), encoding="utf-8")
    db = tmp_path / "facts.sqlite3"
    with pytest.raises(ValueError):
        ingest(path, db)
    s = KnowledgeStore(db)
    try:
        assert s.stats()["observations"] == 0
        assert s.stats()["documents"] == 0
    finally:
        s.close()
