from __future__ import annotations

from pathlib import Path
from typing import Protocol

from entities.document.models import JsonDocument


class DocumentRepositoryError(Exception):
    """Expected document persistence failure presented by the use-case layer."""


class DocumentRepository(Protocol):
    def load_document(self, path: str | Path) -> JsonDocument: ...
    def save_document(self, document: JsonDocument) -> None: ...
