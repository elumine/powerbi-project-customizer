from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path

from entities.document.models import JsonDocument
from services.documents.changes import (
    CommittedChangeSet,
    DocumentChange,
    DocumentChangeKind,
    DocumentSnapshot,
)
from services.documents.ports import DocumentChangeHandler


class DocumentCollection:
    """Ordered, Qt-free source of truth for documents opened by the workspace.

    Presentation adapters observe this collection and translate stable-ID events into
    framework notifications. Features can therefore operate without a QAbstractListModel.
    """

    def __init__(self, documents: Iterable[JsonDocument] = ()) -> None:
        self._documents = list(documents)
        self._handlers: list[DocumentChangeHandler] = []
        self._assert_unique_ids()
        self._assert_unique_paths()

    @property
    def count(self) -> int:
        return len(self._documents)

    def documents(self) -> tuple[JsonDocument, ...]:
        return tuple(self._documents)

    def paths(self) -> set[Path]:
        return {document.path for document in self._documents}

    def document_at(self, index: int) -> JsonDocument | None:
        if not 0 <= index < len(self._documents):
            return None
        return self._documents[index]

    def document_by_id(self, document_id: str) -> JsonDocument | None:
        index = self.index_by_id(document_id)
        return self.document_at(index)

    def index_by_id(self, document_id: str) -> int:
        for index, document in enumerate(self._documents):
            if document.id == document_id:
                return index
        return -1

    def index_by_path(self, path: Path) -> int:
        normalized = Path(path).expanduser().resolve()
        for index, document in enumerate(self._documents):
            if document.path == normalized:
                return index
        return -1

    def subscribe(self, handler: DocumentChangeHandler) -> Callable[[], None]:
        self._handlers.append(handler)

        def unsubscribe() -> None:
            try:
                self._handlers.remove(handler)
            except ValueError:
                pass

        return unsubscribe

    def add_document(self, document: JsonDocument) -> int:
        if self.document_by_id(document.id) is not None:
            raise ValueError(f"A document with id '{document.id}' already exists.")
        if self.index_by_path(document.path) >= 0:
            raise ValueError(f"A document for '{document.path}' is already open.")
        index = len(self._documents)
        self._documents.append(document)
        self._emit(DocumentChange(DocumentChangeKind.ADDED, document.id, index, document=document))
        return index

    def remove_document(self, index: int) -> JsonDocument | None:
        document = self.document_at(index)
        if document is None:
            return None
        removed = self._documents.pop(index)
        self._emit(DocumentChange(DocumentChangeKind.REMOVED, removed.id, index, previous_index=index, document=removed))
        return removed

    def remove_document_by_id(self, document_id: str) -> JsonDocument | None:
        return self.remove_document(self.index_by_id(document_id))

    def clear(self) -> None:
        if not self._documents:
            return
        self._documents.clear()
        self._emit(DocumentChange(DocumentChangeKind.RESET))

    def set_document_text(self, index: int, text: str, *, operation: str = "content-edit") -> CommittedChangeSet:
        document = self.document_at(index)
        if document is None or document.text == text:
            return CommittedChangeSet(operation, ())
        before = self._snapshot(document)
        document.set_text(text)
        after = self._snapshot(document)
        self._emit(DocumentChange(DocumentChangeKind.CONTENT_CHANGED, document.id, index, document=document))
        return CommittedChangeSet(operation, (before, after))

    def set_document_text_by_id(self, document_id: str, text: str, *, operation: str = "content-edit") -> CommittedChangeSet:
        return self.set_document_text(self.index_by_id(document_id), text, operation=operation)

    def mark_saved(self, index: int, *, operation: str = "save") -> CommittedChangeSet:
        document = self.document_at(index)
        if document is None:
            return CommittedChangeSet(operation, ())
        before = self._snapshot(document)
        document.mark_saved()
        after = self._snapshot(document)
        if before == after:
            return CommittedChangeSet(operation, ())
        self._emit(DocumentChange(DocumentChangeKind.SAVE_STATE_CHANGED, document.id, index, document=document))
        return CommittedChangeSet(operation, (before, after))

    def mark_saved_by_id(self, document_id: str, *, operation: str = "save") -> CommittedChangeSet:
        return self.mark_saved(self.index_by_id(document_id), operation=operation)

    def notify_presentation_changed(self, document_ids: Iterable[str]) -> None:
        for document_id in set(document_ids):
            index = self.index_by_id(document_id)
            document = self.document_at(index)
            if document is not None:
                self._emit(DocumentChange(DocumentChangeKind.PRESENTATION_CHANGED, document.id, index, document=document))

    def _emit(self, change: DocumentChange) -> None:
        for handler in tuple(self._handlers):
            handler(change)

    @staticmethod
    def _snapshot(document: JsonDocument) -> DocumentSnapshot:
        return DocumentSnapshot(
            document_id=document.id,
            text=document.text,
            original_text=document.original_text or "",
            is_dirty=document.is_dirty,
        )

    def _assert_unique_ids(self) -> None:
        ids = [document.id for document in self._documents]
        if len(ids) != len(set(ids)):
            raise ValueError("Document collection requires unique document IDs.")

    def _assert_unique_paths(self) -> None:
        paths = [document.path for document in self._documents]
        if len(paths) != len(set(paths)):
            raise ValueError("Document collection requires unique document paths.")
