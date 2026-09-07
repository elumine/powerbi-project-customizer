from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication, QStyleFactory

from app.ui.app_controller import AppController
from app.ui.json_highlighter import SyntaxHighlighterBridge


QML_FILE = Path(__file__).resolve().parent / "qml" / "App.qml"
STYLE_FILE = Path(__file__).resolve().parent / "styles" / "vscode.qss"


def run(argv: list[str] | None = None) -> int:
    args = list(sys.argv if argv is None else argv)
    if "--smoke-test" in args:
        return run_smoke_test(args)

    app, engine, _controller, _syntax_bridge = create_app(args)
    if not engine.rootObjects():
        return 1

    exit_code = app.exec()
    destroy_qml(app, engine)
    return exit_code


def create_app(args: list[str]) -> tuple[QApplication, QQmlApplicationEngine, AppController, SyntaxHighlighterBridge]:
    QQuickStyle.setStyle("Fusion")
    app = QApplication(args)

    fusion = QStyleFactory.create("Fusion")
    if fusion is not None:
        app.setStyle(fusion)
    if STYLE_FILE.exists():
        app.setStyleSheet(STYLE_FILE.read_text(encoding="utf-8"))

    controller = AppController()
    syntax_bridge = SyntaxHighlighterBridge()
    engine = QQmlApplicationEngine()
    engine.warnings.connect(lambda warnings: [print(warning.toString()) for warning in warnings])
    engine.rootContext().setContextProperty("appController", controller)
    engine.rootContext().setContextProperty("syntaxBridge", syntax_bridge)
    engine.load(QUrl.fromLocalFile(str(QML_FILE)))
    return app, engine, controller, syntax_bridge


def destroy_qml(app: QApplication, engine: QQmlApplicationEngine) -> None:
    for root_object in engine.rootObjects():
        root_object.setProperty("visible", False)
        root_object.deleteLater()
    app.processEvents()


