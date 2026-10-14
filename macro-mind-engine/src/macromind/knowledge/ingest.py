"""Validate a complete evidence batch in a private DB before committing it via SQLite backup.

Offline/idempotent: source discovery remains a separate step. Single writer only.
"""

import argparse
import hashlib
import json
import tempfile
from pathlib import Path

from macromind.knowledge.store import DEFAULT_DB, KnowledgeStore


def ingest(batch_path, db_path=DEFAULT_DB):
    batch_path = Path(batch_path)
    batch = json.loads(batch_path.read_text(encoding="utf-8-sig"))
    # Never claim a saved raw source unless its contents still match the acquisition hash.
    for source in batch["sources"]:
        provenance = source["version"].get("provenance", {})
        if provenance.get("raw_file"):
            raw = (batch_path.parent / provenance["raw_file"]).resolve()
            if not raw.is_relative_to(batch_path.parent.resolve()):
                raise ValueError("Raw source must stay inside the batch directory")
            if hashlib.sha256(raw.read_bytes()).hexdigest() != provenance["raw_sha256"]:
                raise ValueError("Raw source checksum mismatch")
    live = KnowledgeStore(db_path)
    before = live.stats()
    try:
        with tempfile.TemporaryDirectory(prefix="macromind-ingest-") as temp:
            staged = KnowledgeStore(Path(temp) / "staged.sqlite3")
            try:
                live.db.backup(staged.db)
                for series in batch["series"]:
                    staged.series(**series)
                ids = []
                for source in batch["sources"]:
                    doc = staged.document(**source["document"])
                    version = staged.version(document_id=doc, **source["version"])
                    for observation in source["observations"]:
                        ids.append(staged.observation(source_version=version, **observation))
                assert staged.db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
                assert not staged.db.execute("PRAGMA foreign_key_check").fetchall()
                after = staged.stats()
                # Backup performs one destination transaction. Failed staging never touches live rows.
                staged.db.backup(live.db)
            finally:
                staged.close()
        return {
            "batch_id": batch["batch_id"],
            "batch_sha256": hashlib.sha256(batch_path.read_bytes()).hexdigest(),
            "before": before,
            "after": after,
            "observation_ids": ids,
            "new_observations": after["observations"] - before["observations"],
            "integrity_check": "ok",
            "foreign_key_errors": [],
        }
    finally:
        live.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", type=Path)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = ingest(args.batch, args.db)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.receipt:
        args.receipt.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
