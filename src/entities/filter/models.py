from __future__ import annotations

import json
import random
import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from entities.powerbi.file_types import FILTER_TARGET_ALL, FILTER_TARGET_TYPES, normalize_filter_target


FILTER_OPERATIONS = ("equals", "includes", "notEquals", "notIncludes")
# Dynamic filter-chip palette. Kept in the entity layer so persisted filters
# remain framework-independent while matching the dashboard theme variation set.
FILTER_COLORS = (
    "#42c6b4",
    "#a78bfa",
    "#f7b733",
    "#ff7b72",
    "#52b6ff",
    "#ff8f66",
    "#59d2b6",
    "#b99aff",
)
FILTER_COLOR_FALLBACK = "#52b6ff"
_HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


def normalize_filter_color(value: str, fallback: str = FILTER_COLOR_FALLBACK) -> str:
    """Accept only safe hex colors before they cross into QML presentation."""
    candidate = str(value or "").strip()
    if _HEX_COLOR.fullmatch(candidate):
        return candidate.lower()
    return fallback


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
            color=normalize_filter_color(color or generate_filter_color(used_colors or set())),
            rules=rules,
            target_json_file_type=normalize_filter_target(target_json_file_type),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContentFilter":
        rules = [FilterRule.from_dict(rule) for rule in data.get("rules", []) if isinstance(rule, dict)]
        return cls(
            id=str(data.get("id") or uuid.uuid4()),
            display_name=str(data.get("displayName", "")).strip(),
            color=normalize_filter_color(str(data.get("color") or generate_filter_color(set()))),
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
    # Reuse a named dashboard chip color rather than emit an arbitrary dark value.
    return random.choice(FILTER_COLORS)
