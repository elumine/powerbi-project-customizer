from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal

from app.core.file_document import JsonDocument
from app.core.json_file_type import JsonFileType
from app.ui.file_list_model import FileListModel


@dataclass(slots=True)
class ProjectTreeRow:
    file_index: int
    document: JsonDocument
    depth: int = 0
    container_only: bool = False


class ProjectTreeModel(QAbstractListModel):
    countChanged = Signal()

    FILE_INDEX_ROLE = Qt.ItemDataRole.UserRole.value + 1
    ID_ROLE = FILE_INDEX_ROLE + 1
    NAME_ROLE = FILE_INDEX_ROLE + 2
    FILE_NAME_ROLE = FILE_INDEX_ROLE + 3
    FILE_TYPE_ROLE = FILE_INDEX_ROLE + 4
    DIRECTORY_ROLE = FILE_INDEX_ROLE + 5
    PATH_ROLE = FILE_INDEX_ROLE + 6
    RELATIVE_PATH_ROLE = FILE_INDEX_ROLE + 7
    PARENT_PAGE_ID_ROLE = FILE_INDEX_ROLE + 8
    DEPTH_ROLE = FILE_INDEX_ROLE + 9
    EXPANDED_ROLE = FILE_INDEX_ROLE + 10
    ACTIVE_ROLE = FILE_INDEX_ROLE + 11
    VISIBLE_ROLE = FILE_INDEX_ROLE + 12
    DIRTY_ROLE = FILE_INDEX_ROLE + 13
    VALID_JSON_ROLE = FILE_INDEX_ROLE + 14
    JSON_ERROR_ROLE = FILE_INDEX_ROLE + 15
    MATCH_COUNT_ROLE = FILE_INDEX_ROLE + 16
    ACTIVE_FILTER_COLOR_ROLE = FILE_INDEX_ROLE + 17
    VISUAL_TYPE_ROLE = FILE_INDEX_ROLE + 18
    CONTAINER_ONLY_ROLE = FILE_INDEX_ROLE + 19

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[ProjectTreeRow] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._rows):
            return None

        row = self._rows[index.row()]
        document = row.document
        if role == self.FILE_INDEX_ROLE:
            return row.file_index
        if role == self.ID_ROLE:
            return document.id
        if role == self.NAME_ROLE or role == Qt.ItemDataRole.DisplayRole:
            return document.name
        if role == self.FILE_NAME_ROLE:
            return document.file_name
        if role == self.FILE_TYPE_ROLE:
            return document.file_type_text
        if role == self.DIRECTORY_ROLE:
            return document.directory
        if role == self.PATH_ROLE:
            return str(document.path)
        if role == self.RELATIVE_PATH_ROLE:
            return document.relative_path
        if role == self.PARENT_PAGE_ID_ROLE:
            return document.parent_page_id
        if role == self.DEPTH_ROLE:
            return row.depth
        if role == self.EXPANDED_ROLE:
            return not document.collapsed
        if role == self.ACTIVE_ROLE:
            return document.is_active
        if role == self.VISIBLE_ROLE:
            return document.visible_in_tree
        if role == self.DIRTY_ROLE:
            return document.is_dirty
        if role == self.VALID_JSON_ROLE:
            return document.is_valid_json
        if role == self.JSON_ERROR_ROLE:
            return document.json_error
        if role == self.MATCH_COUNT_ROLE:
            return document.match_count
        if role == self.ACTIVE_FILTER_COLOR_ROLE:
            return document.active_filter_color
        if role == self.VISUAL_TYPE_ROLE:
            return document.visual_type
        if role == self.CONTAINER_ONLY_ROLE:
            return row.container_only
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.FILE_INDEX_ROLE: QByteArray(b"fileIndex"),
            self.ID_ROLE: QByteArray(b"id"),
            self.NAME_ROLE: QByteArray(b"name"),
            self.FILE_NAME_ROLE: QByteArray(b"fileName"),
            self.FILE_TYPE_ROLE: QByteArray(b"fileType"),
            self.DIRECTORY_ROLE: QByteArray(b"directory"),
            self.PATH_ROLE: QByteArray(b"path"),
            self.RELATIVE_PATH_ROLE: QByteArray(b"relativePath"),
            self.PARENT_PAGE_ID_ROLE: QByteArray(b"parentPageId"),
            self.DEPTH_ROLE: QByteArray(b"depth"),
            self.EXPANDED_ROLE: QByteArray(b"expanded"),
            self.ACTIVE_ROLE: QByteArray(b"activeFile"),
            self.VISIBLE_ROLE: QByteArray(b"visibleInTree"),
            self.DIRTY_ROLE: QByteArray(b"dirty"),
            self.VALID_JSON_ROLE: QByteArray(b"validJson"),
            self.JSON_ERROR_ROLE: QByteArray(b"jsonError"),
            self.MATCH_COUNT_ROLE: QByteArray(b"matchCount"),
            self.ACTIVE_FILTER_COLOR_ROLE: QByteArray(b"activeFilterColor"),
            self.VISUAL_TYPE_ROLE: QByteArray(b"visualType"),
            self.CONTAINER_ONLY_ROLE: QByteArray(b"containerOnly"),
        }

    @property
    def count(self) -> int:
        return len(self._rows)

    def file_index_at(self, row: int) -> int:
        if not 0 <= row < len(self._rows):
            return -1
        return self._rows[row].file_index

    def reset_from_files(self, files: FileListModel) -> None:
        documents = list(files.documents())
        rows = self._build_rows(documents)
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()
        self.countChanged.emit()

    def clear(self) -> None:
        if not self._rows:
            return
        self.beginResetModel()
        self._rows = []
        self.endResetModel()
        self.countChanged.emit()

    def _build_rows(self, documents: list[JsonDocument]) -> list[ProjectTreeRow]:
        indexed = list(enumerate(documents))
        pages = [(index, doc) for index, doc in indexed if doc.file_type == JsonFileType.PAGE]
        visuals = [(index, doc) for index, doc in indexed if doc.file_type == JsonFileType.VISUAL]
        others = [(index, doc) for index, doc in indexed if doc.file_type not in (JsonFileType.PAGE, JsonFileType.VISUAL)]

        if not pages:
            return [ProjectTreeRow(index, doc, 0) for index, doc in indexed if doc.visible_in_tree]

        rows: list[ProjectTreeRow] = []
        visual_ids_seen: set[str] = set()
        for page_index, page in sorted(pages, key=lambda item: self._sort_key(item[1])):
            child_visuals = [
                (index, visual)
                for index, visual in visuals
                if visual.parent_page_id == page.id and visual.visible_in_tree
            ]
            page_visible = page.visible_in_tree or bool(child_visuals)
            if not page_visible:
                continue
            rows.append(ProjectTreeRow(page_index, page, 0, container_only=not page.is_active and bool(child_visuals)))
            if page.collapsed:
                continue
            for visual_index, visual in sorted(child_visuals, key=lambda item: self._visual_sort_key(item[1])):
                rows.append(ProjectTreeRow(visual_index, visual, 1))
                visual_ids_seen.add(visual.id)

        for visual_index, visual in sorted(visuals, key=lambda item: self._visual_sort_key(item[1])):
            if visual.id in visual_ids_seen or not visual.visible_in_tree:
                continue
            rows.append(ProjectTreeRow(visual_index, visual, 0))

        for other_index, other in sorted(others, key=lambda item: self._sort_key(item[1])):
            if other.visible_in_tree:
                rows.append(ProjectTreeRow(other_index, other, 0))

        return rows

    @staticmethod
    def _sort_key(document: JsonDocument) -> tuple[str, str]:
        return (document.name.casefold(), document.relative_path.casefold())

    @staticmethod
    def _visual_sort_key(document: JsonDocument) -> tuple[float, str, str]:
        z_value = 0.0
        if isinstance(document.parsed_json, dict):
            raw_z = document.parsed_json.get("position.z")
            if raw_z is None:
                position = document.parsed_json.get("position")
                if isinstance(position, dict):
                    raw_z = position.get("z")
            try:
                z_value = float(raw_z or 0)
            except (TypeError, ValueError):
                z_value = 0.0
        return (z_value, document.name.casefold(), document.relative_path.casefold())

