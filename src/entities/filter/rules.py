from __future__ import annotations

import json
from typing import Any

from entities.filter.models import FILTER_OPERATIONS, ContentFilter, FilterRule


class ContentFilterMatcher:
    """Pure matching rules for persisted and runtime filters."""

    @classmethod
    def matches_filter(cls, data: Any, content_filter: ContentFilter) -> bool:
        return bool(content_filter.rules) and all(cls.matches_rule(data, rule) for rule in content_filter.rules)

    @classmethod
    def matches_rule(cls, data: Any, rule: FilterRule) -> bool:
        key = cls._normalize_text(rule.key.strip())
        if not key or rule.operation not in FILTER_OPERATIONS:
            return False
        values = [cls._normalize_text(cls._value_to_text(value)) for value in cls._values_for_key(data, key)]
        if not values:
            return False
        needle = cls._normalize_text(rule.value)
        if rule.operation == "equals":
            return any(value == needle for value in values)
        if rule.operation == "includes":
            return any(needle in value for value in values)
        if rule.operation == "notEquals":
            return all(value != needle for value in values)
        return all(needle not in value for value in values)

    @classmethod
    def _values_for_key(cls, data: Any, normalized_key: str) -> list[Any]:
        matches: list[Any] = []
        if isinstance(data, dict):
            for key, value in data.items():
                key_text = str(key)
                if cls._normalize_text(key_text) == normalized_key or cls._normalize_text(cls._flat_leaf_key(key_text)) == normalized_key:
                    matches.append(value)
                matches.extend(cls._values_for_key(value, normalized_key))
        elif isinstance(data, list):
            for item in data:
                matches.extend(cls._values_for_key(item, normalized_key))
        return matches

    @staticmethod
    def _flat_leaf_key(key: str) -> str:
        return key.rsplit(".", 1)[-1]

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
