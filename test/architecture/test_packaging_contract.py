from __future__ import annotations

import ast
import unittest
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[2]


class PackagingContractTests(unittest.TestCase):
    def test_specification_targets_modular_resource_roots(self) -> None:
        specification = (PROJECT / "MyApp.spec").read_text(encoding="utf-8")
        ast.parse(specification, filename="MyApp.spec")
        self.assertIn('Tree("src/ui", prefix="ui"', specification)
        self.assertIn('Tree("src/features", prefix="features"', specification)
        self.assertIn('("content", "content")', specification)
        self.assertNotIn("src/app/ui", specification)

    def test_build_script_uses_the_canonical_specification(self) -> None:
        build_script = (PROJECT / "tools" / "build.cmd").read_text(encoding="utf-8")
        self.assertIn('PyInstaller --noconfirm "MyApp.spec"', build_script)
        self.assertNotIn("--add-data", build_script)

    def test_resource_locator_and_qml_root_match_the_packaged_tree(self) -> None:
        locator = (PROJECT / "src" / "infrastructure" / "packaging" / "resource_locator.py").read_text(encoding="utf-8")
        bootstrap = (PROJECT / "src" / "bootstrap" / "app_bootstrap.py").read_text(encoding="utf-8")
        self.assertIn('source_root_path=root', locator)
        self.assertIn('loadFromModule(ROOT_MODULE_URI, ROOT_TYPE_NAME)', bootstrap)
        self.assertIn('engine.addImportPath(str(graph.resource_locator.source_root()))', bootstrap)
        self.assertIn('raise RuntimeError("QML module load emitted warning(s); see diagnostics above.")', bootstrap)


if __name__ == "__main__":
    unittest.main()
