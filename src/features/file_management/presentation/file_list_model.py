from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal

from entities.document.models import JsonDocument
from services.documents.changes import DocumentChange, DocumentChangeKind
from services.documents.collection import DocumentCollection


class FileListModel(QAbstractListModel):
    """Qt presentation adapter over the Qt-free :class:`DocumentCollection`.

    The public row-based methods are retained while QML is migrated. New feature
    application code should depend on ``collection`` and stable document IDs.
    """

    countChanged = Signal()
    documentChanged = Signal(int)

    PATH_ROLE = Qt.ItemDataRole.UserRole.value + 1
    NAME_ROLE = PATH_ROLE + 1
    DIRECTORY_ROLE = PATH_ROLE + 2
    TEXT_ROLE = PATH_ROLE + 3
    DIRTY_ROLE = PATH_ROLE + 4
    VALID_JSON_ROLE = PATH_ROLE + 5
    JSON_ERROR_ROLE = PATH_ROLE + 6
    MATCH_COUNT_ROLE = PATH_ROLE + 7
    FILE_NAME_ROLE = PATH_ROLE + 8
    MATCH_PREVIEWS_ROLE = PATH_ROLE + 9
    HIGHLIGHTED_HTML_ROLE = PATH_ROLE + 10
    ID_ROLE = PATH_ROLE + 11
    ACTIVE_ROLE = PATH_ROLE + 12
    ACTIVE_FILTER_COLOR_ROLE = PATH_ROLE + 13
    FILE_TYPE_ROLE = PATH_ROLE + 14
    RELATIVE_PATH_ROLE = PATH_ROLE + 15
    PARENT_PAGE_ID_ROLE = PATH_ROLE + 16
    VISUAL_TYPE_ROLE = PATH_ROLE + 17
    VISIBLE_IN_TREE_ROLE = PATH_ROLE + 18
    SCHEMA_URL_ROLE = PATH_ROLE + 19
    PBIR_NAME_ROLE = PATH_ROLE + 20
    DISPLAY_NAME_SOURCE_ROLE = PATH_ROLE + 21
    EXPANDED_ROLE = PATH_ROLE + 22

    def __init__(self, collection: DocumentCollection | None = None) -> None:
        super().__init__()
        self._collection = collection or DocumentCollection()
        self._ignore_collection_events = 0
        self._unsubscribe = self._collection.subscribe(self._on_collection_change)

    @property
    def collection(self) -> DocumentCollection:
        return self._collection

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else self._collection.count

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        document = self.document_at(index.row()) if index.isValid() else None
        if document is None:
            return None
        if role == self.PATH_ROLE:
            return str(document.path)
        if role in (self.NAME_ROLE, Qt.ItemDataRole.DisplayRole):
            return document.name
        if role == self.DIRECTORY_ROLE:
            return document.directory
        if role == self.TEXT_ROLE:
            return document.text
        if role == self.DIRTY_ROLE:
            return document.is_dirty
        if role == self.VALID_JSON_ROLE:
            return document.is_valid_json
        if role == self.JSON_ERROR_ROLE:
            return document.json_error
        if role == self.MATCH_COUNT_ROLE:
            return document.match_count
        if role == self.FILE_NAME_ROLE:
            return document.file_name
        if role == self.MATCH_PREVIEWS_ROLE:
            return document.match_previews
        if role == self.HIGHLIGHTED_HTML_ROLE:
            return document.highlighted_html
        if role == self.ID_ROLE:
            return document.id
        if role == self.ACTIVE_ROLE:
            return document.is_active
        if role == self.ACTIVE_FILTER_COLOR_ROLE:
            return document.active_filter_color
        if role == self.FILE_TYPE_ROLE:
            return document.file_type_text
        if role == self.RELATIVE_PATH_ROLE:
            return document.relative_path
        if role == self.PARENT_PAGE_ID_ROLE:
            return document.parent_page_id
        if role == self.VISUAL_TYPE_ROLE:
            return document.visual_type
        if role == self.VISIBLE_IN_TREE_ROLE:
            return document.visible_in_tree
        if role == self.SCHEMA_URL_ROLE:
            return document.schema_url
        if role == self.PBIR_NAME_ROLE:
            return document.pbir_name
        if role == self.DISPLAY_NAME_SOURCE_ROLE:
            return document.display_name_source
        if role == self.EXPANDED_ROLE:
            return not document.collapsed
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.PATH_ROLE: QByteArray(b"path"), self.NAME_ROLE: QByteArray(b"name"),
            self.DIRECTORY_ROLE: QByteArray(b"directory"), self.TEXT_ROLE: QByteArray(b"text"),
            self.DIRTY_ROLE: QByteArray(b"dirty"), self.VALID_JSON_ROLE: QByteArray(b"validJson"),
            self.JSON_ERROR_ROLE: QByteArray(b"jsonError"), self.MATCH_COUNT_ROLE: QByteArray(b"matchCount"),
            self.FILE_NAME_ROLE: QByteArray(b"fileName"), self.MATCH_PREVIEWS_ROLE: QByteArray(b"matchPreviews"),
            self.HIGHLIGHTED_HTML_ROLE: QByteArray(b"highlightedHtml"), self.ID_ROLE: QByteArray(b"id"),
            self.ACTIVE_ROLE: QByteArray(b"activeFile"), self.ACTIVE_FILTER_COLOR_ROLE: QByteArray(b"activeFilterColor"),
            self.FILE_TYPE_ROLE: QByteArray(b"fileType"), self.RELATIVE_PATH_ROLE: QByteArray(b"relativePath"),
            self.PARENT_PAGE_ID_ROLE: QByteArray(b"parentPageId"), self.VISUAL_TYPE_ROLE: QByteArray(b"visualType"),
            self.VISIBLE_IN_TREE_ROLE: QByteArray(b"visibleInTree"), self.SCHEMA_URL_ROLE: QByteArray(b"schemaUrl"),
            self.PBIR_NAME_ROLE: QByteArray(b"pbirName"), self.DISPLAY_NAME_SOURCE_ROLE: QByteArray(b"displayNameSource"),
            self.EXPANDED_ROLE: QByteArray(b"expanded"),
        }

    @property
    def count(self) -> int:
        return self._collection.count

    def documents(self) -> Iterable[JsonDocument]:
        return self._collection.documents()

    def paths(self) -> set[Path]:
        return self._collection.paths()

    def document_at(self, row: int) -> JsonDocument | None:
        return self._collection.document_at(row)

    def document_index_by_id(self, document_id: str) -> int:
        return self._collection.index_by_id(document_id)

    def add_document(self, document: JsonDocument) -> int:
        row = self.count
        self.beginInsertRows(QModelIndex(), row, row)
        self._ignore_collection_events += 1
        try:
            inserted = self._collection.add_document(document)
        finally:
            self._ignore_collection_events -= 1
        self.endInsertRows()
        self.countChanged.emit()
        return inserted

    def remove_document(self, row: int) -> JsonDocument | None:
        if self.document_at(row) is None:
            return None
        self.beginRemoveRows(QModelIndex(), row, row)
        self._ignore_collection_events += 1
        try:
            document = self._collection.remove_document(row)
        finally:
            self._ignore_collection_events -= 1
        self.endRemoveRows()
        self.countChanged.emit()
        return document

    def clear(self) -> None:
        if not self.count:
            return
        self.beginResetModel()
        self._ignore_collection_events += 1
        try:
            self._collection.clear()
        finally:
            self._ignore_collection_events -= 1
        self.endResetModel()
        self.countChanged.emit()

    def set_document_text(self, row: int, text: str) -> bool:
        change_set = self._collection.set_document_text(row, text)
        return not change_set.is_empty

    def mark_saved(self, row: int) -> None:
        self._collection.mark_saved(row)

    def set_document_active(self, row: int, active: bool, filter_color: str = "") -> None:
        self.set_document_state(row, active, active, filter_color)

    def set_document_state(self, row: int, active: bool, visible: bool, filter_color: str = "") -> None:
        document = self.document_at(row)
        if document is None or (document.is_active == active and document.visible_in_tree == visible and document.active_filter_color == filter_color):
            return
        document.is_active = active
        document.visible_in_tree = visible
        document.active_filter_color = filter_color
        self._collection.notify_presentation_changed((document.id,))

    def set_page_expanded(self, document_id: str, expanded: bool) -> bool:
        row = self.document_index_by_id(document_id)
        document = self.document_at(row)
        if document is None or document.collapsed == (not bool(expanded)):
            return False
        document.collapsed = not bool(expanded)
        self._collection.notify_presentation_changed((document.id,))
        return True

    def refresh_row(self, row: int) -> None:
        document = self.document_at(row)
        if document is not None:
            self._collection.notify_presentation_changed((document.id,))

    def refresh_all(self) -> None:
        self._collection.notify_presentation_changed(document.id for document in self._collection.documents())

    def refresh_search_view(self, row: int, match_count: int, previews: list[dict[str, str | int]], highlighted_html: str) -> None:
        document = self.document_at(row)
        if document is None:
            return
        document.match_count = match_count
        document.match_previews = previews
        document.highlighted_html = highlighted_html
        self._collection.notify_presentation_changed((document.id,))

    def _on_collection_change(self, change: DocumentChange) -> None:
        if self._ignore_collection_events:
            return
        if change.kind == DocumentChangeKind.ADDED:
            self.beginResetModel(); self.endResetModel(); self.countChanged.emit(); return
        if change.kind == DocumentChangeKind.REMOVED:
            self.beginResetModel(); self.endResetModel(); self.countChanged.emit(); return
        if change.kind == DocumentChangeKind.RESET:
            self.beginResetModel(); self.endResetModel(); self.countChanged.emit(); return
        if change.index >= 0:
            self._emit_row_changed(change.index)

    def _emit_row_changed(self, row: int) -> None:
        if not 0 <= row < self.count:
            return
        model_index = self.index(row, 0)
        self.dataChanged.emit(model_index, model_index, [
            self.TEXT_ROLE, self.DIRTY_ROLE, self.VALID_JSON_ROLE, self.JSON_ERROR_ROLE,
            self.MATCH_COUNT_ROLE, self.NAME_ROLE, self.FILE_NAME_ROLE, self.MATCH_PREVIEWS_ROLE,
            self.HIGHLIGHTED_HTML_ROLE, self.ID_ROLE, self.ACTIVE_ROLE, self.ACTIVE_FILTER_COLOR_ROLE,
            self.FILE_TYPE_ROLE, self.RELATIVE_PATH_ROLE, self.PARENT_PAGE_ID_ROLE,
            self.VISUAL_TYPE_ROLE, self.VISIBLE_IN_TREE_ROLE, self.SCHEMA_URL_ROLE,
            self.PBIR_NAME_ROLE, self.DISPLAY_NAME_SOURCE_ROLE, self.EXPANDED_ROLE,
        ])
        self.documentChanged.emit(row)
