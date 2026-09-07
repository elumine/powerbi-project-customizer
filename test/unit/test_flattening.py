from __future__ import annotations

import json
import unittest

from services.documents.flattening import flatten_json, flatten_json_text


class FlatteningContractTests(unittest.TestCase):
    def test_escapes_path_delimiters_and_preserves_array_indexes(self) -> None:
        result = flatten_json({"a.b": {"[value]": [{"slash\\key": 3}]}})
        self.assertEqual(result, {r"a\.b.\[value\].[0].slash\\key": 3})

    def test_preserves_empty_structures_and_root_values(self) -> None:
        self.assertEqual(flatten_json({"empty": {}, "items": []}), {"empty": {}, "items": []})
        self.assertEqual(flatten_json(["a", "b"]), {"[0]": "a", "[1]": "b"})
        self.assertEqual(flatten_json(5), {"": 5})

    def test_text_output_is_valid_flat_json(self) -> None:
        output = flatten_json_text('{"visual":{"visualType":"table"}}')
        self.assertEqual(json.loads(output), {"visual.visualType": "table"})


if __name__ == "__main__":
    unittest.main()
