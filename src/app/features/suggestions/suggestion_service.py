from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from app.core.file_document import JsonDocument
from app.core.stable_color import stable_color, stable_id


@dataclass(slots=True)
class SuggestionOccurrence:
    file_id: str
    file_display_name: str
    json_path: str
    occurrence_type: str
    key: str = ""
    value_preview: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "fileId": self.file_id,
            "fileDisplayName": self.file_display_name,
            "jsonPath": self.json_path,
            "occurrenceType": self.occurrence_type,
            "key": self.key,
            "valuePreview": self.value_preview,
        }


@dataclass(slots=True)
class SuggestionItem:
    id: str
    type: str
    duplication_value: str
    normalized_value: str
    color: str
    occurrences: list[SuggestionOccurrence] = field(default_factory=list)

    @property
    def duplication_count(self) -> int:
        return len(self.occurrences)


@dataclass(slots=True)
class _SuggestionBucket:
    display_value: str
    occurrences: list[SuggestionOccurrence] = field(default_factory=list)


class SuggestionService:
    _IDENTIFIER = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")

    @classmethod
    def analyze(cls, documents: Iterable[JsonDocument]) -> tuple[list[SuggestionItem], list[SuggestionItem]]:
        key_buckets: dict[str, _SuggestionBucket] = {}
        value_buckets: dict[str, _SuggestionBucket] = {}

        for document in documents:
            if not document.is_valid_json:
                continue
            cls._traverse(document.parsed_json, "root", document, "", key_buckets, value_buckets)

        return cls._items("key", key_buckets), cls._items("value", value_buckets)

    @classmethod
    def _traverse(
        cls,
        value: Any,
        path: str,
        document: JsonDocument,
        parent_key: str,
        key_buckets: dict[str, _SuggestionBucket],
        value_buckets: dict[str, _SuggestionBucket],
    ) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                key_text = str(key).strip()
                property_path = cls._append_key(path, str(key))
                if key_text:
                    normalized_key = key_text.casefold()
                    bucket = key_buckets.setdefault(normalized_key, _SuggestionBucket(key_text))
                    bucket.occurrences.append(
                        SuggestionOccurrence(
                            file_id=document.id,
                            file_display_name=document.name,
                            json_path=property_path,
                            occurrence_type="key",
                            key=key_text,
                            value_preview=cls._preview(child),
                        )
                    )
                cls._traverse(child, property_path, document, key_text, key_buckets, value_buckets)
            return

        if isinstance(value, list):
            for index, child in enumerate(value):
                cls._traverse(child, f"{path}[{index}]", document, parent_key, key_buckets, value_buckets)
            return

        if cls._is_primitive(value):
            display_value, normalized_value = cls._primitive_text(value)
            bucket = value_buckets.setdefault(normalized_value, _SuggestionBucket(display_value))
            bucket.occurrences.append(
                SuggestionOccurrence(
                    file_id=document.id,
                    file_display_name=document.name,
                    json_path=path,
                    occurrence_type="value",
                    key=parent_key,
                    value_preview=display_value,
                )
            )

    @classmethod
    def _items(cls, suggestion_type: str, buckets: dict[str, _SuggestionBucket]) -> list[SuggestionItem]:
        items = [
            SuggestionItem(
                id=stable_id(f"suggestion.{suggestion_type}", normalized_value),
                type=suggestion_type,
                duplication_value=bucket.display_value,
                normalized_value=normalized_value,
                color=stable_color(f"{suggestion_type}:{normalized_value}"),
                occurrences=bucket.occurrences,
            )
            for normalized_value, bucket in buckets.items()
            if len(bucket.occurrences) > 1
        ]
        return sorted(items, key=lambda item: (-item.duplication_count, item.duplication_value.casefold()))

    @classmethod
    def _append_key(cls, path: str, key: str) -> str:
        if cls._IDENTIFIER.match(key):
            return f"{path}.{key}"
        return f"{path}[{json.dumps(key, ensure_ascii=False)}]"

    @staticmethod
    def _is_primitive(value: Any) -> bool:
        return value is None or isinstance(value, (str, int, float, bool))

    @staticmethod
    def _primitive_text(value: Any) -> tuple[str, str]:
        if value is None:
            return "null", "null"
        if isinstance(value, bool):
            text = "true" if value else "false"
            return text, text
        if isinstance(value, str):
            return value, value.casefold()
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        return text, text

    @classmethod
    def _preview(cls, value: Any, limit: int = 88) -> str:
        if cls._is_primitive(value):
            preview, _normalized = cls._primitive_text(value)
        else:
            preview = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if len(preview) <= limit:
            return preview
        return preview[: limit - 3] + "..."
