"""Local HTTP protocol demonstration. Scripted replies, NOT a real model evaluation."""

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from macromind.runtime.provider import ModelConfig
from macromind.runtime.runner import run_task
from macromind.runtime.storage import TaskStore, read_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, required=True)
    args = parser.parse_args()
    fixture = Path(__file__).parent
    requests = []

    class FixtureServer(BaseHTTPRequestHandler):
        def do_POST(self):
            payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            requests.append(payload)
            # Follow the wire conversation, not elapsed time or an in-memory round counter.
            used_tool = any(m["role"] == "tool" for m in payload["messages"])
            if not used_tool:
                message = {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "fixture_read_1",
                            "type": "function",
                            "function": {
                                "name": "read_evidence",
                                "arguments": json.dumps(
                                    {"document_id": "news", "start_line": 1, "end_line": 3}
                                ),
                            },
                        }
                    ],
                }
                finish = "tool_calls"
            else:
                output = {
                    "outcome": "analysis",
                    "summary": "合成测试：材料只支持试点计划，不能确认落地成效。",
                    "methods_used": ["M01", "M02"],
                    "claims": [
                        {
                            "statement": "测试材料记载了计划。",
                            "kind": "source_statement",
                            "citations": [
                                {
                                    "document_id": "news",
                                    "start_line": 2,
                                    "end_line": 2,
                                    "quote": "测试机构计划开展小规模试点。",
                                }
                            ],
                        }
                    ],
                    "gaps": ["缺少实际执行与效果证据。"],
                }
                message = {"role": "assistant", "content": json.dumps(output, ensure_ascii=False)}
                finish = "stop"
            body = {
                "id": "synthetic-http-fixture",
                "model": "scripted-fixture-not-an-llm",
                "choices": [{"message": message, "finish_reason": finish}],
                "usage": None,
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureServer)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        store = TaskStore(args.store)
        state = store.create(fixture / "task.json")
        config = ModelConfig(
            protocol="chat_completions",
            model="scripted-fixture-not-an-llm",
            base_url=f"http://127.0.0.1:{server.server_port}/v1",
            api_key_env="MACROMIND_FIXTURE_UNUSED_KEY",
        )
        state = run_task(store, state["id"], config)
        folder = store.task(state["id"]) / "attempts/attempt_001"
        print(
            json.dumps(
                {
                    "verification": "LOCAL_HTTP_FIXTURE_ONLY",
                    "state": state,
                    "requests": len(requests),
                    "report": str(folder / "report.md"),
                    "usage": read_json(folder / "usage.json"),
                },
                ensure_ascii=True,
                indent=2,
            )
        )
        if state["status"] != "succeeded":
            raise SystemExit(1)
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


if __name__ == "__main__":
    main()
