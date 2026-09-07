from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Protocol

from entities.document.models import JsonDocument
from services.documents.changes import CommittedChangeSet, DocumentChange


DocumentChangeHandler = Callable[[DocumentChange], None]


class ReadDocuments(Protocol):
    """Read-only document access required by feature application services."""

    def documents(self) -> tuple[JsonDocument, ...]: ...

    def document_by_id(self, document_id: str) -> JsonDocument | None: ...

    def paths(self) -> set[Path]: ...

    def subscribe(self, handler: DocumentChangeHandler) -> Callable[[], None]: ...


class MutableDocuments(ReadDocuments, Protocol):
    """Document mutations expressed by stable identifiers instead of Qt rows."""

    def add_document(self, document: JsonDocument) -> int: ...

    def remove_document_by_id(self, document_id: str) -> JsonDocument | None: ...

    def clear(self) -> None: ...

    def set_document_text_by_id(self, document_id: str, text: str, *, operation: str = "content-edit") -> CommittedChangeSet: ...

    def mark_saved_by_id(self, document_id: str, *, operation: str = "save") -> CommittedChangeSet: ...

    def notify_presentation_changed(self, document_ids: Iterable[str]) -> None: ...
