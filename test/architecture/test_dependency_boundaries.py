from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "src"


def imports_for(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
    result: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            result.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            result.add(node.module)
    return result


def feature_name_for(path: Path) -> str:
    return path.relative_to(ROOT / "features").parts[0]


class DependencyBoundaryTests(unittest.TestCase):
    def test_entities_do_not_depend_on_framework_or_application_layers(self) -> None:
        for path in (ROOT / "entities").rglob("*.py"):
            forbidden = [value for value in imports_for(path) if value.startswith(("PySide6", "features", "ui", "infrastructure", "services"))]
            self.assertEqual(forbidden, [], f"{path}: forbidden imports {forbidden}")

    def test_services_do_not_depend_on_qt_or_ui(self) -> None:
        for path in (ROOT / "services").rglob("*.py"):
            forbidden = [value for value in imports_for(path) if value.startswith(("PySide6", "ui"))]
            self.assertEqual(forbidden, [], f"{path}: forbidden imports {forbidden}")

    def test_feature_application_code_does_not_import_framework_presentation_or_infrastructure(self) -> None:
        for path in (ROOT / "features").glob("*/application/*.py"):
            own_feature = feature_name_for(path)
            forbidden: list[str] = []
            for value in imports_for(path):
                if value.startswith(("PySide6", "ui", "infrastructure")) or ".presentation" in value:
                    forbidden.append(value)
                elif value.startswith("features."):
                    parts = value.split(".")
                    if len(parts) > 1 and parts[1] != own_feature:
                        forbidden.append(value)
            self.assertEqual(forbidden, [], f"{path}: forbidden imports {forbidden}")

    def test_features_use_only_other_feature_public_apis(self) -> None:
        for path in (ROOT / "features").rglob("*.py"):
            own_feature = feature_name_for(path)
            forbidden: list[str] = []
            for value in imports_for(path):
                if not value.startswith("features."):
                    continue
                parts = value.split(".")
                if len(parts) > 1 and parts[1] != own_feature and not value.endswith(".public"):
                    forbidden.append(value)
            self.assertEqual(forbidden, [], f"{path}: private cross-feature imports {forbidden}")

    def test_ui_does_not_depend_on_bootstrap(self) -> None:
        for path in (ROOT / "ui").rglob("*.py"):
            forbidden = [value for value in imports_for(path) if value == "bootstrap" or value.startswith("bootstrap.")]
            self.assertEqual(forbidden, [], f"{path}: UI must not import bootstrap: {forbidden}")

    def test_no_new_code_uses_legacy_app_package(self) -> None:
        for path in ROOT.rglob("*.py"):
            forbidden = [value for value in imports_for(path) if value == "app" or value.startswith("app.")]
            self.assertEqual(forbidden, [], f"{path}: legacy imports {forbidden}")


if __name__ == "__main__":
    unittest.main()
