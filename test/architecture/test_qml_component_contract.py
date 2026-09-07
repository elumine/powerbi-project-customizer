from __future__ import annotations

import re
import unittest
from pathlib import Path

from ui.styles.theme_tokens import DEFAULT_THEME


ROOT = Path(__file__).resolve().parents[2] / "src"


class QmlComponentContractTests(unittest.TestCase):
    def test_every_component_folder_has_markup_logic_and_style(self) -> None:
        component_roots = [
            ROOT / "ui" / "component",
            ROOT / "ui" / "pages",
            *[path / "presentation" / "component" for path in (ROOT / "features").iterdir() if path.is_dir()],
        ]
        missing: list[str] = []
        for root in component_roots:
            if not root.exists():
                continue
            for component in root.rglob("*"):
                if not component.is_dir() or component.name in {"component", "app", "primitives", "shell", "pages"}:
                    continue
                markup = component / f"{component.name}.qml"
                if not markup.exists():
                    continue
                required = [markup, component / f"{component.name}Logic.js", component / f"{component.name}Style.qml"]
                if not all(path.exists() for path in required):
                    missing.append(str(component.relative_to(ROOT)))
                    continue
                markup_text = markup.read_text(encoding="utf-8")
                if (
                    f'"{component.name}Logic.js" as Logic' not in markup_text
                    or "Logic." not in markup_text
                    or f"{component.name}Style {{" not in markup_text
                ):
                    missing.append(str(component.relative_to(ROOT)) + " (markup does not invoke local logic and style)")
        self.assertEqual(missing, [], f"Component folders missing or not using markup/logic/style files: {missing}")

    def test_all_public_qml_modules_have_qmldir_manifests(self) -> None:
        expected = [
            ROOT / "ui" / "styles" / "qmldir",
            ROOT / "ui" / "component" / "app" / "qmldir",
            ROOT / "ui" / "component" / "primitives" / "qmldir",
            ROOT / "ui" / "component" / "shell" / "qmldir",
            ROOT / "ui" / "pages" / "qmldir",
        ]
        expected.extend(path / "presentation" / "qmldir" for path in (ROOT / "features").iterdir() if (path / "presentation" / "component").exists())
        self.assertEqual([str(path) for path in expected if not path.exists()], [])

    def test_qml_color_declarations_import_qtquick(self) -> None:
        missing = [
            str(path.relative_to(ROOT))
            for path in ROOT.rglob("*.qml")
            if "property color" in path.read_text(encoding="utf-8")
            and "import QtQuick" not in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(missing, [], f"QML color types require QtQuick imports: {missing}")

    def test_qml_theme_matches_python_presentation_tokens(self) -> None:
        theme = (ROOT / "ui" / "styles" / "Theme.qml").read_text(encoding="utf-8")
        qml_values = dict(re.findall(r"readonly property color (\w+): \"(#[0-9a-fA-F]{6})\"", theme))
        for qml_name, value in qml_values.items():
            snake_name = re.sub(r"(?<!^)([A-Z])", r"_\1", qml_name).lower()
            self.assertEqual(getattr(DEFAULT_THEME, snake_name), value, qml_name)

    def test_visual_editor_category_activation_uses_its_combo_instance(self) -> None:
        panel = ROOT / "features" / "visual_editor" / "presentation" / "component" / "VisualEditorPanel" / "VisualEditorPanel.qml"
        markup = panel.read_text(encoding="utf-8")
        self.assertIn("id: categoryCombo", markup)
        self.assertIn("categoryCombo.optionEnabled(option)", markup)
        self.assertIn("categoryCombo.optionValue(option)", markup)

    def test_qmldir_public_type_paths_exist(self) -> None:
        missing: list[str] = []
        for manifest in ROOT.rglob("qmldir"):
            for line in manifest.read_text(encoding="utf-8").splitlines():
                values = line.split()
                if len(values) != 3 or values[0] in {"module", "singleton"}:
                    continue
                source = manifest.parent / values[2]
                if not source.exists():
                    missing.append(f"{manifest.relative_to(ROOT)} -> {values[2]}")
        self.assertEqual(missing, [], f"qmldir points to missing QML files: {missing}")


if __name__ == "__main__":
    unittest.main()
