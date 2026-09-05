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

    with tempfile.TemporaryDirectory(prefix="json_multi_editor_") as temp_dir:
        root = Path(temp_dir)
        filter_path = root / "config" / "filters.json"
        content_root = root / "content"
        _write_smoke_content(content_root)
        os.environ["JSON_MULTI_EDITOR_FILTERS_PATH"] = str(filter_path)
        os.environ["JSON_MULTI_EDITOR_CONTENT_PATH"] = str(content_root)

        app, engine, controller, _syntax_bridge = create_app(args)
        if not engine.rootObjects():
            print("Smoke test failed: QML root did not load.")
            return 1

        try:
            filters = controller.get_filters_model().filters()
            default_filter_names = {content_filter.display_name for content_filter in filters if content_filter.is_read_only}
            assert {"Smoke Table", "Smoke Chart"}.issubset(default_filter_names), "Smoke filters should load from content JSON files"
            assert not filter_path.exists(), "Imported filters should not be persisted as user filter copies"
            chart_filter_index = next(
                index for index, content_filter in enumerate(filters) if content_filter.display_name == "Smoke Chart"
            )
            assert not controller.openEditFilterEditor(chart_filter_index), "Imported filters should be read-only"

            macros = controller.get_macro_model().items()
            macro_names = {macro.name for macro in macros}
            assert {"Find Target Key", "Apply Smoke Table Filter"}.issubset(macro_names), "Imported macros were not loaded"
            invalid_macro = next(macro for macro in macros if macro.name == "Missing Filter Macro")
            assert invalid_macro.validation_errors, "Invalid macros should display validation errors"

            visual_table = root / "theme-a" / "visual.json"
            visual_chart = root / "nested" / "theme-b" / "visual.json"
            visual_invalid = root / "broken" / "visual.json"
            ignored = root / "nested" / "theme-b" / "other.json"
            visual_table.parent.mkdir(parents=True)
            visual_chart.parent.mkdir(parents=True)
            visual_invalid.parent.mkdir(parents=True)
            visual_table.write_text(
                '{"name": "Table View", "visualType": "table", "targetKey": "red", "value": "red"}',
                encoding="utf-8",
            )
            visual_chart.write_text(
                '{"Title": "Chart View", "visualType": "lineChart", "targetKey": "red"}',
                encoding="utf-8",
            )
            visual_invalid.write_text(
                '{"name": "Broken View", "visualType": "table", "targetKey": "red",',
                encoding="utf-8",
            )
            ignored.write_text('{"name": "Ignored", "targetKey": "red"}', encoding="utf-8")

            found = controller.scan_folder_paths([root])
            assert found == 3, "Folder scan should include only visual.json files"
            assert controller.get_folder_import_visible(), "Folder scan should open import modal state"
            assert controller.get_folder_scan_count() == 3, "Folder scan model did not update"

            root_object = engine.rootObjects()[0]
            root_object.setProperty("pageName", "management")
            root_object.setProperty("activePanel", "search")
            app.processEvents()

            added = controller.confirmFolderImport()
            assert added == 3, "Folder import should add scanned visual.json files"
            assert controller.get_file_count() == 3, "Imported files did not reach file model"
            assert controller.get_active_file_count() == 3, "All files should be active before applying a filter"
            app.processEvents()

            key_suggestions = controller.get_suggestion_key_model().items()
            visual_type_index = next(
                index for index, suggestion in enumerate(key_suggestions) if suggestion.duplication_value == "visualType"
            )
            visual_type_suggestion = key_suggestions[visual_type_index]
            assert visual_type_suggestion.duplication_count == 2, "Suggestions should ignore invalid JSON files"
            value_suggestion = next(
                suggestion for suggestion in controller.get_suggestion_value_model().items() if suggestion.duplication_value == "red"
            )
            assert value_suggestion.duplication_count == 3, "Primitive duplicate values should be counted"
            assert controller.openSuggestionSearch("key", visual_type_index), "Suggestion search should open from duplicate text"
            assert controller.get_search_text() == "visualType", "Suggestion search should set the search input"
            assert controller.get_total_matches() == 3, "Suggestion-triggered search should use active-file search behavior"

            find_macro_index = next(index for index, macro in enumerate(controller.get_macro_model().items()) if macro.name == "Find Target Key")
            assert controller.runMacro(find_macro_index), "Valid search macro should start"
            _process_macro_events(app, controller)
            assert controller.get_search_text() == "targetKey", "Search macro should set the search value"
            assert controller.get_total_matches() == 3, "Search macro should run against active files"

            apply_table_macro_index = next(index for index, macro in enumerate(controller.get_macro_model().items()) if macro.name == "Apply Smoke Table Filter")
            assert controller.runMacro(apply_table_macro_index), "Valid filter macro should start"
            _process_macro_events(app, controller)
            assert controller.get_active_filter_name() == "Smoke Table", "Filter macro should apply the named smoke filter"
            assert controller.get_active_file_count() == 1, "Table macro should activate only table visuals"
            controller.deactivateFilter()
            app.processEvents()

            documents = list(controller.get_file_model().documents())
            display_names = {document.name for document in documents}
            assert {"Table View", "Chart View"}.issubset(display_names), "Display names should come from JSON content"
            assert any(not document.is_valid_json for document in documents), "Invalid JSON fixture should stay loaded"
            chart_filter_index = next(
                index for index, content_filter in enumerate(controller.get_filters_model().filters()) if content_filter.display_name == "Smoke Chart"
            )
            controller.applyFilter(chart_filter_index)
            app.processEvents()
            documents = list(controller.get_file_model().documents())
            chart_row = next(index for index, document in enumerate(documents) if document.name == "Chart View")
            assert controller.get_active_file_count() == 1, "Chart filter should activate only chart visuals"
            assert documents[chart_row].is_active, "Chart visual should match the Chart filter case-insensitively"
            controller.deactivateFilter()
            app.processEvents()

            controller.set_search_text("targetKey")
            app.processEvents()
            assert controller.get_total_matches() == 3, "Search should include invalid JSON when no content filter is active"
            first_document = controller.get_file_model().document_at(0)
            assert first_document is not None and first_document.match_previews, "Search previews were not generated"
            assert "background-color" in first_document.highlighted_html, "Highlighted HTML was not generated"

            table_filter_index = next(
                index for index, content_filter in enumerate(controller.get_filters_model().filters()) if content_filter.display_name == "Smoke Table"
            )
            controller.applyFilter(table_filter_index)
            app.processEvents()
            documents = list(controller.get_file_model().documents())
            table_row = next(index for index, document in enumerate(documents) if document.name == "Table View")
            chart_row = next(index for index, document in enumerate(documents) if document.name == "Chart View")
            invalid_row = next(index for index, document in enumerate(documents) if not document.is_valid_json)
            assert controller.get_has_active_filter(), "Table filter should be active"
            assert controller.get_active_file_count() == 1, "Table filter should activate only the table visual"
            assert documents[table_row].is_active, "Table visual should match the Table filter"
            assert not documents[chart_row].is_active, "Chart visual should be inactive under the Table filter"
            assert not documents[invalid_row].is_active, "Invalid JSON should be inactive while a content filter is active"
            controller.set_current_index(chart_row)
            assert controller.get_current_index() == table_row, "Inactive files should not become the selected editor document"

            controller.set_search_text("red")
            controller.set_replace_text("blue")
            app.processEvents()
            assert controller.get_total_matches() == 2, "Search should count matches only in active files"
            replaced = controller.replaceAll()
            assert replaced == 2, "Replace-all should replace only active table matches"
            documents = list(controller.get_file_model().documents())
            assert '"blue"' in documents[table_row].text, "Active table file was not replaced"
            assert '"red"' in documents[chart_row].text, "Inactive chart file should not be replaced"
            assert '"red"' in documents[invalid_row].text, "Inactive invalid file should not be replaced"

            controller.updateFileText(table_row, '{"name": "Table View", "visualType": "card", "targetKey": "blue"}')
            controller._apply_active_filter_state()
            app.processEvents()
            assert controller.get_active_file_count() == 0, "Edited table file should leave the active filter when it no longer matches"
            assert controller.get_current_index() == -1, "No editor document should remain selected when no active files exist"

            controller.deactivateFilter()
            app.processEvents()
            assert controller.get_active_file_count() == 3, "Deactivating filters should reactivate all files"
            controller.set_search_text("red")
            controller.set_replace_text("")
            app.processEvents()
            assert controller.get_total_matches() == 2, "Inactive files should return to search after filter deactivation"

            controller.openNewFilterEditor()
            controller.set_editing_filter_name("Blue Target")
            controller.updateEditingRuleKey(0, "targetKey")
            controller.updateEditingRuleOperation(0, "equals")
            controller.updateEditingRuleValue(0, "blue")
            assert controller.get_editing_filter_can_save(), "Valid new filter should be saveable"
            assert controller.saveFilterEditor(), "New filter should save"
            saved_filters = controller.get_filters_model().filters()
            new_filter = next(content_filter for content_filter in saved_filters if content_filter.display_name == "Blue Target")
            persisted = json.loads(filter_path.read_text(encoding="utf-8"))
            assert any(item["id"] == new_filter.id for item in persisted["filters"]), "New filter should be persisted"
            assert all(item["id"] not in {"smoke.filter.table", "smoke.filter.chart"} for item in persisted["filters"]), "Imported filters should not be persisted"

            new_filter_index = next(index for index, content_filter in enumerate(saved_filters) if content_filter.id == new_filter.id)
            controller.applyFilter(new_filter_index)
            app.processEvents()
            assert controller.get_active_file_count() == 1, "Custom filter should activate the edited blue file"

            controller.openEditFilterEditor(new_filter_index)
            controller.set_editing_filter_name("Blue Target Renamed")
            assert controller.saveFilterEditor(), "Edited filter should save"
            renamed_filters = controller.get_filters_model().filters()
            renamed_filter = next(content_filter for content_filter in renamed_filters if content_filter.id == new_filter.id)
            assert renamed_filter.display_name == "Blue Target Renamed", "Editing should keep filter id and update name"

            renamed_filter_index = next(index for index, content_filter in enumerate(renamed_filters) if content_filter.id == new_filter.id)
            controller.deleteFilter(renamed_filter_index)
            app.processEvents()
            assert controller.get_active_file_count() == 3, "Deleting the active filter should reactivate all files"
            persisted_after_delete = json.loads(filter_path.read_text(encoding="utf-8"))
            assert all(item["id"] != new_filter.id for item in persisted_after_delete["filters"]), "Deleted filter should be removed from persistence"
            assert '"red"' in ignored.read_text(encoding="utf-8"), "Non-visual.json file should not be imported or changed"
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

    print(
        "Smoke test passed: QML loaded, content filters/macros imported, suggestions worked, and active-only search/replace behaved correctly."
    )
    return 0


