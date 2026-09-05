from __future__ import annotations

from app.core.content_filter import ContentFilter
from app.features.macros.macro_repository import MacroRepository
from app.features.macros.macro_types import MACRO_STEP_TYPES, MacroItem
from app.ui.macro_models import MacroListModel


class MacroController:
    def __init__(self, model: MacroListModel, repository: MacroRepository) -> None:
        self._model = model
        self._repository = repository
        self.reload([])

    @property
    def count(self) -> int:
        return self._model.count

    @property
    def any_running(self) -> bool:
        return any(item.running for item in self._model.items())

    def reload(self, filters: list[ContentFilter]) -> None:
        self._model.reset(self._repository.list_macros())
        self.refresh_validation(filters)

    def refresh_validation(self, filters: list[ContentFilter]) -> None:
        filter_names = [content_filter.display_name for content_filter in filters]
        for row, item in enumerate(self._model.items()):
            item.validation_errors = self._validation_errors(item, filter_names)
            self._model.refresh_row(row)

    def macro_at(self, row: int) -> MacroItem | None:
        return self._model.item_at(row)

    def validate_for_run(self, row: int, filters: list[ContentFilter]) -> list[str]:
        item = self._model.item_at(row)
        if item is None:
            return ["Macro was not found."]

        errors = self._validation_errors(item, [content_filter.display_name for content_filter in filters])
        item.validation_errors = errors
        self._model.refresh_row(row)
        return errors

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

    def _validation_errors(self, item: MacroItem, filter_names: list[str]) -> list[str]:
        errors = list(item.load_errors)
        if not item.name.strip():
            errors.append("Macro name is required.")
        if not item.steps:
            errors.append("Macro must have at least one step.")

        for index, step in enumerate(item.steps):
            label = f"Step {index + 1}"
            if step.type not in MACRO_STEP_TYPES:
                if not any(message.startswith(label + ": unknown step type") for message in errors):
                    errors.append(f"{label}: unknown step type '{step.type}'.")
                continue
            if step.type == "filter":
                if not step.filter_name.strip():
                    errors.append(f"{label}: filterName is required.")
                elif step.filter_name not in filter_names:
                    errors.append(f"{label}: no loaded filter named '{step.filter_name}'.")
            elif step.type == "search":
                if not step.search_value:
                    errors.append(f"{label}: searchValue is required.")
            elif step.type == "search-and-replace":
                if not step.search_value:
                    errors.append(f"{label}: searchValue is required.")
                if not step.has_replace_value:
                    errors.append(f"{label}: replaceValue is required.")
        return errors
