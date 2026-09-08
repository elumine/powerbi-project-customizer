from __future__ import annotations

import uuid
from pathlib import Path

from entities.filter.models import ContentFilter
from features.macros.infrastructure.repository import MacroRepository
from features.macros.domain.models import MACRO_STEP_TYPES, MacroItem, MacroStep
from features.macros.presentation.models import MacroListModel


class MacroController:
    def __init__(self, model: MacroListModel, repository: MacroRepository) -> None:
        self._model = model
        self._repository = repository
        self.reload([])

    @property
    def count(self) -> int:
        return self._model.count

    @property
    def search_text(self) -> str:
        return self._model.search_text

    def set_search_text(self, value: str) -> None:
        self._model.set_search_text(value)

    @property
    def any_running(self) -> bool:
        return any(item.running for item in self._model.items())

    def reload(self, filters: list[ContentFilter]) -> None:
        self._model.reset(self._repository.list_macros())
        self.refresh_validation(filters)

    def reset_runtime_state(self) -> None:
        for row, item in enumerate(self._model.items()):
            item.running = False
            item.failed_step_index = -1
            item.runtime_error = ""
            self._model.refresh_row(row)

    def refresh_validation(self, filters: list[ContentFilter]) -> None:
        for row, item in enumerate(self._model.items()):
            item.validation_errors = self._validation_errors(item, filters)
            self._model.refresh_row(row)

    def macro_at(self, row: int) -> MacroItem | None:
        return self._model.item_at(row)

    def validate_for_run(self, row: int, filters: list[ContentFilter]) -> list[str]:
        item = self._model.item_at(row)
        if item is None:
            return ["Macro was not found."]

        errors = self._validation_errors(item, filters)
        item.validation_errors = errors
        self._model.refresh_row(row)
        return errors

    def import_macro(self, path: Path, filters: list[ContentFilter]) -> tuple[bool, str]:
        item = self._repository.load_macro_file(path)
        existing_ids = {macro.id for macro in self._model.items()}
        if item.id in existing_ids:
            item.id = str(uuid.uuid4())
        item.validation_errors = self._validation_errors(item, filters)
        self._model.reset(self._model.items() + [item])
        return True, f"Imported macro {item.name}."

    def export_macro(self, row: int, path: Path) -> tuple[bool, str]:
        item = self._model.item_at(row)
        if item is None:
            return False, "Macro was not found."
        try:
            MacroRepository.export_macro(path, item)
        except OSError as error:
            return False, str(error)
        return True, f"Exported macro {item.name}."

    def begin_run(self, row: int) -> MacroItem | None:
        item = self._model.item_at(row)
        if item is None or self.any_running:
            return None
        item.running = True
        item.failed_step_index = -1
        item.runtime_error = ""
        self._model.refresh_row(row)
        return item

    def finish_run(self, row: int) -> None:
        item = self._model.item_at(row)
        if item is None:
            return
        item.running = False
        item.failed_step_index = -1
        item.runtime_error = ""
        self._model.refresh_row(row)

    def fail_run(self, row: int, step_index: int, error: str) -> None:
        item = self._model.item_at(row)
        if item is None:
            return
        item.running = False
        item.failed_step_index = step_index
        item.runtime_error = error
        self._model.refresh_row(row)

    def create_from_history_entries(self, entries, filters: list[ContentFilter]) -> tuple[bool, str]:
        steps: list[MacroStep] = []
        skipped: list[int] = []
        macro_id = f"recorded.{uuid.uuid4()}"
        for entry in entries:
            step = self._step_from_history_entry(macro_id, len(steps), entry)
            if step is None:
                skipped.append(entry.index)
                continue
            steps.append(step)
        if not steps:
            return False, "No replayable history entries were selected."
        first_index = entries[0].index
        last_index = entries[-1].index
        item = MacroItem(
            id=macro_id,
            name=f"Recorded macro {first_index}-{last_index}",
            steps=steps,
        )
        item.validation_errors = self._validation_errors(item, filters)
        self._model.reset(self._model.items() + [item])
        suffix = f" Skipped history rows: {', '.join(str(index) for index in skipped)}." if skipped else ""
        return True, f"Created macro from history rows {first_index}-{last_index}.{suffix}"

    @staticmethod
    def _step_from_history_entry(macro_id: str, step_index: int, entry) -> MacroStep | None:
        step_id = f"{macro_id}.step.{step_index + 1}"
        metadata = dict(entry.metadata or {})
        operation_type = entry.operation_type
        if operation_type in {"search-replace-one", "search-replace-current-file"}:
            return MacroStep(
                id=step_id,
                type="search-replace-one",
                search_value=str(metadata.get("search", "")),
                replace_value=str(metadata.get("replace", "")),
                source_history_index=entry.index,
            )
        if operation_type == "search-replace-all":
            return MacroStep(
                id=step_id,
                type="search-replace-all",
                search_value=str(metadata.get("search", "")),
                replace_value=str(metadata.get("replace", "")),
                source_history_index=entry.index,
            )
        if operation_type == "visual-editor-change":
            return MacroStep(
                id=step_id,
                type="visual-editor-change",
                control_id=entry.display_name,
                value=metadata.get("value", ""),
                source_history_index=entry.index,
            )
        if operation_type == "filter-apply":
            return MacroStep(id=step_id, type="filter-apply", filter_name=entry.display_name, source_history_index=entry.index)
        if operation_type == "filter-clear":
            return MacroStep(id=step_id, type="filter-clear", source_history_index=entry.index)
        if operation_type == "dynamic-filter-apply":
            return MacroStep(
                id=step_id,
                type="dynamic-filter-apply",
                filter_name=str(metadata.get("kind", "")),
                value=str(metadata.get("value", "")),
                source_history_index=entry.index,
            )
        if operation_type == "format-json":
            return MacroStep(id=step_id, type="format-json", source_history_index=entry.index)
        return None

    def _validation_errors(self, item: MacroItem, filters: list[ContentFilter]) -> list[str]:
        errors = list(item.load_errors)
        if not item.name.strip():
            errors.append("Macro name is required.")
        if not item.steps:
            errors.append("Macro must have at least one step.")

        filter_names = [content_filter.display_name for content_filter in filters]
        filter_ids = [content_filter.id for content_filter in filters]
        for index, step in enumerate(item.steps):
            label = f"Step {index + 1}"
            if step.type not in MACRO_STEP_TYPES:
                if not any(message.startswith(label + ": unknown step type") for message in errors):
                    errors.append(f"{label}: unknown step type '{step.type}'.")
                continue
            if step.type in {"filter", "filter-apply"}:
                has_named_filter = step.filter_name.strip() and step.filter_name in filter_names
                has_filter_id = step.filter_id.strip() and step.filter_id in filter_ids
                if not step.filter_name.strip() and not step.filter_id.strip():
                    errors.append(f"{label}: filterName or filterId is required.")
                elif not has_named_filter and not has_filter_id:
                    errors.append(f"{label}: no loaded filter named '{step.filter_name or step.filter_id}'.")
            elif step.type == "search":
                if not step.search_value:
                    errors.append(f"{label}: searchValue is required.")
            elif step.type in {"search-and-replace", "search-replace", "search-replace-one", "search-replace-all"}:
                if not step.search_value:
                    errors.append(f"{label}: searchValue is required.")
                if step.type == "search-and-replace" and not step.has_replace_value:
                    errors.append(f"{label}: replaceValue is required.")
            elif step.type == "dynamic-filter-apply":
                if step.filter_name not in {"page-name", "visual-type", "visual-name"}:
                    errors.append(f"{label}: dynamic filter kind is required.")
                if str(step.value) == "":
                    errors.append(f"{label}: value is required.")
            elif step.type == "visual-editor-change":
                if not step.control_id:
                    errors.append(f"{label}: controlId is required.")
        return errors
