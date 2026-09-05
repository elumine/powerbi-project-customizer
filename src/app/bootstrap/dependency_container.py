from __future__ import annotations

from pathlib import Path

from app.shell.app_controller import AppController


class DependencyContainer:
    """Builds top-level application objects in one composition root."""

    def create_app_controller(self, filter_storage_path: Path | None = None, content_root: Path | None = None) -> AppController:
        return AppController(filter_storage_path=filter_storage_path, content_root=content_root)