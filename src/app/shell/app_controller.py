from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QObject, Property, QStandardPaths, QTimer, Signal, Slot
from PySide6.QtWidgets import QFileDialog

from app.core.json_file_type import JsonFileType
from app.features.file_management import FileManagementController, FileManagementService, FileRepository
from app.features.filters import FilterController, FilterRepository, ImportedFilterRepository
from app.features.folder_import import FolderImportController, FolderScanner
from app.features.history import FileSnapshot, HistoryController, HistoryService
from app.features.macros import MacroController, MacroRepository, MacroStep
from app.features.search_replace import SearchController
from app.features.suggestions import SuggestionController
from app.features.visual_editor import VisualEditorController, VisualEditorService
from app.features.visual_editor.visual_property_catalog import VisualPropertyCatalog
from app.shared.filesystem.content_locator import locate_content_root
from app.shared.filesystem.path_service import PathService
from app.ui.file_list_model import FileListModel
from app.ui.filter_models import FilterListModel, RuleListModel
from app.ui.folder_scan_model import FolderScanModel
from app.ui.history_model import HistoryListModel
from app.ui.macro_models import MacroListModel
from app.ui.project_tree_model import ProjectTreeModel
from app.ui.search_result_model import SearchResultListModel
from app.ui.suggestion_models import SuggestionListModel
from app.ui.visual_editor_models import VisualEditorControlModel


