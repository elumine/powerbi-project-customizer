from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from app.features.history.history_entry import FileSnapshot, HistoryEntry
from app.ui.file_list_model import FileListModel


class HistoryService:
    def __init__(self) -> None:
        self._entries: list[HistoryEntry] = []
        self._current_index = -1

    @property
    def entries(self) -> tuple[HistoryEntry, ...]:
        return tuple(self._entries)

    @property
    def current_index(self) -> int:
        return self._current_index

    def clear(self) -> None:
        self._entries = []
        self._current_index = -1

    def record(
        self,
        operation_type: str,
        display_name: str,
        metadata: dict[str, Any] | None = None,
        file_changes: Iterable[FileSnapshot] | None = None,
        reversible: bool = True,
    ) -> HistoryEntry:
        if self._current_index < len(self._entries) - 1:
            self._entries = self._entries[: self._current_index + 1]
        entry = HistoryEntry(
            index=len(self._entries),
            timestamp=datetime.now(),
            operation_type=operation_type,
            display_name=display_name,
            metadata=metadata or {},
            file_changes=list(file_changes or []),
            reversible=reversible,
        )
        self._entries.append(entry)
        self._current_index = entry.index
        return entry

    def go_to(self, index: int, files: FileListModel) -> bool:
        if not 0 <= index < len(self._entries):
            return False
        if index == self._current_index:
            return False
        if index < self._current_index:
            return self._rollback_to(index, files)
        return self._rollforward_to(index, files)

    def _rollback_to(self, index: int, files: FileListModel) -> bool:
        if not self._range_reversible(index + 1, self._current_index + 1):
            return False
        for entry in reversed(self._entries[index + 1 : self._current_index + 1]):
            for snapshot in reversed(entry.file_changes):
                self._apply_snapshot(files, snapshot, before=True)
        self._current_index = index
        return True

    def _rollforward_to(self, index: int, files: FileListModel) -> bool:
        if not self._range_reversible(self._current_index + 1, index + 1):
            return False
        for entry in self._entries[self._current_index + 1 : index + 1]:
            for snapshot in entry.file_changes:
                self._apply_snapshot(files, snapshot, before=False)
        self._current_index = index
        return True

    def _range_reversible(self, start: int, end: int) -> bool:
        return all(entry.reversible for entry in self._entries[start:end])

    @staticmethod
    def _apply_snapshot(files: FileListModel, snapshot: FileSnapshot, before: bool) -> None:
        row = files.document_index_by_id(snapshot.document_id)
        document = files.document_at(row)
        if document is None:
            return
        document.set_text(snapshot.before_text if before else snapshot.after_text)
        document.original_text = snapshot.before_original_text if before else snapshot.after_original_text
        files.refresh_row(row)
