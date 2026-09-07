from __future__ import annotations

import uuid
from pathlib import Path

from entities.filter.models import FILTER_OPERATIONS, ContentFilter, FilterRule, generate_filter_color
from entities.filter.rules import ContentFilterMatcher
from entities.powerbi.file_types import FILTER_TARGET_ALL, JsonFileType, normalize_filter_target
from features.filters.application.scope import FilterScopeService
from features.filters.presentation.editor_session import FilterEditorSession
from features.filters.infrastructure.import_repository import ImportedFilterRepository
from features.filters.infrastructure.repository import FilterRepository
from services.documents.workspace_port import DocumentWorkspacePort
from features.filters.presentation.models import FilterListModel, RuleListModel


class FilterController:
    """Feature controller for imported/user filters and the filter editor workflow."""

    def __init__(
        self,
        filter_model: FilterListModel,
        rule_model: RuleListModel,
        repository: FilterRepository,
        imported_filters: list[ContentFilter] | None = None,
        scope_service: FilterScopeService | None = None,
    ) -> None:
        self._filters = filter_model
        self._rules = rule_model
        self._repository = repository
        self._scope_service = scope_service or FilterScopeService()
        self._editor = FilterEditorSession()
        self._imported_filters = list(imported_filters or [])
        self._dynamic_filter: ContentFilter | None = None
        self._filters.reset(self._imported_filters + self._repository.list_filters())

    @property
    def count(self) -> int:
        return self._filters.count

    @property
    def active_filter_name(self) -> str:
        active_filter = self._active_filter()
        return active_filter.display_name if active_filter is not None else ""

    @property
    def active_filter_color(self) -> str:
        active_filter = self._active_filter()
        return active_filter.color if active_filter is not None else ""

    @property
    def active_filter_target(self) -> str:
        active_filter = self._active_filter()
        return active_filter.target_json_file_type if active_filter is not None else ""

    @property
    def has_active_filter(self) -> bool:
        return self._active_filter() is not None

    @property
    def active_dynamic_filter_name(self) -> str:
        return self._dynamic_filter.display_name if self._dynamic_filter is not None else ""

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
    def editor_target(self) -> str:
        return self._editor.target_json_file_type

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

    def set_editor_target(self, value: str) -> bool:
        normalized = normalize_filter_target(value)
        if normalized == self._editor.target_json_file_type:
            return False
        self._editor.target_json_file_type = normalized
        return True

    def randomize_editor_color(self) -> bool:
        return self.set_editor_color(generate_filter_color(self._filters.used_colors(self._editor.filter_id)))

    def apply_filter(self, row: int, files: DocumentWorkspacePort) -> bool:
        content_filter = self._filters.filter_at(row)
        if content_filter is None:
            return False
        self._dynamic_filter = None
        self._filters.set_active_filter_id(content_filter.id)
        self.apply_to_files(files)
        return True

    def apply_dynamic_page_name_filter(self, value: str, files: DocumentWorkspacePort) -> bool:
        return self._apply_dynamic_filter(
            display_name="Page name contains " + value,
            target_json_file_type=JsonFileType.PAGE.value,
            key="displayName",
            value=value,
            files=files,
        )

    def apply_dynamic_visual_type_filter(self, value: str, files: DocumentWorkspacePort) -> bool:
        return self._apply_dynamic_filter(
            display_name="Visual type contains " + value,
            target_json_file_type=JsonFileType.VISUAL.value,
            key="visual.visualType",
            value=value,
            files=files,
        )

    def apply_dynamic_visual_name_filter(self, value: str, files: DocumentWorkspacePort) -> bool:
        return self._apply_dynamic_filter(
            display_name="Visual name contains " + value,
            target_json_file_type=JsonFileType.VISUAL.value,
            key="visualName",
            value=value,
            files=files,
        )

    def deactivate_filter(self, files: DocumentWorkspacePort) -> bool:
        if not self.has_active_filter:
            return False
        self._dynamic_filter = None
        self._filters.set_active_filter_id("")
        self.apply_to_files(files)
        return True

    def reset_active_filter(self, files: DocumentWorkspacePort) -> None:
        self._dynamic_filter = None
        self._filters.set_active_filter_id("")
        self.apply_to_files(files)

    def apply_to_files(self, files: DocumentWorkspacePort) -> None:
        """Apply the pure scope projection through the Qt presentation adapter."""
        for state in self._scope_service.project(files.collection.documents(), self._active_filter()):
            row = files.document_index_by_id(state.document_id)
            files.set_document_state(row, state.is_active, state.is_visible, state.filter_color)

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

    def import_user_filter(self, path: Path, import_repository: ImportedFilterRepository) -> tuple[bool, str]:
        used_ids = {content_filter.id for content_filter in self._filters.filters()}
        content_filter, errors = import_repository.load_filter_file(path, read_only=False, strict_target=False, used_ids=used_ids)
        if errors or content_filter is None:
            return False, errors[0] if errors else "Filter could not be imported."
        content_filter.is_read_only = False
        content_filter.source_path = ""
        if content_filter.id in used_ids:
            content_filter.id = str(uuid.uuid4())
        self._filters.upsert_filter(content_filter)
        self._repository.save_filters(self._user_filters())
        return True, f"Imported filter {content_filter.display_name}."

    def export_filter(self, row: int, path: Path) -> tuple[bool, str]:
        content_filter = self._filters.filter_at(row)
        if content_filter is None:
            return False, "Filter was not found."
        try:
            ImportedFilterRepository.export_filter(path, content_filter)
        except OSError as error:
            return False, str(error)
        return True, f"Exported filter {content_filter.display_name}."

    def delete_filter(self, row: int, files: DocumentWorkspacePort) -> bool:
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

    def _apply_dynamic_filter(
        self,
        display_name: str,
        target_json_file_type: str,
        key: str,
        value: str,
        files: DocumentWorkspacePort,
    ) -> bool:
        normalized_value = (value or "").strip()
        if not normalized_value:
            return False
        self._filters.set_active_filter_id("")
        self._dynamic_filter = ContentFilter(
            id="dynamic." + str(uuid.uuid4()),
            display_name=display_name,
            color="#569cd6",
            rules=[FilterRule.create(key=key, operation="includes", value=normalized_value)],
            target_json_file_type=target_json_file_type,
        )
        self.apply_to_files(files)
        return True

    def _active_filter(self) -> ContentFilter | None:
        if self._dynamic_filter is not None:
            return self._dynamic_filter
        return self._filters.active_filter()

    @staticmethod
    def _is_visual_name_filter(active_filter: ContentFilter) -> bool:
        return any(rule.key.strip().casefold() == "visualname" for rule in active_filter.rules)

    def _document_matches_filter(self, document, active_filter: ContentFilter) -> bool:
        if self._is_visual_name_filter(active_filter):
            return all(self._matches_visual_name_rule(document, rule) for rule in active_filter.rules)
        return ContentFilterMatcher.matches_filter(document.parsed_json, active_filter)

    @staticmethod
    def _matches_visual_name_rule(document, rule: FilterRule) -> bool:
        if rule.operation not in FILTER_OPERATIONS:
            return False
        candidates = [
            document.display_name,
            document.pbir_name,
            document.path.parent.name,
            document.path.name,
            document.relative_path,
        ]
        values = [str(value).casefold() for value in candidates if str(value).strip()]
        needle = rule.value.casefold()
        if rule.operation == "equals":
            return any(value == needle for value in values)
        if rule.operation == "includes":
            return any(needle in value for value in values)
        if rule.operation == "notEquals":
            return all(value != needle for value in values)
        if rule.operation == "notIncludes":
            return all(needle not in value for value in values)
        return False

    def _user_filters(self) -> list[ContentFilter]:
        return [content_filter for content_filter in self._filters.filters() if not content_filter.is_read_only]

    @staticmethod
    def _document_matches_target(document, target: str) -> bool:
        if target == FILTER_TARGET_ALL:
            return True
        return document.file_type_text == target

    @staticmethod
    def _normalized_rule(rule: FilterRule) -> FilterRule:
        operation = rule.operation if rule.operation in FILTER_OPERATIONS else "equals"
        return FilterRule(id=rule.id, key=rule.key.strip(), operation=operation, value=rule.value)

