from __future__ import annotations

from PySide6.QtCore import QObject, QTimer

from features.suggestions.application.service import SuggestionService
from services.documents.workspace_port import DocumentWorkspacePort
from features.suggestions.presentation.models import SuggestionListModel


class SuggestionController(QObject):
    """Maintains duplicate key/value suggestions for the currently loaded files."""

    def __init__(
        self,
        key_model: SuggestionListModel,
        value_model: SuggestionListModel,
        service: type[SuggestionService] = SuggestionService,
    ) -> None:
        super().__init__()
        self._keys = key_model
        self._values = value_model
        self._service = service
        self._files: DocumentWorkspacePort | None = None
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self.refresh_now)

    @property
    def key_count(self) -> int:
        return self._keys.count

    @property
    def value_count(self) -> int:
        return self._values.count

    def schedule_refresh(self, files: DocumentWorkspacePort, delay_ms: int = 250) -> None:
        self._files = files
        self._timer.start(delay_ms)

    def refresh_now(self, files: DocumentWorkspacePort | None = None) -> None:
        if files is not None:
            self._files = files
        documents = self._files.documents() if self._files is not None else []
        key_items, value_items = self._service.analyze(documents)
        self._keys.reset(key_items)
        self._values.reset(value_items)

    def suggestion_value(self, suggestion_type: str, row: int) -> str:
        item = self._model_for_type(suggestion_type).item_at(row)
        return item.duplication_value if item is not None else ""

    def _model_for_type(self, suggestion_type: str) -> SuggestionListModel:
        return self._keys if suggestion_type == "key" else self._values
