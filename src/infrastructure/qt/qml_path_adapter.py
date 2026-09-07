from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse


class PathService:
    """Normalizes Python, Qt, and QML path values into filesystem paths."""

    @classmethod
    def many_from_qml(cls, values: Any) -> list[Path]:
        if values is None:
            return []
        if isinstance(values, (str, Path)) or hasattr(values, "toLocalFile"):
            path = cls.one_from_qml(values)
            return [path] if path is not None else []
        if not isinstance(values, Iterable):
            path = cls.one_from_qml(values)
            return [path] if path is not None else []

        paths: list[Path] = []
        for value in values:
            path = cls.one_from_qml(value)
            if path is not None:
                paths.append(path)
        return paths

    @classmethod
    def one_from_qml(cls, value: Any) -> Path | None:
        if value is None:
            return None
        if isinstance(value, Path):
            return value.expanduser().resolve()

        local_file = cls._local_file_from_qt_url(value)
        if local_file:
            return Path(local_file).expanduser().resolve()

        raw_value = cls._string_value(value)
        if raw_value == "":
            return None
        if raw_value.startswith("file:"):
            return cls._path_from_file_url(raw_value)
        return Path(raw_value).expanduser().resolve()

    @staticmethod
    def _local_file_from_qt_url(value: Any) -> str:
        to_local_file = getattr(value, "toLocalFile", None)
        if not callable(to_local_file):
            return ""
        try:
            return str(to_local_file())
        except RuntimeError:
            return ""

    @staticmethod
    def _string_value(value: Any) -> str:
        if isinstance(value, str):
            return value.strip()

        to_string = getattr(value, "toString", None)
        if callable(to_string):
            try:
                return str(to_string()).strip()
            except RuntimeError:
                return ""
        return str(value).strip()

    @staticmethod
    def _path_from_file_url(value: str) -> Path | None:
        parsed = urlparse(value)
        path_text = unquote(parsed.path)
        if parsed.netloc:
            path_text = f"//{parsed.netloc}{path_text}"
        if len(path_text) >= 3 and path_text[0] == "/" and path_text[2] == ":":
            path_text = path_text[1:]
        if path_text == "":
            return None
        return Path(path_text).expanduser().resolve()
