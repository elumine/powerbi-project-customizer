from __future__ import annotations

from typing import Any, Iterable

from app.features.history.history_entry import FileSnapshot, HistoryEntry
from app.features.history.history_service import HistoryService
from app.ui.file_list_model import FileListModel
from app.ui.history_model import HistoryListModel


class HistoryController:
    def __init__(self, model: HistoryListModel, service: HistoryService) -> None:
        self._model = model
        self._service = service
        self._model.reset(self._service.entries, self._service.current_index)

    @property
    def count(self) -> int:
        return self._model.count

    @property
    def current_index(self) -> int:
        return self._service.current_index

    def clear(self) -> None:
        self._service.clear()
        self._sync_model()

    def record(
        self,
        operation_type: str,
        display_name: str,
        metadata: dict[str, Any] | None = None,
        file_changes: Iterable[FileSnapshot] | None = None,
        reversible: bool = True,
    ) -> HistoryEntry:
        entry = self._service.record(operation_type, display_name, metadata, file_changes, reversible)
        self._sync_model()
        return entry

    def go_to(self, index: int, files: FileListModel) -> bool:
        changed = self._service.go_to(index, files)
        if changed:
            self._sync_model()
        return changed

    def _sync_model(self) -> None:
        self._model.reset(self._service.entries, self._service.current_index)
