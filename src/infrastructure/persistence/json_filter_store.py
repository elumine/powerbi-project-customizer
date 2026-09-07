from __future__ import annotations

import json
from pathlib import Path

from entities.filter.models import ContentFilter


class JsonFilterStore:
    """Concrete user-filter JSON persistence adapter."""

    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> list[ContentFilter]:
        if not self._path.exists():
            return []
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        saved_filters = data.get("filters", []) if isinstance(data, dict) else []
        return [ContentFilter.from_dict(item) for item in saved_filters if isinstance(item, dict)]

    def save(self, filters: list[ContentFilter]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"filters": [item.to_dict() for item in filters if not item.is_read_only]}
        self._path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
