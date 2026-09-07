from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal

from features.suggestions.application.service import SuggestionItem


class SuggestionListModel(QAbstractListModel):
    countChanged = Signal()

    ID_ROLE = Qt.ItemDataRole.UserRole.value + 1
    TYPE_ROLE = ID_ROLE + 1
    DUPLICATION_VALUE_ROLE = ID_ROLE + 2
    NORMALIZED_VALUE_ROLE = ID_ROLE + 3
    DUPLICATION_COUNT_ROLE = ID_ROLE + 4
    COLOR_ROLE = ID_ROLE + 5
    OCCURRENCES_ROLE = ID_ROLE + 6

    def __init__(self) -> None:
        super().__init__()
        self._items: list[SuggestionItem] = []

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
        if role == self.TYPE_ROLE:
            return item.type
        if role == self.DUPLICATION_VALUE_ROLE or role == Qt.ItemDataRole.DisplayRole:
            return item.duplication_value
        if role == self.NORMALIZED_VALUE_ROLE:
            return item.normalized_value
        if role == self.DUPLICATION_COUNT_ROLE:
            return item.duplication_count
        if role == self.COLOR_ROLE:
            return item.color
        if role == self.OCCURRENCES_ROLE:
            return [occurrence.to_dict() for occurrence in item.occurrences]
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.ID_ROLE: QByteArray(b"id"),
            self.TYPE_ROLE: QByteArray(b"type"),
            self.DUPLICATION_VALUE_ROLE: QByteArray(b"duplicationValue"),
            self.NORMALIZED_VALUE_ROLE: QByteArray(b"normalizedValue"),
            self.DUPLICATION_COUNT_ROLE: QByteArray(b"duplicationCount"),
            self.COLOR_ROLE: QByteArray(b"suggestionColor"),
            self.OCCURRENCES_ROLE: QByteArray(b"occurrences"),
        }

    @property
    def count(self) -> int:
        return len(self._items)

    def items(self) -> list[SuggestionItem]:
        return list(self._items)

    def item_at(self, row: int) -> SuggestionItem | None:
        if not 0 <= row < len(self._items):
            return None
        return self._items[row]

    def reset(self, items: list[SuggestionItem]) -> None:
        self.beginResetModel()
        self._items = list(items)
        self.endResetModel()
        self.countChanged.emit()
