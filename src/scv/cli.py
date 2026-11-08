from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from .config import Config
from .errors import ScvError
from .memkeeper import Memkeeper


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="scv", description="Local shared team memory")
    p.add_argument("--token", help=argparse.SUPPRESS)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="initialize or reuse the team store")
    save = sub.add_parser("save", help="save a durable memory")
    save.add_argument("content")
    save.add_argument("--kind", default="decision")
    save.add_argument("--source", default="unknown")
    save.add_argument("--author", default="unknown")
    save.add_argument("--session")
    save.add_argument("--supersedes")
    search = sub.add_parser("search", aliases=["recall"])
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    read = sub.add_parser("read")
    read.add_argument("id")
    correct = sub.add_parser("correct")
    correct.add_argument("id")
    correct.add_argument("content")
    correct.add_argument("--source", default="correction")
    correct.add_argument("--author", default="unknown")
    forget = sub.add_parser("forget")
    forget.add_argument("id")
    forget.add_argument("--reason", required=True)
    backup = sub.add_parser("backup")
    backup.add_argument("output", type=Path)
    restore = sub.add_parser("restore")
    restore.add_argument("backup", type=Path)
    restore.add_argument("--force", action="store_true")
    return p


def emit(value: object) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    config = Config.from_env()
    try:
        if args.command == "init":
            token = config.initialize()
            Memkeeper(config).init()
            emit({"initialized": True, "store": str(config.store), "token": token, "token_fingerprint": config.fingerprint()})
            return 0
        config.authorize(args.token)
        engine = Memkeeper(config)
        if args.command in ("search", "recall"):
            if args.limit < 1 or args.limit > 100:
                raise ScvError("limit must be between 1 and 100")
            emit(engine.search(args.query, args.limit))
        elif args.command == "read":
            emit(engine.get(args.id))
        elif args.command == "save":
            now = utc_now()
            source = {"source": args.source, "author": args.author, "session": args.session, "recorded_at": now}
            payload = {"content": args.content, "kind": args.kind, "source": source, "metadata_json": config.as_metadata(), "observed_at": now}
            if args.supersedes:
                payload["supersedes"] = [args.supersedes]
            emit(engine.remember(payload))
        elif args.command == "correct":
            now = utc_now()
            emit(engine.remember({"content": args.content, "kind": "decision", "source": {"source": args.source, "author": args.author, "recorded_at": now}, "metadata_json": config.as_metadata(), "observed_at": now, "supersedes": [args.id]}))
        elif args.command == "forget":
            emit(engine.forget(args.id, args.reason))
        elif args.command == "backup":
            emit(engine.backup(args.output))
        elif args.command == "restore":
            engine.restore(args.backup, args.force)
            emit({"restored": True, "store": str(config.store)})
        return 0
    except ScvError as exc:
        print(f"scv: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
