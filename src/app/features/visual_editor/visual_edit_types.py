from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


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
        }
