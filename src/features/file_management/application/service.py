from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from features.file_management.application.ports import DocumentRepository, DocumentRepositoryError
from services.documents.ports import MutableDocuments


@dataclass(slots=True)
class FileAddResult:
    added: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    first_added_document_id: str = ""

    @property
    def has_changes(self) -> bool:
        return self.added > 0


@dataclass(slots=True)
class FileSaveResult:
    saved: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return self.saved > 0 and not self.errors


class FileManagementService:
    """Qt-free document loading, editing, formatting, and persistence commands."""

    def __init__(self, documents: MutableDocuments, repository: DocumentRepository) -> None:
        self._documents = documents
        self._repository = repository

    def add_paths(self, paths: list[Path]) -> FileAddResult:
        existing_paths = self._documents.paths()
        result = FileAddResult()
        for path in paths:
            file_path = path.expanduser().resolve()
            if file_path in existing_paths or not file_path.is_file() or file_path.suffix.casefold() != ".json":
                result.skipped += 1
                continue
            try:
                document = self._repository.load_document(file_path)
                self._documents.add_document(document)
            except (DocumentRepositoryError, ValueError, json.JSONDecodeError) as error:
                result.errors.append(str(error))
                continue
            existing_paths.add(document.path)
            if not result.first_added_document_id:
                result.first_added_document_id = document.id
            result.added += 1
        return result

    def remove_document(self, document_id: str) -> bool:
        return self._documents.remove_document_by_id(document_id) is not None

    def update_text(self, document_id: str, text: str) -> bool:
        return not self._documents.set_document_text_by_id(document_id, text).is_empty

    def format_document(self, document_id: str) -> bool:
        document = self._documents.document_by_id(document_id)
        if document is None:
            return False
        try:
            formatted = document.formatted_text(indent=2)
        except (TypeError, ValueError, json.JSONDecodeError):
            return False
        return self.update_text(document_id, formatted)

    def save_document(self, document_id: str) -> FileSaveResult:
        document = self._documents.document_by_id(document_id)
        if document is None:
            return FileSaveResult(errors=["No file selected."])
        if not document.is_dirty:
            return FileSaveResult()
        try:
            self._repository.save_document(document)
        except DocumentRepositoryError as error:
            return FileSaveResult(errors=[str(error)])
        self._documents.mark_saved_by_id(document_id)
        return FileSaveResult(saved=1)

    def save_all(self) -> FileSaveResult:
        result = FileSaveResult()
        for document in self._documents.documents():
            if not document.is_dirty:
                continue
            saved = self.save_document(document.id)
            result.saved += saved.saved
            result.errors.extend(saved.errors)
        return result
