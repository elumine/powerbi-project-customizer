from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class FileSnapshot:
    document_id: str
    path: str
    before_text: str
    after_text: str
    before_original_text: str
    after_original_text: str
    before_dirty: bool
    after_dirty: bool


@dataclass(slots=True)
class HistoryEntry:
    index: int
    timestamp: datetime
    operation_type: str
    display_name: str
    metadata: dict[str, Any] = field(default_factory=dict)
    file_changes: list[FileSnapshot] = field(default_factory=list)
    reversible: bool = True

    @property
    def time_text(self) -> str:
        return self.timestamp.strftime("%H:%M:%S")

    @property
    def metadata_text(self) -> str:
        parts: list[str] = []
        for key, value in self.metadata.items():
            if value in (None, "", [], {}):
                continue
            label = key.replace("_", " ")
            parts.append(f"{label}: {value}")
        return ", ".join(parts)
