from __future__ import annotations

from pathlib import Path

from app.core.content_filter import ContentFilter, FilterStorage


class FilterRepository:
    """Persistence boundary for user content filters."""

    def __init__(self, path: Path) -> None:
        self._storage = FilterStorage(path)

    @property
    def path(self) -> Path:
        return self._storage.path

    def list_filters(self) -> list[ContentFilter]:
        return self._storage.load()

    def save_filters(self, filters: list[ContentFilter]) -> None:
        self._storage.save(filters)