def run_smoke_test(args: list[str]) -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    previous_filter_path = os.environ.get("JSON_MULTI_EDITOR_FILTERS_PATH")
    previous_content_path = os.environ.get("JSON_MULTI_EDITOR_CONTENT_PATH")

    with tempfile.TemporaryDirectory(prefix="json_multi_editor_v5_") as temp_dir:
        root = Path(temp_dir)
        filter_path = root / "config" / "filters.json"
        content_root = root / "content"
        report_root = _write_pbir_fixture(root)
        _write_smoke_content(content_root)
        os.environ["JSON_MULTI_EDITOR_FILTERS_PATH"] = str(filter_path)
        os.environ["JSON_MULTI_EDITOR_CONTENT_PATH"] = str(content_root)

        app, engine, controller, _syntax_bridge = create_app(args)
        if not engine.rootObjects():
            print("Smoke test failed: QML root did not load.")
            return 1

        try:
            filters = controller.get_filters_model().filters()
            filter_names = {content_filter.display_name for content_filter in filters if content_filter.is_read_only}
            assert {"Smoke Table", "Smoke Chart", "Smoke Page"}.issubset(filter_names), "Imported filters should load"
            assert not filter_path.exists(), "Imported filters should not be persisted as user filter copies"

            macros = controller.get_macro_model().items()
            macro_names = {macro.name for macro in macros}
            assert {"Find Target Key", "Apply Smoke Table Filter", "Set Table Title Blue"}.issubset(macro_names), "Imported macros were not loaded"
            invalid_macro = next(macro for macro in macros if macro.name == "Missing Filter Macro")
            assert invalid_macro.validation_errors, "Invalid macros should display validation errors"

            found = controller.scan_folder_paths([report_root])
            assert found == 5, "Folder scan should include every non-skipped JSON file"
            assert controller.get_folder_import_visible(), "Folder scan should open import modal state"
            assert controller.get_folder_scan_count() == 5, "Folder scan model did not update"
            added = controller.confirmFolderImport()
            assert added == 4, "Folder import should add valid JSON files and skip invalid JSON during flattening"
            assert controller.get_file_count() == 4, "Imported JSON files did not reach file model"
            assert controller.get_project_tree_count() == 4, "Project tree should show imported flat JSON files"

            documents = list(controller.get_file_model().documents())
            assert any(document.file_type_text == "Visual" for document in documents), "Flattened visual imports should remain classified as Visual"
            assert any(document.file_type_text == "Page" for document in documents), "Flattened page imports should remain classified as Page"
            assert any(document.file_type_text == "Json" for document in documents), "Generic flattened imports should remain classified as Json"
            assert any("visual.visualType" in document.text for document in documents), "PBIR visual JSON should be flattened on read"
            assert any(document.file_name == "other.json" for document in documents), "Folder import should include generic JSON files"

            controller.set_search_text("targetKey")
            controller.set_replace_text("changedKey")
            app.processEvents()
            assert controller.get_total_matches() == 2, "Search should include active flattened JSON documents"
            assert controller.replaceCurrentMatch() == 1, "Replace should change one selected/first match"
            assert controller.get_total_matches() == 1, "Single replace should refresh remaining match positions"

            find_macro_index = next(index for index, macro in enumerate(controller.get_macro_model().items()) if macro.name == "Find Target Key")
            assert controller.runMacro(find_macro_index), "Valid search macro should start"
            _process_macro_events(app, controller)
            assert controller.get_search_text() == "targetKey", "Search macro should set the search value"

            target_row = next(index for index, document in enumerate(controller.get_file_model().documents()) if "changedKey" in document.text)
            target_document = controller.get_file_model().document_at(target_row)
            assert target_document is not None and target_document.is_dirty, "Replace should mark flattened JSON dirty"
            assert controller.saveAll() >= 1, "Save All should save dirty flattened JSON files"
            assert not controller.get_file_model().document_at(target_row).is_dirty, "Saved flattened JSON should be marked clean"

            controller.openNewFilterEditor()
            controller.set_editing_filter_name("Target Key Contains")
            controller.set_editing_filter_target("All")
            controller.updateEditingRuleKey(0, "targetKey")
            controller.updateEditingRuleOperation(0, "includes")
            controller.updateEditingRuleValue(0, "red")
            assert controller.get_editing_filter_can_save(), "Valid flat JSON filter should be saveable"
            assert controller.saveFilterEditor(), "Flat JSON filter should save"
            persisted = json.loads(filter_path.read_text(encoding="utf-8"))
            saved_filter = next(item for item in persisted["filters"] if item["displayName"] == "Target Key Contains")
            assert saved_filter["targetJsonFileType"] == "All", "Saved flat JSON filters should persist targetJsonFileType"
            assert saved_filter["rules"][0]["operation"] == "includes", "Filter operation selector should preserve includes"

            controller.startAgain()
            assert controller.get_file_count() == 0, "Start Again should clear loaded files"
            assert controller.get_project_tree_count() == 0, "Start Again should clear project tree"
            assert controller.get_current_index() == -1, "Start Again should clear selection"
            assert controller.get_search_text() == "", "Start Again should clear search"
        finally:
            app.processEvents()
            destroy_qml(app, engine)
            if previous_filter_path is None:
                os.environ.pop("JSON_MULTI_EDITOR_FILTERS_PATH", None)
            else:
                os.environ["JSON_MULTI_EDITOR_FILTERS_PATH"] = previous_filter_path
            if previous_content_path is None:
                os.environ.pop("JSON_MULTI_EDITOR_CONTENT_PATH", None)
            else:
                os.environ["JSON_MULTI_EDITOR_CONTENT_PATH"] = previous_content_path

    print("Smoke test passed: flat JSON folder import, search replace, macros, save, filters, and reset worked.")
    return 0


