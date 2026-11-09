"""Small newline-delimited JSON-RPC/MCP server for shared team memory.

The server deliberately keeps authorization at the invocation boundary. MCP
does not provide a portable caller-identity field, so clients must include the
configured team token as ``auth_token`` in every memory call.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from .config import Config
from .errors import ScvError
from .memkeeper import Memkeeper

SERVER_INFO = {"name": "sidecaravan", "version": "0.1.0"}


def _tool(name: str, description: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": {"auth_token": {"type": "string", "description": "Team access token"}, **properties},
            "required": ["auth_token", *required],
            "additionalProperties": False,
        },
    }


def tools() -> list[dict[str, Any]]:
    return [
        _tool("scv.memory.save", "Save one explicit shared team memory.", {
            "content": {"type": "string"}, "kind": {"type": "string"},
            "source": {"type": "string"}, "author": {"type": "string"}, "session": {"type": "string"},
        }, ["content"]),
        _tool("scv.memory.recall", "Recall bounded shared memories with provenance.", {
            "query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 100},
        }, ["query"]),
        _tool("scv.memory.read", "Read one memory and its available history.", {"id": {"type": "string"}}, ["id"]),
        _tool("scv.memory.correct", "Supersede one memory with an explicit correction.", {
            "id": {"type": "string"}, "content": {"type": "string"},
            "source": {"type": "string"}, "author": {"type": "string"},
        }, ["id", "content"]),
        _tool("scv.memory.forget", "Tombstone one memory.", {
            "id": {"type": "string"}, "reason": {"type": "string"},
        }, ["id", "reason"]),
    ]


def _text_result(value: Any, *, error: bool = False) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(value, sort_keys=True)}], "isError": error}


class McpServer:
    def __init__(self, config: Config):
        self.config = config
        self.engine = Memkeeper(config)

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        supplied = arguments.pop("auth_token", None)
        self.config.authorize(supplied)
        if name == "scv.memory.save":
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            payload = {
                "content": arguments["content"], "kind": arguments.get("kind", "decision"),
                "source": {"source": arguments.get("source", "unknown"), "author": arguments.get("author", "unknown"), "session": arguments.get("session"), "recorded_at": now},
                "metadata_json": self.config.as_metadata(), "observed_at": now,
            }
            return self.engine.remember(payload)
        if name == "scv.memory.recall":
            limit = arguments.get("limit", 10)
            if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 100:
                raise ScvError("limit must be between 1 and 100")
            return self.engine.search(arguments["query"], limit)
        if name == "scv.memory.read":
            return self.engine.get(arguments["id"])
        if name == "scv.memory.correct":
            from datetime import datetime, timezone
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            return self.engine.remember({"content": arguments["content"], "kind": "decision", "source": {"source": arguments.get("source", "correction"), "author": arguments.get("author", "unknown"), "recorded_at": now}, "metadata_json": self.config.as_metadata(), "observed_at": now, "supersedes": [arguments["id"]]})
        if name == "scv.memory.forget":
            return self.engine.forget(arguments["id"], arguments["reason"])
        raise ScvError(f"unknown tool: {name}")

    def handle(self, request: dict[str, Any]) -> dict[str, Any] | None:
        method = request.get("method")
        request_id = request.get("id")
        if method in {"notifications/initialized", "notifications/cancelled"}:
            return None
        if method == "ping":
            return {"jsonrpc": "2.0", "id": request_id, "result": {}}
        if method == "initialize":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"protocolVersion": "2024-11-05", "capabilities": {"tools": {"listChanged": False}}, "serverInfo": SERVER_INFO, "instructions": "Use auth_token in every scv.memory tool call."}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": tools()}}
        if method == "tools/call":
            try:
                params = request.get("params", {})
                result = self.call_tool(params["name"], dict(params.get("arguments", {})))
                return {"jsonrpc": "2.0", "id": request_id, "result": _text_result(result)}
            except (KeyError, ScvError) as exc:
                return {"jsonrpc": "2.0", "id": request_id, "result": _text_result({"error": str(exc)}, error=True)}
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": f"method not found: {method}"}}


def serve(config: Config, input_stream: Any = sys.stdin, output_stream: Any = sys.stdout) -> None:
    server = McpServer(config)
    for line in input_stream:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            response = server.handle(request)
        except json.JSONDecodeError as exc:
            response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": str(exc)}}
        if response is not None:
            output_stream.write(json.dumps(response, separators=(",", ":")) + "\n")
            output_stream.flush()


def main() -> None:
    serve(Config.from_env())
