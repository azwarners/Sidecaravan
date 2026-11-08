#!/usr/bin/env python3
"""Exercise Sidecaravan against a real, pinned Memkeeper binary.

This is intentionally a subprocess-based check: every CLI invocation starts a
new Python and Memkeeper process, making persistence across restarts explicit.
It uses a temporary store and never touches the user's normal Sidecaravan data.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def run_scv(data_dir: Path, memkeeper: str, *args: str, token: str | None = None) -> tuple[dict[str, Any], str]:
    env = os.environ | {
        "PYTHONPATH": str(ROOT / "src"),
        "SCV_DATA_DIR": str(data_dir),
        "SCV_MEMKEEPER": memkeeper,
    }
    if token is not None:
        env["SCV_TOKEN"] = token
    completed = subprocess.run(
        [sys.executable, "-m", "scv.cli", *args],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )
    if completed.returncode:
        raise AssertionError(f"scv {' '.join(args)} failed: {completed.stderr.strip()}")
    return json.loads(completed.stdout), completed.stderr


def first_id(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("id", "memory_id"):
            if isinstance(value.get(key), str) and not value[key].startswith("evt_"):
                return value[key]
        for child in value.values():
            try:
                return first_id(child)
            except AssertionError:
                pass
    elif isinstance(value, list):
        for child in value:
            try:
                return first_id(child)
            except AssertionError:
                pass
    raise AssertionError(f"Memkeeper response did not contain a memory id: {value!r}")


def contains_text(value: Any, text: str) -> bool:
    if isinstance(value, str):
        return text in value
    if isinstance(value, dict):
        return any(contains_text(child, text) for child in value.values())
    if isinstance(value, list):
        return any(contains_text(child, text) for child in value)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--memkeeper", default="memkeeper")
    args = parser.parse_args()
    try:
        version = subprocess.run([args.memkeeper, "--version"], text=True, capture_output=True)
    except FileNotFoundError as exc:
        raise SystemExit("real Memkeeper v0.5.3 is required; install it or pass --memkeeper PATH") from exc
    if version.returncode or "memkeeper" not in (version.stdout + version.stderr).lower():
        raise SystemExit("a real Memkeeper binary is required; install pinned v0.5.3 or pass --memkeeper PATH")

    with tempfile.TemporaryDirectory(prefix="sidecaravan-real-") as temporary:
        data_dir = Path(temporary) / "data"
        backup = Path(temporary) / "team.sqlite.backup"
        initialized, _ = run_scv(data_dir, args.memkeeper, "init")
        token = initialized["token"]
        repeated, _ = run_scv(data_dir, args.memkeeper, "init")
        assert repeated["token"] == token, "repeat init changed the access token"

        saved, _ = run_scv(
            data_dir,
            args.memkeeper,
            "save",
            "The release checklist requires a signed backup.",
            "--source",
            "real-memkeeper-check",
            "--author",
            "integration",
            token=token,
        )
        original_id = first_id(saved)
        searched, _ = run_scv(data_dir, args.memkeeper, "search", "signed backup", "--limit", "1", token=token)
        assert contains_text(searched, "signed backup"), "bounded search did not return the saved memory"
        read, _ = run_scv(data_dir, args.memkeeper, "read", original_id, token=token)
        assert contains_text(read, "real-memkeeper-check"), "read lost provenance"

        corrected, _ = run_scv(
            data_dir,
            args.memkeeper,
            "correct",
            original_id,
            "The release checklist requires a signed and tested backup.",
            token=token,
        )
        corrected_id = first_id(corrected)
        assert corrected_id != original_id, "correction did not create a superseding record"
        current, _ = run_scv(data_dir, args.memkeeper, "search", "signed tested backup", "--limit", "1", token=token)
        assert contains_text(current, "signed and tested"), "corrected memory was not current"
        assert not contains_text(current, "requires a signed backup."), "superseded memory remained current"

        forgotten, _ = run_scv(
            data_dir, args.memkeeper, "forget", corrected_id, "--reason", "integration cleanup", token=token
        )
        assert contains_text(forgotten, "tombstone"), "forget did not report a tombstone"
        after_forget, _ = run_scv(data_dir, args.memkeeper, "search", "signed tested backup", "--limit", "1", token=token)
        assert not contains_text(after_forget, "signed and tested"), "forgotten memory remained current"

        unauthorized = subprocess.run(
            [sys.executable, "-m", "scv.cli", "search", "signed backup"],
            cwd=ROOT,
            env=os.environ | {"PYTHONPATH": str(ROOT / "src"), "SCV_DATA_DIR": str(data_dir), "SCV_MEMKEEPER": args.memkeeper, "SCV_TOKEN": "wrong"},
            text=True,
            capture_output=True,
        )
        assert unauthorized.returncode != 0 and "access denied" in unauthorized.stderr

        run_scv(data_dir, args.memkeeper, "backup", str(backup), token=token)
        store = data_dir / "team.sqlite"
        store.unlink()
        run_scv(data_dir, args.memkeeper, "restore", str(backup), token=token)
        restored, _ = run_scv(data_dir, args.memkeeper, "search", "signed tested backup", "--limit", "1", token=token)
        assert not contains_text(restored, "signed and tested"), "backup/restore changed tombstone state"

    print("real Memkeeper v0.5.3 lifecycle: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
