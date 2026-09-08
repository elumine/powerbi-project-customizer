from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


MACRO_STEP_TYPES = (
    "filter",
    "filter-apply",
    "filter-clear",
    "search",
    "search-and-replace",
    "search-replace",
    "replace-current",
    "replace-all",
    "search-replace-one",
    "search-replace-all",
    "dynamic-filter-apply",
    "format-json",
    "visual-editor-change",
)


@dataclass(slots=True)
class MacroStep:
    id: str
    type: str
    filter_name: str = ""
    filter_id: str = ""
    search_value: str = ""
    replace_value: str = ""
    has_replace_value: bool = True
    control_id: str = ""
    value: Any = ""
    allow_no_change: bool = False
    source_history_index: int = -1

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "filterName": self.filter_name,
            "filterId": self.filter_id,
            "searchValue": self.search_value,
            "replaceValue": self.replace_value,
            "controlId": self.control_id,
            "value": self.value,
            "allowNoChange": self.allow_no_change,
            "summary": self.summary,
            "sourceHistoryIndex": self.source_history_index,
        }

    def to_export_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"type": self.type}
        if self.filter_name:
            data["filterName"] = self.filter_name
        if self.filter_id:
            data["filterId"] = self.filter_id
        if self.search_value:
            data["searchValue"] = self.search_value
        if self.type in {"search-and-replace", "search-replace", "search-replace-one", "search-replace-all"} or self.replace_value or self.has_replace_value:
            data["replaceValue"] = self.replace_value
        if self.control_id:
            data["controlId"] = self.control_id
        if self.type in {"visual-editor-change", "dynamic-filter-apply"}:
            data["value"] = self.value
        if self.allow_no_change:
            data["allowNoChange"] = True
        if self.source_history_index >= 0:
            data["sourceHistoryIndex"] = self.source_history_index
        return data

    @property
    def summary(self) -> str:
        if self.type in {"filter", "filter-apply"}:
            return f"filterName: {self.filter_name or self.filter_id}"
        if self.type == "filter-clear":
            return "clear active filter"
        if self.type == "search":
            return f"searchValue: {self.search_value}"
        if self.type in {"search-and-replace", "search-replace"}:
            return f"searchValue: {self.search_value}; replaceValue: {self.replace_value}"
        if self.type == "replace-current":
            return "replace current match"
        if self.type == "replace-all":
            return "replace all active matches"
        if self.type == "search-replace-one":
            return f"searchValue: {self.search_value}; replace current with: {self.replace_value}"
        if self.type == "search-replace-all":
            return f"searchValue: {self.search_value}; replace all with: {self.replace_value}"
        if self.type == "dynamic-filter-apply":
            return f"dynamicFilter: {self.filter_name}; value: {self.value}"
        if self.type == "format-json":
            return "format current JSON"
        if self.type == "visual-editor-change":
            return f"controlId: {self.control_id}; value: {self.value}"
        return "unknown step"


@dataclass(slots=True)
class MacroGroup:
    """Named, ordered collection of macro steps.

    Groups are presentation metadata; execution still uses the flattened step
    order exposed by ``MacroItem.steps`` so old macros remain compatible.
    """

    id: str
    name: str
    steps: list[MacroStep] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "steps": [step.to_export_dict() for step in self.steps],
        }

    def to_view_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "steps": [step.to_dict() for step in self.steps],
        }


@dataclass(slots=True)
class MacroItem:
    id: str
    name: str
    steps: list[MacroStep] = field(default_factory=list)
    groups: list[MacroGroup] = field(default_factory=list)
    source_path: str = ""
    load_errors: list[str] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)
    running: bool = False
    failed_step_index: int = -1
    runtime_error: str = ""

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def can_run(self) -> bool:
        return not self.running and not self.validation_errors

    @property
    def status_text(self) -> str:
        if self.running:
            return "Running"
        if self.runtime_error:
            step_text = f"Step {self.failed_step_index + 1}: " if self.failed_step_index >= 0 else ""
            return step_text + self.runtime_error
        if self.validation_errors:
            return self.validation_errors[0]
        return "Ready"

    def to_export_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"id": self.id, "name": self.name}
        if self.groups:
            result["groups"] = [group.to_dict() for group in self.groups]
        else:
            result["steps"] = [step.to_export_dict() for step in self.steps]
        return result
