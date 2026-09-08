from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from features.filters.infrastructure.repository import FilterRepository


class LegacyFilterCleanupTests(unittest.TestCase):
    def test_retired_in_memory_samples_are_removed_from_user_storage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "filters.json"
            path.write_text(json.dumps({"filters": [
                {"id": "table", "displayName": "Table", "color": "#42c6b4", "rules": []},
                {"id": "chart", "displayName": "Chart", "color": "#a78bfa", "rules": []},
                {"id": "title", "displayName": "Title1", "color": "#f7b733", "rules": []},
                {"id": "keep", "displayName": "My rule", "color": "#52b6ff", "rules": []},
            ]}), encoding="utf-8")

            filters = FilterRepository(path).list_filters()

            self.assertEqual([content_filter.display_name for content_filter in filters], ["My rule"])
            stored = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual([item["displayName"] for item in stored["filters"]], ["My rule"])


if __name__ == "__main__":
    unittest.main()
