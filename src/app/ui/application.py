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

    with tempfile.TemporaryDirectory(prefix="json_multi_editor_") as temp_dir:
        root = Path(temp_dir)
        filter_path = root / "config" / "filters.json"
        os.environ["JSON_MULTI_EDITOR_FILTERS_PATH"] = str(filter_path)

        app, engine, controller, _syntax_bridge = create_app(args)
        if not engine.rootObjects():
            print("Smoke test failed: QML root did not load.")
            return 1

        try:
            filters = controller.get_filters_model().filters()
            default_filter_names = {content_filter.display_name for content_filter in filters}
            assert {"Table", "Chart"}.issubset(default_filter_names), "Default filters were not created"
            assert filter_path.exists(), "Default filters should be persisted on first run"

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

            documents = list(controller.get_file_model().documents())
            display_names = {document.name for document in documents}
            assert {"Table View", "Chart View"}.issubset(display_names), "Display names should come from JSON content"
            assert any(not document.is_valid_json for document in documents), "Invalid JSON fixture should stay loaded"
            chart_filter_index = next(
                index for index, content_filter in enumerate(controller.get_filters_model().filters()) if content_filter.display_name == "Chart"
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
                index for index, content_filter in enumerate(controller.get_filters_model().filters()) if content_filter.display_name == "Table"
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

    print(
        "Smoke test passed: QML loaded, visual.json import worked, filters persisted, active-only search/replace behaved correctly."
    )
    return 0

