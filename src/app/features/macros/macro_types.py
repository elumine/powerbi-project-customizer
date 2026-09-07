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
            "summary": self.summary,
            "sourceHistoryIndex": self.source_history_index,
        }

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
class MacroItem:
    id: str
    name: str
    steps: list[MacroStep] = field(default_factory=list)
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
        steps: list[dict[str, Any]] = []
        for step in self.steps:
            data: dict[str, Any] = {"type": step.type}
            if step.filter_name:
                data["filterName"] = step.filter_name
            if step.filter_id:
                data["filterId"] = step.filter_id
            if step.search_value:
                data["searchValue"] = step.search_value
            if step.type in {"search-and-replace", "search-replace", "search-replace-one", "search-replace-all"} or step.replace_value or step.has_replace_value:
                data["replaceValue"] = step.replace_value
            if step.control_id:
                data["controlId"] = step.control_id
            if step.type in {"visual-editor-change", "dynamic-filter-apply"}:
                data["value"] = step.value
            if step.source_history_index >= 0:
                data["sourceHistoryIndex"] = step.source_history_index
            steps.append(data)
        return {"id": self.id, "name": self.name, "steps": steps}
