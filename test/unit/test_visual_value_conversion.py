from __future__ import annotations

import unittest

from features.visual_editor.application.value_conversion import VisualValueConverter


class VisualValueConverterTests(unittest.TestCase):
    def test_normalizes_visual_editor_types(self) -> None:
        self.assertEqual(VisualValueConverter.convert("percentage", 120), 100)
        self.assertEqual(VisualValueConverter.convert("percentage", -5), 0)
        self.assertEqual(VisualValueConverter.convert("integer", "2.7"), 3)
        self.assertEqual(VisualValueConverter.convert("boolean", "yes"), True)
        self.assertEqual(VisualValueConverter.convert("hexColor", "aBc123"), "#ABC123")
        self.assertEqual(VisualValueConverter.convert("hexColor", "bad"), "#000000")
        self.assertEqual(VisualValueConverter.convert("enum", "bad", ["one", "two"]), "one")


if __name__ == "__main__":
    unittest.main()
