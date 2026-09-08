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
            self.assertIn('"visual.title": "After"', document.text)
            self.assertNotIn('"visual": {', document.text)
            self.assertTrue(document.is_dirty)
            self.assertEqual([change.kind.value for change in changes], ["content_changed"])

    def test_macro_style_creation_stays_flat(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            document = JsonDocument(
                path=Path(temporary) / "visual.json",
                text='{"visual.visualType":"barChart","visual.visualContainerObjects.title.[0].properties":{}}',
            )
            collection = DocumentCollection([document])
            service = VisualEditorService([
                VisualEditorControl(
                    id="header-filter",
                    label="Header filter",
                    category="General",
                    control="boolean",
                    value_type="boolean",
                    visual_types=["*"],
                    paths=[["visual", "visualContainerObjects", "visualHeader", 0, "properties", "showFilterRestatementButton"]],
                    creates_missing_path=True,
                )
            ])

            result = service.apply_change(collection, "header-filter", False)

            self.assertEqual(1, result.changed_files)
            self.assertNotIn('"visual": {', document.text)
            self.assertIn(
                '"visual.visualContainerObjects.visualHeader.[0].properties.showFilterRestatementButton.expr.Literal.Value": "false"',
                document.text,
            )

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
