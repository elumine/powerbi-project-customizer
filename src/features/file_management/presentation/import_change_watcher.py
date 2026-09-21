from __future__ import annotations

import hashlib
from pathlib import Path

from PySide6.QtCore import QFileSystemWatcher, QObject, Signal


class ImportChangeWatcher(QObject):
    """Reports externally changed imports once per user decision."""

    changed = Signal(list)

    def __init__(self) -> None:
        super().__init__()
        self._watcher = QFileSystemWatcher(self)
        self._watcher.fileChanged.connect(self._on_file_changed)
        self._watcher.directoryChanged.connect(self._on_directory_changed)
        self._fingerprints: dict[Path, str] = {}
        self._pending: set[Path] = set()

    def watch_paths(self, paths: list[Path]) -> None:
        normalized = {path.expanduser().resolve() for path in paths}
        obsolete = set(self._fingerprints) - normalized
        self._watcher.removePaths([str(path) for path in obsolete if str(path) in self._watcher.files()])
        current_directories = {path.parent for path in normalized}
        self._watcher.removePaths([
            directory
            for directory in self._watcher.directories()
            if Path(directory).expanduser().resolve() not in current_directories
        ])
        self._fingerprints = {path: self._fingerprint(path) for path in normalized}
        self._pending.intersection_update(normalized)
        self._add_paths(normalized)
        self._add_directories(current_directories)

    def acknowledge(self, paths: list[Path] | None = None) -> None:
        acknowledged = set(self._fingerprints) if paths is None else {path.expanduser().resolve() for path in paths}
        for path in acknowledged:
            if path in self._fingerprints:
                self._fingerprints[path] = self._fingerprint(path)
        self._pending.difference_update(acknowledged)

    def clear(self) -> None:
        watched = self._watcher.files() + self._watcher.directories()
        if watched:
            self._watcher.removePaths(watched)
        self._fingerprints.clear()
        self._pending.clear()

    def _on_file_changed(self, value: str) -> None:
        path = Path(value).expanduser().resolve()
        if path not in self._fingerprints:
            return
        if self._fingerprint(path) == self._fingerprints[path] or path in self._pending:
            self._add_paths({path})
            return
        self._pending.add(path)
        self._add_paths({path})
        self.changed.emit([str(path)])

    def _on_directory_changed(self, value: str) -> None:
        directory = Path(value).expanduser().resolve()
        for path in tuple(self._fingerprints):
            if path.parent == directory:
                self._on_file_changed(str(path))

    def _add_paths(self, paths: set[Path]) -> None:
        missing = [str(path) for path in paths if path.exists() and str(path) not in self._watcher.files()]
        if missing:
            self._watcher.addPaths(missing)

    def _add_directories(self, directories: set[Path]) -> None:
        missing = [str(path) for path in directories if path.exists() and str(path) not in self._watcher.directories()]
        if missing:
            self._watcher.addPaths(missing)

    @staticmethod
    def _fingerprint(path: Path) -> str:
        try:
            return hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            return "<missing>"
