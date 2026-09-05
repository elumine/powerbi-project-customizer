from __future__ import annotations

import json
import random
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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
    source_path: str = ""
    is_read_only: bool = False

    @classmethod
    def create(
        cls,
        display_name: str,
        rules: list[FilterRule],
        color: str | None = None,
        used_colors: set[str] | None = None,
    ) -> "ContentFilter":
        return cls(
            id=str(uuid.uuid4()),
            display_name=display_name,
            color=color or generate_filter_color(used_colors or set()),
            rules=rules,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ContentFilter":
        rules = [FilterRule.from_dict(rule) for rule in data.get("rules", []) if isinstance(rule, dict)]
        return cls(
            id=str(data.get("id") or uuid.uuid4()),
            display_name=str(data.get("displayName", "")).strip(),
            color=str(data.get("color") or generate_filter_color(set())),
            rules=rules,
            source_path=str(data.get("sourcePath", "")),
            is_read_only=bool(data.get("isReadOnly", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "displayName": self.display_name,
            "color": self.color,
            "rules": [rule.to_dict() for rule in self.rules],
        }


def generate_filter_color(used_colors: set[str]) -> str:
    available = [color for color in FILTER_COLORS if color not in used_colors]
    if available:
        return random.choice(available)
    return f"#{random.randint(0x355070, 0xE0FBFC):06x}"


class ContentFilterMatcher:
    @classmethod
    def matches_filter(cls, data: Any, content_filter: ContentFilter) -> bool:
        if not content_filter.rules:
            return False
        return all(cls.matches_rule(data, rule) for rule in content_filter.rules)

    @classmethod
    def matches_rule(cls, data: Any, rule: FilterRule) -> bool:
        key = cls._normalize_text(rule.key.strip())
        if key == "" or rule.operation not in FILTER_OPERATIONS:
            return False

        values = [cls._normalize_text(cls._value_to_text(value)) for value in cls._values_for_key(data, key)]
        if not values:
            return False

        rule_value = cls._normalize_text(rule.value)
        if rule.operation == "equals":
            return any(value == rule_value for value in values)
        if rule.operation == "includes":
            return any(rule_value in value for value in values)
        if rule.operation == "notEquals":
            return all(value != rule_value for value in values)
        if rule.operation == "notIncludes":
            return all(rule_value not in value for value in values)
        return False

    @classmethod
    def _values_for_key(cls, data: Any, normalized_key: str) -> list[Any]:
        matches: list[Any] = []
        if isinstance(data, dict):
            for key, value in data.items():
                if cls._normalize_text(str(key)) == normalized_key:
                    matches.append(value)
                matches.extend(cls._values_for_key(value, normalized_key))
        elif isinstance(data, list):
            for item in data:
                matches.extend(cls._values_for_key(item, normalized_key))
        return matches

    @staticmethod
    def _value_to_text(value: Any) -> str:
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, sort_keys=True)
        return str(value)

    @staticmethod
    def _normalize_text(value: str) -> str:
        return value.casefold()


class FilterStorage:
    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> list[ContentFilter]:
        if not self._path.exists():
            return []

        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        saved_filters = data.get("filters", []) if isinstance(data, dict) else []
        return [ContentFilter.from_dict(item) for item in saved_filters if isinstance(item, dict)]

    def save(self, filters: list[ContentFilter]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"filters": [content_filter.to_dict() for content_filter in filters if not content_filter.is_read_only]}
        self._path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")