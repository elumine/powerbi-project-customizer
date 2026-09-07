from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal

from features.visual_editor.domain.models import VisualEditorControl


class VisualEditorControlModel(QAbstractListModel):
    countChanged = Signal()

    ID_ROLE = Qt.ItemDataRole.UserRole.value + 1
    LABEL_ROLE = ID_ROLE + 1
    CATEGORY_ROLE = ID_ROLE + 2
    CONTROL_ROLE = ID_ROLE + 3
    VALUE_TYPE_ROLE = ID_ROLE + 4
    OPTIONS_ROLE = ID_ROLE + 5
    VISUAL_TYPES_ROLE = ID_ROLE + 6
    MATCHING_COUNT_ROLE = ID_ROLE + 7
    VISUAL_TYPE_GROUP_ROLE = ID_ROLE + 8
    DESCRIPTION_ROLE = ID_ROLE + 9
    DEFAULT_VALUE_ROLE = ID_ROLE + 10
    MATCHES_ROLE = ID_ROLE + 11
    GROUP_PATH_ROLE = ID_ROLE + 12
    GROUP_LABEL_ROLE = ID_ROLE + 13

    def __init__(self) -> None:
        super().__init__()
        self._items: list[VisualEditorControl] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._items)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None
        item = self._items[index.row()]
        if role == self.ID_ROLE:
            return item.id
        if role == self.LABEL_ROLE or role == Qt.ItemDataRole.DisplayRole:
            return item.label
        if role == self.CATEGORY_ROLE:
            return item.category
        if role == self.CONTROL_ROLE:
            return item.control
        if role == self.VALUE_TYPE_ROLE:
            return item.value_type
        if role == self.OPTIONS_ROLE:
            return list(item.options)
        if role == self.VISUAL_TYPES_ROLE:
            return list(item.visual_types)
        if role == self.MATCHING_COUNT_ROLE:
            return item.matching_count
        if role == self.VISUAL_TYPE_GROUP_ROLE:
            return item.visual_type_group
        if role == self.DESCRIPTION_ROLE:
            return item.description
        if role == self.DEFAULT_VALUE_ROLE:
            return "" if item.default_value is None else str(item.default_value)
        if role == self.MATCHES_ROLE:
            return [match.to_dict() for match in item.matches]
        if role == self.GROUP_PATH_ROLE:
            return list(item.group_path)
        if role == self.GROUP_LABEL_ROLE:
            return " > ".join(str(part) for part in item.group_path)
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.ID_ROLE: QByteArray(b"id"),
            self.LABEL_ROLE: QByteArray(b"label"),
            self.CATEGORY_ROLE: QByteArray(b"category"),
            self.CONTROL_ROLE: QByteArray(b"control"),
            self.VALUE_TYPE_ROLE: QByteArray(b"valueType"),
            self.OPTIONS_ROLE: QByteArray(b"options"),
            self.VISUAL_TYPES_ROLE: QByteArray(b"visualTypes"),
            self.MATCHING_COUNT_ROLE: QByteArray(b"matchingCount"),
            self.VISUAL_TYPE_GROUP_ROLE: QByteArray(b"visualTypeGroup"),
            self.DESCRIPTION_ROLE: QByteArray(b"description"),
            self.DEFAULT_VALUE_ROLE: QByteArray(b"defaultValue"),
            self.MATCHES_ROLE: QByteArray(b"matches"),
            self.GROUP_PATH_ROLE: QByteArray(b"groupPath"),
            self.GROUP_LABEL_ROLE: QByteArray(b"groupLabel"),
        }

    @property
    def count(self) -> int:
        return len(self._items)

    def items(self) -> list[VisualEditorControl]:
        return list(self._items)

    def reset(self, items: list[VisualEditorControl]) -> None:
        self.beginResetModel()
        self._items = list(items)
        self.endResetModel()
        self.countChanged.emit()
