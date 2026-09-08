from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2] / "src"


class DashboardRefinementTests(unittest.TestCase):
    def test_recording_control_has_record_and_stop_shapes(self) -> None:
        header = (ROOT / "ui" / "component" / "shell" / "AppHeader" / "AppHeader.qml").read_text(encoding="utf-8")
        self.assertIn('readonly property bool recording', header)
        self.assertIn('radius: recordingButton.recording ? Geometry.radiusXs : width / 2', header)
        self.assertIn('color: Theme.accentRed', header)
        self.assertIn('color: Theme.white', header)

    def test_quick_filter_rows_cover_name_type_and_page(self) -> None:
        filter_panel = (ROOT / "features" / "filters" / "presentation" / "component" / "FilterPanel" / "FilterPanel.qml").read_text(encoding="utf-8")
        self.assertIn("applyDynamicVisualNameFilter", filter_panel)
        self.assertIn("applyDynamicVisualTypeFilter", filter_panel)
        self.assertIn("applyDynamicPageNameFilter", filter_panel)
        self.assertIn("Filter by visual name", filter_panel)
        self.assertIn("Filter by visual type", filter_panel)
        self.assertIn("Filter by page name", filter_panel)

    def test_filter_cards_keep_only_the_compact_dynamic_target_chip(self) -> None:
        filter_panel = (ROOT / "features" / "filters" / "presentation" / "component" / "FilterPanel" / "FilterPanel.qml").read_text(encoding="utf-8")
        self.assertIn("chipColor: filterHue", filter_panel)
        self.assertIn("chipTextColor: Theme.contrastText(filterHue)", filter_panel)
        self.assertNotIn('targetJsonFileType === "Visual"', filter_panel)
        self.assertNotIn("Layout.preferredWidth: 34", filter_panel)

    def test_empty_workspace_hides_header_tabs_and_loaded_badge(self) -> None:
        header = (ROOT / "ui" / "component" / "shell" / "AppHeader" / "AppHeader.qml").read_text(encoding="utf-8")
        picker = (ROOT / "ui" / "pages" / "FilePickerPage" / "FilePickerPage.qml").read_text(encoding="utf-8")
        self.assertIn('visible: app.controller.fileCount > 0', header)
        self.assertIn('color: Theme.white', header)
        self.assertIn('color: Theme.accentRed', header)
        self.assertIn('visible: app.controller.fileCount > 0', picker)

    def test_sidebar_uses_packaged_svg_assets_and_enlarged_icons(self) -> None:
        sidebar = (ROOT / "ui" / "component" / "shell" / "PanelsSidebar" / "PanelsSidebar.qml").read_text(encoding="utf-8")
        button = (ROOT / "ui" / "component" / "primitives" / "PanelButton" / "PanelButton.qml").read_text(encoding="utf-8")
        icon_button = (ROOT / "ui" / "component" / "primitives" / "IconButton" / "IconButton.qml").read_text(encoding="utf-8")
        self.assertIn('assets/icons/workspace.svg', sidebar)
        self.assertIn('iconSource: modelData.icon', sidebar)
        self.assertIn('Typography.sectionSize * 2', button)
        self.assertIn('Typography.sectionSize * 2', icon_button)

    def test_visual_editor_match_toggle_is_compact_and_in_header_row(self) -> None:
        editor = (ROOT / "features" / "visual_editor" / "presentation" / "component" / "VisualEditorPanel" / "VisualEditorPanel.qml").read_text(encoding="utf-8")
        self.assertIn("Layout.preferredWidth: 20", editor)
        self.assertIn("Layout.preferredHeight: 20", editor)
        self.assertLess(editor.index('Layout.preferredWidth: 20'), editor.index('text: controlMatches.length + " existing values"'))

    def test_visual_editor_shows_all_currently_applicable_controls(self) -> None:
        editor = (ROOT / "features" / "visual_editor" / "presentation" / "component" / "VisualEditorPanel" / "VisualEditorPanel.qml").read_text(encoding="utf-8")
        self.assertNotIn("collapsedGroups", editor)
        self.assertNotIn("toggleGroup", editor)
        self.assertNotIn("groupCollapsed", editor)
        self.assertIn('section.property: "groupLabel"', editor)

    def test_search_is_explicit_not_live(self) -> None:
        controller = (ROOT / "features" / "search_replace" / "presentation" / "controller.py").read_text(encoding="utf-8")
        panel = (ROOT / "features" / "search_replace" / "presentation" / "component" / "SearchPanel" / "SearchPanel.qml").read_text(encoding="utf-8")
        self.assertIn("def execute_search", controller)
        self.assertIn("controller.runSearch()", panel)
        self.assertIn("text: \"Search\"", panel)

    def test_json_editor_has_raw_flat_display_mode(self) -> None:
        editor = (ROOT / "features" / "editor" / "presentation" / "component" / "JsonEditor" / "JsonEditor.qml").read_text(encoding="utf-8")
        shell = (ROOT / "ui" / "component" / "shell" / "shell_adapter.py").read_text(encoding="utf-8")
        self.assertIn('property string displayMode: "raw"', editor)
        self.assertIn("currentRawText", editor)
        self.assertIn('editorRoot.displayMode = "flat"', editor)
        self.assertIn('editorRoot.displayMode = "raw"', editor)
        self.assertIn("function onCurrentDocumentChanged()", editor)
        self.assertIn("currentRawText = Property", shell)

    def test_insights_is_after_sidebar_spacer(self) -> None:
        sidebar = (ROOT / "ui" / "component" / "shell" / "PanelsSidebar" / "PanelsSidebar.qml").read_text(encoding="utf-8")
        self.assertGreater(sidebar.index('Item { Layout.fillHeight: true }'), sidebar.index('"panel": "macros"'))
        self.assertGreater(sidebar.index('active: app.activePanel === "suggestions"'), sidebar.index('Item { Layout.fillHeight: true }'))

    def test_macro_steps_use_a_single_column_and_500px_cap(self) -> None:
        macros = (ROOT / "features" / "macros" / "presentation" / "component" / "MacrosPanel" / "MacrosPanel.qml").read_text(encoding="utf-8")
        style = (ROOT / "features" / "macros" / "presentation" / "component" / "MacrosPanel" / "MacrosPanelStyle.qml").read_text(encoding="utf-8")
        self.assertIn('columns: 1', macros)
        self.assertIn('Math.min(style.maxStepsHeight', macros)
        self.assertIn('readonly property int maxStepsHeight: 500', style)
        self.assertIn('Layout.maximumHeight: style.maxStepsHeight', macros)
        self.assertIn('ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }', macros)

    def test_macro_panel_search_is_debounced_and_clearable(self) -> None:
        macros = (ROOT / "features" / "macros" / "presentation" / "component" / "MacrosPanel" / "MacrosPanel.qml").read_text(encoding="utf-8")
        model = (ROOT / "features" / "macros" / "presentation" / "models.py").read_text(encoding="utf-8")
        self.assertIn('interval: 200', macros)
        self.assertIn('tooltipText: "Clear macro search"', macros)
        self.assertIn('def set_search_text', model)
        self.assertIn('item.name.casefold()', model)

    def test_workspace_uses_requested_responsive_widths(self) -> None:
        page = (ROOT / "ui" / "pages" / "WorkspacePage" / "WorkspacePage.qml").read_text(encoding="utf-8")
        logic = (ROOT / "ui" / "pages" / "WorkspacePage" / "WorkspacePageLogic.js").read_text(encoding="utf-8")
        style = (ROOT / "ui" / "pages" / "WorkspacePage" / "WorkspacePageStyle.qml").read_text(encoding="utf-8")
        self.assertIn('readonly property real sidebarRatio: 0.10', style)
        self.assertIn('workspaceLayout.panelRatio', page)
        self.assertIn('panel === "macros"', logic)
        self.assertIn('panel === "changes"', logic)
        self.assertIn('return 0.50', logic)
        self.assertIn('return 0.40', logic)
        self.assertIn('return 0.30', logic)

    def test_semantic_button_colors_and_color_picker_are_wired(self) -> None:
        button = (ROOT / "ui" / "component" / "primitives" / "ChromeButton" / "ChromeButton.qml").read_text(encoding="utf-8")
        visual_editor = (ROOT / "features" / "visual_editor" / "presentation" / "component" / "VisualEditorPanel" / "VisualEditorPanel.qml").read_text(encoding="utf-8")
        primitives = (ROOT / "ui" / "component" / "primitives" / "qmldir").read_text(encoding="utf-8")
        self.assertIn('property string actionType: "execute"', button)
        self.assertIn('Theme.actionSave', button)
        self.assertIn('Theme.actionCancel', button)
        self.assertIn('ColorPickerPopup {', visual_editor)
        self.assertIn('ColorPickerPopup 1.0', primitives)


if __name__ == "__main__":
    unittest.main()
