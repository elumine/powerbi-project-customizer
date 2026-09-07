from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog


class QtDialogGateway:
    """Qt Widgets implementation of the shell's narrow file-dialog operations."""

    _JSON_FILTER = "JSON files (*.json);;All files (*.*)"

    def choose_json_files(self) -> list[Path]:
        values, _ = QFileDialog.getOpenFileNames(None, "Open JSON files", "", self._JSON_FILTER)
        return [Path(value) for value in values]

    def choose_folder(self) -> Path | None:
        value = QFileDialog.getExistingDirectory(None, "Add JSON folder")
        return Path(value) if value else None

    def choose_filter_import(self) -> Path | None:
        value, _ = QFileDialog.getOpenFileName(None, "Import filter", "", self._JSON_FILTER)
        return Path(value) if value else None

    def choose_filter_export(self) -> Path | None:
        value, _ = QFileDialog.getSaveFileName(None, "Export filter", "filter.json", self._JSON_FILTER)
        return Path(value) if value else None

    def choose_macro_import(self) -> Path | None:
        value, _ = QFileDialog.getOpenFileName(None, "Import macro", "", self._JSON_FILTER)
        return Path(value) if value else None

    def choose_macro_export(self) -> Path | None:
        value, _ = QFileDialog.getSaveFileName(None, "Export macro", "macro.json", self._JSON_FILTER)
        return Path(value) if value else None
