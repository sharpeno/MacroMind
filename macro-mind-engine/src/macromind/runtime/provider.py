"""Standard-library adapters for Responses and Chat Completions function tools."""

import json
import os
import time
from dataclasses import dataclass
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from pydantic import Field, model_validator

from macromind.runtime.models import StrictModel


class ProviderError(RuntimeError):
    """Safe diagnostic: never include headers, response bodies or credentials."""


class ModelConfig(StrictModel):
    protocol: Literal["responses", "chat_completions"] = "responses"
    base_url: str
    model: str = Field(min_length=1, max_length=150)
    api_key_env: str = Field(default="MACROMIND_API_KEY", pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    timeout_seconds: float = Field(default=45, gt=0, le=60)
    max_retries: int = Field(default=2, ge=0, le=3)
    max_rounds: int = Field(default=8, ge=2, le=20)
    chat_token_parameter: Literal["max_completion_tokens", "max_tokens"] = "max_completion_tokens"
    max_output_tokens: int = Field(default=3000, ge=128, le=16000)

    @model_validator(mode="after")
    def endpoint(self):
        url = urlsplit(self.base_url)
        if url.username or url.password or url.query or url.fragment or not url.hostname:
            raise ValueError("Base URL must have no credentials, query or fragment")
        local = url.hostname in ("localhost", "127.0.0.1", "::1")
        if url.scheme != "https" and not (local and url.scheme == "http"):
            raise ValueError("HTTPS required except for loopback local models")
        self.base_url = self.base_url.rstrip("/")
        return self


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ProviderError("Provider redirect refused")


@dataclass
class Reply:
    message: dict
    calls: list
    content: str
    usage: dict | None
    actual_model: str | None
    response_id: str | None


class CompatibleProvider:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.key = os.environ.get(config.api_key_env, "")
        if not self.key and urlsplit(config.base_url).hostname not in (
            "localhost",
            "127.0.0.1",
            "::1",
        ):
            raise ProviderError(f"Missing environment variable: {config.api_key_env}")
        self.opener = build_opener(NoRedirect())

    def payload(self, messages, tools):
        cfg = self.config
        if cfg.protocol == "chat_completions":
            return {
                "model": cfg.model,
                "messages": messages,
                "tools": tools,
                "tool_choice": "auto",
                cfg.chat_token_parameter: cfg.max_output_tokens,
            }
        items = []
        for message in messages[1:]:
            if message["role"] == "assistant":
                items.extend(message["response_output"])
            elif message["role"] == "tool":
                items.append(
                    {
                        "type": "function_call_output",
                        "call_id": message["tool_call_id"],
                        "output": message["content"],
                    }
                )
            else:
                items.append(message)
        return {
            "model": cfg.model,
            "instructions": messages[0]["content"],
            "input": items,
            "tools": [{"type": "function", **t["function"], "strict": False} for t in tools],
            "tool_choice": "auto",
            "max_output_tokens": cfg.max_output_tokens,
            "store": False,
            "include": ["reasoning.encrypted_content"],
        }

    def complete(self, messages, tools, log):
        cfg = self.config
        suffix = "/responses" if cfg.protocol == "responses" else "/chat/completions"
        payload = json.dumps(self.payload(messages, tools), ensure_ascii=False).encode("utf-8")
        if len(payload) > 1_000_000:
            raise ProviderError("Model context exceeded runtime byte limit")
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["Authorization"] = "Bearer " + self.key
        for attempt in range(cfg.max_retries + 1):
            started = time.perf_counter()
            try:
                request = Request(
                    cfg.base_url + suffix, data=payload, headers=headers, method="POST"
                )
                with self.opener.open(request, timeout=cfg.timeout_seconds) as response:
                    raw = response.read(2_000_001)
                if len(raw) > 2_000_000:
                    raise ProviderError("Provider response exceeds size limit")
                data = json.loads(raw)
                reply = self.parse(data)
                log(
                    "model_call",
                    {
                        "request_attempt": attempt + 1,
                        "elapsed_ms": round((time.perf_counter() - started) * 1000),
                        "requested_model": cfg.model,
                        "actual_model": reply.actual_model,
                        "response_id": reply.response_id,
                        "usage": reply.usage,
                        "billing_verified": False,
                    },
                )
                return reply
            except HTTPError as exc:
                retryable = exc.code in (408, 429, 500, 502, 503, 504)
                error = f"Provider HTTP {exc.code}"
                exc.close()
            except (URLError, TimeoutError, OSError):
                retryable, error = True, "Provider connection or timeout failure"
            except (ValueError, KeyError, TypeError, IndexError):
                retryable, error = False, "Malformed or incomplete provider response"
            except ProviderError as exc:
                retryable, error = False, str(exc)
            log(
                "model_error",
                {
                    "request_attempt": attempt + 1,
                    "error": error,
                    "elapsed_ms": round((time.perf_counter() - started) * 1000),
                    "usage": None,
                    "billing_unknown": True,
                    "will_retry": retryable and attempt < cfg.max_retries,
                },
            )
            if not retryable or attempt == cfg.max_retries:
                raise ProviderError(error)
            time.sleep(min(2**attempt, 4))
        raise ProviderError("Provider retry budget exhausted")

    def parse(self, data):
        if not isinstance(data, dict):
            raise ProviderError("Provider response must be an object")
        if data.get("usage") is not None and not isinstance(data["usage"], dict):
            raise ProviderError("Provider usage must be an object")
        if self.config.protocol == "responses":
            if data.get("status") != "completed":
                raise ProviderError("Response incomplete, refused or failed")
            output = data["output"]
            calls = [
                {
                    "id": item["call_id"],
                    "type": "function",
                    "function": {"name": item["name"], "arguments": item["arguments"]},
                }
                for item in output
                if item["type"] == "function_call"
            ]
            texts = [
                part["text"]
                for item in output
                if item["type"] == "message"
                for part in item.get("content", [])
                if part["type"] == "output_text"
            ]
            content = "".join(texts)
            message = {"role": "assistant", "response_output": output}
            usage = data.get("usage")
        else:
            choice = data["choices"][0]
            if choice["finish_reason"] not in ("stop", "tool_calls"):
                raise ProviderError("Completion truncated, filtered or incomplete")
            raw_message = choice["message"]
            calls = raw_message.get("tool_calls") or []
            content = raw_message.get("content") or ""
            message = {"role": "assistant", "content": content or None}
            if calls:
                message["tool_calls"] = calls
            # Some compatible reasoning providers require this field in subsequent turns.
            if "reasoning_content" in raw_message:
                message["reasoning_content"] = raw_message["reasoning_content"]
            reported = data.get("usage")
            usage = (
                None
                if reported is None
                else {
                    "input_tokens": reported.get("prompt_tokens"),
                    "output_tokens": reported.get("completion_tokens"),
                    "total_tokens": reported.get("total_tokens"),
                }
            )
        if not isinstance(content, str) or len(calls) > 12 or (not calls and not content):
            raise ProviderError("Empty or oversized model turn")
        ids = set()
        for call in calls:
            if (
                call.get("type") != "function"
                or not isinstance(call["id"], str)
                or call["id"] in ids
            ):
                raise ProviderError("Invalid or duplicate tool call ID")
            ids.add(call["id"])
            if not isinstance(call["function"]["arguments"], str):
                raise ProviderError("Tool arguments must be JSON text")
        return Reply(message, calls, content, usage, data.get("model"), data.get("id"))
