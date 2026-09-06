from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal

from app.core.file_document import JsonDocument


class FileListModel(QAbstractListModel):
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

    def __init__(self) -> None:
        super().__init__()
        self._documents: list[JsonDocument] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._documents)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._documents):
            return None

        document = self._documents[index.row()]
        if role == self.PATH_ROLE:
            return str(document.path)
        if role == self.NAME_ROLE or role == Qt.ItemDataRole.DisplayRole:
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
            self.PATH_ROLE: QByteArray(b"path"),
            self.NAME_ROLE: QByteArray(b"name"),
            self.DIRECTORY_ROLE: QByteArray(b"directory"),
            self.TEXT_ROLE: QByteArray(b"text"),
            self.DIRTY_ROLE: QByteArray(b"dirty"),
            self.VALID_JSON_ROLE: QByteArray(b"validJson"),
            self.JSON_ERROR_ROLE: QByteArray(b"jsonError"),
            self.MATCH_COUNT_ROLE: QByteArray(b"matchCount"),
            self.FILE_NAME_ROLE: QByteArray(b"fileName"),
            self.MATCH_PREVIEWS_ROLE: QByteArray(b"matchPreviews"),
            self.HIGHLIGHTED_HTML_ROLE: QByteArray(b"highlightedHtml"),
            self.ID_ROLE: QByteArray(b"id"),
            self.ACTIVE_ROLE: QByteArray(b"activeFile"),
            self.ACTIVE_FILTER_COLOR_ROLE: QByteArray(b"activeFilterColor"),
            self.FILE_TYPE_ROLE: QByteArray(b"fileType"),
            self.RELATIVE_PATH_ROLE: QByteArray(b"relativePath"),
            self.PARENT_PAGE_ID_ROLE: QByteArray(b"parentPageId"),
            self.VISUAL_TYPE_ROLE: QByteArray(b"visualType"),
            self.VISIBLE_IN_TREE_ROLE: QByteArray(b"visibleInTree"),
            self.SCHEMA_URL_ROLE: QByteArray(b"schemaUrl"),
            self.PBIR_NAME_ROLE: QByteArray(b"pbirName"),
            self.DISPLAY_NAME_SOURCE_ROLE: QByteArray(b"displayNameSource"),
            self.EXPANDED_ROLE: QByteArray(b"expanded"),
        }

    @property
    def count(self) -> int:
        return len(self._documents)

    def documents(self) -> Iterable[JsonDocument]:
        return tuple(self._documents)

    def paths(self) -> set[Path]:
        return {document.path for document in self._documents}

    def document_at(self, row: int) -> JsonDocument | None:
        if not 0 <= row < len(self._documents):
            return None
        return self._documents[row]

    def document_index_by_id(self, document_id: str) -> int:
        for row, document in enumerate(self._documents):
            if document.id == document_id:
                return row
        return -1

    def add_document(self, document: JsonDocument) -> int:
        row = len(self._documents)
        self.beginInsertRows(QModelIndex(), row, row)
        self._documents.append(document)
        self.endInsertRows()
        self.countChanged.emit()
        return row

    def remove_document(self, row: int) -> JsonDocument | None:
        if not 0 <= row < len(self._documents):
            return None

        self.beginRemoveRows(QModelIndex(), row, row)
        document = self._documents.pop(row)
        self.endRemoveRows()
        self.countChanged.emit()
        return document

    def clear(self) -> None:
        if not self._documents:
            return
        self.beginResetModel()
        self._documents = []
        self.endResetModel()
        self.countChanged.emit()

    def set_document_text(self, row: int, text: str) -> bool:
        document = self.document_at(row)
        if document is None or document.text == text:
            return False

        document.set_text(text)
        self._emit_row_changed(row)
        return True

    def mark_saved(self, row: int) -> None:
        document = self.document_at(row)
        if document is None:
            return

        document.mark_saved()
        self._emit_row_changed(row)

    def set_document_active(self, row: int, active: bool, filter_color: str = "") -> None:
        self.set_document_state(row, active, active, filter_color)

    def set_document_state(self, row: int, active: bool, visible: bool, filter_color: str = "") -> None:
        document = self.document_at(row)
        if document is None:
            return

        if (
            document.is_active == active
            and document.visible_in_tree == visible
            and document.active_filter_color == filter_color
        ):
            return
        document.is_active = active
        document.visible_in_tree = visible
        document.active_filter_color = filter_color
        model_index = self.index(row, 0)
        self.dataChanged.emit(
            model_index,
            model_index,
            [self.ACTIVE_ROLE, self.VISIBLE_IN_TREE_ROLE, self.ACTIVE_FILTER_COLOR_ROLE],
        )
        self.documentChanged.emit(row)

    def set_page_expanded(self, document_id: str, expanded: bool) -> bool:
        row = self.document_index_by_id(document_id)
        document = self.document_at(row)
        if document is None:
            return False
        collapsed = not bool(expanded)
        if document.collapsed == collapsed:
            return False
        document.collapsed = collapsed
        self._emit_row_changed(row)
        return True

    def refresh_row(self, row: int) -> None:
        if not 0 <= row < len(self._documents):
            return
        self._emit_row_changed(row)

    def refresh_all(self) -> None:
        if not self._documents:
            return
        top = self.index(0, 0)
        bottom = self.index(len(self._documents) - 1, 0)
        self.dataChanged.emit(top, bottom)
        for row in range(len(self._documents)):
            self.documentChanged.emit(row)

    def refresh_search_view(self, row: int, match_count: int, previews: list[dict[str, str | int]], highlighted_html: str) -> None:
        document = self.document_at(row)
        if document is None:
            return

        document.match_count = match_count
        document.match_previews = previews
        document.highlighted_html = highlighted_html
        model_index = self.index(row, 0)
        self.dataChanged.emit(
            model_index,
            model_index,
            [self.MATCH_COUNT_ROLE, self.MATCH_PREVIEWS_ROLE, self.HIGHLIGHTED_HTML_ROLE],
        )
        self.documentChanged.emit(row)

    def _emit_row_changed(self, row: int) -> None:
        model_index = self.index(row, 0)
        self.dataChanged.emit(
            model_index,
            model_index,
            [
                self.TEXT_ROLE,
                self.DIRTY_ROLE,
                self.VALID_JSON_ROLE,
                self.JSON_ERROR_ROLE,
                self.MATCH_COUNT_ROLE,
                self.NAME_ROLE,
                self.FILE_NAME_ROLE,
                self.MATCH_PREVIEWS_ROLE,
                self.HIGHLIGHTED_HTML_ROLE,
                self.ID_ROLE,
                self.ACTIVE_ROLE,
                self.ACTIVE_FILTER_COLOR_ROLE,
                self.FILE_TYPE_ROLE,
                self.RELATIVE_PATH_ROLE,
                self.PARENT_PAGE_ID_ROLE,
                self.VISUAL_TYPE_ROLE,
                self.VISIBLE_IN_TREE_ROLE,
                self.SCHEMA_URL_ROLE,
                self.PBIR_NAME_ROLE,
                self.DISPLAY_NAME_SOURCE_ROLE,
                self.EXPANDED_ROLE,
            ],
        )
        self.documentChanged.emit(row)
