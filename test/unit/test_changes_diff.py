from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from entities.document.models import JsonDocument
from features.changes.application.service import ChangeDiffService


class ChangesDiffTests(unittest.TestCase):
    def test_build_marks_removed_and_added_lines_with_numbers(self) -> None:
        lines = ChangeDiffService().build("one\ntwo\n", "one\nthree\n")

        self.assertEqual(
            ["context", "removed", "added"],
            [line["kind"] for line in lines],
        )
        self.assertEqual((2, ""), (lines[1]["oldLine"], lines[1]["newLine"]))
        self.assertEqual(("", 2), (lines[2]["oldLine"], lines[2]["newLine"]))
        self.assertEqual("-", lines[1]["prefix"])
        self.assertEqual("+", lines[2]["prefix"])

    def test_line_counts_ignore_equal_context(self) -> None:
        added, removed = ChangeDiffService().line_counts("one\ntwo", "one\ntwo\nthree")
        self.assertEqual((1, 0), (added, removed))

    def test_initial_baseline_survives_save(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            document = JsonDocument(path=Path(temporary) / "file.json", text='{"value": 1}')
            document.set_text('{"value": 2}')
            document.mark_saved()
            self.assertFalse(document.is_dirty)
            self.assertTrue(document.has_changes_from_initial)
            document.set_text('{"value": 1}')
            self.assertFalse(document.has_changes_from_initial)


if __name__ == "__main__":
    unittest.main()
