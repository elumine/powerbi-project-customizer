from __future__ import annotations

from collections.abc import Collection
from typing import Protocol

from features.macros.domain.models import MacroStep


class MacroOperationPort(Protocol):
    def apply_filter_macro_step(self, step: MacroStep) -> None: ...
    def clear_filter_macro_step(self, step: MacroStep) -> None: ...
    def search_macro_step(self, step: MacroStep) -> None: ...
    def replace_macro_step(self, step: MacroStep) -> None: ...
    def dynamic_filter_macro_step(self, step: MacroStep) -> None: ...
    def format_macro_step(self, step: MacroStep) -> None: ...
    def visual_editor_macro_step(self, step: MacroStep) -> None: ...


class MacroStepHandler(Protocol):
    name="MacroStepHandler"
    step_types: Collection[str]
    def execute(self, step: MacroStep, operations: MacroOperationPort) -> None: ...


class FilterStepHandler:
    name="FilterStepHandler"
    step_types = ("filter-apply",)
    def execute(self, step: MacroStep, operations: MacroOperationPort) -> None:
        operations.apply_filter_macro_step(step)


class ClearFilterStepHandler:
    name="ClearFilterStepHandler"
    step_types = ("filter-clear",)
    def execute(self, step: MacroStep, operations: MacroOperationPort) -> None:
        operations.clear_filter_macro_step(step)


class SearchStepHandler:
    name="SearchStepHandler"
    step_types = ("search",)
    def execute(self, step: MacroStep, operations: MacroOperationPort) -> None:
        operations.search_macro_step(step)


class ReplaceStepHandler:
    name="ReplaceStepHandler"
    step_types = ("search-replace-one", "search-replace-all")
    def execute(self, step: MacroStep, operations: MacroOperationPort) -> None:
        operations.replace_macro_step(step)


class DynamicFilterStepHandler:
    name="DynamicFilterStepHandler"
    step_types = ("dynamic-filter-apply",)
    def execute(self, step: MacroStep, operations: MacroOperationPort) -> None:
        operations.dynamic_filter_macro_step(step)


class FormatJsonStepHandler:
    name="FormatJsonStepHandler"
    step_types = ("format-json",)
    def execute(self, step: MacroStep, operations: MacroOperationPort) -> None:
        operations.format_macro_step(step)


class VisualEditorStepHandler:
    name="VisualEditorStepHandler"
    step_types = ("visual-editor-change",)
    def execute(self, step: MacroStep, operations: MacroOperationPort) -> None:
        operations.visual_editor_macro_step(step)


class MacroStepHandlerRegistry:
    def __init__(self, handlers: Collection[MacroStepHandler]) -> None:
        mapping: dict[str, MacroStepHandler] = {}
        for handler in handlers:
            for step_type in handler.step_types:
                if step_type in mapping:
                    errorText = "Duplicate macro step handler. stepType: " + step_type + ", handler: " + handler.name + "."
                    raise ValueError(errorText)
                    #raise ValueError(f"Duplicate macro step handler for '{step_type}', handler: '{ handler.name }'.")
                mapping[step_type] = handler
        self._handlers = mapping

    def execute(self, step: MacroStep, operations: MacroOperationPort) -> None:
        handler = self._handlers.get(step.type)
        if handler is None:
            raise ValueError(f"Unknown step type '{step.type}'.")
        handler.execute(step, operations)


def default_macro_step_registry() -> MacroStepHandlerRegistry:
    return MacroStepHandlerRegistry((
        FilterStepHandler(), ClearFilterStepHandler(), SearchStepHandler(), ReplaceStepHandler(),
        DynamicFilterStepHandler(), FormatJsonStepHandler(), VisualEditorStepHandler(),
    ))
