from __future__ import annotations

from enum import Enum


class JsonFileType(str, Enum):
    PAGE = "Page"
    VISUAL = "Visual"


FILTER_TARGET_ALL = "All"
FILTER_TARGET_TYPES = (FILTER_TARGET_ALL, JsonFileType.PAGE.value, JsonFileType.VISUAL.value)


def normalize_filter_target(value: str | None, default: str = FILTER_TARGET_ALL) -> str:
    text = str(value or default).strip()
    for option in FILTER_TARGET_TYPES:
        if text.casefold() == option.casefold():
            return option
    return default


def file_type_to_text(value: JsonFileType | str | None) -> str:
    if isinstance(value, JsonFileType):
        return value.value
    text = str(value or "").strip()
    return text if text else "Json"
