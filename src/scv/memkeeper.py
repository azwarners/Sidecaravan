from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from .config import Config
from .errors import ScvError

MEMKEEPER_VERSION = "0.5.3"


class Memkeeper:
    def __init__(self, config: Config):
        self.config = config

    def run(self, command: str, payload: dict[str, Any] | None = None, *extra: str) -> Any:
        args = [self.config.memkeeper, command, "--store", str(self.config.store)]
        if payload is not None:
            args += ["--json", json.dumps(payload, separators=(",", ":"))]
        args += list(extra)
        try:
            completed = subprocess.run(args, text=True, capture_output=True, check=False)
        except FileNotFoundError as exc:
            raise ScvError(
                "Memkeeper is not installed or SCV_MEMKEEPER is incorrect; "
                f"install pinned Memkeeper {MEMKEEPER_VERSION}"
            ) from exc
        if completed.returncode:
            detail = (completed.stderr or completed.stdout).strip()
            raise ScvError(f"Memkeeper {command} failed ({completed.returncode}): {detail}")
        output = completed.stdout.strip()
        if not output:
            return None
        try:
            return json.loads(output)
        except json.JSONDecodeError as exc:
            raise ScvError(f"Memkeeper returned non-JSON output for {command}: {output[:300]}") from exc

    def init(self) -> Any:
        self.config.store.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        return self.run("init")

    def remember(self, payload: dict[str, Any]) -> Any:
        return self.run("remember", payload)

    def search(self, query: str, limit: int) -> Any:
        return self.run("search", {"query": query, "limit": limit, "include_content": True, "include_source": True})

    def get(self, memory_id: str) -> Any:
        return self.run("get", None, "--id", memory_id, "--include-history", "--include-source")

    def forget(self, memory_id: str, reason: str) -> Any:
        return self.run("forget", {"id": memory_id, "reason": reason, "mode": "tombstone"})

    def backup(self, output: Path) -> Any:
        output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        return self.run("backup", {"output": str(output)})

    def export(self, output: Path) -> Any:
        output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        return self.run("export", {"output": str(output), "format": "jsonl"})

    def restore(self, backup: Path, force: bool) -> None:
        if not backup.is_file():
            raise ScvError(f"backup does not exist: {backup}")
        if self.config.store.exists() and not force:
            raise ScvError("store already exists; pass --force to restore over it")
        self.config.store.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        temporary = self.config.store.with_suffix(self.config.store.suffix + ".restore.tmp")
        shutil.copy2(backup, temporary)
        temporary.replace(self.config.store)