def _write_pbir_fixture(root: Path) -> Path:
    report_root = root / "Sample.Report"
    page_root = report_root / "definition" / "pages" / "Page1"
    visuals_root = page_root / "visuals"
    (visuals_root / "VisualTable").mkdir(parents=True)
    (visuals_root / "VisualLine").mkdir(parents=True)
    (visuals_root / "VisualBroken").mkdir(parents=True)
    (report_root / ".pbi").mkdir(parents=True)

    (page_root / "page.json").write_text(json.dumps({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "Page1",
        "displayName": "Retention Cockpit",
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280
    }, indent=2), encoding="utf-8")
    (visuals_root / "VisualTable" / "visual.json").write_text(json.dumps(_visual_payload("visualTable", "table", "Table Visual", "#111111"), indent=2), encoding="utf-8")
    (visuals_root / "VisualLine" / "visual.json").write_text(json.dumps(_visual_payload("visualLine", "lineChart", "Line Visual", "#222222"), indent=2), encoding="utf-8")
    (visuals_root / "VisualBroken" / "visual.json").write_text('{"name":"Broken","visual":{"visualType":"table"},"targetKey":"red",', encoding="utf-8")
    (report_root / ".pbi" / "localSettings.json").write_text('{"ignored":true}', encoding="utf-8")
    (page_root / "other.json").write_text('{"ignored":true}', encoding="utf-8")
    return report_root


def _visual_payload(name: str, visual_type: str, title: str, title_color: str) -> dict:
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json",
        "name": name,
        "position": {"x": 10, "y": 20, "width": 300, "height": 200, "z": 1},
        "visual": {
            "visualType": visual_type,
            "visualContainerObjects": {
                "title": [{
                    "properties": {
                        "text": {"expr": {"Literal": {"Value": "'" + title + "'"}}},
                        "fontColor": {"solid": {"color": title_color}}
                    }
                }],
                "background": [{"properties": {"show": True, "color": {"solid": {"color": "#FFFFFF"}}, "transparency": 0}}]
            }
        },
        "targetKey": "red"
    }


def _write_smoke_content(content_root: Path) -> None:
    filters_root = content_root / "filters"
    macros_root = content_root / "macros"
    filters_root.mkdir(parents=True)
    macros_root.mkdir(parents=True)
    filters = [
        ("table.json", "smoke.filter.table", "Smoke Table", "Visual", "visual.visualType", "equals", "table", "#4ec9b0"),
        ("chart.json", "smoke.filter.chart", "Smoke Chart", "Visual", "visual.visualType", "includes", "chart", "#c586c0"),
        ("page.json", "smoke.filter.page", "Smoke Page", "Page", "displayName", "includes", "Retention", "#dcdcaa"),
    ]
    for file_name, filter_id, display_name, target, key, operation, value, color in filters:
        (filters_root / file_name).write_text(json.dumps({
            "id": filter_id,
            "displayName": display_name,
            "targetJsonFileType": target,
            "color": color,
            "rules": [{"key": key, "operation": operation, "value": value}],
        }, indent=2), encoding="utf-8")
    macros = {
        "find-target-key.json": {"id": "smoke.macro.find-target-key", "name": "Find Target Key", "steps": [{"type": "search", "searchValue": "targetKey"}]},
        "apply-table-filter.json": {"id": "smoke.macro.apply-table-filter", "name": "Apply Smoke Table Filter", "steps": [{"type": "filter", "filterName": "Smoke Table"}]},
        "set-title-blue.json": {"id": "smoke.macro.title-blue", "name": "Set Table Title Blue", "steps": [{"type": "filter-apply", "filterName": "Smoke Table"}, {"type": "visual-editor-change", "controlId": "general-title-font-color", "value": "#3B82F6"}]},
        "missing-filter.json": {"id": "smoke.macro.missing-filter", "name": "Missing Filter Macro", "steps": [{"type": "filter", "filterName": "Missing"}]},
    }
    for file_name, payload in macros.items():
        (macros_root / file_name).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _process_macro_events(app: QApplication, controller: AppController) -> None:
    for _attempt in range(50):
        app.processEvents()
        if not controller.get_any_macro_running():
            return
    raise AssertionError("Macro did not finish within the smoke-test event budget")




