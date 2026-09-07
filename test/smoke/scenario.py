from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from bootstrap.app_bootstrap import create_app, destroy_qml


def run_smoke_test(args: list[str] | None = None) -> int:
    """Executable black-box smoke scenario kept out of production bootstrap."""
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    previous_filter_path = os.environ.get("JSON_MULTI_EDITOR_FILTERS_PATH")
    previous_content_path = os.environ.get("JSON_MULTI_EDITOR_CONTENT_PATH")
    try:
        with tempfile.TemporaryDirectory(prefix="json_multi_editor_smoke_") as temp_dir:
            root = Path(temp_dir)
            filter_path = root / "config" / "filters.json"
            content_root = root / "content"
            report_root = _write_pbir_fixture(root)
            _write_smoke_content(content_root)
            os.environ["JSON_MULTI_EDITOR_FILTERS_PATH"] = str(filter_path)
            os.environ["JSON_MULTI_EDITOR_CONTENT_PATH"] = str(content_root)

            app, engine, graph = create_app(list(args or ["smoke-test"]))
            if not engine.rootObjects():
                raise AssertionError("QML root did not load.")
            controller = graph.shell_adapter
            try:
                filter_names = {item.display_name for item in controller.get_filters_model().filters() if item.is_read_only}
                assert {"Smoke Table", "Smoke Chart", "Smoke Page"}.issubset(filter_names)
                assert not filter_path.exists(), "Imported filters must not become user filters."

                macro_names = {macro.name for macro in controller.get_macro_model().items()}
                assert {"Find Target Key", "Apply Smoke Table Filter", "Set Table Title Blue"}.issubset(macro_names)
                assert next(item for item in controller.get_macro_model().items() if item.name == "Missing Filter Macro").validation_errors

                assert controller.scan_folder_paths([report_root]) == 5
                assert controller.get_folder_import_visible()
                assert controller.get_folder_scan_count() == 5
                assert controller.confirmFolderImport() == 4
                assert controller.get_file_count() == 4
                assert controller.get_project_tree_count() == 4

                documents = tuple(controller.get_file_model().documents())
                assert any(document.file_type_text == "Visual" for document in documents)
                assert any(document.file_type_text == "Page" for document in documents)
                assert any(document.file_type_text == "Json" for document in documents)
                assert any("visual.visualType" in document.text for document in documents)
                assert any(document.file_name == "other.json" for document in documents)

                controller.set_search_text("targetKey")
                controller.set_replace_text("changedKey")
                app.processEvents()
                assert controller.get_total_matches() == 2
                assert controller.replaceCurrentMatch() == 1
                assert controller.get_total_matches() == 1

                index = next(index for index, item in enumerate(controller.get_macro_model().items()) if item.name == "Find Target Key")
                assert controller.runMacro(index)
                _process_macro_events(app, controller)
                assert controller.get_search_text() == "targetKey"

                target_row = next(index for index, document in enumerate(controller.get_file_model().documents()) if "changedKey" in document.text)
                target_document = controller.get_file_model().document_at(target_row)
                assert target_document is not None and target_document.is_dirty
                assert controller.saveAll() >= 1
                assert not controller.get_file_model().document_at(target_row).is_dirty

                controller.openNewFilterEditor()
                controller.set_editing_filter_name("Target Key Contains")
                controller.set_editing_filter_target("All")
                controller.updateEditingRuleKey(0, "targetKey")
                controller.updateEditingRuleOperation(0, "includes")
                controller.updateEditingRuleValue(0, "red")
                assert controller.get_editing_filter_can_save()
                assert controller.saveFilterEditor()
                persisted = json.loads(filter_path.read_text(encoding="utf-8"))
                saved_filter = next(item for item in persisted["filters"] if item["displayName"] == "Target Key Contains")
                assert saved_filter["targetJsonFileType"] == "All"
                assert saved_filter["rules"][0]["operation"] == "includes"

                controller.startAgain()
                assert controller.get_file_count() == 0
                assert controller.get_project_tree_count() == 0
                assert controller.get_current_index() == -1
                assert controller.get_search_text() == ""
            finally:
                destroy_qml(app, engine, graph)
    finally:
        _restore_environment("JSON_MULTI_EDITOR_FILTERS_PATH", previous_filter_path)
        _restore_environment("JSON_MULTI_EDITOR_CONTENT_PATH", previous_content_path)
    print("Smoke test passed: folder import, search/replace, macros, save, filters, reset, and modular QML loading worked.")
    return 0


