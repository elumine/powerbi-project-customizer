from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SearchQuery:
    needle: str = ""
    replacement: str = ""
    case_sensitive: bool = False

    @property
    def is_empty(self) -> bool:
        return self.needle == ""