class AppController(QObject):
    """QML facade that composes feature controllers."""

    filesChanged = Signal()
    currentIndexChanged = Signal()
    currentDocumentChanged = Signal()
    searchChanged = Signal()
    statusChanged = Signal()
    folderScanChanged = Signal()
    matchNavigationChanged = Signal()
    filtersChanged = Signal()
    filterEditorChanged = Signal()
    suggestionsChanged = Signal()
    macrosChanged = Signal()
    projectTreeChanged = Signal()
    visualEditorChanged = Signal()
    historyChanged = Signal()
    sessionResetRequested = Signal()
    panelRequested = Signal(str)

    def __init__(self, filter_storage_path: Path | None = None, content_root: Path | None = None) -> None:
        super().__init__()
        self._status_message = "Ready"
        self._content_root = content_root or locate_content_root()

        self._files = FileListModel()
        self._project_tree = ProjectTreeModel()
        self._folder_scan = FolderScanModel()
        self._filters = FilterListModel()
        self._editing_rules = RuleListModel()
        self._suggestion_keys = SuggestionListModel()
        self._suggestion_values = SuggestionListModel()
        self._macros = MacroListModel()
        self._history_model = HistoryListModel()
        self._search_results = SearchResultListModel()
        self._visual_editor_controls = VisualEditorControlModel()

        file_repository = FileRepository()
        self.file_management = FileManagementController(self._files, FileManagementService(self._files, file_repository))
        self.folder_import = FolderImportController(self._folder_scan, FolderScanner())
        self.search_replace = SearchController(self._files)

        self._imported_filter_repository = ImportedFilterRepository(self._content_root)
        imported_filter_result = self._imported_filter_repository.list_filters()
        self._log_import_errors("Imported filter", imported_filter_result.errors)
        self.filters = FilterController(
            self._filters,
            self._editing_rules,
            FilterRepository(filter_storage_path or self._filters_storage_path()),
            imported_filters=imported_filter_result.filters,
        )
        self.suggestions = SuggestionController(self._suggestion_keys, self._suggestion_values)
        self.macros = MacroController(self._macros, MacroRepository(self._content_root))
        self.history = HistoryController(self._history_model, HistoryService())
        self.macros.refresh_validation(self._filters.filters())
        catalog = VisualPropertyCatalog(self._content_root)
        self.visual_editor = VisualEditorController(self._visual_editor_controls, VisualEditorService(catalog.list_controls()))

        self._running_macro_index = -1
        self._running_macro_step_index = 0
        self._macro_recording_start_index = -1
        self._macro_timer = QTimer(self)
        self._macro_timer.setSingleShot(True)
        self._macro_timer.timeout.connect(self._run_next_macro_step)

        self._connect_model_signals()
        self._refresh_document_views()
        self._refresh_suggestions_now()

    def _connect_model_signals(self) -> None:
        self._files.countChanged.connect(self.filesChanged.emit)
        self._folder_scan.countChanged.connect(self.folderScanChanged.emit)
        self._filters.countChanged.connect(self.filtersChanged.emit)
        self._editing_rules.countChanged.connect(self.filterEditorChanged.emit)
        self._suggestion_keys.countChanged.connect(self.suggestionsChanged.emit)
        self._suggestion_values.countChanged.connect(self.suggestionsChanged.emit)
        self._macros.countChanged.connect(self.macrosChanged.emit)
        self._project_tree.countChanged.connect(self.projectTreeChanged.emit)
        self._visual_editor_controls.countChanged.connect(self.visualEditorChanged.emit)
        self._history_model.countChanged.connect(self.historyChanged.emit)
        self._search_results.countChanged.connect(self.searchChanged.emit)

    def get_file_model(self) -> FileListModel:
        return self._files

    def get_project_tree_model(self) -> ProjectTreeModel:
        return self._project_tree

    def get_folder_scan_model(self) -> FolderScanModel:
        return self._folder_scan

    def get_filter_model(self) -> FilterListModel:
        return self._filters

    def get_filters_model(self) -> FilterListModel:
        return self._filters

    def get_editing_rule_model(self) -> RuleListModel:
        return self._editing_rules

    def get_suggestion_key_model(self) -> SuggestionListModel:
        return self._suggestion_keys

    def get_suggestion_value_model(self) -> SuggestionListModel:
        return self._suggestion_values

    def get_macro_model(self) -> MacroListModel:
        return self._macros

    def get_visual_editor_control_model(self) -> VisualEditorControlModel:
        return self._visual_editor_controls

    def get_history_model(self) -> HistoryListModel:
        return self._history_model

    def get_search_result_model(self) -> SearchResultListModel:
        return self._search_results

    def get_folder_scan_count(self) -> int:
        return self.folder_import.count

    def get_folder_scan_root(self) -> str:
        return self.folder_import.scan_root

    def get_folder_import_visible(self) -> bool:
        return self.folder_import.visible

    def get_filter_count(self) -> int:
        return self.filters.count

    def get_suggestion_key_count(self) -> int:
        return self.suggestions.key_count

    def get_suggestion_value_count(self) -> int:
        return self.suggestions.value_count

    def get_macro_count(self) -> int:
        return self.macros.count

    def get_visual_editor_control_count(self) -> int:
        return self._visual_editor_controls.count

    def get_history_count(self) -> int:
        return self.history.count

    def get_history_current_index(self) -> int:
        return self.history.current_index

    def get_any_macro_running(self) -> bool:
        return self.macros.any_running

    def get_is_macro_recording(self) -> bool:
        return self._macro_recording_start_index >= 0

    def get_active_filter_id(self) -> str:
        return self._filters.active_filter_id()

    def get_active_filter_name(self) -> str:
        return self.filters.active_filter_name

    def get_active_filter_color(self) -> str:
        return self.filters.active_filter_color

    def get_active_filter_target(self) -> str:
        return self.filters.active_filter_target

    def get_active_dynamic_filter_name(self) -> str:
        return self.filters.active_dynamic_filter_name

    def get_has_active_filter(self) -> bool:
        return self.filters.has_active_filter

    def get_file_count(self) -> int:
        return self.file_management.file_count

    def get_active_file_count(self) -> int:
        return self.file_management.active_file_count

    def get_operation_active_file_count(self) -> int:
        return self.file_management.active_file_count

    def get_visible_file_count(self) -> int:
        return self.file_management.visible_file_count

    def get_project_tree_count(self) -> int:
        return self._project_tree.count

    def get_active_visual_count(self) -> int:
        return self.visual_editor.active_visual_count(self._files)

    def get_has_files(self) -> bool:
        return self.file_management.file_count > 0

    def get_has_dirty_files(self) -> bool:
        return self.file_management.has_dirty_files

    def get_current_index(self) -> int:
        return self.file_management.current_index

    def set_current_index(self, index: int) -> None:
        if self.file_management.set_current_index(index):
            self.currentIndexChanged.emit()
            self.currentDocumentChanged.emit()

    def get_current_text(self) -> str:
        return self.file_management.current_document_text()

    def get_current_name(self) -> str:
        return self.file_management.current_document_name()

    def get_current_path(self) -> str:
        return self.file_management.current_document_path()

    def get_current_file_type(self) -> str:
        return self.file_management.current_document_file_type()

    def get_current_relative_path(self) -> str:
        return self.file_management.current_document_relative_path()

    def get_current_highlighted_html(self) -> str:
        return self.file_management.current_document_highlighted_html()

    def get_current_dirty(self) -> bool:
        return self.file_management.current_document_dirty()

    def get_current_valid_json(self) -> bool:
        return self.file_management.current_document_valid_json()

    def get_current_json_error(self) -> str:
        return self.file_management.current_document_json_error()

    def get_current_match_count(self) -> int:
        return self.file_management.current_document_match_count()

    def get_active_match_file_index(self) -> int:
        return self.search_replace.active_match_file_index

    def get_active_match_index(self) -> int:
        return self.search_replace.active_match_index

    def get_active_match_line(self) -> int:
        return self.search_replace.active_match_line

    def get_active_match_start(self) -> int:
        return self.search_replace.active_match_start

    def get_active_match_end(self) -> int:
        return self.search_replace.active_match_end

    def get_active_match_display_index(self) -> int:
        return self.search_replace.active_match_display_index

    def get_active_match_file_count(self) -> int:
        return self.search_replace.active_match_file_count()

    def get_search_text(self) -> str:
        return self.search_replace.search_text

    def set_search_text(self, text: str) -> None:
        if self.search_replace.set_search_text(text):
            self._refresh_project_tree()
            self._refresh_search_results()
            self._emit_search_state_changed()

    def get_replace_text(self) -> str:
        return self.search_replace.replace_text

    def set_replace_text(self, text: str) -> None:
        if self.search_replace.set_replace_text(text):
            self._refresh_project_tree()
            self._refresh_search_results()
            self._emit_search_state_changed()

    def get_case_sensitive(self) -> bool:
        return self.search_replace.case_sensitive

    def set_case_sensitive(self, value: bool) -> None:
        if self.search_replace.set_case_sensitive(value):
            self._refresh_project_tree()
            self._refresh_search_results()
            self._emit_search_state_changed()

    def get_total_matches(self) -> int:
        return self.search_replace.total_matches

    def get_search_result_count(self) -> int:
        return self._search_results.count

    def get_status_message(self) -> str:
        return self._status_message

    def get_filter_editor_visible(self) -> bool:
        return self.filters.editor_visible

    def get_editing_filter_name(self) -> str:
        return self.filters.editor_name

    def set_editing_filter_name(self, value: str) -> None:
        if self.filters.set_editor_name(value):
            self.filterEditorChanged.emit()

    def get_editing_filter_color(self) -> str:
        return self.filters.editor_color

    def set_editing_filter_color(self, value: str) -> None:
        if self.filters.set_editor_color(value):
            self.filterEditorChanged.emit()

    def get_editing_filter_target(self) -> str:
        return self.filters.editor_target

    def set_editing_filter_target(self, value: str) -> None:
        if self.filters.set_editor_target(value):
            self.filterEditorChanged.emit()

    def get_editing_rule_count(self) -> int:
        return self.filters.editor_rule_count

    def get_editing_filter_can_save(self) -> bool:
        return self.filters.editor_can_save

    def get_visual_editor_category(self) -> str:
        return self.visual_editor.category

    def set_visual_editor_category(self, value: str) -> None:
        if self.visual_editor.set_category(value, self._files):
            self.visualEditorChanged.emit()

    def get_visual_editor_status(self) -> str:
        return self.visual_editor.last_status


    def get_visual_editor_category_options(self):
        return self.visual_editor.category_options(self._files)
    @Slot("QVariant", result=int)
    def addFiles(self, values) -> int:
        return self._add_paths_from_user(PathService.many_from_qml(values))

    @Slot(result=int)
    def openFileDialog(self) -> int:
        selected_paths, _selected_filter = QFileDialog.getOpenFileNames(
            None,
            "Open JSON files",
            "",
            "JSON files (*.json);;All files (*.*)",
        )
        return self._add_paths_from_user(PathService.many_from_qml(selected_paths))

    @Slot(result=int)
    def openFolderDialog(self) -> int:
        selected_folder = QFileDialog.getExistingDirectory(None, "Add JSON folder")
        if not selected_folder:
            return 0
        return self.scan_folder_paths([Path(selected_folder)])

    @Slot(int, result=bool)
    def selectTreeRow(self, tree_index: int) -> bool:
        file_index = self._project_tree.file_index_at(tree_index)
        if file_index < 0:
            return False
        self.set_current_index(file_index)
        return True

    @Slot(str, bool, result=bool)
    def setPageExpanded(self, document_id: str, expanded: bool) -> bool:
        if not self._files.set_page_expanded(document_id, expanded):
            return False
        self._refresh_project_tree()
        return True

    @Slot(int, result=bool)
    def removeFile(self, index: int) -> bool:
        document = self._files.document_at(index)
        display_name = document.name if document is not None else "File"
        if not self.file_management.remove_file(index):
            self._set_status("No file was removed.")
            return False
        self._record_history_event("file-remove", display_name, {"not_reversible": True}, reversible=False)
        self._refresh_document_views()
        self._refresh_suggestions_now()
        self._set_status("Removed file.")
        self._emit_document_state_changed()
        return True

    @Slot(int, result=bool)
    def saveFile(self, index: int) -> bool:
        before = self._document_snapshots()
        result = self.file_management.save_file(index)
        if result.errors:
            self._set_status(result.errors[0])
            return False
        self._set_status("No changes to save." if result.saved == 0 else "Saved file.")
        if result.saved > 0:
            self._record_history_from_snapshots("save-file", self.file_management.current_document_name(), before, {"saved": result.saved})
        self.filesChanged.emit()
        self.currentDocumentChanged.emit()
        self._refresh_project_tree()
        return result.saved > 0

    @Slot(result=int)
    def saveAll(self) -> int:
        before = self._document_snapshots()
        result = self.file_management.save_all()
        if result.errors:
            self._set_status(f"Saved {result.saved} file(s). First error: {result.errors[0]}")
        elif result.saved == 0:
            self._set_status("No changes to save.")
        else:
            self._set_status(f"Saved {result.saved} file(s).")
        if result.saved > 0:
            self._record_history_from_snapshots("save-all", "Save all", before, {"saved": result.saved})
        self.filesChanged.emit()
        self.currentDocumentChanged.emit()
        self._refresh_project_tree()
        return result.saved

    @Slot(int, str, result=bool)
    def updateFileText(self, index: int, text: str) -> bool:
        before = self._document_snapshots()
        document = self._files.document_at(index)
        display_name = document.name if document is not None else "Text edit"
        if not self.file_management.update_text(index, text):
            return False
        self._record_history_from_snapshots("content-edit", display_name, before)
        self._refresh_document_views()
        self._schedule_suggestions_refresh()
        self._emit_document_state_changed()
        return True

    @Slot(result=bool)
    def formatCurrentJson(self) -> bool:
        before = self._document_snapshots()
        display_name = self.file_management.current_document_name()
        if not self.file_management.format_current_file():
            self._set_status("Current file is not valid JSON.")
            return False
        self._refresh_document_views()
        self._refresh_suggestions_now()
        self._set_status("Formatted JSON.")
        self._record_history_from_snapshots("format-json", display_name, before)
        self._emit_document_state_changed()
        return True

    @Slot(result=int)
    def replaceCurrentMatch(self) -> int:
        before = self._document_snapshots()
        replaced = self.search_replace.replace_current_match()
        self._refresh_document_views()
        if replaced > 0:
            self._refresh_suggestions_now()
            self._record_history_from_snapshots("search-replace-one", "Replace current match", before, {"matches": replaced, "search": self.search_replace.search_text, "replace": self.search_replace.replace_text})
        self._set_status(f"Replaced {replaced} match(es).")
        self._emit_document_state_changed()
        return replaced

    @Slot(result=int)
    def replaceCurrentFile(self) -> int:
        before = self._document_snapshots()
        replaced = self.search_replace.replace_current_file(self.file_management.current_index)
        self._refresh_document_views()
        if replaced > 0:
            self._refresh_suggestions_now()
            self._record_history_from_snapshots("search-replace-current-file", "Replace current file", before, {"matches": replaced, "search": self.search_replace.search_text, "replace": self.search_replace.replace_text})
        self._set_status(f"Replaced {replaced} match(es).")
        self._emit_document_state_changed()
        return replaced

    @Slot(result=int)
    def replaceAll(self) -> int:
        before = self._document_snapshots()
        replaced = self.search_replace.replace_all()
        self._refresh_document_views()
        if replaced > 0:
            self._refresh_suggestions_now()
            self._record_history_from_snapshots("search-replace-all", "Replace all", before, {"matches": replaced, "search": self.search_replace.search_text, "replace": self.search_replace.replace_text})
        self._set_status(f"Replaced {replaced} match(es).")
        self._emit_document_state_changed()
        return replaced

    @Slot(int, int, result=bool)
    def navigateToMatch(self, file_index: int, match_index: int) -> bool:
        if not self.search_replace.navigate_to_match(file_index, match_index):
            return False
        self.file_management.set_current_index(file_index)
        self.currentIndexChanged.emit()
        self.currentDocumentChanged.emit()
        self.matchNavigationChanged.emit()
        return True

    @Slot(result=bool)
    def navigateNextMatch(self) -> bool:
        if not self.search_replace.navigate_next():
            self.matchNavigationChanged.emit()
            return False
        self.file_management.set_current_index(self.search_replace.active_match_file_index)
        self.currentIndexChanged.emit()
        self.currentDocumentChanged.emit()
        self.matchNavigationChanged.emit()
        return True

    @Slot(result=bool)
    def navigatePreviousMatch(self) -> bool:
        if not self.search_replace.navigate_previous():
            self.matchNavigationChanged.emit()
            return False
        self.file_management.set_current_index(self.search_replace.active_match_file_index)
        self.currentIndexChanged.emit()
        self.currentDocumentChanged.emit()
        self.matchNavigationChanged.emit()
        return True

    @Slot("QVariant", result=int)
    def scanFolderPaths(self, values) -> int:
        return self.scan_folder_paths(PathService.many_from_qml(values))

    def scan_folder_paths(self, paths) -> int:
        normalized_paths = PathService.many_from_qml(paths)
        if not normalized_paths:
            self._set_status("No folder selected.")
            return 0
        result = self.folder_import.scan_paths(normalized_paths, self._files.paths())
        self.folderScanChanged.emit()
        if result.errors and not result.items:
            self._set_status(result.errors[0])
        elif result.skipped_duplicates:
            self._set_status(f"Found {len(result.items)} Power BI JSON file(s), skipped {result.skipped_duplicates} duplicate(s).")
        else:
            self._set_status(f"Found {len(result.items)} Power BI JSON file(s).")
        return len(result.items)

    @Slot(result=int)
    def confirmFolderImport(self) -> int:
        paths = self.folder_import.confirm()
        self.folderScanChanged.emit()
        result = self.file_management.add_files(paths)
        self._refresh_document_views()
        self._refresh_suggestions_now()
        self._set_add_status(result)
        self._emit_document_state_changed()
        return result.added

    @Slot()
    def cancelFolderImport(self) -> None:
        self.folder_import.cancel()
        self.folderScanChanged.emit()
        self._set_status("Folder import canceled.")

    @Slot(int, result=bool)
    def applyFilter(self, index: int) -> bool:
        if not self.filters.apply_filter(index, self._files):
            self._set_status("Filter was not applied.")
            return False
        self._record_history_event("filter-apply", self.filters.active_filter_name, {"target": self.filters.active_filter_target})
        self._refresh_document_views(reapply_filter=False)
        self._set_status(f"Applied {self.filters.active_filter_name} filter.")
        self._emit_filter_state_changed()
        return True

    @Slot(result=bool)
    def deactivateFilter(self) -> bool:
        if not self.filters.deactivate_filter(self._files):
            return False
        self._record_history_event("filter-clear", "Filter deactivated")
        self._refresh_document_views(reapply_filter=False)
        self._set_status("Filter deactivated.")
        self._emit_filter_state_changed()
        return True

    @Slot(str, result=bool)
    def applyDynamicPageNameFilter(self, value: str) -> bool:
        if not self.filters.apply_dynamic_page_name_filter(value, self._files):
            self._set_status("Page name filter needs text.")
            return False
        self._record_history_event("dynamic-filter-apply", self.filters.active_filter_name, {"kind": "page-name", "value": value})
        self._refresh_document_views(reapply_filter=False)
        self._set_status(f"Applied {self.filters.active_filter_name}.")
        self._emit_filter_state_changed()
        return True

    @Slot(str, result=bool)
    def applyDynamicVisualTypeFilter(self, value: str) -> bool:
        if not self.filters.apply_dynamic_visual_type_filter(value, self._files):
            self._set_status("Visual type filter needs text.")
            return False
        self._record_history_event("dynamic-filter-apply", self.filters.active_filter_name, {"kind": "visual-type", "value": value})
        self._refresh_document_views(reapply_filter=False)
        self._set_status(f"Applied {self.filters.active_filter_name}.")
        self._emit_filter_state_changed()
        return True

    @Slot(str, result=bool)
    def applyDynamicVisualNameFilter(self, value: str) -> bool:
        if not self.filters.apply_dynamic_visual_name_filter(value, self._files):
            self._set_status("Visual name filter needs text.")
            return False
        self._record_history_event("dynamic-filter-apply", self.filters.active_filter_name, {"kind": "visual-name", "value": value})
        self._refresh_document_views(reapply_filter=False)
        self._set_status(f"Applied {self.filters.active_filter_name}.")
        self._emit_filter_state_changed()
        return True

    @Slot()
    def openNewFilterEditor(self) -> None:
        self.filters.open_new_editor()
        self.filterEditorChanged.emit()

    @Slot(int, result=bool)
    def openEditFilterEditor(self, index: int) -> bool:
        opened = self.filters.open_edit_editor(index)
        if opened:
            self.filterEditorChanged.emit()
        else:
            self._set_status("Imported filters are read-only.")
        return opened

    @Slot()
    def cancelFilterEditor(self) -> None:
        self.filters.cancel_editor()
        self.filterEditorChanged.emit()

    @Slot(result=bool)
    def saveFilterEditor(self) -> bool:
        was_editing = self.filters.editor_visible
        if not self.filters.save_editor():
            self._set_status("Filter name and at least one keyed rule are required.")
            return False
        self._refresh_document_views()
        self._set_status("Saved filter.")
        self._record_history_event("filter-update", "Saved filter")
        self.filterEditorChanged.emit()
        self._emit_filter_state_changed()
        return True

    @Slot(result=bool)
    def importFilter(self) -> bool:
        selected_path, _selected_filter = QFileDialog.getOpenFileName(None, "Import filter", "", "JSON files (*.json);;All files (*.*)")
        if not selected_path:
            return False
        ok, message = self.filters.import_user_filter(Path(selected_path), self._imported_filter_repository)
        self._set_status(message)
        if ok:
            self._record_history_event("filter-import", message)
        self._emit_filter_state_changed()
        return ok

    @Slot(int, result=bool)
    def exportFilter(self, index: int) -> bool:
        selected_path, _selected_filter = QFileDialog.getSaveFileName(None, "Export filter", "filter.json", "JSON files (*.json);;All files (*.*)")
        if not selected_path:
            return False
        ok, message = self.filters.export_filter(index, Path(selected_path))
        self._set_status(message)
        return ok

    @Slot(int, result=bool)
    def deleteFilter(self, index: int) -> bool:
        deleted = self.filters.delete_filter(index, self._files)
        if not deleted:
            self._set_status("Imported filters cannot be deleted here.")
            return False
        self._refresh_document_views(reapply_filter=False)
        self._set_status("Deleted filter.")
        self._record_history_event("filter-delete", "Deleted filter")
        self._emit_filter_state_changed()
        return True

    @Slot()
    def randomizeEditingFilterColor(self) -> None:
        self.filters.randomize_editor_color()
        self.filterEditorChanged.emit()

    @Slot()
    def addEditingRule(self) -> None:
        self.filters.add_rule()
        self.filterEditorChanged.emit()

    @Slot(int)
    def removeEditingRule(self, index: int) -> None:
        self.filters.remove_rule(index)
        self.filterEditorChanged.emit()

    @Slot(int, str)
    def updateEditingRuleKey(self, index: int, value: str) -> None:
        self.filters.update_rule_key(index, value)
        self.filterEditorChanged.emit()

    @Slot(int, str)
    def updateEditingRuleOperation(self, index: int, value: str) -> None:
        self.filters.update_rule_operation(index, value)
        self.filterEditorChanged.emit()

    @Slot(int, str)
    def updateEditingRuleValue(self, index: int, value: str) -> None:
        self.filters.update_rule_value(index, value)
        self.filterEditorChanged.emit()

    @Slot(str, int, result=bool)
    def openSuggestionSearch(self, suggestion_type: str, index: int) -> bool:
        value = self.suggestions.suggestion_value(suggestion_type, index)
        if not value:
            self._set_status("Suggestion was not found.")
            return False
        self.panelRequested.emit("search")
        self.search_replace.set_search_text(value)
        self._refresh_project_tree()
        self._set_status(f"Searching for {value}.")
        self._emit_search_state_changed()
        return True

    @Slot(result=bool)
    def reloadContent(self) -> bool:
        filter_result = self._imported_filter_repository.list_filters()
        self._log_import_errors("Imported filter", filter_result.errors)
        self.filters.set_imported_filters(filter_result.filters)
        self.macros.reload(self._filters.filters())
        self._refresh_document_views()
        self._emit_filter_state_changed()
        self.macrosChanged.emit()
        self._set_status(f"Reloaded content with {len(filter_result.errors)} filter error(s)." if filter_result.errors else "Reloaded content.")
        return True

    @Slot(result=bool)
    def importMacro(self) -> bool:
        selected_path, _selected_filter = QFileDialog.getOpenFileName(None, "Import macro", "", "JSON files (*.json);;All files (*.*)")
        if not selected_path:
            return False
        ok, message = self.macros.import_macro(Path(selected_path), self._filters.filters())
        self._set_status(message)
        if ok:
            self._record_history_event("macro-import", message)
        self.macrosChanged.emit()
        return ok

    @Slot(int, result=bool)
    def exportMacro(self, index: int) -> bool:
        selected_path, _selected_filter = QFileDialog.getSaveFileName(None, "Export macro", "macro.json", "JSON files (*.json);;All files (*.*)")
        if not selected_path:
            return False
        ok, message = self.macros.export_macro(index, Path(selected_path))
        self._set_status(message)
        return ok

    @Slot(str)
    def setVisualEditorCategory(self, category: str) -> None:
        self.set_visual_editor_category(category)

    @Slot(str, "QVariant", result=bool)
    def applyVisualEditorChange(self, control_id: str, value) -> bool:
        before = self._document_snapshots()
        result = self.visual_editor.apply_change(self._files, control_id, value)
        self._refresh_document_views()
        self._refresh_suggestions_now()
        self._set_status(result.summary)
        if result.changed_values > 0:
            self._record_history_from_snapshots(
                "visual-editor-change",
                control_id,
                before,
                {"changed_values": result.changed_values, "files": result.changed_files, "value": value},
            )
        self.visualEditorChanged.emit()
        self._emit_document_state_changed()
        return result.changed_values > 0

    @Slot(result=bool)
    def startAgain(self) -> bool:
        if self._files.count > 0 or self.history.count > 0:
            self._record_history_event("start-again", "Start again", {"not_reversible": True}, reversible=False)
        self._macro_timer.stop()
        self._reset_macro_run()
        self.macros.reset_runtime_state()
        self.file_management.reset()
        self.folder_import.cancel()
        self.search_replace.reset()
        self.filters.reset_active_filter(self._files)
        self._suggestion_keys.reset([])
        self._suggestion_values.reset([])
        self.visual_editor.refresh(self._files)
        self._project_tree.clear()
        self._set_status("Ready")
        self.sessionResetRequested.emit()
        self.filesChanged.emit()
        self.currentIndexChanged.emit()
        self.currentDocumentChanged.emit()
        self.searchChanged.emit()
        self.matchNavigationChanged.emit()
        self.folderScanChanged.emit()
        self.filtersChanged.emit()
        self.suggestionsChanged.emit()
        self.macrosChanged.emit()
        self.visualEditorChanged.emit()
        self.projectTreeChanged.emit()
        return True

    @Slot(int, result=bool)
    def goToHistoryIndex(self, index: int) -> bool:
        if not self.history.go_to(index, self._files):
            self._set_status("History row cannot be applied.")
            return False
        self._refresh_document_views()
        self._refresh_suggestions_now()
        self._set_status(f"Moved to history row {index}.")
        self.historyChanged.emit()
        self._emit_document_state_changed()
        return True
    @Slot(result=bool)
    def startMacroRecording(self) -> bool:
        if self._macro_recording_start_index >= 0:
            self._set_status("Macro recording is already active.")
            return False
        if self._running_macro_index >= 0 or self.macros.any_running:
            self._set_status("Stop the running macro before recording.")
            return False
        self._macro_recording_start_index = self.history.current_index + 1
        self._set_status("Started macro recording.")
        self.macrosChanged.emit()
        return True

    @Slot(result=bool)
    def stopMacroRecording(self) -> bool:
        if self._macro_recording_start_index < 0:
            self._set_status("Macro recording is not active.")
            return False
        start_index = self._macro_recording_start_index
        end_index = self.history.current_index
        self._macro_recording_start_index = -1
        entries = [entry for entry in self.history.entries if start_index <= entry.index <= end_index]
        if not entries:
            self._set_status("No actions were recorded.")
            self.macrosChanged.emit()
            return False
        ok, message = self.macros.create_from_history_entries(entries, self._filters.filters())
        self._set_status(message)
        self.macrosChanged.emit()
        return ok

    @Slot(result=bool)
    def createMacroFromHistory(self) -> bool:
        return self.stopMacroRecording() if self._macro_recording_start_index >= 0 else self.startMacroRecording()

    @Slot(result=bool)
    def stopMacro(self) -> bool:
        if self._running_macro_index < 0 and not self.macros.any_running:
            self._set_status("No macro is running.")
            return False
        self._macro_timer.stop()
        self._reset_macro_run()
        self._macro_recording_start_index = -1
        self.macros.reset_runtime_state()
        self._set_status("Stopped macro.")
        self.macrosChanged.emit()
        return True

    @Slot(int, result=bool)
    def runMacro(self, index: int) -> bool:
        if self._macro_recording_start_index >= 0:
            self._set_status("Stop macro recording before running a macro.")
            return False
        if self._running_macro_index >= 0 or self.macros.any_running:
            self._set_status("A macro is already running.")
            return False
        errors = self.macros.validate_for_run(index, self._filters.filters())
        self.macrosChanged.emit()
        if errors:
            self._set_status(errors[0])
            return False
        macro = self.macros.begin_run(index)
        if macro is None:
            self._set_status("Macro could not be started.")
            return False
        self._running_macro_index = index
        self._running_macro_step_index = 0
        self._record_history_event("macro-run", macro.name, {"steps": len(macro.steps)})
        self._set_status(f"Running {macro.name}.")
        self.macrosChanged.emit()
        self._macro_timer.start(0)
        return True

    def _run_next_macro_step(self) -> None:
        macro = self.macros.macro_at(self._running_macro_index)
        if macro is None:
            self._reset_macro_run()
            return
        if self._running_macro_step_index >= len(macro.steps):
            macro_name = macro.name
            self.macros.finish_run(self._running_macro_index)
            self._reset_macro_run()
            self._record_history_event("macro-complete", macro_name)
            self._set_status(f"Finished {macro_name}.")
            self.macrosChanged.emit()
            return
        step_index = self._running_macro_step_index
        step = macro.steps[step_index]
        try:
            before = self._document_snapshots()
            self._execute_macro_step(step)
            self._record_history_from_snapshots("macro-step", step.type, before, {"step": step_index + 1})
        except Exception as error:
            self.macros.fail_run(self._running_macro_index, step_index, str(error))
            self._set_status(f"Macro failed at step {step_index + 1}: {error}")
            self._reset_macro_run()
            self.macrosChanged.emit()
            return
        self._running_macro_step_index += 1
        self.macrosChanged.emit()
        self._macro_timer.start(0)

    def _execute_macro_step(self, step: MacroStep) -> None:
        if step.type in {"filter", "filter-apply"}:
            filter_index = self._filter_index_for_macro_step(step)
            label = step.filter_name or step.filter_id
            if filter_index < 0:
                raise ValueError(f"No loaded filter named '{label}'.")
            if not self.filters.apply_filter(filter_index, self._files):
                raise ValueError(f"Filter '{label}' could not be applied.")
            self._refresh_document_views(reapply_filter=False)
            self._set_status(f"Applied {self.filters.active_filter_name} filter.")
            self._emit_filter_state_changed()
            return
        if step.type == "filter-clear":
            self.filters.reset_active_filter(self._files)
            self._refresh_document_views(reapply_filter=False)
            self._set_status("Filter deactivated.")
            self._emit_filter_state_changed()
            return
        if step.type == "search":
            self.panelRequested.emit("search")
            self.search_replace.set_search_text(step.search_value)
            self._refresh_project_tree()
            self._set_status(f"Searching for {step.search_value}.")
            self._emit_search_state_changed()
            return
        if step.type in {"search-and-replace", "search-replace"}:
            self.panelRequested.emit("search")
            self.search_replace.set_search_text(step.search_value)
            self.search_replace.set_replace_text(step.replace_value)
            replaced = self.replaceAll()
            self._set_status(f"Macro replaced {replaced} match(es).")
            return
        if step.type == "replace-current":
            self._set_status(f"Macro replaced {self.replaceCurrentMatch()} match(es).")
            return
        if step.type == "replace-all":
            self._set_status(f"Macro replaced {self.replaceAll()} match(es).")
            return
        if step.type == "search-replace-one":
            self.panelRequested.emit("search")
            self.search_replace.set_search_text(step.search_value)
            self.search_replace.set_replace_text(step.replace_value)
            if self.search_replace.active_match_index < 0:
                self.search_replace.navigate_next()
            self._set_status(f"Macro replaced {self.replaceCurrentMatch()} match(es).")
            return
        if step.type == "search-replace-all":
            self.panelRequested.emit("search")
            self.search_replace.set_search_text(step.search_value)
            self.search_replace.set_replace_text(step.replace_value)
            self._set_status(f"Macro replaced {self.replaceAll()} match(es).")
            return
        if step.type == "dynamic-filter-apply":
            kind = step.filter_name
            if kind == "page-name":
                if not self.applyDynamicPageNameFilter(str(step.value)):
                    raise ValueError("Page name filter could not be applied.")
                return
            if kind == "visual-type":
                if not self.applyDynamicVisualTypeFilter(str(step.value)):
                    raise ValueError("Visual type filter could not be applied.")
                return
            if kind == "visual-name":
                if not self.applyDynamicVisualNameFilter(str(step.value)):
                    raise ValueError("Visual name filter could not be applied.")
                return
            raise ValueError(f"Unknown dynamic filter kind '{kind}'.")
        if step.type == "format-json":
            if not self.formatCurrentJson():
                raise ValueError("Current file could not be formatted as JSON.")
            return
        if step.type == "visual-editor-change":
            result = self.visual_editor.apply_change(self._files, step.control_id, step.value)
            self._refresh_document_views()
            self._refresh_suggestions_now()
            if result.changed_values <= 0:
                raise ValueError(result.summary)
            self._set_status(result.summary)
            self.visualEditorChanged.emit()
            self._emit_document_state_changed()
            return
        raise ValueError(f"Unknown step type '{step.type}'.")

    def _filter_index_for_macro_step(self, step: MacroStep) -> int:
        for index, content_filter in enumerate(self._filters.filters()):
            if step.filter_id and content_filter.id == step.filter_id:
                return index
            if step.filter_name and content_filter.display_name == step.filter_name:
                return index
        return -1

    def _reset_macro_run(self) -> None:
        self._running_macro_index = -1
        self._running_macro_step_index = 0

    def _document_snapshots(self) -> dict[str, tuple[str, str, bool]]:
        return {
            document.id: (document.text, document.original_text or "", document.is_dirty)
            for document in self._files.documents()
        }

    def _history_file_changes(self, before: dict[str, tuple[str, str, bool]]) -> list[FileSnapshot]:
        changes: list[FileSnapshot] = []
        for document in self._files.documents():
            previous = before.get(document.id)
            if previous is None:
                continue
            before_text, before_original_text, before_dirty = previous
            after_text = document.text
            after_original_text = document.original_text or ""
            after_dirty = document.is_dirty
            if (before_text, before_original_text, before_dirty) == (after_text, after_original_text, after_dirty):
                continue
            changes.append(
                FileSnapshot(
                    document_id=document.id,
                    path=str(document.path),
                    before_text=before_text,
                    after_text=after_text,
                    before_original_text=before_original_text,
                    after_original_text=after_original_text,
                    before_dirty=before_dirty,
                    after_dirty=after_dirty,
                )
            )
        return changes

    def _record_history_from_snapshots(
        self,
        operation_type: str,
        display_name: str,
        before: dict[str, tuple[str, str, bool]],
        metadata: dict | None = None,
    ) -> None:
        changes = self._history_file_changes(before)
        if not changes:
            return
        enriched = dict(metadata or {})
        enriched.setdefault("files", len(changes))
        self.history.record(operation_type, display_name, enriched, changes)
        self.historyChanged.emit()

    def _record_history_event(self, operation_type: str, display_name: str, metadata: dict | None = None, reversible: bool = True) -> None:
        self.history.record(operation_type, display_name, metadata or {}, [], reversible=reversible)
        self.historyChanged.emit()
    def _apply_active_filter_state(self) -> None:
        self._refresh_document_views()
        self._emit_filter_state_changed()

    def _add_paths_from_user(self, paths: list[Path]) -> int:
        file_paths = [path for path in paths if path.is_file()]
        folder_paths = [path for path in paths if path.is_dir()]
        added = 0
        if file_paths:
            result = self.file_management.add_files(file_paths)
            added = result.added
            self._refresh_document_views()
            self._refresh_suggestions_now()
            self._set_add_status(result)
            self._emit_document_state_changed()
        if folder_paths:
            self.scan_folder_paths(folder_paths)
        elif not file_paths:
            self._set_status("No JSON files or folders selected.")
        return added

    def _refresh_document_views(self, reapply_filter: bool = True) -> None:
        self._rebuild_powerbi_relationships()
        if reapply_filter:
            self.filters.apply_to_files(self._files)
        self.file_management.ensure_current_index()
        self.search_replace.refresh()
        self._refresh_search_results()
        self.visual_editor.refresh(self._files)
        self._refresh_project_tree()

    def _refresh_search_results(self) -> None:
        self._search_results.reset_from_files(self._files)

    def _refresh_project_tree(self) -> None:
        self._project_tree.reset_from_files(self._files)
        self.projectTreeChanged.emit()
        self.currentDocumentChanged.emit()

    def _refresh_suggestions_now(self) -> None:
        self.suggestions.refresh_now(self._files)

    def _schedule_suggestions_refresh(self) -> None:
        self.suggestions.schedule_refresh(self._files)

    def _refresh_macro_validation(self) -> None:
        self.macros.refresh_validation(self._filters.filters())
        self.macrosChanged.emit()

    def _emit_document_state_changed(self) -> None:
        self.filesChanged.emit()
        self.currentIndexChanged.emit()
        self.currentDocumentChanged.emit()
        self.searchChanged.emit()
        self.matchNavigationChanged.emit()
        self.filtersChanged.emit()
        self.projectTreeChanged.emit()
        self.visualEditorChanged.emit()

    def _emit_filter_state_changed(self) -> None:
        self._refresh_macro_validation()
        self.filtersChanged.emit()
        self.filesChanged.emit()
        self.currentIndexChanged.emit()
        self.currentDocumentChanged.emit()
        self.searchChanged.emit()
        self.matchNavigationChanged.emit()
        self.projectTreeChanged.emit()
        self.visualEditorChanged.emit()

    def _emit_search_state_changed(self) -> None:
        self.searchChanged.emit()
        self.currentDocumentChanged.emit()
        self.matchNavigationChanged.emit()
        self.projectTreeChanged.emit()

    def _rebuild_powerbi_relationships(self) -> None:
        documents = list(self._files.documents())
        pages_by_folder = {}
        for document in documents:
            document.visual_ids.clear()
            if document.file_type == JsonFileType.VISUAL:
                document.parent_page_id = ""
            if document.file_type == JsonFileType.PAGE:
                pages_by_folder[document.path.parent] = document
        if not pages_by_folder:
            return
        for document in documents:
            if document.file_type != JsonFileType.VISUAL:
                continue
            for parent in document.path.parents:
                page = pages_by_folder.get(parent)
                if page is None:
                    continue
                document.parent_page_id = page.id
                if document.id not in page.visual_ids:
                    page.visual_ids.append(document.id)
                break

    def _set_add_status(self, result) -> None:
        if result.errors:
            self._set_status(f"Added {result.added} file(s). First error: {result.errors[0]}")
        elif result.skipped:
            self._set_status(f"Added {result.added} file(s), skipped {result.skipped}.")
        else:
            self._set_status(f"Added {result.added} file(s).")

    def _set_status(self, message: str) -> None:
        if self._status_message != message:
            self._status_message = message
            self.statusChanged.emit()

    @staticmethod
    def _log_import_errors(label: str, errors: list[str]) -> None:
        for error in errors:
            print(f"{label} skipped: {error}")

    @staticmethod
    def _filters_storage_path() -> Path:
        override = os.environ.get("JSON_MULTI_EDITOR_FILTERS_PATH")
        if override:
            return Path(override).expanduser().resolve()
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "JSON Multi Editor" / "filters.json"
        location = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        if location:
            return Path(location) / "filters.json"
        return Path.home() / ".json_multi_editor" / "filters.json"

    fileModel = Property(QObject, get_file_model, notify=filesChanged)
    projectTreeModel = Property(QObject, get_project_tree_model, notify=projectTreeChanged)
    folderScanModel = Property(QObject, get_folder_scan_model, notify=folderScanChanged)
    filterModel = Property(QObject, get_filter_model, notify=filtersChanged)
    editingRuleModel = Property(QObject, get_editing_rule_model, notify=filterEditorChanged)
    suggestionKeyModel = Property(QObject, get_suggestion_key_model, notify=suggestionsChanged)
    suggestionValueModel = Property(QObject, get_suggestion_value_model, notify=suggestionsChanged)
    macroModel = Property(QObject, get_macro_model, notify=macrosChanged)
    visualEditorControlModel = Property(QObject, get_visual_editor_control_model, notify=visualEditorChanged)
    historyModel = Property(QObject, get_history_model, notify=historyChanged)
    searchResultModel = Property(QObject, get_search_result_model, notify=searchChanged)

    folderScanCount = Property(int, get_folder_scan_count, notify=folderScanChanged)
    folderScanRoot = Property(str, get_folder_scan_root, notify=folderScanChanged)
    folderImportVisible = Property(bool, get_folder_import_visible, notify=folderScanChanged)
    filterCount = Property(int, get_filter_count, notify=filtersChanged)
    suggestionKeyCount = Property(int, get_suggestion_key_count, notify=suggestionsChanged)
    suggestionValueCount = Property(int, get_suggestion_value_count, notify=suggestionsChanged)
    macroCount = Property(int, get_macro_count, notify=macrosChanged)
    visualEditorControlCount = Property(int, get_visual_editor_control_count, notify=visualEditorChanged)
    historyCount = Property(int, get_history_count, notify=historyChanged)
    historyCurrentIndex = Property(int, get_history_current_index, notify=historyChanged)
    anyMacroRunning = Property(bool, get_any_macro_running, notify=macrosChanged)
    macroRecording = Property(bool, get_is_macro_recording, notify=macrosChanged)
    activeFilterId = Property(str, get_active_filter_id, notify=filtersChanged)
    activeFilterName = Property(str, get_active_filter_name, notify=filtersChanged)
    activeFilterColor = Property(str, get_active_filter_color, notify=filtersChanged)
    activeFilterTarget = Property(str, get_active_filter_target, notify=filtersChanged)
    activeDynamicFilterName = Property(str, get_active_dynamic_filter_name, notify=filtersChanged)
    hasActiveFilter = Property(bool, get_has_active_filter, notify=filtersChanged)

    fileCount = Property(int, get_file_count, notify=filesChanged)
    activeFileCount = Property(int, get_active_file_count, notify=filesChanged)
    operationActiveFileCount = Property(int, get_operation_active_file_count, notify=filesChanged)
    visibleFileCount = Property(int, get_visible_file_count, notify=filesChanged)
    projectTreeCount = Property(int, get_project_tree_count, notify=projectTreeChanged)
    activeVisualCount = Property(int, get_active_visual_count, notify=visualEditorChanged)
    hasFiles = Property(bool, get_has_files, notify=filesChanged)
    hasDirtyFiles = Property(bool, get_has_dirty_files, notify=filesChanged)

    currentIndex = Property(int, get_current_index, set_current_index, notify=currentIndexChanged)
    currentText = Property(str, get_current_text, notify=currentDocumentChanged)
    currentName = Property(str, get_current_name, notify=currentDocumentChanged)
    currentPath = Property(str, get_current_path, notify=currentDocumentChanged)
    currentFileType = Property(str, get_current_file_type, notify=currentDocumentChanged)
    currentRelativePath = Property(str, get_current_relative_path, notify=currentDocumentChanged)
    currentHighlightedHtml = Property(str, get_current_highlighted_html, notify=currentDocumentChanged)
    currentDirty = Property(bool, get_current_dirty, notify=currentDocumentChanged)
    currentValidJson = Property(bool, get_current_valid_json, notify=currentDocumentChanged)
    currentJsonError = Property(str, get_current_json_error, notify=currentDocumentChanged)
    currentMatchCount = Property(int, get_current_match_count, notify=currentDocumentChanged)

    searchText = Property(str, get_search_text, set_search_text, notify=searchChanged)
    replaceText = Property(str, get_replace_text, set_replace_text, notify=searchChanged)
    caseSensitive = Property(bool, get_case_sensitive, set_case_sensitive, notify=searchChanged)
    totalMatches = Property(int, get_total_matches, notify=searchChanged)
    searchResultCount = Property(int, get_search_result_count, notify=searchChanged)
    activeMatchFileIndex = Property(int, get_active_match_file_index, notify=matchNavigationChanged)
    activeMatchIndex = Property(int, get_active_match_index, notify=matchNavigationChanged)
    activeMatchLine = Property(int, get_active_match_line, notify=matchNavigationChanged)
    activeMatchStart = Property(int, get_active_match_start, notify=matchNavigationChanged)
    activeMatchEnd = Property(int, get_active_match_end, notify=matchNavigationChanged)
    activeMatchDisplayIndex = Property(int, get_active_match_display_index, notify=matchNavigationChanged)
    activeMatchFileCount = Property(int, get_active_match_file_count, notify=matchNavigationChanged)

    statusMessage = Property(str, get_status_message, notify=statusChanged)
    filterEditorVisible = Property(bool, get_filter_editor_visible, notify=filterEditorChanged)
    editingFilterName = Property(str, get_editing_filter_name, set_editing_filter_name, notify=filterEditorChanged)
    editingFilterColor = Property(str, get_editing_filter_color, set_editing_filter_color, notify=filterEditorChanged)
    editingFilterTarget = Property(str, get_editing_filter_target, set_editing_filter_target, notify=filterEditorChanged)
    editingRuleCount = Property(int, get_editing_rule_count, notify=filterEditorChanged)
    editingFilterCanSave = Property(bool, get_editing_filter_can_save, notify=filterEditorChanged)
    visualEditorCategory = Property(str, get_visual_editor_category, set_visual_editor_category, notify=visualEditorChanged)
    visualEditorStatus = Property(str, get_visual_editor_status, notify=visualEditorChanged)
    visualEditorCategoryOptions = Property("QVariantList", get_visual_editor_category_options, notify=visualEditorChanged)
