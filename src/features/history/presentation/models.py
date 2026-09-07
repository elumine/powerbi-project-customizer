from __future__ import annotations

from collections.abc import Iterable

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal

from features.history.domain.models import HistoryEntry


class HistoryListModel(QAbstractListModel):
    countChanged = Signal()

    INDEX_ROLE = Qt.ItemDataRole.UserRole.value + 1
    TIME_TEXT_ROLE = INDEX_ROLE + 1
    OPERATION_TYPE_ROLE = INDEX_ROLE + 2
    DISPLAY_NAME_ROLE = INDEX_ROLE + 3
    METADATA_TEXT_ROLE = INDEX_ROLE + 4
    ROW_STATE_ROLE = INDEX_ROLE + 5
    REVERSIBLE_ROLE = INDEX_ROLE + 6
    AFFECTED_FILE_COUNT_ROLE = INDEX_ROLE + 7
    CHANGED_VALUE_COUNT_ROLE = INDEX_ROLE + 8

    def __init__(self) -> None:
        super().__init__()
        self._entries: list[HistoryEntry] = []
        self._current_index = -1

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._entries)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._entries):
            return None
        entry = self._entries[index.row()]
        if role == self.INDEX_ROLE or role == Qt.ItemDataRole.DisplayRole:
            return entry.index
        if role == self.TIME_TEXT_ROLE:
            return entry.time_text
        if role == self.OPERATION_TYPE_ROLE:
            return entry.operation_type
        if role == self.DISPLAY_NAME_ROLE:
            return entry.display_name
        if role == self.METADATA_TEXT_ROLE:
            return entry.metadata_text
        if role == self.ROW_STATE_ROLE:
            if entry.index == self._current_index:
                return "current"
            return "previous" if entry.index < self._current_index else "next"
        if role == self.REVERSIBLE_ROLE:
            return entry.reversible
        if role == self.AFFECTED_FILE_COUNT_ROLE:
            return len(entry.file_changes)
        if role == self.CHANGED_VALUE_COUNT_ROLE:
            return int(entry.metadata.get("changed_values", 0) or 0)
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.INDEX_ROLE: QByteArray(b"historyIndex"),
            self.TIME_TEXT_ROLE: QByteArray(b"timeText"),
            self.OPERATION_TYPE_ROLE: QByteArray(b"operationType"),
            self.DISPLAY_NAME_ROLE: QByteArray(b"displayName"),
            self.METADATA_TEXT_ROLE: QByteArray(b"metadataText"),
            self.ROW_STATE_ROLE: QByteArray(b"rowState"),
            self.REVERSIBLE_ROLE: QByteArray(b"reversible"),
            self.AFFECTED_FILE_COUNT_ROLE: QByteArray(b"affectedFileCount"),
            self.CHANGED_VALUE_COUNT_ROLE: QByteArray(b"changedValueCount"),
        }

    @property
    def count(self) -> int:
        return len(self._entries)

    def reset(self, entries: Iterable[HistoryEntry], current_index: int) -> None:
        self.beginResetModel()
        self._entries = list(entries)
        self._current_index = current_index
        self.endResetModel()
        self.countChanged.emit()
