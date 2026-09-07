from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ResourceLocator:
    """Resolves logical application resources in development and PyInstaller mode."""

    source_root_path: Path
    content_root_path: Path

    @classmethod
    def discover(cls) -> "ResourceLocator":
        bundle_root = getattr(sys, "_MEIPASS", None)
        if bundle_root:
            root = Path(bundle_root).resolve()
            return cls(source_root_path=root, content_root_path=cls._content_root(root))

        # This module lives at src/infrastructure/packaging/; parents[2] is src.
        source_root = Path(__file__).resolve().parents[2]
        project_root = source_root.parent
        return cls(source_root_path=source_root, content_root_path=cls._content_root(project_root))

    @staticmethod
    def _content_root(default_root: Path) -> Path:
        override = os.environ.get("JSON_MULTI_EDITOR_CONTENT_PATH")
        if override:
            return Path(override).expanduser().resolve()
        return (default_root / "content").resolve()

    def source_root(self) -> Path:
        return self.source_root_path

    def content_root(self) -> Path:
        return self.content_root_path

    def ui_style_file(self) -> Path:
        return self.source_root_path / "ui" / "styles" / "vscode.qss"

    def qml_module_root(self, uri: str) -> Path:
        relative = Path(*uri.split("."))
        return self.source_root_path / relative


def locate_content_root() -> Path:
    """Compatibility helper for callers not yet constructed through bootstrap."""

    return ResourceLocator.discover().content_root()
