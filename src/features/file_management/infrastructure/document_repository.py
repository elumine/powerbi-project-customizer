from __future__ import annotations

from pathlib import Path

from entities.document.models import JsonDocument
from features.file_management.application.ports import DocumentRepositoryError
from infrastructure.filesystem.file_service import FileService, FileServiceError
from services.documents.flattening import flatten_json_text


class FileRepository:
    """Persistence boundary for JSON documents."""

    def load_document(self, path: str | Path) -> JsonDocument:
        file_path = Path(path).expanduser().resolve()
        try:
            text = FileService.read_text(file_path)
        except FileServiceError as error:
            raise DocumentRepositoryError(str(error)) from error
        return JsonDocument(path=file_path, text=flatten_json_text(text), file_type=None)

    def save_document(self, document: JsonDocument) -> None:
        try:
            FileService.write_text(document.path, document.text)
        except FileServiceError as error:
            raise DocumentRepositoryError(str(error)) from error
