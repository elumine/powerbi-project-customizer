from __future__ import annotations

import json
import unittest
from pathlib import Path

from entities.document.models import JsonDocument
from features.macros.infrastructure.repository import MacroRepository
from features.visual_editor.application.service import VisualEditorService
from features.visual_editor.infrastructure.property_catalog import VisualPropertyCatalog
from services.documents.collection import DocumentCollection


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class PowerBiStandardFormattingMacroTests(unittest.TestCase):
    def test_grouped_macro_loads_and_only_references_catalog_controls(self) -> None:
        content_root = PROJECT_ROOT / "content"
        macro = MacroRepository(content_root).load_macro_file(
            content_root / "macros" / "powerbi-standard-visual-formatting.json"
        )

        self.assertEqual([], macro.load_errors)
        self.assertEqual(6, len(macro.groups))
        self.assertEqual(
            [
                "All visuals",
                "Graphs, line charts, and bar charts",
                "Slicer",
                "Bookmark navigator",
                "Text visuals with Title in the name",
                "Card",
            ],
            [group.name for group in macro.groups],
        )
        self.assertGreater(macro.step_count, 50)
        control_ids = {control.id for control in VisualPropertyCatalog.BUILTIN_CONTROLS}
        missing = {
            step.control_id
            for step in macro.steps
            if step.type == "visual-editor-change" and step.control_id not in control_ids
        }
        self.assertEqual(set(), missing)
        self.assertTrue(
            all(
                step.allow_no_change
                for step in macro.steps
                if step.type == "visual-editor-change"
            )
        )
        self.assertIn("groups", macro.to_export_dict())
        self.assertNotIn("steps", macro.to_export_dict())
        self.assertIn("summary", macro.groups[0].to_view_dict()["steps"][0])

    def test_standard_controls_create_pbir_wrappers_and_selector_entries(self) -> None:
        bar_document = JsonDocument(
            path=PROJECT_ROOT / "bar-visual.json",
            text=json.dumps({
                "visual": {
                    "visualType": "barChart",
                    "objects": {"valueAxis": [{"properties": {}}]},
                    "visualContainerObjects": {"title": [{"properties": {}}]},
                },
            }),
        )
        textbox_document = JsonDocument(
            path=PROJECT_ROOT / "textbox-visual.json",
            text=json.dumps({
                "visual": {
                    "visualType": "textbox",
                    "objects": {"general": [{"properties": {"paragraphs": [{"textRuns": [{"value": "Title"}]}]}}]},
                },
            }),
        )
        card_document = JsonDocument(
            path=PROJECT_ROOT / "card-visual.json",
            text=json.dumps({"visual": {"visualType": "cardVisual", "objects": {}}}),
        )
        collection = DocumentCollection([bar_document, textbox_document, card_document])
        service = VisualEditorService(VisualPropertyCatalog.BUILTIN_CONTROLS)

        self.assertEqual(3, service.apply_change(collection, "general-title-font-size", 10).changed_values)
        self.assertEqual(1, service.apply_change(collection, "textbox-text-font-size", 18).changed_values)
        self.assertEqual(1, service.apply_change(collection, "card-accent-bar-position", "Left").changed_values)

        bar_data = bar_document.parsed_json
        self.assertEqual(
            "10D",
            bar_data["visual.visualContainerObjects.title.[0].properties.fontSize.expr.Literal.Value"],
        )
        self.assertNotIn('"visual": {', bar_document.text)
        textbox_data = textbox_document.parsed_json
        self.assertEqual(
            "18D",
            textbox_data["visual.objects.general.[0].properties.paragraphs.[0].textRuns.[0].textStyle.fontSize.expr.Literal.Value"],
        )
        card_data = card_document.parsed_json
        self.assertEqual(
            "default",
            card_data["visual.objects.accentBar.[0].selector.id"],
        )
        self.assertEqual(
            "'Left'",
            card_data["visual.objects.accentBar.[0].properties.position.expr.Literal.Value"],
        )


if __name__ == "__main__":
    unittest.main()
