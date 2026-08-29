import json
from pathlib import Path


class JsonManager:
    @staticmethod
    def read_json(path: str):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def write_json(path: str, data) -> None:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)