from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core.content_filter import FILTER_OPERATIONS, ContentFilter, FilterRule, filter_value_to_text
from app.core.stable_color import stable_color, stable_id


@dataclass(slots=True)
class ImportedFilterLoadResult:
    filters: list[ContentFilter] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class ImportedFilterRepository:
    def __init__(self, content_root: Path) -> None:
        self._content_root = content_root

    @property
    def filters_path(self) -> Path:
        return self._content_root / "filters"

    def list_filters(self) -> ImportedFilterLoadResult:
        result = ImportedFilterLoadResult()
        folder = self.filters_path
        if not folder.exists() or not folder.is_dir():
            return result

        for path in sorted(folder.rglob("*.json"), key=lambda item: str(item).casefold()):
            content_filter, errors = self._load_file(path)
            if errors:
                result.errors.extend(errors)
                continue
            if content_filter is not None:
                result.filters.append(content_filter)
        return result

    def _load_file(self, path: Path) -> tuple[ContentFilter | None, list[str]]:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as error:
            return None, [f"{path.name}: {error}"]

        if not isinstance(data, dict):
            return None, [f"{path.name}: filter file must contain a JSON object."]

        errors: list[str] = []
        rules_data = data.get("rules")
        if not isinstance(rules_data, list):
            return None, [f"{path.name}: rules must be an array."]
        if not rules_data:
            errors.append(f"{path.name}: at least one rule is required.")

        filter_id = self._filter_id(path, data)
        rules: list[FilterRule] = []
        for index, rule_data in enumerate(rules_data):
            rule, rule_errors = self._rule_from_data(filter_id, index, rule_data)
            if rule is not None:
                rules.append(rule)
            errors.extend(f"{path.name}: {message}" for message in rule_errors)

        if errors:
            return None, errors

        display_name = str(data.get("displayName") or path.stem).strip()
        if not display_name:
            return None, [f"{path.name}: displayName is required."]

        color = str(data.get("color") or stable_color(f"filter:{filter_id}"))
        return (
            ContentFilter(
                id=filter_id,
                display_name=display_name,
                color=color,
                rules=rules,
                source_path=str(path),
                is_read_only=True,
            ),
            [],
        )

    def _rule_from_data(self, filter_id: str, index: int, data: Any) -> tuple[FilterRule | None, list[str]]:
        label = f"rule {index + 1}"
        if not isinstance(data, dict):
            return None, [f"{label} must be an object."]

        errors: list[str] = []
        key = str(data.get("key", "")).strip()
        operation = str(data.get("operation", "")).strip()
        if not key:
            errors.append(f"{label}: key is required.")
        if operation not in FILTER_OPERATIONS:
            errors.append(f"{label}: operation must be one of {', '.join(FILTER_OPERATIONS)}.")
        if "value" not in data:
            errors.append(f"{label}: value is required.")

        if errors:
            return None, errors

        return (
            FilterRule(
                id=str(data.get("id") or f"{filter_id}.rule.{index + 1}"),
                key=key,
                operation=operation,
                value=filter_value_to_text(data.get("value", "")),
            ),
            [],
        )

    def _filter_id(self, path: Path, data: dict[str, Any]) -> str:
        explicit_id = str(data.get("id", "")).strip()
        if explicit_id:
            return explicit_id
        return stable_id("filter", self._relative_seed(path))

    def _relative_seed(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self._content_root.resolve())).replace("\\", "/")
        except ValueError:
            return str(path.resolve())
