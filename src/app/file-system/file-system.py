from pathlib import Path


class FileSystem:
    @staticmethod
    def read(path: str) -> str:
        return Path(path).read_text(encoding="utf-8")

    @staticmethod
    def write(path: str, content: str) -> None:
        Path(path).write_text(content, encoding="utf-8")

    @staticmethod
    def exists(path: str) -> bool:
        return Path(path).exists()

    @staticmethod
    def delete(path: str) -> None:
        Path(path).unlink()

    @staticmethod
    def create_directory(path: str) -> None:
        Path(path).mkdir(parents=True, exist_ok=True)