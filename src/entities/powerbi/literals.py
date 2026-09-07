from __future__ import annotations

from typing import Any


def encode_powerbi_literal_string(value: str) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def decode_powerbi_literal_string(value: Any) -> str:
    text = str(value or "")
    stripped = text.strip()
    if len(stripped) >= 2 and stripped[0] == "'" and stripped[-1] == "'":
        return stripped[1:-1].replace("''", "'")
    if len(stripped) >= 2 and stripped[0] == '"' and stripped[-1] == '"':
        return stripped[1:-1]
    return stripped
