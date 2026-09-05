from __future__ import annotations

from pathlib import Path

from app.core.file_document import JsonDocument
from app.core.file_service import FileService


class FileRepository:
    """Persistence boundary for JSON documents."""

    def load_document(self, path: str | Path) -> JsonDocument:
        file_path = Path(path).expanduser().resolve()
        return JsonDocument(path=file_path, text=FileService.read_text(file_path))

    def save_document(self, document: JsonDocument) -> None:
        FileService.write_text(document.path, document.text)
