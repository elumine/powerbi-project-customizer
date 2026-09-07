from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from entities.powerbi.metadata import classify_json_file, display_name_for_document, load_json_for_metadata, relative_path_for_display
from features.folder_import.application.models import FolderScanItem
from services.filesystem.ports import TextFileReader


@dataclass(slots=True)
class FolderScanResult:
    root_label: str = ""
    items: list[FolderScanItem] = field(default_factory=list)
    skipped_duplicates: int = 0
    errors: list[str] = field(default_factory=list)


class FolderScanner:
    """Find importable JSON files under selected roots."""

    SKIPPED_DIRECTORIES = {".pbi", "__pycache__", ".git"}
    SKIPPED_FILE_NAMES = {
        ".platform",
        "cache.abf",
        "localsettings.json",
        "mobilestate.json",
        "report.json",
        "semanticmodeldiagramlayout.json",
    }

    def __init__(self, reader: TextFileReader) -> None:
        self._reader = reader

    def scan(self, roots: list[Path], existing_paths: set[Path] | None = None) -> FolderScanResult:
        existing = set(existing_paths or set())
        seen: set[Path] = set()
        result = FolderScanResult(root_label=self._root_label(roots))

        for root in roots:
            root_path = root.expanduser().resolve()
            if root_path.is_file():
                self._append_file(root_path, root_path.parent, existing, seen, result, allow_loose=True)
                continue
            if not root_path.is_dir():
                result.errors.append(f"{root_path} is not a folder.")
                continue

            for current_root, directories, files in os.walk(
                root_path,
                onerror=lambda error: result.errors.append(str(error)),
            ):
                directories[:] = [directory for directory in directories if directory.casefold() not in self.SKIPPED_DIRECTORIES]
                for file_name in files:
                    self._append_file(Path(current_root) / file_name, root_path, existing, seen, result, allow_loose=True)

        result.items.sort(key=lambda item: item.relative_path.casefold())
        return result

    def _append_file(
        self,
        file_path: Path,
        scan_root: Path,
        existing_paths: set[Path],
        seen_paths: set[Path],
        result: FolderScanResult,
        allow_loose: bool = False,
    ) -> None:
        resolved = file_path.expanduser().resolve()
        if resolved.name.casefold() in self.SKIPPED_FILE_NAMES:
            return
        if resolved.suffix.casefold() != ".json":
            return
        if resolved in existing_paths or resolved in seen_paths:
            result.skipped_duplicates += 1
            return

        data = self._json_data(resolved)
        file_type = classify_json_file(resolved, data)

        seen_paths.add(resolved)
        display_name, _source = display_name_for_document(resolved, data, file_type, resolved.name)
        result.items.append(
            FolderScanItem(
                path=resolved,
                display_name=display_name,
                relative_path=self._relative_path(resolved, scan_root),
                file_type=file_type.value if file_type is not None else "Json",
            )
        )

    def _json_data(self, path: Path):
        try:
            text = self._reader.read_text(path)
        except OSError:
            return None
        return load_json_for_metadata(text)

    @staticmethod
    def _relative_path(path: Path, root: Path) -> str:
        try:
            return str(path.relative_to(root)).replace("\\", "/")
        except ValueError:
            return relative_path_for_display(path)

    @staticmethod
    def _root_label(roots: list[Path]) -> str:
        if len(roots) == 1:
            return str(roots[0].expanduser().resolve())
        return f"{len(roots)} selected locations"
