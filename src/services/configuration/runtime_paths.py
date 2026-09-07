from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RuntimePaths:
    """Application configuration paths independent from Qt presentation objects."""

    filter_storage_path: Path

    @classmethod
    def discover(cls) -> "RuntimePaths":
        override = os.environ.get("JSON_MULTI_EDITOR_FILTERS_PATH")
        if override:
            return cls(Path(override).expanduser().resolve())
        appdata = os.environ.get("APPDATA")
        if appdata:
            return cls(Path(appdata) / "JSON Multi Editor" / "filters.json")
        return cls(Path.home() / ".json_multi_editor" / "filters.json")
