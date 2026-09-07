from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from entities.document.models import JsonDocument
from services.documents.collection import DocumentCollection


class DocumentWorkspacePort(Protocol):
    """Presentation-facing document projection contract implemented by the Qt list adapter."""

    @property
    def collection(self) -> DocumentCollection: ...

    @property
    def count(self) -> int: ...

    def documents(self) -> Iterable[JsonDocument]: ...

    def document_at(self, row: int) -> JsonDocument | None: ...

    def document_index_by_id(self, document_id: str) -> int: ...

    def set_document_text(self, row: int, text: str) -> bool: ...

    def set_document_state(self, row: int, active: bool, visible: bool, filter_color: str = "") -> None: ...

    def refresh_row(self, row: int) -> None: ...

    def refresh_search_view(self, row: int, match_count: int, previews: list[dict[str, str | int]], highlighted_html: str) -> None: ...
