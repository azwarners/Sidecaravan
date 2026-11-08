import json
import os
import stat
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]


def fake_memkeeper(tmp_path: Path) -> Path:
    script = tmp_path / "memkeeper"
    script.write_text(
        """#!/usr/bin/env python3
import json, pathlib, sys
args = sys.argv[1:]
command = args[0]
store = pathlib.Path(args[args.index('--store') + 1])
store.parent.mkdir(parents=True, exist_ok=True)
if command == 'init':
    store.touch()
    print(json.dumps({'initialized': True}))
elif command in ('remember', 'search', 'forget', 'backup'):
    payload = json.loads(args[args.index('--json') + 1])
    if command == 'backup': pathlib.Path(payload['output']).write_bytes(store.read_bytes())
    print(json.dumps({'command': command, 'payload': payload, 'id': 'm1'}))
elif command == 'get': print(json.dumps({'id': args[args.index('--id') + 1]}))
""",
        encoding="utf-8",
    )
    script.chmod(script.stat().st_mode | stat.S_IXUSR)
    return script


def run(tmp_path: Path, *args: str, token: str | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ | {
        "PYTHONPATH": str(ROOT / "src"),
        "SCV_DATA_DIR": str(tmp_path / "data"),
        "SCV_MEMKEEPER": str(fake_memkeeper(tmp_path)),
    }
    if token:
        env["SCV_TOKEN"] = token
    return subprocess.run([sys.executable, "-m", "scv.cli", *args], cwd=ROOT, env=env, text=True, capture_output=True)


def test_init_is_idempotent_and_unauthorized_access_is_denied(tmp_path: Path) -> None:
    first = run(tmp_path, "init")
    assert first.returncode == 0
    token = json.loads(first.stdout)["token"]
    second = run(tmp_path, "init")
    assert json.loads(second.stdout)["token"] == token
    denied = run(tmp_path, "save", "secret decision")
    assert denied.returncode == 1
    assert "access denied" in denied.stderr


def test_save_correction_forget_and_bounded_search_are_forwarded(tmp_path: Path) -> None:
    init = run(tmp_path, "init")
    token = json.loads(init.stdout)["token"]
    saved = run(tmp_path, "save", "Use SQLite", "--source", "issue-4", token=token)
    assert json.loads(saved.stdout)["payload"]["source"]["source"] == "issue-4"
    corrected = run(tmp_path, "correct", "m1", "Use SQLite WAL", token=token)
    assert json.loads(corrected.stdout)["payload"]["supersedes"] == ["m1"]
    searched = run(tmp_path, "search", "storage", "--limit", "3", token=token)
    assert json.loads(searched.stdout)["payload"]["limit"] == 3
    forgotten = run(tmp_path, "forget", "m1", "--reason", "removed", token=token)
    assert json.loads(forgotten.stdout)["payload"]["mode"] == "tombstone"
