"""Disposable cross-process check for the Sidecaravan MCP boundary."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--memkeeper", default="memkeeper")
    args = parser.parse_args()
    root = Path(__file__).parents[1]
    env = os.environ | {"PYTHONPATH": str(root / "src"), "SCV_MEMKEEPER": args.memkeeper}
    with tempfile.TemporaryDirectory(prefix="scv-mcp-") as data_dir:
        env["SCV_DATA_DIR"] = data_dir
        initialized = subprocess.run(
            [sys.executable, "-m", "scv.cli", "init"],
            cwd=root, env=env, text=True, capture_output=True, check=True,
        )
        token = json.loads(initialized.stdout)["token"]
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {
                "name": "scv.memory.save",
                "arguments": {"auth_token": token, "content": "MCP handoff works", "source": "mcp-lifecycle", "author": "test"},
            }},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {
                "name": "scv.memory.recall",
                "arguments": {"auth_token": token, "query": "handoff", "limit": 5},
            }},
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {
                "name": "scv.memory.recall",
                "arguments": {"auth_token": "wrong", "query": "handoff"},
            }},
        ]
        completed = subprocess.run(
            [sys.executable, "-m", "scv.cli", "mcp"],
            cwd=root, env=env,
            input="\n".join(json.dumps(request) for request in requests) + "\n",
            text=True, capture_output=True, check=True,
        )
        responses = [json.loads(line) for line in completed.stdout.splitlines()]
        assert len(responses) == 5
        assert any("MCP handoff works" in response["result"]["content"][0]["text"] for response in responses[3:])
        assert responses[4]["result"]["isError"] is True
        assert "access denied" in responses[4]["result"]["content"][0]["text"]
    print("Sidecaravan MCP lifecycle: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
