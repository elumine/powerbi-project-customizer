from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal


class ImportChangeModel(QAbstractListModel):
    """The externally changed imported files awaiting a user decision."""

    countChanged = Signal()
    PATH_ROLE = Qt.ItemDataRole.UserRole.value + 1
    NAME_ROLE = PATH_ROLE + 1

    def __init__(self) -> None:
        super().__init__()
        self._paths: list[Path] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self._paths)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._paths):
            return None
        path = self._paths[index.row()]
        if role == self.PATH_ROLE:
            return str(path)
        if role in (self.NAME_ROLE, Qt.ItemDataRole.DisplayRole):
            return path.name
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {self.PATH_ROLE: QByteArray(b"path"), self.NAME_ROLE: QByteArray(b"name")}

    @property
    def count(self) -> int:
        return len(self._paths)

    def paths(self) -> list[Path]:
        return list(self._paths)

    def reset(self, paths: list[Path]) -> None:
        self.beginResetModel()
        self._paths = list(dict.fromkeys(path.expanduser().resolve() for path in paths))
        self.endResetModel()
        self.countChanged.emit()

    def clear(self) -> None:
        self.reset([])
