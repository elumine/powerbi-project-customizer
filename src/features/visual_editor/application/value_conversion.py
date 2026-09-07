from __future__ import annotations

import re
from typing import Any


class VisualValueConverter:
    """Converts QML raw control input into validated PBIR-compatible values."""

    @staticmethod
    def convert(value_type: str, raw_value: Any, options: list[str] | None = None) -> Any:
        if value_type in {"number", "percentage", "powerBiLiteralNumber", "integer"}:
            try:
                numeric = float(raw_value)
            except (TypeError, ValueError):
                numeric = 0
            if value_type == "percentage":
                numeric = float(max(0, min(100, numeric)))
            if value_type == "integer":
                return int(round(numeric))
            return int(numeric) if numeric.is_integer() else numeric
        if value_type == "boolean":
            if isinstance(raw_value, bool):
                return raw_value
            return str(raw_value).strip().casefold() in {"1", "true", "yes", "on"}
        if value_type == "hexColor":
            value = str(raw_value or "").strip()
            if re.fullmatch(r"[0-9A-Fa-f]{6}", value):
                return "#" + value.upper()
            if re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
                return value.upper()
            return "#000000"
        if value_type == "enum" and options:
            value = str(raw_value or "").strip()
            return value if value in options else options[0]
        return str(raw_value)
