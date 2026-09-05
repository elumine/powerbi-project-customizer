from __future__ import annotations

from pathlib import Path

from app.features.folder_import.folder_scanner import FolderScanResult, FolderScanner
from app.ui.folder_scan_model import FolderScanModel


class FolderImportController:
    """Feature controller for the folder import preview lifecycle."""

    def __init__(self, scan_model: FolderScanModel, scanner: FolderScanner) -> None:
        self._scan_model = scan_model
        self._scanner = scanner
        self._scan_root = ""
        self._visible = False
        self._last_result = FolderScanResult()

    @property
    def scan_root(self) -> str:
        return self._scan_root

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def count(self) -> int:
        return self._scan_model.count

    @property
    def last_result(self) -> FolderScanResult:
        return self._last_result

    def scan_paths(self, roots: list[Path], existing_paths: set[Path] | None = None) -> FolderScanResult:
        self._last_result = self._scanner.scan(roots, existing_paths)
        self._scan_root = self._last_result.root_label
        self._scan_model.reset(self._last_result.items)
        self._visible = True
        return self._last_result

    def confirm(self) -> list[Path]:
        paths = self._scan_model.paths()
        self.cancel()
        return paths

    def cancel(self) -> None:
        self._scan_model.clear()
        self._scan_root = ""
        self._visible = False
