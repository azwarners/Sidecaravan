"""The versioned capability catalog exposed by Sidecaravan."""

from __future__ import annotations

from typing import Any

CAPABILITY_VERSION = "1"


def catalog() -> list[dict[str, Any]]:
    """Return the capabilities available through the standalone boundary."""
    return [
        {
            "id": "scv.memory",
            "version": CAPABILITY_VERSION,
            "description": "Explicitly save and retrieve shared team memories.",
            "provider": "sidecaravan",
            "provider_version": "0.1.0",
            "availability": "available",
            "permissions": {
                "save": "team.write",
                "recall": "team.read",
                "read": "team.read",
                "correct": "team.write",
                "forget": "team.write",
            },
            "operations": ["save", "recall", "read", "correct", "forget"],
        }
    ]

