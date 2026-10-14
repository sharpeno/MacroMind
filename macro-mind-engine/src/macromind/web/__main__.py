"""Loopback-only development server. Run: python -m macromind.web."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from macromind.knowledge.store import DEFAULT_DB
from macromind.web.service import DEFAULT_STATE, Workbench

STATIC = Path(__file__).parent / "static"


def make_server(workbench, port=8765):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def send(self, status, body, content_type="application/json; charset=utf-8"):
            if not isinstance(body, bytes):
                body = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
                "connect-src 'self'; object-src 'none'; frame-ancestors 'none'",
            )
            self.end_headers()
            self.wfile.write(body)

        def valid_host(self):
            hosts = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
            return self.headers.get("Host") in hosts

        def do_GET(self):
            if not self.valid_host():
                return self.send(403, {"error": "仅允许本机访问"})
            parts = urlsplit(self.path)
            params = parse_qs(parts.query)
            try:
                if parts.path == "/api/catalog":
                    return self.send(200, workbench.catalog())
                if parts.path == "/api/source":
                    return self.send(200, workbench.source(params.get("id", [""])[0]))
                if parts.path == "/api/state":
                    return self.send(200, workbench.state())
                if parts.path == "/api/graph":
                    return self.send(200, workbench.graph())
                if parts.path == "/api/market":
                    return self.send(200, workbench.market(params.get("id", [""])[0]))
                if parts.path.startswith("/api/jobs/"):
                    return self.send(200, workbench.job(parts.path.rsplit("/", 1)[-1]))
                files = {
                    "/": ("index.html", "text/html; charset=utf-8"),
                    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                    "/market.js": ("market.js", "text/javascript; charset=utf-8"),
                    "/style.css": ("style.css", "text/css; charset=utf-8"),
                }
                if parts.path in files:
                    name, mime = files[parts.path]
                    return self.send(200, (STATIC / name).read_bytes(), mime)
                return self.send(404, {"error": "未找到页面"})
            except ValueError as exc:
                return self.send(400, {"error": str(exc)})
            except Exception:
                return self.send(500, {"error": "读取失败，请检查本地数据文件"})

        def do_POST(self):
            origin = self.headers.get("Origin")
            if (
                not self.valid_host()
                or self.headers.get("X-MacroMind") != "workbench"
                or (origin and origin != "http://" + self.headers.get("Host", ""))
            ):
                return self.send(403, {"error": "请求来源不允许"})
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length < 1 or length > 2_000_000:
                    return self.send(413, {"error": "请求内容过大或为空"})
                if not self.headers.get("Content-Type", "").startswith("application/json"):
                    return self.send(415, {"error": "需要 JSON 请求"})
                data = json.loads(self.rfile.read(length))
                if not isinstance(data, dict):
                    raise ValueError("需要 JSON 对象")
                route = urlsplit(self.path).path
                if route == "/api/chat":
                    return self.send(200, workbench.chat(data))
                if route == "/api/topics":
                    return self.send(200, workbench.save_topic(data))
                if route == "/api/topics/delete":
                    return self.send(200, workbench.delete_topic(data.get("id")))
                if route == "/api/market-links":
                    return self.send(200, workbench.link_market_event(data))
                if route == "/api/market-links/delete":
                    return self.send(200, workbench.remove_market_link(data.get("id")))
                if route == "/api/events":
                    return self.send(200, workbench.annotate_event(data))
                if route == "/api/reviews":
                    return self.send(200, workbench.review(data))
                return self.send(404, {"error": "未知操作"})
            except (ValueError, TypeError) as exc:
                return self.send(400, {"error": str(exc)})
            except Exception:
                return self.send(500, {"error": "操作失败，原始知识库未被修改"})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main():
    parser = argparse.ArgumentParser(description="MacroMind 本地研究工作台")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--state", type=Path, default=DEFAULT_STATE)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--model-config", type=Path)
    parser.add_argument("--method-file", type=Path)
    parser.add_argument("--method-available-on")
    args = parser.parse_args()
    try:
        workbench = Workbench(
            args.db, args.state, args.model_config, args.method_file, args.method_available_on
        )
        server = make_server(workbench, args.port)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"无法启动：{exc}\n")
    print(f"MacroMind: http://127.0.0.1:{server.server_port}", flush=True)
    print(f"Read-only database: {workbench.db_path}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        workbench.pool.shutdown(wait=False, cancel_futures=True)


if __name__ == "__main__":
    main()