def _restore_environment(name: str, value: str | None) -> None:
    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value


def _write_pbir_fixture(root: Path) -> Path:
    report_root = root / "Sample.Report"
    page_root = report_root / "definition" / "pages" / "Page1"
    visuals_root = page_root / "visuals"
    for name in ("VisualTable", "VisualLine", "VisualBroken"):
        (visuals_root / name).mkdir(parents=True)
    (report_root / ".pbi").mkdir(parents=True)
    (page_root / "page.json").write_text(json.dumps({"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json", "name": "Page1", "displayName": "Retention Cockpit", "displayOption": "FitToPage", "height": 720, "width": 1280}, indent=2), encoding="utf-8")
    (visuals_root / "VisualTable" / "visual.json").write_text(json.dumps(_visual_payload("visualTable", "table", "Table Visual", "#111111"), indent=2), encoding="utf-8")
    (visuals_root / "VisualLine" / "visual.json").write_text(json.dumps(_visual_payload("visualLine", "lineChart", "Line Visual", "#222222"), indent=2), encoding="utf-8")
    (visuals_root / "VisualBroken" / "visual.json").write_text('{"name":"Broken","visual":{"visualType":"table"},"targetKey":"red",', encoding="utf-8")
    (report_root / ".pbi" / "localSettings.json").write_text('{"ignored":true}', encoding="utf-8")
    (page_root / "other.json").write_text('{"ignored":true}', encoding="utf-8")
    return report_root


def _visual_payload(name: str, visual_type: str, title: str, title_color: str) -> dict:
    return {"$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json", "name": name, "position": {"x": 10, "y": 20, "width": 300, "height": 200, "z": 1}, "visual": {"visualType": visual_type, "visualContainerObjects": {"title": [{"properties": {"text": {"expr": {"Literal": {"Value": "'" + title + "'"}}}, "fontColor": {"solid": {"color": title_color}}}}], "background": [{"properties": {"show": True, "color": {"solid": {"color": "#FFFFFF"}}, "transparency": 0}}]}}, "targetKey": "red"}


def _write_smoke_content(content_root: Path) -> None:
    filters_root, macros_root = content_root / "filters", content_root / "macros"
    filters_root.mkdir(parents=True)
    macros_root.mkdir(parents=True)
    for file_name, filter_id, name, target, key, operation, value, color in [
        ("table.json", "smoke.filter.table", "Smoke Table", "Visual", "visual.visualType", "equals", "table", "#4ec9b0"),
        ("chart.json", "smoke.filter.chart", "Smoke Chart", "Visual", "visual.visualType", "includes", "chart", "#c586c0"),
        ("page.json", "smoke.filter.page", "Smoke Page", "Page", "displayName", "includes", "Retention", "#dcdcaa"),
    ]:
        (filters_root / file_name).write_text(json.dumps({"id": filter_id, "displayName": name, "targetJsonFileType": target, "color": color, "rules": [{"key": key, "operation": operation, "value": value}]}, indent=2), encoding="utf-8")
    macros = {
        "find-target-key.json": {"id": "smoke.macro.find-target-key", "name": "Find Target Key", "steps": [{"type": "search", "searchValue": "targetKey"}]},
        "apply-table-filter.json": {"id": "smoke.macro.apply-table-filter", "name": "Apply Smoke Table Filter", "steps": [{"type": "filter", "filterName": "Smoke Table"}]},
        "set-title-blue.json": {"id": "smoke.macro.title-blue", "name": "Set Table Title Blue", "steps": [{"type": "filter-apply", "filterName": "Smoke Table"}, {"type": "visual-editor-change", "controlId": "general-title-font-color", "value": "#3B82F6"}]},
        "missing-filter.json": {"id": "smoke.macro.missing-filter", "name": "Missing Filter Macro", "steps": [{"type": "filter", "filterName": "Missing"}]},
    }
    for file_name, payload in macros.items():
        (macros_root / file_name).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _process_macro_events(app, controller) -> None:
    for _ in range(50):
        app.processEvents()
        if not controller.get_any_macro_running():
            return
    raise AssertionError("Macro did not finish within the event budget")
