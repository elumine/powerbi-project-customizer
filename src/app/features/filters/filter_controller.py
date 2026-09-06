from __future__ import annotations

import uuid
from pathlib import Path

from app.core.content_filter import FILTER_OPERATIONS, ContentFilter, ContentFilterMatcher, FilterRule, generate_filter_color
from app.core.json_file_type import FILTER_TARGET_ALL, JsonFileType, normalize_filter_target
from app.features.filters.filter_editor_session import FilterEditorSession
from app.features.filters.filter_import_repository import ImportedFilterRepository
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

    def apply_filter(self, row: int, files: FileListModel) -> bool:
        content_filter = self._filters.filter_at(row)
        if content_filter is None:
            return False
        self._dynamic_filter = None
        self._filters.set_active_filter_id(content_filter.id)
        self.apply_to_files(files)
        return True

    def apply_dynamic_page_name_filter(self, value: str, files: FileListModel) -> bool:
        return self._apply_dynamic_filter(
            display_name="Page name contains " + value,
            target_json_file_type=JsonFileType.PAGE.value,
            key="displayName",
            value=value,
            files=files,
        )

    def apply_dynamic_visual_type_filter(self, value: str, files: FileListModel) -> bool:
        return self._apply_dynamic_filter(
            display_name="Visual type contains " + value,
            target_json_file_type=JsonFileType.VISUAL.value,
            key="visualType",
            value=value,
            files=files,
        )

    def deactivate_filter(self, files: FileListModel) -> bool:
        if not self.has_active_filter:
            return False
        self._dynamic_filter = None
        self._filters.set_active_filter_id("")
        self.apply_to_files(files)
        return True

    def reset_active_filter(self, files: FileListModel) -> None:
        self._dynamic_filter = None
        self._filters.set_active_filter_id("")
        self.apply_to_files(files)

    def apply_to_files(self, files: FileListModel) -> None:
        active_filter = self._active_filter()
        documents = list(files.documents())
        if active_filter is None:
            for row, _document in enumerate(documents):
                files.set_document_state(row, True, True, "")
            return

        matched_rows: set[int] = set()
        visible_rows: set[int] = set()
        page_id_to_row = {document.id: row for row, document in enumerate(documents) if document.file_type == JsonFileType.PAGE}
        target = normalize_filter_target(active_filter.target_json_file_type)

        for row, document in enumerate(documents):
            if not document.is_valid_json:
                continue
            if not self._document_matches_target(document, target):
                continue
            if ContentFilterMatcher.matches_filter(document.parsed_json, active_filter):
                matched_rows.add(row)
                visible_rows.add(row)

        if target == JsonFileType.PAGE.value:
            matching_page_ids = {documents[row].id for row in matched_rows if documents[row].file_type == JsonFileType.PAGE}
            for row, document in enumerate(documents):
                if document.parent_page_id in matching_page_ids:
                    matched_rows.add(row)
                    visible_rows.add(row)
        elif target == JsonFileType.VISUAL.value:
            for row in list(matched_rows):
                parent_page_id = documents[row].parent_page_id
                parent_row = page_id_to_row.get(parent_page_id)
                if parent_row is not None:
                    visible_rows.add(parent_row)
        else:
            for row in list(matched_rows):
                document = documents[row]
                if document.file_type == JsonFileType.VISUAL and document.parent_page_id:
                    parent_row = page_id_to_row.get(document.parent_page_id)
                    if parent_row is not None:
                        visible_rows.add(parent_row)

        for row, _document in enumerate(documents):
            is_active = row in matched_rows
            is_visible = row in visible_rows
            files.set_document_state(row, is_active, is_visible, active_filter.color if is_active else "")

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

    def _apply_dynamic_filter(
        self,
        display_name: str,
        target_json_file_type: str,
        key: str,
        value: str,
        files: FileListModel,
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
