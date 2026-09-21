from __future__ import annotations

from pathlib import Path

from features.file_management.application.service import FileAddResult, FileManagementService, FileSaveResult
from features.file_management.presentation.file_list_model import FileListModel


class FileManagementController:
    """Qt-facing selection adapter over framework-independent file commands."""

    def __init__(self, file_model: FileListModel, service: FileManagementService) -> None:
        self._files = file_model
        self._service = service
        self._current_document_id = ""

    @property
    def current_index(self) -> int:
        return self._files.document_index_by_id(self._current_document_id)

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
        self._current_document_id = ""

    def set_current_index(self, index: int) -> bool:
        selected = self._document_id_for_selectable_index(index)
        if selected == self._current_document_id:
            return False
        self._current_document_id = selected
        return True

    def force_current_index(self, index: int) -> bool:
        document = self._files.document_at(index)
        selected = document.id if document is not None else ""
        if selected == self._current_document_id:
            return False
        self._current_document_id = selected
        return True

    def ensure_current_index(self) -> bool:
        return self.set_current_index(self.current_index)

    def add_files(self, paths: list[Path]) -> FileAddResult:
        result = self._service.add_paths(paths)
        if not self._current_document_id and result.first_added_document_id:
            self._current_document_id = result.first_added_document_id
        return result

    def remove_file(self, row: int) -> bool:
        document = self._files.document_at(row)
        if document is None or not self._service.remove_document(document.id):
            return False
        if document.id == self._current_document_id:
            self._current_document_id = ""
        self.ensure_current_index()
        return True

    def update_text(self, row: int, text: str) -> bool:
        document = self._files.document_at(row)
        return document is not None and self._service.update_text(document.id, text)

    def format_current_file(self) -> bool:
        return bool(self._current_document_id and self._service.format_document(self._current_document_id))

    def save_file(self, row: int) -> FileSaveResult:
        document = self._files.document_at(row)
        return self._service.save_document(document.id) if document is not None else FileSaveResult(errors=["No file selected."])

    def save_all(self) -> FileSaveResult:
        return self._service.save_all()

    def reload_paths(self, paths: list[Path]) -> FileAddResult:
        return self._service.reload_paths(paths)

    def _document_id_for_selectable_index(self, index: int) -> str:
        document = self._files.document_at(index)
        if document is not None and document.visible_in_tree:
            return document.id
        for candidate in self._files.documents():
            if candidate.visible_in_tree:
                return candidate.id
        return ""

    def _current_document(self):
        return self._files.collection.document_by_id(self._current_document_id)

    def current_document_text(self) -> str:
        document = self._current_document()
        return document.text if document is not None else ""

    def current_document_raw_text(self) -> str:
        document = self._current_document()
        return (document.raw_text or "") if document is not None else ""

    def current_document_name(self) -> str:
        document = self._current_document()
        return document.name if document is not None else "No file selected"

    def current_document_path(self) -> str:
        document = self._current_document()
        return str(document.path) if document is not None else ""

    def current_document_file_type(self) -> str:
        document = self._current_document()
        return document.file_type_text if document is not None else ""

    def current_document_relative_path(self) -> str:
        document = self._current_document()
        return document.relative_path if document is not None else ""

    def current_document_highlighted_html(self) -> str:
        document = self._current_document()
        return document.highlighted_html if document is not None else ""

    def current_document_dirty(self) -> bool:
        document = self._current_document()
        return document.is_dirty if document is not None else False

    def current_document_valid_json(self) -> bool:
        document = self._current_document()
        return document.is_valid_json if document is not None else True

    def current_document_json_error(self) -> str:
        document = self._current_document()
        return document.json_error if document is not None else ""

    def current_document_match_count(self) -> int:
        document = self._current_document()
        return document.match_count if document is not None else 0
