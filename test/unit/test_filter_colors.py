from __future__ import annotations

import unittest

from entities.filter.models import FILTER_COLOR_FALLBACK, ContentFilter, normalize_filter_color


class FilterColorTests(unittest.TestCase):
    def test_external_filter_colors_are_normalized_before_qml_presentation(self) -> None:
        self.assertEqual(normalize_filter_color("#A78BFA"), "#a78bfa")
        self.assertEqual(normalize_filter_color("not-a-color"), FILTER_COLOR_FALLBACK)
        self.assertEqual(normalize_filter_color("#12345"), FILTER_COLOR_FALLBACK)

    def test_deserialized_invalid_filter_color_uses_dashboard_fallback(self) -> None:
        content_filter = ContentFilter.from_dict({"id": "x", "displayName": "Unsafe", "color": "red", "rules": []})
        self.assertEqual(content_filter.color, FILTER_COLOR_FALLBACK)


if __name__ == "__main__":
    unittest.main()
