from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from app.core.file_service import FileServiceError
from app.features.file_management.file_repository import FileRepository
from app.ui.file_list_model import FileListModel


@dataclass(slots=True)
class FileAddResult:
    added: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    first_added_index: int = -1

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
    """Application use cases for loading, editing, formatting, and saving files."""

    def __init__(self, file_model: FileListModel, repository: FileRepository) -> None:
        self._files = file_model
        self._repository = repository

    def add_paths(self, paths: list[Path]) -> FileAddResult:
        existing_paths = self._files.paths()
        result = FileAddResult()

        for path in paths:
            file_path = path.expanduser().resolve()
            if file_path in existing_paths:
                result.skipped += 1
                continue
            if not file_path.is_file():
                result.skipped += 1
                continue
            if file_path.suffix.casefold() != ".json":
                result.skipped += 1
                continue

            try:
                document = self._repository.load_document(file_path)
            except (FileServiceError, ValueError, json.JSONDecodeError) as error:
                result.errors.append(str(error))
                continue

            row = self._files.add_document(document)
            existing_paths.add(document.path)
            if result.first_added_index < 0:
                result.first_added_index = row
            result.added += 1

        return result

    def remove_file(self, row: int) -> bool:
        return self._files.remove_document(row) is not None

    def update_text(self, row: int, text: str) -> bool:
        return self._files.set_document_text(row, text)

    def format_file(self, row: int) -> bool:
        document = self._files.document_at(row)
        if document is None:
            return False
        try:
            formatted = document.formatted_text(indent=2)
        except (TypeError, ValueError, json.JSONDecodeError):
            return False
        return self._files.set_document_text(row, formatted)

    def save_file(self, row: int) -> FileSaveResult:
        document = self._files.document_at(row)
        if document is None:
            return FileSaveResult(errors=["No file selected."])
        if not document.is_dirty:
            return FileSaveResult()

        try:
            self._repository.save_document(document)
        except FileServiceError as error:
            return FileSaveResult(errors=[str(error)])

        self._files.mark_saved(row)
        return FileSaveResult(saved=1)

    def save_all(self) -> FileSaveResult:
        result = FileSaveResult()
        for row, document in enumerate(self._files.documents()):
            if not document.is_dirty:
                continue
            try:
                self._repository.save_document(document)
            except (FileServiceError, ValueError, json.JSONDecodeError) as error:
                result.errors.append(str(error))
                continue
            self._files.mark_saved(row)
            result.saved += 1
        return result
