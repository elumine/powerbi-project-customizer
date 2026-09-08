from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from features.file_management.infrastructure.document_repository import FileRepository


class RawFlatDocumentTests(unittest.TestCase):
    def test_import_retains_raw_file_source_and_flattened_working_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "visual.json"
            raw = '{\n  "visual": {"visualType": "table"},\n  "width": 120\n}'
            path.write_text(raw, encoding="utf-8")

            document = FileRepository().load_document(path)

            self.assertEqual(document.raw_text, raw)
            self.assertIn('"visual.visualType": "table"', document.text)
            self.assertNotEqual(document.text, document.raw_text)

    def test_save_converts_flat_working_text_back_to_hierarchy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "visual.json"
            path.write_text('{"visual":{"visualType":"table"}}', encoding="utf-8")
            repository = FileRepository()
            document = repository.load_document(path)
            document.set_text('{"visual.visualType":"table","visual.title":"After"}')

            repository.save_document(document)

            self.assertEqual(
                {"visual": {"visualType": "table", "title": "After"}},
                json.loads(path.read_text(encoding="utf-8")),
            )
            self.assertEqual(json.loads(document.raw_text or "{}"), json.loads(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
