from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QObject, Property, QStandardPaths, QTimer, Signal, Slot
from PySide6.QtWidgets import QFileDialog

from app.features.file_management import FileManagementController, FileManagementService, FileRepository
from app.features.filters import FilterController, FilterRepository, ImportedFilterRepository
from app.features.folder_import import FolderImportController, FolderScanner
from app.features.macros import MacroController, MacroRepository, MacroStep
from app.features.search_replace import SearchController
from app.features.suggestions import SuggestionController
from app.shared.filesystem.content_locator import locate_content_root
from app.shared.filesystem.path_service import PathService
from app.ui.file_list_model import FileListModel
from app.ui.filter_models import FilterListModel, RuleListModel
from app.ui.folder_scan_model import FolderScanModel
from app.ui.macro_models import MacroListModel
from app.ui.suggestion_models import SuggestionListModel


class AppController(QObject):
    """QML facade that composes feature controllers.

    The facade keeps the existing QML contract stable while application behavior
    lives in feature-scoped controllers and services.
    """

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
    panelRequested = Signal(str)

    def __init__(self, filter_storage_path: Path | None = None, content_root: Path | None = None) -> None:
        super().__init__()
        self._status_message = "Ready"
        self._content_root = content_root or locate_content_root()

        self._files = FileListModel()
        self._folder_scan = FolderScanModel()
        self._filters = FilterListModel()
        self._editing_rules = RuleListModel()
        self._suggestion_keys = SuggestionListModel()
        self._suggestion_values = SuggestionListModel()
        self._macros = MacroListModel()

        file_repository = FileRepository()
        file_service = FileManagementService(self._files, file_repository)
        self.file_management = FileManagementController(self._files, file_service)
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
        self.macros.refresh_validation(self._filters.filters())

        self._running_macro_index = -1
        self._running_macro_step_index = 0
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

    def get_file_model(self) -> FileListModel:
        return self._files

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

    def get_any_macro_running(self) -> bool:
        return self.macros.any_running

    def get_active_filter_id(self) -> str:
        return self._filters.active_filter_id()

    def get_active_filter_name(self) -> str:
        return self.filters.active_filter_name

    def get_active_filter_color(self) -> str:
        return self.filters.active_filter_color

    def get_has_active_filter(self) -> bool:
        return self.filters.has_active_filter

    def get_file_count(self) -> int:
        return self.file_management.file_count

    def get_active_file_count(self) -> int:
        return self.file_management.active_file_count

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

    def get_active_match_display_index(self) -> int:
        return self.search_replace.active_match_display_index

    def get_active_match_file_count(self) -> int:
        return self.search_replace.active_match_file_count()

    def get_search_text(self) -> str:
        return self.search_replace.search_text

    def set_search_text(self, text: str) -> None:
        if self.search_replace.set_search_text(text):
            self._emit_search_state_changed()

    def get_replace_text(self) -> str:
        return self.search_replace.replace_text

    def set_replace_text(self, text: str) -> None:
        if self.search_replace.set_replace_text(text):
            self._emit_search_state_changed()

    def get_case_sensitive(self) -> bool:
        return self.search_replace.case_sensitive

    def set_case_sensitive(self, value: bool) -> None:
        if self.search_replace.set_case_sensitive(value):
            self._emit_search_state_changed()

    def get_total_matches(self) -> int:
        return self.search_replace.total_matches

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

    def get_editing_rule_count(self) -> int:
        return self.filters.editor_rule_count

    def get_editing_filter_can_save(self) -> bool:
        return self.filters.editor_can_save

    @Slot("QVariant", result=int)
    def addFiles(self, values) -> int:
        paths = PathService.many_from_qml(values)
        return self._add_paths_from_user(paths)

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
        selected_folder = QFileDialog.getExistingDirectory(None, "Add folder")
        if not selected_folder:
            return 0
        return self.scan_folder_paths([Path(selected_folder)])

    @Slot(int, result=bool)
    def removeFile(self, index: int) -> bool:
        if not self.file_management.remove_file(index):
            self._set_status("No file was removed.")
            return False

        self._refresh_document_views()
        self._refresh_suggestions_now()
        self._set_status("Removed file.")
        self._emit_document_state_changed()
        return True

    @Slot(int, result=bool)
    def saveFile(self, index: int) -> bool:
        result = self.file_management.save_file(index)
        if result.errors:
            self._set_status(result.errors[0])
            return False
        if result.saved == 0:
            self._set_status("No changes to save.")
        else:
            self._set_status("Saved file.")
        self.filesChanged.emit()
        self.currentDocumentChanged.emit()
        return result.saved > 0

    @Slot(result=int)
    def saveAll(self) -> int:
        result = self.file_management.save_all()
        if result.errors:
            self._set_status(f"Saved {result.saved} file(s). First error: {result.errors[0]}")
        elif result.saved == 0:
            self._set_status("No changes to save.")
        else:
            self._set_status(f"Saved {result.saved} file(s).")
        self.filesChanged.emit()
        self.currentDocumentChanged.emit()
        return result.saved

    @Slot(int, str, result=bool)
    def updateFileText(self, index: int, text: str) -> bool:
        if not self.file_management.update_text(index, text):
            return False
        self._refresh_document_views()
        self._schedule_suggestions_refresh()
        self._emit_document_state_changed()
        return True

    @Slot(result=bool)
    def formatCurrentJson(self) -> bool:
        if not self.file_management.format_current_file():
            self._set_status("Current file is not valid JSON.")
            return False
        self._refresh_document_views()
        self._refresh_suggestions_now()
        self._set_status("Formatted JSON.")
        self._emit_document_state_changed()
        return True

    @Slot(result=int)
    def replaceCurrentFile(self) -> int:
        replaced = self.search_replace.replace_current_file(self.file_management.current_index)
        self._refresh_document_views()
        if replaced > 0:
            self._refresh_suggestions_now()
        self._set_status(f"Replaced {replaced} match(es).")
        self._emit_document_state_changed()
        return replaced

    @Slot(result=int)
    def replaceAll(self) -> int:
        replaced = self.search_replace.replace_all()
        self._refresh_document_views()
        if replaced > 0:
            self._refresh_suggestions_now()
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
            self._set_status(f"Found {len(result.items)} visual.json file(s), skipped {result.skipped_duplicates} duplicate(s).")
        else:
            self._set_status(f"Found {len(result.items)} visual.json file(s).")
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
        self._refresh_document_views()
        self._set_status(f"Applied {self.filters.active_filter_name} filter.")
        self._emit_filter_state_changed()
        return True

    @Slot(result=bool)
    def deactivateFilter(self) -> bool:
        if not self.filters.deactivate_filter(self._files):
            return False
        self._refresh_document_views()
        self._set_status("Filter deactivated.")
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
        if not self.filters.save_editor():
            self._set_status("Filter name and at least one keyed rule are required.")
            return False
        self._refresh_document_views()
        self._set_status("Saved filter.")
        self.filterEditorChanged.emit()
        self._emit_filter_state_changed()
        return True

    @Slot(int, result=bool)
    def deleteFilter(self, index: int) -> bool:
        deleted = self.filters.delete_filter(index, self._files)
        if not deleted:
            self._set_status("Imported filters cannot be deleted here.")
            return False
        self._refresh_document_views()
        self._set_status("Deleted filter.")
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
        if filter_result.errors:
            self._set_status(f"Reloaded content with {len(filter_result.errors)} filter error(s).")
        else:
            self._set_status("Reloaded content.")
        return True

    @Slot(int, result=bool)
    def runMacro(self, index: int) -> bool:
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
            self._set_status(f"Finished {macro_name}.")
            self.macrosChanged.emit()
            return

        step_index = self._running_macro_step_index
        step = macro.steps[step_index]
        try:
            self._execute_macro_step(step)
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
        if step.type == "filter":
            filter_index = self.filters.filter_index_by_display_name(step.filter_name)
            if filter_index < 0:
                raise ValueError(f"No loaded filter named '{step.filter_name}'.")
            if not self.filters.apply_filter(filter_index, self._files):
                raise ValueError(f"Filter '{step.filter_name}' could not be applied.")
            self._refresh_document_views()
            self._set_status(f"Applied {step.filter_name} filter.")
            self._emit_filter_state_changed()
            return

        if step.type == "search":
            self.panelRequested.emit("search")
            self.search_replace.set_search_text(step.search_value)
            self._set_status(f"Searching for {step.search_value}.")
            self._emit_search_state_changed()
            return

        if step.type == "search-and-replace":
            self.panelRequested.emit("search")
            self.search_replace.set_search_text(step.search_value)
            self.search_replace.set_replace_text(step.replace_value)
            replaced = self.replaceAll()
            self._set_status(f"Macro replaced {replaced} match(es).")
            return

        raise ValueError(f"Unknown step type '{step.type}'.")

    def _reset_macro_run(self) -> None:
        self._running_macro_index = -1
        self._running_macro_step_index = 0

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

    def _refresh_document_views(self) -> None:
        self.filters.apply_to_files(self._files)
        self.file_management.ensure_current_index()
        self.search_replace.refresh()

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

    def _emit_filter_state_changed(self) -> None:
        self._refresh_macro_validation()
        self.filtersChanged.emit()
        self.filesChanged.emit()
        self.currentIndexChanged.emit()
        self.currentDocumentChanged.emit()
        self.searchChanged.emit()
        self.matchNavigationChanged.emit()

    def _emit_search_state_changed(self) -> None:
        self.searchChanged.emit()
        self.currentDocumentChanged.emit()
        self.matchNavigationChanged.emit()

    def _set_add_status(self, result) -> None:
        if result.errors:
            self._set_status(f"Added {result.added} file(s). First error: {result.errors[0]}")
        elif result.skipped:
            self._set_status(f"Added {result.added} file(s), skipped {result.skipped}.")
        else:
            self._set_status(f"Added {result.added} file(s).")

    def _set_status(self, message: str) -> None:
        if self._status_message == message:
            return
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
    folderScanModel = Property(QObject, get_folder_scan_model, notify=folderScanChanged)
    filterModel = Property(QObject, get_filter_model, notify=filtersChanged)
    editingRuleModel = Property(QObject, get_editing_rule_model, notify=filterEditorChanged)
    suggestionKeyModel = Property(QObject, get_suggestion_key_model, notify=suggestionsChanged)
    suggestionValueModel = Property(QObject, get_suggestion_value_model, notify=suggestionsChanged)
    macroModel = Property(QObject, get_macro_model, notify=macrosChanged)

    folderScanCount = Property(int, get_folder_scan_count, notify=folderScanChanged)
    folderScanRoot = Property(str, get_folder_scan_root, notify=folderScanChanged)
    folderImportVisible = Property(bool, get_folder_import_visible, notify=folderScanChanged)

    filterCount = Property(int, get_filter_count, notify=filtersChanged)
    suggestionKeyCount = Property(int, get_suggestion_key_count, notify=suggestionsChanged)
    suggestionValueCount = Property(int, get_suggestion_value_count, notify=suggestionsChanged)
    macroCount = Property(int, get_macro_count, notify=macrosChanged)
    anyMacroRunning = Property(bool, get_any_macro_running, notify=macrosChanged)
    activeFilterId = Property(str, get_active_filter_id, notify=filtersChanged)
    activeFilterName = Property(str, get_active_filter_name, notify=filtersChanged)
    activeFilterColor = Property(str, get_active_filter_color, notify=filtersChanged)
    hasActiveFilter = Property(bool, get_has_active_filter, notify=filtersChanged)

    fileCount = Property(int, get_file_count, notify=filesChanged)
    activeFileCount = Property(int, get_active_file_count, notify=filesChanged)
    hasFiles = Property(bool, get_has_files, notify=filesChanged)
    hasDirtyFiles = Property(bool, get_has_dirty_files, notify=filesChanged)

    currentIndex = Property(int, get_current_index, set_current_index, notify=currentIndexChanged)
    currentText = Property(str, get_current_text, notify=currentDocumentChanged)
    currentName = Property(str, get_current_name, notify=currentDocumentChanged)
    currentPath = Property(str, get_current_path, notify=currentDocumentChanged)
    currentDirty = Property(bool, get_current_dirty, notify=currentDocumentChanged)
    currentValidJson = Property(bool, get_current_valid_json, notify=currentDocumentChanged)
    currentJsonError = Property(str, get_current_json_error, notify=currentDocumentChanged)
    currentMatchCount = Property(int, get_current_match_count, notify=currentDocumentChanged)

    searchText = Property(str, get_search_text, set_search_text, notify=searchChanged)
    replaceText = Property(str, get_replace_text, set_replace_text, notify=searchChanged)
    caseSensitive = Property(bool, get_case_sensitive, set_case_sensitive, notify=searchChanged)
    totalMatches = Property(int, get_total_matches, notify=searchChanged)

    activeMatchFileIndex = Property(int, get_active_match_file_index, notify=matchNavigationChanged)
    activeMatchIndex = Property(int, get_active_match_index, notify=matchNavigationChanged)
    activeMatchLine = Property(int, get_active_match_line, notify=matchNavigationChanged)
    activeMatchDisplayIndex = Property(int, get_active_match_display_index, notify=matchNavigationChanged)
    activeMatchFileCount = Property(int, get_active_match_file_count, notify=matchNavigationChanged)

    statusMessage = Property(str, get_status_message, notify=statusChanged)
    filterEditorVisible = Property(bool, get_filter_editor_visible, notify=filterEditorChanged)
    editingFilterName = Property(str, get_editing_filter_name, set_editing_filter_name, notify=filterEditorChanged)
    editingFilterColor = Property(str, get_editing_filter_color, set_editing_filter_color, notify=filterEditorChanged)
    editingRuleCount = Property(int, get_editing_rule_count, notify=filterEditorChanged)
    editingFilterCanSave = Property(bool, get_editing_filter_can_save, notify=filterEditorChanged)