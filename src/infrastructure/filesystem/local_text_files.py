from __future__ import annotations

from pathlib import Path

from infrastructure.filesystem.file_service import FileService, FileServiceError


class LocalTextFileReader:
    def read_text(self, path: Path) -> str:
        try:
            return FileService.read_text(path)
        except FileServiceError as error:
            raise OSError(str(error)) from error
