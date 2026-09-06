from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.core.json_file_type import JsonFileType


SUPPORTED_POWERBI_FILE_NAMES = {"page.json", "visual.json"}
_PROJECT_ROOT_NAMES = {"definition", "definitions"}


def classify_json_file(path: Path, data: Any | None = None) -> JsonFileType | None:
    file_name = path.name.casefold()
    if file_name == "page.json":
        return JsonFileType.PAGE
    if file_name == "visual.json":
        return JsonFileType.VISUAL

    if isinstance(data, dict):
        visual = data.get("visual")
        if isinstance(visual, dict) or "visualType" in data or "visualGroup" in data:
            return JsonFileType.VISUAL
        if "displayName" in data and ("height" in data or "width" in data or "displayOption" in data) and "visual" not in data:
            return JsonFileType.PAGE

    return None


def schema_url_from_data(data: Any) -> str:
    if isinstance(data, dict):
        value = data.get("$schema", "")
        return str(value) if value is not None else ""
    return ""


def pbir_name_from_data(data: Any) -> str:
    if isinstance(data, dict):
        value = data.get("name", "")
        return str(value).strip() if value is not None else ""
    return ""


def visual_type_from_data(data: Any) -> str:
    if not isinstance(data, dict):
        return ""
    visual = data.get("visual")
    if isinstance(visual, dict):
        value = visual.get("visualType", "")
        if value is not None and str(value).strip():
            return str(value).strip()
    value = data.get("visualType", "")
    return str(value).strip() if value is not None else ""


def display_name_for_document(path: Path, data: Any, file_type: JsonFileType | None, fallback: str) -> tuple[str, str]:
    if file_type == JsonFileType.PAGE:
        if isinstance(data, dict):
            for key in ("displayName", "name"):
                value = data.get(key)
                if value is not None and str(value).strip():
                    return str(value).strip(), key
        if path.parent.name:
            return path.parent.name, "folder"
        return fallback, "fallback"

    if file_type == JsonFileType.VISUAL:
        title = _visual_title(data)
        if title:
            return title, "visualTitle"
        visual_type = visual_type_from_data(data)
        if visual_type:
            return visual_type, "visualType"
        if isinstance(data, dict):
            value = data.get("name")
            if value is not None and str(value).strip():
                return str(value).strip(), "name"
        if path.parent.name:
            return path.parent.name, "folder"
        return fallback, "fallback"

    if isinstance(data, dict):
        for key in ("name", "Name", "Title", "title", "displayName"):
            value = data.get(key)
            if value is not None and str(value).strip():
                return str(value).strip(), key
    return fallback, "fallback"


def infer_project_root(path: Path) -> Path | None:
    for parent in path.parents:
        if parent.name.casefold() in _PROJECT_ROOT_NAMES:
            return parent
        if parent.name.casefold().endswith(".report"):
            return parent
    return None


def relative_path_for_display(path: Path, project_root: Path | None = None) -> str:
    root = project_root or infer_project_root(path)
    if root is not None:
        try:
            return str(path.relative_to(root)).replace("\\", "/")
        except ValueError:
            pass
    return path.name


def load_json_for_metadata(text: str) -> Any | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


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


def _visual_title(data: Any) -> str:
    # First priority from PBIR visualContainer schema.
    value = _get_path(data, ["visual", "visualContainerObjects", "title", 0, "properties", "text", "expr", "Literal", "Value"])
    title = decode_powerbi_literal_string(value)
    if title:
        return title

    # Compatibility with older app fixtures and theme-like JSON examples.
    if isinstance(data, dict):
        for key in ("Title", "title"):
            value = data.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()
    return ""


def _get_path(data: Any, path: list[str | int]) -> Any:
    current = data
    for part in path:
        if isinstance(part, int):
            if not isinstance(current, list) or not 0 <= part < len(current):
                return None
            current = current[part]
            continue
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current
