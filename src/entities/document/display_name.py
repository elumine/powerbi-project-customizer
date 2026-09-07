from __future__ import annotations

import json
from collections import deque
from typing import Any

DISPLAY_NAME_KEYS = ("name", "Name", "Title", "title", "displayName")


def display_name_from_json_text(text: str, fallback: str) -> str:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return fallback

    value = _find_first_name_value(data)
    if value is None:
        return fallback

    display_name = str(value).strip()
    return display_name if display_name else fallback


def _find_first_name_value(data: Any) -> Any | None:
    queue: deque[Any] = deque([data])
    while queue:
        current = queue.popleft()
        if isinstance(current, dict):
            for key in DISPLAY_NAME_KEYS:
                value = current.get(key)
                if isinstance(value, (str, int, float)) and str(value).strip():
                    return value
            for key, value in current.items():
                leaf_key = str(key).rsplit(".", 1)[-1]
                if leaf_key in DISPLAY_NAME_KEYS and isinstance(value, (str, int, float)) and str(value).strip():
                    return value
            queue.extend(current.values())
        elif isinstance(current, list):
            queue.extend(current)

    return None

