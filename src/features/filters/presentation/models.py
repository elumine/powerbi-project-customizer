from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QByteArray, QModelIndex, Qt, Signal

from entities.filter.models import ContentFilter, FilterRule


class FilterListModel(QAbstractListModel):
    countChanged = Signal()

    ID_ROLE = Qt.ItemDataRole.UserRole.value + 1
    DISPLAY_NAME_ROLE = ID_ROLE + 1
    COLOR_ROLE = ID_ROLE + 2
    RULE_SUMMARY_ROLE = ID_ROLE + 3
    ACTIVE_ROLE = ID_ROLE + 4
    SOURCE_PATH_ROLE = ID_ROLE + 5
    READ_ONLY_ROLE = ID_ROLE + 6
    TARGET_FILE_TYPE_ROLE = ID_ROLE + 7

    def __init__(self) -> None:
        super().__init__()
        self._filters: list[ContentFilter] = []
        self._active_filter_id = ""

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._filters)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._filters):
            return None

        content_filter = self._filters[index.row()]
        if role == self.ID_ROLE:
            return content_filter.id
        if role == self.DISPLAY_NAME_ROLE or role == Qt.ItemDataRole.DisplayRole:
            return content_filter.display_name
        if role == self.COLOR_ROLE:
            return content_filter.color
        if role == self.RULE_SUMMARY_ROLE:
            return self._rule_summary(content_filter)
        if role == self.ACTIVE_ROLE:
            return content_filter.id == self._active_filter_id
        if role == self.SOURCE_PATH_ROLE:
            return content_filter.source_path
        if role == self.READ_ONLY_ROLE:
            return content_filter.is_read_only
        if role == self.TARGET_FILE_TYPE_ROLE:
            return content_filter.target_json_file_type
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.ID_ROLE: QByteArray(b"id"),
            self.DISPLAY_NAME_ROLE: QByteArray(b"displayName"),
            self.COLOR_ROLE: QByteArray(b"color"),
            self.RULE_SUMMARY_ROLE: QByteArray(b"ruleSummary"),
            self.ACTIVE_ROLE: QByteArray(b"active"),
            self.SOURCE_PATH_ROLE: QByteArray(b"sourcePath"),
            self.READ_ONLY_ROLE: QByteArray(b"readOnly"),
            self.TARGET_FILE_TYPE_ROLE: QByteArray(b"targetJsonFileType"),
        }

    @property
    def count(self) -> int:
        return len(self._filters)

    def filters(self) -> list[ContentFilter]:
        return list(self._filters)

    def filter_at(self, row: int) -> ContentFilter | None:
        if not 0 <= row < len(self._filters):
            return None
        return self._filters[row]

    def active_filter(self) -> ContentFilter | None:
        for content_filter in self._filters:
            if content_filter.id == self._active_filter_id:
                return content_filter
        return None

    def active_filter_id(self) -> str:
        return self._active_filter_id

    def active_filter_color(self) -> str:
        active_filter = self.active_filter()
        return active_filter.color if active_filter is not None else ""

    def active_filter_name(self) -> str:
        active_filter = self.active_filter()
        return active_filter.display_name if active_filter is not None else ""

    def used_colors(self, exclude_filter_id: str = "") -> set[str]:
        return {item.color for item in self._filters if item.id != exclude_filter_id}

    def reset(self, filters: list[ContentFilter], active_filter_id: str = "") -> None:
        active_id = active_filter_id if any(item.id == active_filter_id for item in filters) else ""
        self.beginResetModel()
        self._filters = filters
        self._active_filter_id = active_id
        self.endResetModel()
        self.countChanged.emit()

    def upsert_filter(self, content_filter: ContentFilter) -> None:
        for row, existing in enumerate(self._filters):
            if existing.id == content_filter.id:
                self._filters[row] = content_filter
                model_index = self.index(row, 0)
                self.dataChanged.emit(model_index, model_index)
                return

        row = len(self._filters)
        self.beginInsertRows(QModelIndex(), row, row)
        self._filters.append(content_filter)
        self.endInsertRows()
        self.countChanged.emit()

    def remove_filter(self, row: int) -> ContentFilter | None:
        if not 0 <= row < len(self._filters):
            return None

        self.beginRemoveRows(QModelIndex(), row, row)
        removed = self._filters.pop(row)
        self.endRemoveRows()
        if removed.id == self._active_filter_id:
            self._active_filter_id = ""
            self.refresh_active_roles()
        self.countChanged.emit()
        return removed

    def set_active_filter_id(self, filter_id: str) -> None:
        if self._active_filter_id == filter_id:
            return
        self._active_filter_id = filter_id
        self.refresh_active_roles()

    def refresh_active_roles(self) -> None:
        if not self._filters:
            return
        top = self.index(0, 0)
        bottom = self.index(len(self._filters) - 1, 0)
        self.dataChanged.emit(top, bottom, [self.ACTIVE_ROLE])

    @staticmethod
    def _rule_summary(content_filter: ContentFilter) -> str:
        if not content_filter.rules:
            return f"{content_filter.target_json_file_type}: No rules"
        parts = [f"{rule.key} {rule.operation} {rule.value}" for rule in content_filter.rules]
        return f"{content_filter.target_json_file_type}: " + "; ".join(parts)


