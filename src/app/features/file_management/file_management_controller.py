from __future__ import annotations

from pathlib import Path

from app.features.file_management.file_management_service import FileAddResult, FileManagementService, FileSaveResult
from app.ui.file_list_model import FileListModel


class FileManagementController:
    """Feature controller for document collection and current-file state."""

    def __init__(self, file_model: FileListModel, service: FileManagementService) -> None:
        self._files = file_model
        self._service = service
        self._current_index = -1

    @property
    def current_index(self) -> int:
        return self._current_index

    @property
    def file_count(self) -> int:
        return self._files.count

    @property
    def active_file_count(self) -> int:
        return sum(1 for document in self._files.documents() if document.is_active)

    @property
    def visible_file_count(self) -> int:
        return sum(1 for document in self._files.documents() if document.visible_in_tree)

    @property
    def has_dirty_files(self) -> bool:
        return any(document.is_dirty for document in self._files.documents())

    def reset(self) -> None:
        self._files.clear()
        self._current_index = -1

    def set_current_index(self, index: int) -> bool:
        coerced = self.coerce_selectable_index(index)
        if coerced == self._current_index:
            return False
        self._current_index = coerced
        return True

    def force_current_index(self, index: int) -> bool:
        if not 0 <= index < self._files.count:
            index = -1
        if index == self._current_index:
            return False
        self._current_index = index
        return True

    def ensure_current_index(self) -> bool:
        return self.set_current_index(self._current_index)

    def add_files(self, paths: list[Path]) -> FileAddResult:
        result = self._service.add_paths(paths)
        if self._current_index < 0 and result.first_added_index >= 0:
            self.set_current_index(result.first_added_index)
        return result

    def remove_file(self, row: int) -> bool:
        if not self._service.remove_file(row):
            return False

        if self._files.count == 0:
            changed = self._current_index != -1
            self._current_index = -1
            return changed

        if row < self._current_index:
            self._current_index -= 1
            return True
        if row == self._current_index or self._current_index >= self._files.count:
            return self.set_current_index(self._current_index)
        return self.ensure_current_index()

    def update_text(self, row: int, text: str) -> bool:
        return self._service.update_text(row, text)

    def format_current_file(self) -> bool:
        return self._service.format_file(self._current_index)

    def save_file(self, row: int) -> FileSaveResult:
        return self._service.save_file(row)

    def save_all(self) -> FileSaveResult:
        return self._service.save_all()

    def coerce_selectable_index(self, index: int) -> int:
        document = self._files.document_at(index)
        if document is not None and document.visible_in_tree:
            return index
        for row, candidate in enumerate(self._files.documents()):
            if candidate.visible_in_tree:
                return row
        return -1

    def current_document_text(self) -> str:
        document = self._files.document_at(self._current_index)
        return document.text if document is not None else ""

    def current_document_name(self) -> str:
        document = self._files.document_at(self._current_index)
        return document.name if document is not None else "No file selected"

    def current_document_path(self) -> str:
        document = self._files.document_at(self._current_index)
        return str(document.path) if document is not None else ""

    def current_document_file_type(self) -> str:
        document = self._files.document_at(self._current_index)
        return document.file_type_text if document is not None else ""

    def current_document_relative_path(self) -> str:
        document = self._files.document_at(self._current_index)
        return document.relative_path if document is not None else ""

    def current_document_highlighted_html(self) -> str:
        document = self._files.document_at(self._current_index)
        return document.highlighted_html if document is not None else ""

    def current_document_dirty(self) -> bool:
        document = self._files.document_at(self._current_index)
        return document.is_dirty if document is not None else False

    def current_document_valid_json(self) -> bool:
        document = self._files.document_at(self._current_index)
        return document.is_valid_json if document is not None else True

    def current_document_json_error(self) -> str:
        document = self._files.document_at(self._current_index)
        return document.json_error if document is not None else ""

    def current_document_match_count(self) -> int:
        document = self._files.document_at(self._current_index)
        return document.match_count if document is not None else 0
