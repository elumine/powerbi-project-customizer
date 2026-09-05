from __future__ import annotations

from app.core.content_filter import FILTER_OPERATIONS, ContentFilter, ContentFilterMatcher, FilterRule, generate_filter_color
from app.features.filters.filter_editor_session import FilterEditorSession
from app.features.filters.filter_repository import FilterRepository
from app.ui.file_list_model import FileListModel
from app.ui.filter_models import FilterListModel, RuleListModel


class FilterController:
    """Feature controller for imported/user filters and the filter editor workflow."""

    def __init__(
        self,
        filter_model: FilterListModel,
        rule_model: RuleListModel,
        repository: FilterRepository,
        imported_filters: list[ContentFilter] | None = None,
    ) -> None:
        self._filters = filter_model
        self._rules = rule_model
        self._repository = repository
        self._editor = FilterEditorSession()
        self._imported_filters = list(imported_filters or [])
        self._filters.reset(self._imported_filters + self._repository.list_filters())

    @property
    def count(self) -> int:
        return self._filters.count

    @property
    def active_filter_name(self) -> str:
        return self._filters.active_filter_name()

    @property
    def active_filter_color(self) -> str:
        return self._filters.active_filter_color()

    @property
    def has_active_filter(self) -> bool:
        return self._filters.active_filter() is not None

    @property
    def editor_visible(self) -> bool:
        return self._editor.visible

    @property
    def editor_name(self) -> str:
        return self._editor.name

    @property
    def editor_color(self) -> str:
        return self._editor.color

    @property
    def editor_rule_count(self) -> int:
        return self._rules.count

    @property
    def editor_can_save(self) -> bool:
        rules = self._rules.rules()
        return bool(self._editor.name.strip()) and bool(rules) and all(rule.key.strip() for rule in rules)

    def set_imported_filters(self, imported_filters: list[ContentFilter]) -> None:
        active_filter_id = self._filters.active_filter_id()
        user_filters = self._user_filters()
        self._imported_filters = list(imported_filters)
        self._filters.reset(self._imported_filters + user_filters, active_filter_id)

    def filter_index_by_display_name(self, display_name: str) -> int:
        for index, content_filter in enumerate(self._filters.filters()):
            if content_filter.display_name == display_name:
                return index
        return -1

    def set_editor_name(self, value: str) -> bool:
        normalized = value or ""
        if normalized == self._editor.name:
            return False
        self._editor.name = normalized
        return True

    def set_editor_color(self, value: str) -> bool:
        normalized = value or generate_filter_color(self._filters.used_colors(self._editor.filter_id))
        if normalized == self._editor.color:
            return False
        self._editor.color = normalized
        return True

    def randomize_editor_color(self) -> bool:
        return self.set_editor_color(generate_filter_color(self._filters.used_colors(self._editor.filter_id)))

    def apply_filter(self, row: int, files: FileListModel) -> bool:
        content_filter = self._filters.filter_at(row)
        if content_filter is None:
            return False
        self._filters.set_active_filter_id(content_filter.id)
        self.apply_to_files(files)
        return True

    def deactivate_filter(self, files: FileListModel) -> bool:
        if not self.has_active_filter:
            return False
        self._filters.set_active_filter_id("")
        self.apply_to_files(files)
        return True

    def apply_to_files(self, files: FileListModel) -> None:
        active_filter = self._filters.active_filter()
        for row, document in enumerate(files.documents()):
            if active_filter is None:
                files.set_document_active(row, True, "")
                continue

            is_active = document.is_valid_json and ContentFilterMatcher.matches_filter(document.parsed_json, active_filter)
            files.set_document_active(row, is_active, active_filter.color if is_active else "")

    def open_new_editor(self) -> None:
        self._editor = FilterEditorSession.new_filter(self._filters.used_colors())
        self._rules.reset([FilterRule.create()])

    def open_edit_editor(self, row: int) -> bool:
        content_filter = self._filters.filter_at(row)
        if content_filter is None or content_filter.is_read_only:
            return False
        self._editor = FilterEditorSession.edit_filter(content_filter)
        self._rules.reset(content_filter.rules)
        return True

    def cancel_editor(self) -> None:
        self._editor = FilterEditorSession()
        self._rules.reset([])

    def save_editor(self) -> bool:
        if not self.editor_can_save:
            return False

        rules = [self._normalized_rule(rule) for rule in self._rules.rules()]
        content_filter = self._editor.to_filter(rules, self._filters.used_colors(self._editor.filter_id))
        content_filter.source_path = ""
        content_filter.is_read_only = False
        self._filters.upsert_filter(content_filter)
        self._repository.save_filters(self._user_filters())
        self.cancel_editor()
        return True

    def delete_filter(self, row: int, files: FileListModel) -> bool:
        content_filter = self._filters.filter_at(row)
        if content_filter is None or content_filter.is_read_only:
            return False
        removed = self._filters.remove_filter(row)
        if removed is None:
            return False
        self._repository.save_filters(self._user_filters())
        self.apply_to_files(files)
        return True

    def add_rule(self) -> None:
        self._rules.add_rule()

    def remove_rule(self, row: int) -> None:
        self._rules.remove_rule(row)

    def update_rule_key(self, row: int, value: str) -> None:
        self._rules.update_rule(row, key=value or "")

    def update_rule_operation(self, row: int, value: str) -> None:
        operation = value if value in FILTER_OPERATIONS else "equals"
        self._rules.update_rule(row, operation=operation)

    def update_rule_value(self, row: int, value: str) -> None:
        self._rules.update_rule(row, value=value or "")

    def _user_filters(self) -> list[ContentFilter]:
        return [content_filter for content_filter in self._filters.filters() if not content_filter.is_read_only]

    @staticmethod
    def _normalized_rule(rule: FilterRule) -> FilterRule:
        operation = rule.operation if rule.operation in FILTER_OPERATIONS else "equals"
        return FilterRule(id=rule.id, key=rule.key.strip(), operation=operation, value=rule.value)