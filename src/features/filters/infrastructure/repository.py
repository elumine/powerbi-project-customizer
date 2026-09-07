from __future__ import annotations

from pathlib import Path

from entities.filter.models import ContentFilter
from infrastructure.persistence.json_filter_store import JsonFilterStore


class FilterRepository:
    """Persistence boundary for user content filters."""

    def __init__(self, path: Path) -> None:
        self._storage = JsonFilterStore(path)

    @property
    def path(self) -> Path:
        return self._storage.path

    def list_filters(self) -> list[ContentFilter]:
        return self._storage.load()

    def save_filters(self, filters: list[ContentFilter]) -> None:
        self._storage.save(filters)
