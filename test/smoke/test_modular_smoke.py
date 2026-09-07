from __future__ import annotations

import importlib.util
import unittest


@unittest.skipUnless(importlib.util.find_spec("PySide6") is not None, "PySide6 is required for the Qt/QML smoke scenario")
class ModularSmokeTests(unittest.TestCase):
    def test_modular_smoke(self) -> None:
        from test.smoke.scenario import run_smoke_test

        self.assertEqual(run_smoke_test(["test-smoke"]), 0)
