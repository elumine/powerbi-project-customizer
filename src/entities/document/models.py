from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from entities.document.display_name import display_name_from_json_text
from entities.powerbi.file_types import JsonFileType
from entities.document.flattening import flatten_json
from entities.powerbi.metadata import (
    classify_json_file,
    display_name_for_document,
    infer_project_root,
    pbir_name_from_data,
    relative_path_for_display,
    schema_url_from_data,
    visual_type_from_data,
)


@dataclass(slots=True)
class JsonDocument:
    path: Path
    text: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_text: str | None = None
    # Immutable session baseline used by the Changes panel. ``original_text``
    # remains the save/dirty baseline and may advance after a save.
    initial_text: str | None = None
    # Unmodified file bytes decoded at import time; shown by the raw editor mode.
    raw_text: str | None = None
    parsed_json: Any | None = None
    json_error: str = ""
    is_active: bool = True
    visible_in_tree: bool = True
    active_filter_color: str = ""
    match_count: int = 0
    match_previews: list[dict[str, str | int]] = field(default_factory=list)
    highlighted_html: str = ""
    display_name: str = ""
    file_type: JsonFileType | None = None
    project_root: Path | None = None
    relative_path: str = ""
    schema_url: str = ""
    pbir_name: str = ""
    parent_page_id: str = ""
    display_name_source: str = ""
    visual_type: str = ""
    visual_ids: list[str] = field(default_factory=list)
    collapsed: bool = False

    def __post_init__(self) -> None:
        self.path = Path(self.path).resolve()
        imported_text = self.text
        if self.raw_text is None:
            self.raw_text = imported_text
        self.text = self._canonical_flat_text(imported_text)
        if self.original_text is None:
            self.original_text = self.text
        else:
            self.original_text = self._canonical_flat_text(self.original_text)
        if self.initial_text is None:
            self.initial_text = self.text
        else:
            self.initial_text = self._canonical_flat_text(self.initial_text)
        self.project_root = self.project_root.resolve() if self.project_root is not None else infer_project_root(self.path)
        self.validate()
        self.refresh_metadata()

    @staticmethod
    def _canonical_flat_text(text: str) -> str:
        """Normalize hierarchical JSON at the document boundary.

        ``raw_text`` is retained solely for the read-only preview. Every
        mutable representation, baseline, filter, search, and macro operation
        receives the flat key/value document instead.
        """
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return text
        is_flat = isinstance(data, dict) and all(
            not isinstance(value, (dict, list))
            or "." in str(key)
            or "[" in str(key)
            for key, value in data.items()
        )
        is_hierarchical = isinstance(data, list) or (
            isinstance(data, dict)
            and not is_flat
            and any(isinstance(value, (dict, list)) for value in data.values())
        )
        if not is_hierarchical:
            return text
        return json.dumps(flatten_json(data), ensure_ascii=False, indent=2)

    @property
    def file_name(self) -> str:
        return self.path.name

    @property
    def name(self) -> str:
        return self.display_name or self.path.name

    @property
    def directory(self) -> str:
        return str(self.path.parent)

    @property
    def is_dirty(self) -> bool:
        return self.text != self.original_text

    @property
    def has_changes_from_initial(self) -> bool:
        return self.text != (self.initial_text or "")

    @property
    def is_valid_json(self) -> bool:
        return self.json_error == ""

    @property
    def file_type_text(self) -> str:
        return self.file_type.value if isinstance(self.file_type, JsonFileType) else "Json"

    def set_text(self, text: str) -> None:
        self.text = self._canonical_flat_text(text)
        self.validate()
        self.refresh_metadata()

    def mark_saved(self) -> None:
        self.original_text = self.text

    def validate(self) -> bool:
        try:
            self.parsed_json = json.loads(self.text)
        except json.JSONDecodeError as error:
            self.parsed_json = None
            self.json_error = f"Line {error.lineno}, column {error.colno}: {error.msg}"
            return False

        self.json_error = ""
        return True

    def refresh_metadata(self) -> None:
        data = self.parsed_json
        classified = classify_json_file(self.path, data)
        if classified is not None:
            self.file_type = classified

        self.schema_url = schema_url_from_data(data)
        self.pbir_name = pbir_name_from_data(data)
        self.visual_type = visual_type_from_data(data)
        if self.project_root is None:
            self.project_root = infer_project_root(self.path)
        self.relative_path = relative_path_for_display(self.path, self.project_root)
        self.refresh_display_name()

    def refresh_display_name(self) -> None:
        if self.parsed_json is not None:
            self.display_name, self.display_name_source = display_name_for_document(
                self.path,
                self.parsed_json,
                self.file_type,
                self.path.name,
            )
            return
        self.display_name = display_name_from_json_text(self.text, self.path.name)
        self.display_name_source = "fallback"

    def formatted_text(self, indent: int = 2) -> str:
        data = json.loads(self.text)
        return json.dumps(data, ensure_ascii=False, indent=indent)


@dataclass(slots=True)
class PageFile(JsonDocument):
    pass


@dataclass(slots=True)
class VisualFile(JsonDocument):
    pass
