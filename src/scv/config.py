from __future__ import annotations

import hashlib
import json
import os
import secrets
from dataclasses import dataclass
from pathlib import Path

from .errors import AuthorizationError, ScvError


@dataclass(frozen=True)
class Config:
    data_dir: Path
    store: Path
    token_file: Path
    memkeeper: str

    @classmethod
    def from_env(cls) -> "Config":
        data_dir = Path(os.environ.get("SCV_DATA_DIR", "~/.sidecaravan")).expanduser()
        return cls(
            data_dir=data_dir,
            store=Path(os.environ.get("SCV_STORE", str(data_dir / "team.sqlite"))).expanduser(),
            token_file=Path(os.environ.get("SCV_TOKEN_FILE", str(data_dir / "team.token"))).expanduser(),
            memkeeper=os.environ.get("SCV_MEMKEEPER", "memkeeper"),
        )

    def initialize(self) -> str:
        self.data_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        if self.token_file.exists():
            token = self.token_file.read_text(encoding="utf-8").strip()
            if not token:
                raise ScvError(f"token file is empty: {self.token_file}")
        else:
            token = secrets.token_urlsafe(32)
            self.token_file.write_text(token + "\n", encoding="utf-8")
            self.token_file.chmod(0o600)
        return token

    def authorize(self, supplied: str | None) -> None:
        if not self.token_file.exists():
            raise AuthorizationError("team is not initialized; run `scv init` first")
        expected = self.token_file.read_text(encoding="utf-8").strip()
        actual = supplied or os.environ.get("SCV_TOKEN")
        if not actual or not secrets.compare_digest(actual, expected):
            raise AuthorizationError("access denied: provide the team token via --token or SCV_TOKEN")

    def fingerprint(self) -> str:
        return hashlib.sha256(self.token_file.read_bytes()).hexdigest()[:12]

    def as_metadata(self) -> str:
        return json.dumps({"team": self.data_dir.name, "token_fingerprint": self.fingerprint()})
