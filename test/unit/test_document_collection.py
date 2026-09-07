from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from entities.document.models import JsonDocument
from services.documents.collection import DocumentCollection


class DocumentCollectionTests(unittest.TestCase):
    def test_mutations_publish_stable_identity_events(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "page.json"
            collection = DocumentCollection()
            events = []
            collection.subscribe(events.append)
            document = JsonDocument(path=path, text='{"displayName":"One","height":1}')
            row = collection.add_document(document)
            self.assertEqual(row, 0)
            self.assertEqual(collection.document_by_id(document.id), document)
            result = collection.set_document_text_by_id(document.id, '{"displayName":"Two","height":1}')
            self.assertFalse(result.is_empty)
            self.assertTrue(document.is_dirty)
            saved = collection.mark_saved_by_id(document.id)
            self.assertFalse(saved.is_empty)
            self.assertFalse(document.is_dirty)
            collection.remove_document_by_id(document.id)
            self.assertEqual(collection.count, 0)
            self.assertEqual([event.kind.value for event in events], ["added", "content_changed", "save_state_changed", "removed"])

    def test_duplicate_ids_and_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "visual.json"
            collection = DocumentCollection()
            first = JsonDocument(path=path, text='{}', id="one")
            collection.add_document(first)
            with self.assertRaises(ValueError):
                collection.add_document(JsonDocument(path=path, text='{}', id="two"))
            with self.assertRaises(ValueError):
                collection.add_document(JsonDocument(path=Path(temporary) / "other.json", text='{}', id="one"))


if __name__ == "__main__":
    unittest.main()
