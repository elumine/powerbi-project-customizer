from __future__ import annotations

import unittest

from features.visual_editor.infrastructure.property_catalog import VisualPropertyCatalog


class VisualEditorCatalogTests(unittest.TestCase):
    def test_position_controls_are_not_exposed(self) -> None:
        ids = {control.id for control in VisualPropertyCatalog.BUILTIN_CONTROLS}
        self.assertFalse(any(control_id.startswith("general-position-") for control_id in ids))

    def test_all_builtin_controls_use_unified_general_category(self) -> None:
        self.assertEqual({control.category for control in VisualPropertyCatalog.BUILTIN_CONTROLS}, {"General"})


if __name__ == "__main__":
    unittest.main()
