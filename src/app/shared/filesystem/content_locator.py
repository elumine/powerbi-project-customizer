from __future__ import annotations

import os
import sys
from pathlib import Path


def locate_content_root() -> Path:
    override = os.environ.get("JSON_MULTI_EDITOR_CONTENT_PATH")
    if override:
        return Path(override).expanduser().resolve()

    candidates: list[Path] = []
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        candidates.append(Path(bundle_root) / "content")

    candidates.extend(
        [
            Path.cwd() / "content",
            Path(__file__).resolve().parents[4] / "content",
            Path(sys.executable).resolve().parent / "content",
        ]
    )
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return candidates[0].resolve()
