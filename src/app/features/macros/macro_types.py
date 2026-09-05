from __future__ import annotations

from dataclasses import dataclass, field


MACRO_STEP_TYPES = ("filter", "search", "search-and-replace")


@dataclass(slots=True)
class MacroStep:
    id: str
    type: str
    filter_name: str = ""
    search_value: str = ""
    replace_value: str = ""
    has_replace_value: bool = True

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "type": self.type,
            "filterName": self.filter_name,
            "searchValue": self.search_value,
            "replaceValue": self.replace_value,
            "summary": self.summary,
        }

    @property
    def summary(self) -> str:
        if self.type == "filter":
            return f"filterName: {self.filter_name}"
        if self.type == "search":
            return f"searchValue: {self.search_value}"
        if self.type == "search-and-replace":
            return f"searchValue: {self.search_value}; replaceValue: {self.replace_value}"
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
