from __future__ import annotations

from pathlib import Path

from app.core.file_document import JsonDocument, PageFile, VisualFile
from app.core.file_service import FileService
from app.core.json_file_type import JsonFileType
from app.core.powerbi_metadata import classify_json_file, load_json_for_metadata


class FileRepository:
    """Persistence boundary for JSON documents."""

    def load_document(self, path: str | Path) -> JsonDocument:
        file_path = Path(path).expanduser().resolve()
        text = FileService.read_text(file_path)
        data = load_json_for_metadata(text)
        file_type = classify_json_file(file_path, data)
        document_type: type[JsonDocument]
        if file_type == JsonFileType.PAGE:
            document_type = PageFile
        elif file_type == JsonFileType.VISUAL:
            document_type = VisualFile
        else:
            document_type = JsonDocument
        return document_type(path=file_path, text=text, file_type=file_type)

    def save_document(self, document: JsonDocument) -> None:
        FileService.write_text(document.path, document.text)