class RuleListModel(QAbstractListModel):
    countChanged = Signal()

    ID_ROLE = Qt.ItemDataRole.UserRole.value + 1
    KEY_ROLE = ID_ROLE + 1
    OPERATION_ROLE = ID_ROLE + 2
    VALUE_ROLE = ID_ROLE + 3

    def __init__(self) -> None:
        super().__init__()
        self._rules: list[FilterRule] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._rules)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._rules):
            return None

        rule = self._rules[index.row()]
        if role == self.ID_ROLE:
            return rule.id
        if role == self.KEY_ROLE or role == Qt.ItemDataRole.DisplayRole:
            return rule.key
        if role == self.OPERATION_ROLE:
            return rule.operation
        if role == self.VALUE_ROLE:
            return rule.value
        return None

    def roleNames(self) -> dict[int, QByteArray]:
        return {
            self.ID_ROLE: QByteArray(b"id"),
            self.KEY_ROLE: QByteArray(b"key"),
            self.OPERATION_ROLE: QByteArray(b"operation"),
            self.VALUE_ROLE: QByteArray(b"value"),
        }

    @property
    def count(self) -> int:
        return len(self._rules)

    def rules(self) -> list[FilterRule]:
        return [FilterRule(rule.id, rule.key, rule.operation, rule.value) for rule in self._rules]

    def reset(self, rules: list[FilterRule]) -> None:
        self.beginResetModel()
        self._rules = [FilterRule(rule.id, rule.key, rule.operation, rule.value) for rule in rules]
        self.endResetModel()
        self.countChanged.emit()

    def add_rule(self, rule: FilterRule | None = None) -> None:
        row = len(self._rules)
        self.beginInsertRows(QModelIndex(), row, row)
        self._rules.append(rule or FilterRule.create())
        self.endInsertRows()
        self.countChanged.emit()

    def remove_rule(self, row: int) -> None:
        if not 0 <= row < len(self._rules):
            return
        self.beginRemoveRows(QModelIndex(), row, row)
        self._rules.pop(row)
        self.endRemoveRows()
        self.countChanged.emit()

    def update_rule(self, row: int, key: str | None = None, operation: str | None = None, value: str | None = None) -> None:
        if not 0 <= row < len(self._rules):
            return

        rule = self._rules[row]
        if key is not None:
            rule.key = key
        if operation is not None:
            rule.operation = operation
        if value is not None:
            rule.value = value
        model_index = self.index(row, 0)
        self.dataChanged.emit(model_index, model_index)
