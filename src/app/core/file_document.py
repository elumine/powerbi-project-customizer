from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core.display_name import display_name_from_json_text


@dataclass(slots=True)
class JsonDocument:
    path: Path
    text: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    original_text: str | None = None
    parsed_json: Any | None = None
    json_error: str = ""
    is_active: bool = True
    active_filter_color: str = ""
    match_count: int = 0
    match_previews: list[dict[str, str | int]] = field(default_factory=list)
    highlighted_html: str = ""
    display_name: str = ""

    def __post_init__(self) -> None:
        self.path = Path(self.path).resolve()
        if self.original_text is None:
            self.original_text = self.text
        self.validate()
        self.refresh_display_name()

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
    def is_valid_json(self) -> bool:
        return self.json_error == ""

    def set_text(self, text: str) -> None:
        self.text = text
        self.validate()
        self.refresh_display_name()

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

    def refresh_display_name(self) -> None:
        self.display_name = display_name_from_json_text(self.text, self.path.name)

    def formatted_text(self, indent: int = 2) -> str:
        data = json.loads(self.text)
        return json.dumps(data, ensure_ascii=False, indent=indent)


