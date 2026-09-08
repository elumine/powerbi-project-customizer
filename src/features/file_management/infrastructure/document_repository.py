from __future__ import annotations

from pathlib import Path

from entities.document.flattening import flatten_json_text, unflatten_json_text
from entities.document.models import JsonDocument
from features.file_management.application.ports import DocumentRepositoryError
from infrastructure.filesystem.file_service import FileService, FileServiceError


class FileRepository:
    """Persistence boundary for JSON documents."""

    def load_document(self, path: str | Path) -> JsonDocument:
        file_path = Path(path).expanduser().resolve()
        try:
            raw_text = FileService.read_text(file_path)
        except FileServiceError as error:
            raise DocumentRepositoryError(str(error)) from error
        return JsonDocument(path=file_path, text=flatten_json_text(raw_text), raw_text=raw_text, file_type=None)

    def save_document(self, document: JsonDocument) -> None:
        try:
            hierarchical_text = unflatten_json_text(document.text)
            FileService.write_text(document.path, hierarchical_text)
        except FileServiceError as error:
            raise DocumentRepositoryError(str(error)) from error
        except (TypeError, ValueError) as error:
            raise DocumentRepositoryError(f"Cannot convert flat JSON before save: {error}") from error
        document.raw_text = hierarchical_text
