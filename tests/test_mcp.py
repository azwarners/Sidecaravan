import io
import json

from scv.config import Config
from scv.mcp import McpServer, serve


def test_initialize_and_tool_discovery_are_structured(tmp_path):
    config = Config(tmp_path, tmp_path / "team.sqlite", tmp_path / "team.token", "memkeeper")
    request = io.StringIO(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize"}) + "\n")
    output = io.StringIO()
    serve(config, request, output)
    response = json.loads(output.getvalue())
    assert response["result"]["serverInfo"]["name"] == "sidecaravan"


def test_unauthorized_tool_call_is_an_error(tmp_path):
    config = Config(tmp_path, tmp_path / "team.sqlite", tmp_path / "team.token", "missing")
    token = config.initialize()
    server = McpServer(config)
    denied = server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "scv.memory.recall", "arguments": {"auth_token": "wrong", "query": "x"}}})
    assert denied["result"]["isError"] is True
    assert "access denied" in denied["result"]["content"][0]["text"]


def test_authorized_call_forwards_to_engine(tmp_path, monkeypatch):
    config = Config(tmp_path, tmp_path / "team.sqlite", tmp_path / "team.token", "memkeeper")
    token = config.initialize()
    server = McpServer(config)
    seen = {}
    monkeypatch.setattr(server.engine, "search", lambda query, limit: seen.update(query=query, limit=limit) or [{"id": "m1"}])
    response = server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "scv.memory.recall", "arguments": {"auth_token": token, "query": "decision", "limit": 3}}})
    assert response["result"]["isError"] is False
    assert seen == {"query": "decision", "limit": 3}
