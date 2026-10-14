"""Usage: python -m macromind.knowledge --help."""

import argparse
import json
from pathlib import Path

from .store import DEFAULT_DB, KnowledgeStore


def main():
    parser = argparse.ArgumentParser(description="按公开时间检索新闻、研报、经济数据和每日行情")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    sub = parser.add_subparsers(dest="command", required=True)
    for cmd in ["init", "stats", "series", "pending"]:
        sub.add_parser(cmd)
    search = sub.add_parser("search")
    search.add_argument("query", nargs="?", default="")
    search.add_argument("--as-of", required=True, help="ISO8601 with UTC offset")
    search.add_argument("--kind")
    search.add_argument("--strict-version", action="store_true")
    search.add_argument("--known-by")
    obs = sub.add_parser("observations")
    obs.add_argument("series_id")
    obs.add_argument("--as-of", required=True)
    obs.add_argument(
        "--field", default="close", choices=["close", "settlement", "fixing", "release_value"]
    )
    obs.add_argument("--strict-version", action="store_true")
    obs.add_argument("--known-by")
    for cmd in ["document", "version", "mention", "observation", "queue"]:
        command = sub.add_parser("add-" + cmd)
        command.add_argument("record", type=Path, help="UTF-8 JSON object of method arguments")
    resolve = sub.add_parser("resolve-queue")
    resolve.add_argument("record", type=Path)
    command = sub.add_parser("add-series")
    command.add_argument("record", type=Path)
    args = parser.parse_args()
    store = KnowledgeStore(args.db)
    try:
        if args.command in ("init", "stats"):
            result = store.stats()
        elif args.command == "series":
            result = [dict(r) for r in store.db.execute("SELECT * FROM series ORDER BY kind,id")]
        elif args.command == "pending":
            result = [
                dict(r)
                for r in store.db.execute(
                    "SELECT * FROM collection_queue WHERE status='pending' ORDER BY kind,target"
                )
            ]
        elif args.command == "search":
            result = store.search(
                args.query, args.as_of, args.kind, args.strict_version, args.known_by
            )
        elif args.command == "observations":
            result = store.observations(
                args.series_id, args.as_of, args.field, args.strict_version, args.known_by
            )
        else:
            record = json.loads(args.record.read_text(encoding="utf-8-sig"))
            method = (
                "resolve_queue"
                if args.command == "resolve-queue"
                else args.command.removeprefix("add-")
            )
            result = {"id": getattr(store, method)(**record)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        store.close()


if __name__ == "__main__":
    main()
