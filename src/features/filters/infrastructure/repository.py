from __future__ import annotations

from pathlib import Path

from entities.filter.models import ContentFilter
from infrastructure.persistence.json_filter_store import JsonFilterStore


# Retire the pre-JSON in-memory filter samples from earlier application versions.
LEGACY_SEEDED_FILTER_NAMES = frozenset({"table", "chart", "title1"})


class FilterRepository:
    """Persistence boundary for user content filters."""

    def __init__(self, path: Path) -> None:
        self._storage = JsonFilterStore(path)

    @property
    def path(self) -> Path:
        return self._storage.path

    def list_filters(self) -> list[ContentFilter]:
        filters = self._storage.load()
        retained = [
            content_filter
            for content_filter in filters
            if content_filter.display_name.strip().casefold() not in LEGACY_SEEDED_FILTER_NAMES
        ]
        # Persist the one-time cleanup so retired samples never return on reload.
        if len(retained) != len(filters):
            self._storage.save(retained)
        return retained

    def save_filters(self, filters: list[ContentFilter]) -> None:
        self._storage.save(filters)
