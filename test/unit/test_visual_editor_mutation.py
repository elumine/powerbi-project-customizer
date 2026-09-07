from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from entities.document.models import JsonDocument
from features.visual_editor.application.service import VisualEditorService
from features.visual_editor.domain.models import VisualEditorControl
from services.documents.collection import DocumentCollection


class VisualEditorMutationTests(unittest.TestCase):
    def test_commits_valid_mutation_through_document_collection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            document = JsonDocument(
                path=Path(temporary) / "visual.json",
                text='{"visual":{"visualType":"table","title":"Before"}}',
            )
            collection = DocumentCollection([document])
            changes = []
            collection.subscribe(changes.append)
            service = VisualEditorService([
                VisualEditorControl(
                    id="test-title",
                    label="Title",
                    category="General",
                    control="text",
                    value_type="string",
                    paths=[["visual", "title"]],
                )
            ])

            result = service.apply_change(collection, "test-title", "After")

            self.assertEqual(result.changed_files, 1)
            self.assertEqual(result.changed_values, 1)
            self.assertIn('"title": "After"', document.text)
            self.assertTrue(document.is_dirty)
            self.assertEqual([change.kind.value for change in changes], ["content_changed"])

    def test_invalid_or_nonmatching_mutation_leaves_live_document_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            document = JsonDocument(path=Path(temporary) / "visual.json", text='{"visual":{"visualType":"table"}}')
            original = document.text
            collection = DocumentCollection([document])
            service = VisualEditorService([
                VisualEditorControl(
                    id="missing",
                    label="Missing",
                    category="General",
                    control="text",
                    value_type="string",
                    paths=[["visual", "missing"]],
                )
            ])

            result = service.apply_change(collection, "missing", "After")

            self.assertEqual(result.changed_values, 0)
            self.assertEqual(document.text, original)
            self.assertFalse(document.is_dirty)


if __name__ == "__main__":
    unittest.main()
