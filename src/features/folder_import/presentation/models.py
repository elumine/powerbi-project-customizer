from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal

from features.folder_import.application.models import FolderScanItem


class FolderScanModel(QAbstractListModel):
    countChanged = Signal()

    PATH_ROLE = Qt.ItemDataRole.UserRole.value + 1
    DISPLAY_NAME_ROLE = PATH_ROLE + 1
    RELATIVE_PATH_ROLE = PATH_ROLE + 2
    DEPTH_ROLE = PATH_ROLE + 3
    FILE_TYPE_ROLE = PATH_ROLE + 4

    def __init__(self) -> None:
        super().__init__()
        self._items: list[FolderScanItem] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._items)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None

        item = self._items[index.row()]
        if role == self.PATH_ROLE:
            return str(item.path)
        if role == self.DISPLAY_NAME_ROLE or role == Qt.ItemDataRole.DisplayRole:
            return item.display_name
        if role == self.RELATIVE_PATH_ROLE:
            return item.relative_path
        if role == self.DEPTH_ROLE:
            return max(0, len(Path(item.relative_path).parts) - 1)
        if role == self.FILE_TYPE_ROLE:
            return item.file_type
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.PATH_ROLE: QByteArray(b"path"),
            self.DISPLAY_NAME_ROLE: QByteArray(b"displayName"),
            self.RELATIVE_PATH_ROLE: QByteArray(b"relativePath"),
            self.DEPTH_ROLE: QByteArray(b"depth"),
            self.FILE_TYPE_ROLE: QByteArray(b"fileType"),
        }

    @property
    def count(self) -> int:
        return len(self._items)

    def paths(self) -> list[Path]:
        return [item.path for item in self._items]

    def reset(self, items: list[FolderScanItem]) -> None:
        self.beginResetModel()
        self._items = items
        self.endResetModel()
        self.countChanged.emit()

    def clear(self) -> None:
        self.reset([])
