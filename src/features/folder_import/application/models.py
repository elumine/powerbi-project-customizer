from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class FolderScanItem:
    path: Path
    display_name: str
    relative_path: str
    file_type: str = "Json"
