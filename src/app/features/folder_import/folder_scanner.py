from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from app.core.display_name import display_name_from_json_text
from app.core.file_service import FileService, FileServiceError
from app.ui.folder_scan_model import FolderScanItem


@dataclass(slots=True)
class FolderScanResult:
    root_label: str = ""
    items: list[FolderScanItem] = field(default_factory=list)
    skipped_duplicates: int = 0
    errors: list[str] = field(default_factory=list)


class FolderScanner:
    """Finds importable visual.json files under selected roots."""

    TARGET_FILE_NAME = "visual.json"

    def scan(self, roots: list[Path], existing_paths: set[Path] | None = None) -> FolderScanResult:
        existing = set(existing_paths or set())
        seen: set[Path] = set()
        result = FolderScanResult(root_label=self._root_label(roots))

        for root in roots:
            root_path = root.expanduser().resolve()
            if root_path.is_file():
                self._append_file(root_path, root_path.parent, existing, seen, result)
                continue
            if not root_path.is_dir():
                result.errors.append(f"{root_path} is not a folder.")
                continue

            for current_root, _directories, files in os.walk(
                root_path,
                onerror=lambda error: result.errors.append(str(error)),
            ):
                if self.TARGET_FILE_NAME not in files:
                    continue
                self._append_file(Path(current_root) / self.TARGET_FILE_NAME, root_path, existing, seen, result)

        result.items.sort(key=lambda item: item.relative_path.casefold())
        return result

    def _append_file(
        self,
        file_path: Path,
        scan_root: Path,
        existing_paths: set[Path],
        seen_paths: set[Path],
        result: FolderScanResult,
    ) -> None:
        resolved = file_path.expanduser().resolve()
        if resolved.name.casefold() != self.TARGET_FILE_NAME:
            return
        if resolved in existing_paths or resolved in seen_paths:
            result.skipped_duplicates += 1
            return

        seen_paths.add(resolved)
        result.items.append(
            FolderScanItem(
                path=resolved,
                display_name=self._display_name(resolved),
                relative_path=self._relative_path(resolved, scan_root),
            )
        )

    @staticmethod
    def _display_name(path: Path) -> str:
        try:
            text = FileService.read_text(path)
        except FileServiceError:
            return path.name
        return display_name_from_json_text(text, path.name)

    @staticmethod
    def _relative_path(path: Path, root: Path) -> str:
        try:
            return str(path.relative_to(root))
        except ValueError:
            return path.name

    @staticmethod
    def _root_label(roots: list[Path]) -> str:
        if len(roots) == 1:
            return str(roots[0].expanduser().resolve())
        return f"{len(roots)} selected locations"
