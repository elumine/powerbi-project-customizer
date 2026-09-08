from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from features.filters.infrastructure.repository import FilterRepository


class FilterRepositoryMigrationTests(unittest.TestCase):
    def test_removes_retired_pre_json_sample_filters_once(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "filters.json"
            path.write_text(json.dumps({"filters": [
                {"id": "table", "displayName": "Table", "color": "#42c6b4", "rules": []},
                {"id": "chart", "displayName": "Chart", "color": "#a78bfa", "rules": []},
                {"id": "title", "displayName": "Title1", "color": "#f7b733", "rules": []},
                {"id": "real", "displayName": "Revenue", "color": "#52b6ff", "rules": []},
            ]}), encoding="utf-8")

            filters = FilterRepository(path).list_filters()

            self.assertEqual([item.display_name for item in filters], ["Revenue"])
            persisted = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual([item["displayName"] for item in persisted["filters"]], ["Revenue"])


if __name__ == "__main__":
    unittest.main()
