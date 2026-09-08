from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal

from entities.document.models import JsonDocument
from features.changes.application.service import ChangeDiffService
from services.documents.changes import DocumentChange, DocumentChangeKind
from services.documents.collection import DocumentCollection


class ChangesListModel(QAbstractListModel):
    """Projection of documents whose text differs from the import baseline."""

    countChanged = Signal()

    DOCUMENT_ID_ROLE = Qt.ItemDataRole.UserRole.value + 1
    NAME_ROLE = DOCUMENT_ID_ROLE + 1
    PATH_ROLE = DOCUMENT_ID_ROLE + 2
    RELATIVE_PATH_ROLE = DOCUMENT_ID_ROLE + 3
    ADDED_LINES_ROLE = DOCUMENT_ID_ROLE + 4
    REMOVED_LINES_ROLE = DOCUMENT_ID_ROLE + 5
    CHANGE_SUMMARY_ROLE = DOCUMENT_ID_ROLE + 6

    def __init__(self, collection: DocumentCollection) -> None:
        super().__init__()
        self._collection = collection
        self._diff_service = ChangeDiffService()
        self._documents: list[JsonDocument] = []
        self._unsubscribe = collection.subscribe(self._on_collection_change)
        self.refresh()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._documents)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._documents):
            return None
        document = self._documents[index.row()]
        added, removed = self._line_counts(document)
        if role in (self.DOCUMENT_ID_ROLE,):
            return document.id
        if role in (self.NAME_ROLE, Qt.ItemDataRole.DisplayRole):
            return document.name
        if role == self.PATH_ROLE:
            return str(document.path)
        if role == self.RELATIVE_PATH_ROLE:
            return document.relative_path
        if role == self.ADDED_LINES_ROLE:
            return added
        if role == self.REMOVED_LINES_ROLE:
            return removed
        if role == self.CHANGE_SUMMARY_ROLE:
            return f"+{added}  -{removed}"
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.DOCUMENT_ID_ROLE: QByteArray(b"documentId"),
            self.NAME_ROLE: QByteArray(b"name"),
            self.PATH_ROLE: QByteArray(b"path"),
            self.RELATIVE_PATH_ROLE: QByteArray(b"relativePath"),
            self.ADDED_LINES_ROLE: QByteArray(b"addedLines"),
            self.REMOVED_LINES_ROLE: QByteArray(b"removedLines"),
            self.CHANGE_SUMMARY_ROLE: QByteArray(b"changeSummary"),
        }

    @property
    def count(self) -> int:
        return len(self._documents)

    def document_at(self, row: int) -> JsonDocument | None:
        return self._documents[row] if 0 <= row < len(self._documents) else None

    def refresh(self) -> None:
        changed = [document for document in self._collection.documents() if document.has_changes_from_initial]
        self.beginResetModel()
        self._documents = changed
        self.endResetModel()
        self.countChanged.emit()

    def _line_counts(self, document: JsonDocument) -> tuple[int, int]:
        return self._diff_service.line_counts(document.initial_text or "", document.text)

    def _on_collection_change(self, change: DocumentChange) -> None:
        # Presentation changes can affect selection metadata but never the
        # baseline comparison; refreshing is cheap and keeps the projection
        # correct for all collection mutation paths.
        if change.kind in {
            DocumentChangeKind.ADDED,
            DocumentChangeKind.REMOVED,
            DocumentChangeKind.CONTENT_CHANGED,
            DocumentChangeKind.SAVE_STATE_CHANGED,
            DocumentChangeKind.RESET,
        }:
            self.refresh()