def _write_smoke_content(content_root: Path) -> None:
    filters_root = content_root / "filters"
    macros_root = content_root / "macros"
    filters_root.mkdir(parents=True)
    macros_root.mkdir(parents=True)
    (filters_root / "table.json").write_text(
        json.dumps(
            {
                "id": "smoke.filter.table",
                "displayName": "Smoke Table",
                "color": "#4ec9b0",
                "rules": [{"key": "visualType", "operation": "equals", "value": "table"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (filters_root / "chart.json").write_text(
        json.dumps(
            {
                "id": "smoke.filter.chart",
                "displayName": "Smoke Chart",
                "color": "#c586c0",
                "rules": [{"key": "visualType", "operation": "includes", "value": "chart"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (macros_root / "find-target-key.json").write_text(
        json.dumps(
            {
                "id": "builtin.macro.find-target-key",
                "name": "Find Target Key",
                "steps": [{"type": "search", "searchValue": "targetKey"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (macros_root / "apply-table-filter.json").write_text(
        json.dumps(
            {
                "id": "smoke.macro.apply-table-filter",
                "name": "Apply Smoke Table Filter",
                "steps": [{"type": "filter", "filterName": "Smoke Table"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (macros_root / "missing-filter.json").write_text(
        json.dumps(
            {
                "id": "smoke.macro.missing-filter",
                "name": "Missing Filter Macro",
                "steps": [{"type": "filter", "filterName": "Missing"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _process_macro_events(app: QApplication, controller: AppController) -> None:
    for _attempt in range(50):
        app.processEvents()
        if not controller.get_any_macro_running():
            return
    raise AssertionError("Macro did not finish within the smoke-test event budget")