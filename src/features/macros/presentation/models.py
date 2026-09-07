from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal

from features.macros.domain.models import MacroItem


class MacroListModel(QAbstractListModel):
    countChanged = Signal()

    ID_ROLE = Qt.ItemDataRole.UserRole.value + 1
    NAME_ROLE = ID_ROLE + 1
    STEP_COUNT_ROLE = ID_ROLE + 2
    STEPS_ROLE = ID_ROLE + 3
    SOURCE_PATH_ROLE = ID_ROLE + 4
    VALIDATION_ERRORS_ROLE = ID_ROLE + 5
    VALIDATION_TEXT_ROLE = ID_ROLE + 6
    CAN_RUN_ROLE = ID_ROLE + 7
    RUNNING_ROLE = ID_ROLE + 8
    STATUS_TEXT_ROLE = ID_ROLE + 9
    FAILED_STEP_INDEX_ROLE = ID_ROLE + 10

    def __init__(self) -> None:
        super().__init__()
        self._items: list[MacroItem] = []

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
        if role == self.NAME_ROLE or role == Qt.ItemDataRole.DisplayRole:
            return item.name
        if role == self.STEP_COUNT_ROLE:
            return item.step_count
        if role == self.STEPS_ROLE:
            return [step.to_dict() for step in item.steps]
        if role == self.SOURCE_PATH_ROLE:
            return item.source_path
        if role == self.VALIDATION_ERRORS_ROLE:
            return list(item.validation_errors)
        if role == self.VALIDATION_TEXT_ROLE:
            return "\n".join(item.validation_errors)
        if role == self.CAN_RUN_ROLE:
            return item.can_run
        if role == self.RUNNING_ROLE:
            return item.running
        if role == self.STATUS_TEXT_ROLE:
            return item.status_text
        if role == self.FAILED_STEP_INDEX_ROLE:
            return item.failed_step_index
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.ID_ROLE: QByteArray(b"id"),
            self.NAME_ROLE: QByteArray(b"name"),
            self.STEP_COUNT_ROLE: QByteArray(b"stepCount"),
            self.STEPS_ROLE: QByteArray(b"steps"),
            self.SOURCE_PATH_ROLE: QByteArray(b"sourcePath"),
            self.VALIDATION_ERRORS_ROLE: QByteArray(b"validationErrors"),
            self.VALIDATION_TEXT_ROLE: QByteArray(b"validationText"),
            self.CAN_RUN_ROLE: QByteArray(b"canRun"),
            self.RUNNING_ROLE: QByteArray(b"running"),
            self.STATUS_TEXT_ROLE: QByteArray(b"statusText"),
            self.FAILED_STEP_INDEX_ROLE: QByteArray(b"failedStepIndex"),
        }

    @property
    def count(self) -> int:
        return len(self._items)

    def items(self) -> list[MacroItem]:
        return list(self._items)

    def item_at(self, row: int) -> MacroItem | None:
        if not 0 <= row < len(self._items):
            return None
        return self._items[row]

    def reset(self, items: list[MacroItem]) -> None:
        self.beginResetModel()
        self._items = list(items)
        self.endResetModel()
        self.countChanged.emit()

    def replace_item(self, row: int, item: MacroItem) -> None:
        if not 0 <= row < len(self._items):
            return
        self._items[row] = item
        self.refresh_row(row)

    def refresh_row(self, row: int) -> None:
        if not 0 <= row < len(self._items):
            return
        model_index = self.index(row, 0)
        self.dataChanged.emit(model_index, model_index)
