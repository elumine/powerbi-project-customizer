from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class VisualEditorPropertyMatch:
    document_id: str
    file_path: str
    line: int
    property_path: str
    value: Any

    def to_dict(self) -> dict[str, Any]:
        return {
            "documentId": self.document_id,
            "file": self.file_path,
            "line": self.line,
            "property": self.property_path,
            "value": self.value,
            "text": f"[{self.file_path}] [{self.line if self.line > 0 else '?'}] {self.property_path}: {self.value}",
        }


@dataclass(slots=True)
class VisualEditorControl:
    id: str
    label: str
    category: str
    control: str
    value_type: str
    visual_types: list[str] = field(default_factory=lambda: ["*"])
    options: list[str] = field(default_factory=list)
    paths: list[list[str | int]] = field(default_factory=list)
    creates_missing_path: bool = False
    matching_count: int = 0
    visual_type_group: str = ""
    description: str = ""
    default_value: Any | None = None
    matches: list[VisualEditorPropertyMatch] = field(default_factory=list)
    group_path: list[str] = field(default_factory=list)
    selector_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "category": self.category,
            "control": self.control,
            "valueType": self.value_type,
            "visualTypes": list(self.visual_types),
            "options": list(self.options),
            "paths": [list(path) for path in self.paths],
            "createsMissingPath": self.creates_missing_path,
            "description": self.description,
            "defaultValue": self.default_value,
            "matches": [match.to_dict() for match in self.matches],
            "groupPath": list(self.group_path),
            "selectorId": self.selector_id,
        }
