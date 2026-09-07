from __future__ import annotations

import json
import random
import uuid
from dataclasses import dataclass, field
from typing import Any

from entities.powerbi.file_types import FILTER_TARGET_ALL, FILTER_TARGET_TYPES, normalize_filter_target


FILTER_OPERATIONS = ("equals", "includes", "notEquals", "notIncludes")
FILTER_COLORS = (
    "#4ec9b0",
    "#c586c0",
    "#dcdcaa",
    "#ce9178",
    "#9cdcfe",
    "#b5cea8",
    "#d7ba7d",
    "#569cd6",
)


def filter_value_to_text(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


@dataclass(slots=True)
class FilterRule:
    id: str
    key: str
    operation: str
    value: str

    @classmethod
    def create(cls, key: str = "", operation: str = "equals", value: str = "") -> "FilterRule":
        return cls(id=str(uuid.uuid4()), key=key, operation=operation, value=value)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FilterRule":
        operation = str(data.get("operation", "equals"))
        if operation not in FILTER_OPERATIONS:
            operation = "equals"
        return cls(
            id=str(data.get("id") or uuid.uuid4()),
            key=str(data.get("key", "")),
            operation=operation,
            value=filter_value_to_text(data.get("value", "")),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "key": self.key,
            "operation": self.operation,
            "value": self.value,
        }


@dataclass(slots=True)
class ContentFilter:
    id: str
    display_name: str
    color: str
    rules: list[FilterRule] = field(default_factory=list)
    target_json_file_type: str = FILTER_TARGET_ALL
    source_path: str = ""
    is_read_only: bool = False

    @classmethod
    def create(
        cls,
        display_name: str,
        rules: list[FilterRule],
        color: str | None = None,
        used_colors: set[str] | None = None,
        target_json_file_type: str = FILTER_TARGET_ALL,
    ) -> "ContentFilter":
        return cls(
            id=str(uuid.uuid4()),
            display_name=display_name,
            color=color or generate_filter_color(used_colors or set()),
            rules=rules,
            target_json_file_type=normalize_filter_target(target_json_file_type),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContentFilter":
        rules = [FilterRule.from_dict(rule) for rule in data.get("rules", []) if isinstance(rule, dict)]
        return cls(
            id=str(data.get("id") or uuid.uuid4()),
            display_name=str(data.get("displayName", "")).strip(),
            color=str(data.get("color") or generate_filter_color(set())),
            rules=rules,
            target_json_file_type=normalize_filter_target(str(data.get("targetJsonFileType", FILTER_TARGET_ALL))),
            source_path=str(data.get("sourcePath", "")),
            is_read_only=bool(data.get("isReadOnly", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "displayName": self.display_name,
            "targetJsonFileType": self.target_json_file_type,
            "color": self.color,
            "rules": [rule.to_dict() for rule in self.rules],
        }


def generate_filter_color(used_colors: set[str]) -> str:
    available = [color for color in FILTER_COLORS if color not in used_colors]
    if available:
        return random.choice(available)
    return f"#{random.randint(0x355070, 0xE0FBFC):06x}"
