from __future__ import annotations

from typing import Any

from app.features.visual_editor.visual_editor_service import VisualEditorService, VisualEditResult
from app.ui.file_list_model import FileListModel
from app.ui.visual_editor_models import VisualEditorControlModel


class VisualEditorController:
    def __init__(self, model: VisualEditorControlModel, service: VisualEditorService) -> None:
        self._model = model
        self._service = service
        self._category = "General"
        self._last_result = VisualEditResult()

    @property
    def category(self) -> str:
        return self._category

    @property
    def last_status(self) -> str:
        return self._last_result.summary

    def category_options(self, files: FileListModel) -> list[dict[str, Any]]:
        return [
            {"label": "General", "value": "General", "enabled": True, "count": self.active_visual_count(files)},
            {"label": "Specific", "value": "Specific", "enabled": True, "count": self.active_visual_count(files)},
            *self._service.visual_type_category_options(files.documents()),
        ]

    def active_visual_count(self, files: FileListModel) -> int:
        return sum(1 for document in files.documents() if document.file_type_text == "Visual" and document.is_active)

    def refresh(self, files: FileListModel) -> None:
        enabled_values = self._enabled_category_values(files)
        if self._category not in enabled_values:
            self._category = "General"
        self._model.reset(self._service.applicable_controls(files.documents(), self._category))

    def set_category(self, category: str, files: FileListModel) -> bool:
        normalized = category if category in self._enabled_category_values(files) else "General"
        if normalized == self._category:
            return False
        self._category = normalized
        self.refresh(files)
        return True

    def apply_change(self, files: FileListModel, control_id: str, value: Any) -> VisualEditResult:
        self._last_result = self._service.apply_change(files.documents(), control_id, value)
        self.refresh(files)
        return self._last_result

    def _enabled_category_values(self, files: FileListModel) -> set[str]:
        return {str(option["value"]) for option in self.category_options(files) if option.get("enabled", True)}
