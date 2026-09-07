from __future__ import annotations

import json
from collections import OrderedDict
from typing import Any


class FlatJsonCollisionError(ValueError):
    """Raised when two hierarchical paths resolve to the same flat key."""


def flatten_json_text(text: str, indent: int = 2) -> str:
    data = json.loads(text)
    flat = flatten_json(data)
    return json.dumps(flat, ensure_ascii=False, indent=indent)


def flatten_json(data: Any) -> dict[str, Any]:
    flat: OrderedDict[str, Any] = OrderedDict()
    _flatten(data, [], flat)
    return dict(flat)


def _flatten(value: Any, path: list[str], flat: OrderedDict[str, Any]) -> None:
    if isinstance(value, dict) and value:
        for key, child in value.items():
            _flatten(child, path + [_escape_key(str(key))], flat)
        return

    if isinstance(value, list) and value:
        for index, child in enumerate(value):
            _flatten(child, path + [f"[{index}]"], flat)
        return

    key = ".".join(path)
    if key in flat:
        raise FlatJsonCollisionError(f"Flat JSON key collision at '{key}'.")
    flat[key] = value


def _escape_key(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(".", "\\.")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )
