from __future__ import annotations

from pathlib import Path


class FileServiceError(Exception):
    """Raised when a JSON file cannot be loaded or saved."""


class FileService:
    @staticmethod
    def read_text(path: str | Path) -> str:
        file_path = Path(path).expanduser().resolve()
        if not file_path.exists():
            raise FileServiceError(f"{file_path} does not exist.")
        if not file_path.is_file():
            raise FileServiceError(f"{file_path} is not a file.")

        try:
            return file_path.read_text(encoding="utf-8-sig")
        except OSError as error:
            raise FileServiceError(f"Could not read {file_path}: {error}") from error
        except UnicodeDecodeError as error:
            raise FileServiceError(f"{file_path.name} is not valid UTF-8 text.") from error

    @staticmethod
    def write_text(path: str | Path, content: str) -> None:
        file_path = Path(path).expanduser().resolve()
        if not file_path.parent.exists():
            raise FileServiceError(f"Folder does not exist: {file_path.parent}")

        try:
            file_path.write_text(content, encoding="utf-8")
        except OSError as error:
            raise FileServiceError(f"Could not save {file_path}: {error}") from error
