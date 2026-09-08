from __future__ import annotations

from collections import OrderedDict
import re
from typing import Any


class FlatJsonCollisionError(ValueError):
    """Raised when two hierarchical paths resolve to the same flat key."""


def flatten_json_text(text: str, indent: int = 2) -> str:
    import json

    data = json.loads(text)
    return json.dumps(flatten_json(data), ensure_ascii=False, indent=indent)


def unflatten_json_text(text: str, indent: int = 2) -> str:
    import json

    data = json.loads(text)
    return json.dumps(unflatten_json(data), ensure_ascii=False, indent=indent)


def unflatten_json(data: Any) -> Any:
    """Reconstruct hierarchical JSON from canonical dotted-key JSON."""
    if not isinstance(data, dict):
        return data
    if "" in data and len(data) == 1:
        return data[""]

    root: Any = [] if any(_parse_flat_key(key) and isinstance(_parse_flat_key(key)[0], int) for key in data) else {}
    for raw_key, value in data.items():
        parts = _parse_flat_key(str(raw_key))
        if not parts:
            if raw_key == "":
                root = value
                continue
            raise FlatJsonCollisionError(f"Invalid flat JSON key '{raw_key}'.")
        root = _assign_path(root, parts, value, str(raw_key))
    return root


def _parse_flat_key(key: str) -> list[str | int]:
    parts: list[str | int] = []
    buffer: list[str] = []
    escaped = False

    def flush() -> None:
        if buffer or not parts:
            token = "".join(buffer)
            match = re.fullmatch(r"\[(\d+)\]", token)
            parts.append(int(match.group(1)) if match else token)
            buffer.clear()

    for character in key:
        if escaped:
            buffer.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == ".":
            flush()
        else:
            buffer.append(character)
    if escaped:
        buffer.append("\\")
    flush()
    return parts


def _assign_path(root: Any, parts: list[str | int], value: Any, raw_key: str) -> Any:
    first = parts[0]
    if isinstance(first, int):
        if not isinstance(root, list):
            root = []
    elif not isinstance(root, dict):
        root = {}

    current = root
    for index, part in enumerate(parts):
        last = index == len(parts) - 1
        next_part = None if last else parts[index + 1]
        if isinstance(part, int):
            if not isinstance(current, list):
                raise FlatJsonCollisionError(f"Flat JSON key collision at '{raw_key}'.")
            while len(current) <= part:
                current.append([] if isinstance(next_part, int) else {})
            if last:
                if current[part] not in ([], {}) and current[part] != value:
                    raise FlatJsonCollisionError(f"Flat JSON key collision at '{raw_key}'.")
                current[part] = value
            else:
                current = current[part]
        else:
            if not isinstance(current, dict):
                raise FlatJsonCollisionError(f"Flat JSON key collision at '{raw_key}'.")
            if last:
                if part in current and current[part] != value:
                    raise FlatJsonCollisionError(f"Flat JSON key collision at '{raw_key}'.")
                current[part] = value
            else:
                if part not in current:
                    current[part] = [] if isinstance(next_part, int) else {}
                current = current[part]
    return root


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
    return value.replace("\\", "\\\\").replace(".", "\\.").replace("[", "\\[").replace("]", "\\]")
