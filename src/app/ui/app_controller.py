from __future__ import annotations

import os
import re
from collections.abc import Iterable
from pathlib import Path

from PySide6.QtCore import QObject, Property, QStandardPaths, QTimer, QUrl, Signal, Slot
from PySide6.QtWidgets import QFileDialog

from app.core.content_filter import (
    FILTER_OPERATIONS,
    ContentFilter,
    ContentFilterMatcher,
    FilterRule,
    FilterStorage,
    generate_filter_color,
)
from app.core.display_name import display_name_from_json_text
from app.core.file_document import JsonDocument
from app.core.file_service import FileService, FileServiceError
from app.core.search_service import SearchService
from app.ui.file_list_model import FileListModel
from app.ui.filter_models import FilterListModel, RuleListModel
from app.ui.folder_scan_model import FolderScanItem, FolderScanModel


class AppController(QObject):
    filesChanged = Signal()
    currentIndexChanged = Signal()
    currentDocumentChanged = Signal()
    searchChanged = Signal()
    statusChanged = Signal()
    folderScanChanged = Signal()
    matchNavigationChanged = Signal()
    filtersChanged = Signal()
    filterEditorChanged = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._files = FileListModel()
        self._folder_scan = FolderScanModel()
        self._filters = FilterListModel()
        self._editing_rules = RuleListModel()
        self._filter_storage = FilterStorage(self._filters_storage_path())
        self._filters.reset(self._filter_storage.load())

        self._current_index = -1
        self._search_text = ""
        self._replace_text = ""
        self._case_sensitive = False
        self._total_matches = 0
        self._status_message = "Ready"
        self._folder_import_visible = False
        self._folder_scan_root = ""
        self._active_match_file_index = -1
        self._active_match_index = -1
        self._active_match_line = 0
        self._filter_editor_visible = False
        self._editing_filter_id = ""
        self._editing_filter_name = ""
        self._editing_filter_color = ""

        self._filter_update_timer = QTimer(self)
        self._filter_update_timer.setSingleShot(True)
        self._filter_update_timer.setInterval(250)
        self._filter_update_timer.timeout.connect(self._apply_active_filter_state)

    def get_file_model(self) -> FileListModel:
        return self._files

    def get_folder_scan_model(self) -> FolderScanModel:
        return self._folder_scan

    def get_filters_model(self) -> FilterListModel:
        return self._filters

    def get_editing_rule_model(self) -> RuleListModel:
        return self._editing_rules

    def get_folder_scan_count(self) -> int:
        return self._folder_scan.count

    def get_folder_scan_root(self) -> str:
        return self._folder_scan_root

    def get_folder_import_visible(self) -> bool:
        return self._folder_import_visible

    def get_filter_count(self) -> int:
        return self._filters.count

    def get_active_filter_id(self) -> str:
        return self._filters.active_filter_id()

    def get_active_filter_name(self) -> str:
        return self._filters.active_filter_name()

    def get_active_filter_color(self) -> str:
        return self._filters.active_filter_color()

    def get_has_active_filter(self) -> bool:
        return self._filters.active_filter() is not None

    def get_file_count(self) -> int:
        return self._files.count

    def get_active_file_count(self) -> int:
        return sum(1 for document in self._files.documents() if document.is_active)

    def get_has_files(self) -> bool:
        return self._files.count > 0

    def get_has_dirty_files(self) -> bool:
        return any(document.is_dirty for document in self._files.documents())

    def get_current_index(self) -> int:
        return self._current_index

    def set_current_index(self, index: int) -> None:
        index = self._coerce_user_selected_index(index)
        if self._current_index == index:
            return
        self._current_index = index
        self.currentIndexChanged.emit()
        self.currentDocumentChanged.emit()

    def get_current_text(self) -> str:
        document = self._current_document()
        return document.text if document is not None else ""

    def get_current_name(self) -> str:
        document = self._current_document()
        return document.name if document is not None else "No file selected"

    def get_current_path(self) -> str:
        document = self._current_document()
        return str(document.path) if document is not None else ""

    def get_current_dirty(self) -> bool:
        document = self._current_document()
        return document.is_dirty if document is not None else False

    def get_current_valid_json(self) -> bool:
        document = self._current_document()
        return document.is_valid_json if document is not None else True

    def get_current_json_error(self) -> str:
        document = self._current_document()
        return document.json_error if document is not None else ""

    def get_current_match_count(self) -> int:
        document = self._current_document()
        return document.match_count if document is not None else 0

    def get_active_match_file_index(self) -> int:
        return self._active_match_file_index

    def get_active_match_index(self) -> int:
        return self._active_match_index

    def get_active_match_line(self) -> int:
        return self._active_match_line

    def get_active_match_display_index(self) -> int:
        return self._active_match_index + 1 if self._active_match_index >= 0 else 0

    def get_active_match_file_count(self) -> int:
        document = self._files.document_at(self._active_match_file_index)
        return document.match_count if document is not None and document.is_active else 0

    def get_search_text(self) -> str:
        return self._search_text

    def set_search_text(self, text: str) -> None:
        text = text or ""
        if self._search_text == text:
            return
        self._search_text = text
        self._refresh_match_counts()
        self.searchChanged.emit()
        self.currentDocumentChanged.emit()

    def get_replace_text(self) -> str:
        return self._replace_text

    def set_replace_text(self, text: str) -> None:
        text = text or ""
        if self._replace_text == text:
            return
        self._replace_text = text
        self._refresh_match_counts()
        self.searchChanged.emit()
        self.currentDocumentChanged.emit()

    def get_case_sensitive(self) -> bool:
        return self._case_sensitive

    def set_case_sensitive(self, value: bool) -> None:
        value = bool(value)
        if self._case_sensitive == value:
            return
        self._case_sensitive = value
        self._refresh_match_counts()
        self.searchChanged.emit()
        self.currentDocumentChanged.emit()

    def get_total_matches(self) -> int:
        return self._total_matches

    def get_status_message(self) -> str:
        return self._status_message

    def get_filter_editor_visible(self) -> bool:
        return self._filter_editor_visible

    def get_editing_filter_name(self) -> str:
        return self._editing_filter_name

    def set_editing_filter_name(self, value: str) -> None:
        value = value or ""
        if self._editing_filter_name == value:
            return
        self._editing_filter_name = value
        self.filterEditorChanged.emit()

    def get_editing_filter_color(self) -> str:
        return self._editing_filter_color

    def set_editing_filter_color(self, value: str) -> None:
        value = value or generate_filter_color(self._filters.used_colors(self._editing_filter_id))
        if self._editing_filter_color == value:
            return
        self._editing_filter_color = value
        self.filterEditorChanged.emit()

    def get_editing_rule_count(self) -> int:
        return self._editing_rules.count

    def get_editing_filter_can_save(self) -> bool:
        rules = self._editing_rules.rules()
        return bool(self._editing_filter_name.strip()) and bool(rules) and all(rule.key.strip() for rule in rules)

    @Slot(result=int)
    def openFileDialog(self) -> int:
        paths, _selected_filter = QFileDialog.getOpenFileNames(
            None,
            "Open JSON files",
            "",
            "JSON files (*.json);;All files (*.*)",
        )
        return self._add_file_paths(Path(path) for path in paths)

    @Slot(result=int)
    def openFolderDialog(self) -> int:
        folder = QFileDialog.getExistingDirectory(None, "Add folder")
        if not folder:
            return 0
        return self.scan_folder_paths([Path(folder)])

    @Slot("QVariant", result=int)
    def addFiles(self, items) -> int:
        paths = self._paths_from_input(items)
        file_paths = [path for path in paths if path.is_file()]
        folder_paths = [path for path in paths if path.is_dir()]
        added = self._add_file_paths(file_paths)
        if folder_paths:
            self.scan_folder_paths(folder_paths)
        return added

    @Slot(int)
    def removeFile(self, index: int) -> None:
        removed = self._files.remove_document(index)
        if removed is None:
            return

        if self._current_index == index:
            self._current_index = self._first_active_index(start=index)
            self.currentIndexChanged.emit()
            self.currentDocumentChanged.emit()
        elif self._current_index > index:
            self._current_index -= 1
            self.currentIndexChanged.emit()
            self.currentDocumentChanged.emit()

        self._refresh_match_counts()
        self._emit_files_changed()
        self._set_status(f"Removed {removed.name}.")

    @Slot(int, str)
    def updateFileText(self, index: int, text: str) -> None:
        if not self._files.set_document_text(index, text or ""):
            return

        if self._current_index == index:
            self.currentDocumentChanged.emit()
        self._emit_files_changed()
        if self.get_has_active_filter():
            self._filter_update_timer.start()
        else:
            self._refresh_match_counts()

    @Slot(result=bool)
    def formatCurrentJson(self) -> bool:
        if self._current_index < 0:
            self._set_status("Select a JSON file before formatting.")
            return False

        document = self._files.document_at(self._current_index)
        if document is None:
            return False

        try:
            formatted = document.formatted_text()
        except ValueError:
            self._set_status(f"Cannot format {document.name}: {document.json_error}")
            return False

        if self._files.set_document_text(self._current_index, formatted):
            self.currentDocumentChanged.emit()
            self._emit_files_changed()
            if self.get_has_active_filter():
                self._filter_update_timer.start()
            else:
                self._refresh_match_counts()
        self._set_status(f"Formatted {document.name}.")
        return True

    @Slot(int, result=bool)
    def saveFile(self, index: int) -> bool:
        document = self._files.document_at(index)
        if document is None:
            return False

        try:
            FileService.write_text(document.path, document.text)
        except FileServiceError as error:
            self._set_status(str(error))
            return False

        self._files.mark_saved(index)
        self._emit_files_changed()
        if index == self._current_index:
            self.currentDocumentChanged.emit()
        self._set_status(f"Saved {document.name}.")
        return True

    @Slot(result=int)
    def saveAll(self) -> int:
        saved = 0
        for row, document in enumerate(self._files.documents()):
            if not document.is_dirty:
                continue
            try:
                FileService.write_text(document.path, document.text)
            except FileServiceError as error:
                self._set_status(str(error))
                continue
            self._files.mark_saved(row)
            saved += 1

        self._emit_files_changed()
        self.currentDocumentChanged.emit()
        self._set_status(f"Saved {saved} file(s).")
        return saved

    @Slot(result=int)
    def replaceCurrentFile(self) -> int:
        return self.replaceInFile(self._current_index)

    @Slot(int, result=int)
    def replaceInFile(self, index: int) -> int:
        document = self._files.document_at(index)
        if document is None or self._search_text == "":
            return 0
        if not document.is_active:
            self._set_status("Replace in file is available only for active files.")
            return 0

        updated_text, replacements = SearchService.replace(
            document.text,
            self._search_text,
            self._replace_text,
            self._case_sensitive,
        )
        if replacements == 0:
            self._set_status(f"No matches in {document.name}.")
            return 0

        self._files.set_document_text(index, updated_text)
        if index == self._current_index:
            self.currentDocumentChanged.emit()
        self._emit_files_changed()
        self._after_replacement(f"Replaced {replacements} match(es) in {document.name}.")
        return replacements

    @Slot(result=int)
    def replaceAll(self) -> int:
        if self._search_text == "":
            return 0

        total_replacements = 0
        active_rows = [(row, document) for row, document in enumerate(self._files.documents()) if document.is_active]
        for row, document in active_rows:
            updated_text, replacements = SearchService.replace(
                document.text,
                self._search_text,
                self._replace_text,
                self._case_sensitive,
            )
            if replacements == 0:
                continue
            self._files.set_document_text(row, updated_text)
            total_replacements += replacements

        self._emit_files_changed()
        self.currentDocumentChanged.emit()
        self._after_replacement(f"Replaced {total_replacements} match(es) in active files.")
        return total_replacements

    @Slot(int, int)
    def navigateToMatch(self, file_index: int, match_index: int) -> None:
        document = self._files.document_at(file_index)
        if document is None or not document.is_active or document.match_count <= 0:
            return

        match_index = max(0, min(match_index, document.match_count - 1))
        self._set_current_index_internal(file_index)
        self._set_active_match(file_index, match_index)

    @Slot()
    def navigateNextMatch(self) -> None:
        self._navigate_match(step=1)

    @Slot()
    def navigatePreviousMatch(self) -> None:
        self._navigate_match(step=-1)

    def scan_folder_paths(self, paths: Iterable[str | Path | QUrl]) -> int:
        folder_paths = [path for path in self._paths_from_input(paths) if path.exists()]
        roots = [path for path in folder_paths if path.is_dir()]
        file_roots = [path for path in folder_paths if path.is_file() and path.name.lower() == "visual.json"]

        found_paths: list[Path] = []
        for root in roots:
            found_paths.extend(path.resolve() for path in root.rglob("visual.json") if path.is_file())
        found_paths.extend(path.resolve() for path in file_roots)

        unique_paths = sorted(set(found_paths), key=lambda item: str(item).casefold())
        base = self._folder_scan_base(roots, unique_paths)
        items: list[FolderScanItem] = []
        for path in unique_paths:
            try:
                text = FileService.read_text(path)
                display_name = display_name_from_json_text(text, path.name)
            except FileServiceError:
                display_name = path.name
            items.append(FolderScanItem(path=path, display_name=display_name, relative_path=self._relative_path(path, base)))

        self._folder_scan.reset(items)
        self._folder_scan_root = "; ".join(str(path) for path in roots or file_roots)
        self._folder_import_visible = True
        self.folderScanChanged.emit()
        self._set_status(f"Found {len(items)} visual.json file(s).")
        return len(items)

    @Slot(result=int)
    def confirmFolderImport(self) -> int:
        paths = self._folder_scan.paths()
        added = self._add_file_paths(paths)
        self._folder_import_visible = False
        self._folder_scan_root = ""
        self._folder_scan.clear()
        self.folderScanChanged.emit()
        self._set_status(f"Imported {added} file(s).")
        return added

    @Slot()
    def cancelFolderImport(self) -> None:
        self._folder_import_visible = False
        self._folder_scan_root = ""
        self._folder_scan.clear()
        self.folderScanChanged.emit()
        self._set_status("Folder import cancelled.")

    @Slot(int)
    def applyFilter(self, index: int) -> None:
        content_filter = self._filters.filter_at(index)
        if content_filter is None:
            return
        self._filters.set_active_filter_id(content_filter.id)
        self.filtersChanged.emit()
        self._apply_active_filter_state()
        self._set_status(f"Applied filter: {content_filter.display_name}.")

    @Slot()
    def deactivateFilter(self) -> None:
        if self._filters.active_filter() is None:
            return
        self._filters.set_active_filter_id("")
        self.filtersChanged.emit()
        self._apply_active_filter_state()
        self._set_status("Filter deactivated.")

    @Slot(int)
    def deleteFilter(self, index: int) -> None:
        active_id = self._filters.active_filter_id()
        removed = self._filters.remove_filter(index)
        if removed is None:
            return

        self._persist_filters()
        if self._editing_filter_id == removed.id:
            self.cancelFilterEditor()
        self.filtersChanged.emit()
        if active_id == removed.id:
            self._apply_active_filter_state()
        self._set_status(f"Deleted filter: {removed.display_name}.")

    @Slot()
    def openNewFilterEditor(self) -> None:
        self._editing_filter_id = ""
        self._editing_filter_name = ""
        self._editing_filter_color = generate_filter_color(self._filters.used_colors())
        self._editing_rules.reset([FilterRule.create()])
        self._filter_editor_visible = True
        self.filterEditorChanged.emit()

    @Slot(int)
    def openEditFilterEditor(self, index: int) -> None:
        content_filter = self._filters.filter_at(index)
        if content_filter is None:
            return
        self._editing_filter_id = content_filter.id
        self._editing_filter_name = content_filter.display_name
        self._editing_filter_color = content_filter.color
        self._editing_rules.reset(content_filter.rules)
        self._filter_editor_visible = True
        self.filterEditorChanged.emit()

    @Slot()
    def cancelFilterEditor(self) -> None:
        self._filter_editor_visible = False
        self._editing_filter_id = ""
        self._editing_filter_name = ""
        self._editing_filter_color = ""
        self._editing_rules.reset([])
        self.filterEditorChanged.emit()

    @Slot(result=bool)
    def saveFilterEditor(self) -> bool:
        raw_rules = self._editing_rules.rules()
        display_name = self._editing_filter_name.strip()
        if not display_name or not raw_rules or any(not rule.key.strip() for rule in raw_rules):
            self._set_status("Filter name and every rule key are required.")
            return False

        rules = self._clean_editing_rules()

        if self._editing_filter_id:
            content_filter = ContentFilter(
                id=self._editing_filter_id,
                display_name=display_name,
                color=self._editing_filter_color,
                rules=rules,
            )
        else:
            content_filter = ContentFilter.create(
                display_name,
                rules,
                color=self._editing_filter_color,
                used_colors=self._filters.used_colors(),
            )

        was_active = content_filter.id == self._filters.active_filter_id()
        self._filters.upsert_filter(content_filter)
        self._persist_filters()
        self.cancelFilterEditor()
        self.filtersChanged.emit()
        if was_active:
            self._apply_active_filter_state()
        self._set_status(f"Saved filter: {content_filter.display_name}.")
        return True

    @Slot()
    def randomizeEditingFilterColor(self) -> None:
        self._editing_filter_color = generate_filter_color(self._filters.used_colors(self._editing_filter_id))
        self.filterEditorChanged.emit()

    @Slot()
    def addEditingRule(self) -> None:
        self._editing_rules.add_rule()
        self.filterEditorChanged.emit()

    @Slot(int)
    def removeEditingRule(self, index: int) -> None:
        self._editing_rules.remove_rule(index)
        self.filterEditorChanged.emit()

    @Slot(int, str)
    def updateEditingRuleKey(self, index: int, key: str) -> None:
        self._editing_rules.update_rule(index, key=key or "")
        self.filterEditorChanged.emit()

    @Slot(int, str)
    def updateEditingRuleOperation(self, index: int, operation: str) -> None:
        if operation not in FILTER_OPERATIONS:
            operation = "equals"
        self._editing_rules.update_rule(index, operation=operation)
        self.filterEditorChanged.emit()

    @Slot(int, str)
    def updateEditingRuleValue(self, index: int, value: str) -> None:
        self._editing_rules.update_rule(index, value=value or "")
        self.filterEditorChanged.emit()

    def _add_file_paths(self, paths: Iterable[str | Path]) -> int:
        existing_paths = self._files.paths()
        added = 0
        skipped = 0
        errors: list[str] = []

        for raw_path in paths:
            path = Path(raw_path).expanduser().resolve()
            if path in existing_paths:
                skipped += 1
                continue
            if not path.is_file() or path.suffix.casefold() != ".json":
                skipped += 1
                continue

            try:
                text = FileService.read_text(path)
            except FileServiceError as error:
                errors.append(str(error))
                continue

            row = self._files.add_document(JsonDocument(path=path, text=text))
            existing_paths.add(path)
            added += 1
            if self._current_index < 0:
                self._current_index = row
                self.currentIndexChanged.emit()
                self.currentDocumentChanged.emit()

        if added:
            self._apply_active_filter_state()
        else:
            self._refresh_match_counts()

        self._emit_files_changed()
        if errors:
            self._set_status(errors[-1])
        elif added:
            suffix = f" ({skipped} skipped)." if skipped else "."
            self._set_status(f"Added {added} JSON file(s){suffix}")
        elif skipped:
            self._set_status("No new JSON files were added.")
        return added

    def _after_replacement(self, status_message: str) -> None:
        if self.get_has_active_filter():
            self._apply_active_filter_state()
        else:
            self._refresh_match_counts()
        self._set_status(status_message)

    def _apply_active_filter_state(self) -> None:
        active_filter = self._filters.active_filter()
        active_color = active_filter.color if active_filter is not None else ""

        for row, document in enumerate(self._files.documents()):
            if active_filter is None:
                self._files.set_document_active(row, True, "")
                continue

            is_match = document.is_valid_json and ContentFilterMatcher.matches_filter(document.parsed_json, active_filter)
            self._files.set_document_active(row, is_match, active_color if is_match else "")

        self._ensure_selectable_current()
        self._refresh_match_counts()
        self._emit_files_changed()
        self.filtersChanged.emit()
        self.currentDocumentChanged.emit()

    def _refresh_match_counts(self) -> None:
        total_matches = 0
        for row, document in enumerate(self._files.documents()):
            if document.is_active:
                match_count = SearchService.count(document.text, self._search_text, self._case_sensitive)
                previews = SearchService.previews(document.text, self._search_text, self._replace_text, self._case_sensitive)
                highlighted = SearchService.highlighted_html(
                    document.text,
                    self._search_text,
                    self._replace_text,
                    self._case_sensitive,
                )
                total_matches += match_count
            else:
                match_count = 0
                previews = []
                highlighted = SearchService.highlighted_html(document.text, "", "", self._case_sensitive)
            self._files.refresh_search_view(row, match_count, previews, highlighted)

        self._total_matches = total_matches
        self._sync_active_match_after_refresh()
        self.searchChanged.emit()

    def _sync_active_match_after_refresh(self) -> None:
        old_state = (self._active_match_file_index, self._active_match_index, self._active_match_line)

        document = self._files.document_at(self._active_match_file_index)
        if self._search_text == "" or self._total_matches == 0:
            self._active_match_file_index = -1
            self._active_match_index = -1
            self._active_match_line = 0
        elif document is not None and document.is_active and 0 <= self._active_match_index < document.match_count:
            self._active_match_line = self._line_for_match_index(document.text, self._active_match_index)
        else:
            first = self._first_file_with_matches()
            if first >= 0:
                self._active_match_file_index = first
                self._active_match_index = 0
                first_document = self._files.document_at(first)
                self._active_match_line = self._line_for_match_index(first_document.text, 0) if first_document else 0
            else:
                self._active_match_file_index = -1
                self._active_match_index = -1
                self._active_match_line = 0

        if old_state != (self._active_match_file_index, self._active_match_index, self._active_match_line):
            self.matchNavigationChanged.emit()

    def _navigate_match(self, step: int) -> None:
        positions = self._match_positions()
        if not positions:
            self._set_active_match(-1, -1)
            return

        current = (self._active_match_file_index, self._active_match_index)
        try:
            current_position = positions.index(current)
        except ValueError:
            current_position = -1 if step > 0 else 0

        next_file_index, next_match_index = positions[(current_position + step) % len(positions)]
        self.navigateToMatch(next_file_index, next_match_index)

    def _match_positions(self) -> list[tuple[int, int]]:
        positions: list[tuple[int, int]] = []
        for row, document in enumerate(self._files.documents()):
            if not document.is_active or document.match_count <= 0:
                continue
            positions.extend((row, match_index) for match_index in range(document.match_count))
        return positions

    def _set_active_match(self, file_index: int, match_index: int) -> None:
        old_state = (self._active_match_file_index, self._active_match_index, self._active_match_line)
        document = self._files.document_at(file_index)
        if document is None or match_index < 0 or not document.is_active or document.match_count <= 0:
            self._active_match_file_index = -1
            self._active_match_index = -1
            self._active_match_line = 0
        else:
            self._active_match_file_index = file_index
            self._active_match_index = min(match_index, document.match_count - 1)
            self._active_match_line = self._line_for_match_index(document.text, self._active_match_index)

        if old_state != (self._active_match_file_index, self._active_match_index, self._active_match_line):
            self.matchNavigationChanged.emit()

    def _line_for_match_index(self, text: str, match_index: int) -> int:
        if self._search_text == "":
            return 0
        flags = 0 if self._case_sensitive else re.IGNORECASE
        for index, match in enumerate(re.finditer(re.escape(self._search_text), text, flags)):
            if index == match_index:
                return text.count("\n", 0, match.start()) + 1
        return 0

    def _first_file_with_matches(self) -> int:
        for row, document in enumerate(self._files.documents()):
            if document.is_active and document.match_count > 0:
                return row
        return -1

    def _first_active_index(self, start: int = 0) -> int:
        documents = list(self._files.documents())
        if not documents:
            return -1
        for row in range(max(0, start), len(documents)):
            if documents[row].is_active:
                return row
        for row, document in enumerate(documents):
            if document.is_active:
                return row
        return -1

    def _ensure_selectable_current(self) -> None:
        current = self._files.document_at(self._current_index)
        if current is not None and current.is_active:
            return

        new_index = self._first_active_index()
        if self._current_index == new_index:
            return
        self._current_index = new_index
        self.currentIndexChanged.emit()

    def _coerce_user_selected_index(self, index: int) -> int:
        document = self._files.document_at(index)
        if document is None:
            return -1
        if document.is_active:
            return index

        current = self._files.document_at(self._current_index)
        if current is not None and current.is_active:
            return self._current_index
        return self._first_active_index()

    def _set_current_index_internal(self, index: int) -> None:
        if self._current_index == index:
            return
        self._current_index = index
        self.currentIndexChanged.emit()
        self.currentDocumentChanged.emit()

    def _current_document(self) -> JsonDocument | None:
        document = self._files.document_at(self._current_index)
        if document is None or not document.is_active:
            return None
        return document

    def _clean_editing_rules(self) -> list[FilterRule]:
        rules: list[FilterRule] = []
        for rule in self._editing_rules.rules():
            key = rule.key.strip()
            if key == "":
                continue
            operation = rule.operation if rule.operation in FILTER_OPERATIONS else "equals"
            rules.append(FilterRule(id=rule.id, key=key, operation=operation, value=rule.value))
        return rules

    def _persist_filters(self) -> None:
        try:
            self._filter_storage.save(self._filters.filters())
        except OSError as error:
            self._set_status(f"Could not save filters: {error}")

    def _emit_files_changed(self) -> None:
        self.filesChanged.emit()

    def _set_status(self, message: str) -> None:
        if self._status_message == message:
            return
        self._status_message = message
        self.statusChanged.emit()

    @staticmethod
    def _paths_from_input(items) -> list[Path]:
        if items is None:
            return []
        if isinstance(items, (str, Path, QUrl)):
            iterable = [items]
        else:
            try:
                iterable = list(items)
            except TypeError:
                iterable = [items]

        paths: list[Path] = []
        for item in iterable:
            if isinstance(item, QUrl):
                value = item.toLocalFile() if item.isLocalFile() else item.toString()
            elif hasattr(item, "toLocalFile"):
                value = item.toLocalFile()
            else:
                value = str(item)

            if value.startswith("file:"):
                value = QUrl(value).toLocalFile()
            if value:
                paths.append(Path(value).expanduser().resolve())
        return paths

    @staticmethod
    def _folder_scan_base(roots: list[Path], found_paths: list[Path]) -> Path | None:
        if roots:
            return roots[0] if len(roots) == 1 else None
        if found_paths:
            return found_paths[0].parent
        return None

    @staticmethod
    def _relative_path(path: Path, base: Path | None) -> str:
        if base is None:
            return str(path)
        try:
            return str(path.relative_to(base))
        except ValueError:
            return str(path)

    @staticmethod
    def _filters_storage_path() -> Path:
        override = os.environ.get("JSON_MULTI_EDITOR_FILTERS_PATH")
        if override:
            return Path(override).expanduser().resolve()

        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "JSON Multi Editor" / "filters.json"

        config_root = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)
        if config_root:
            return Path(config_root) / "filters.json"

        return Path.home() / ".json_multi_editor" / "filters.json"

    fileModel = Property(QObject, get_file_model, notify=filesChanged)
    folderScanModel = Property(QObject, get_folder_scan_model, notify=folderScanChanged)
    filterModel = Property(QObject, get_filters_model, notify=filtersChanged)
    editingRuleModel = Property(QObject, get_editing_rule_model, notify=filterEditorChanged)
    folderScanCount = Property(int, get_folder_scan_count, notify=folderScanChanged)
    folderScanRoot = Property(str, get_folder_scan_root, notify=folderScanChanged)
    folderImportVisible = Property(bool, get_folder_import_visible, notify=folderScanChanged)
    filterCount = Property(int, get_filter_count, notify=filtersChanged)
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
    activeMatchFileIndex = Property(int, get_active_match_file_index, notify=matchNavigationChanged)
    activeMatchIndex = Property(int, get_active_match_index, notify=matchNavigationChanged)
    activeMatchLine = Property(int, get_active_match_line, notify=matchNavigationChanged)
    activeMatchDisplayIndex = Property(int, get_active_match_display_index, notify=matchNavigationChanged)
    activeMatchFileCount = Property(int, get_active_match_file_count, notify=matchNavigationChanged)
    searchText = Property(str, get_search_text, set_search_text, notify=searchChanged)
    replaceText = Property(str, get_replace_text, set_replace_text, notify=searchChanged)
    caseSensitive = Property(bool, get_case_sensitive, set_case_sensitive, notify=searchChanged)
    totalMatches = Property(int, get_total_matches, notify=searchChanged)
    statusMessage = Property(str, get_status_message, notify=statusChanged)
    filterEditorVisible = Property(bool, get_filter_editor_visible, notify=filterEditorChanged)
    editingFilterName = Property(str, get_editing_filter_name, set_editing_filter_name, notify=filterEditorChanged)
    editingFilterColor = Property(str, get_editing_filter_color, set_editing_filter_color, notify=filterEditorChanged)
    editingRuleCount = Property(int, get_editing_rule_count, notify=filterEditorChanged)
    editingFilterCanSave = Property(bool, get_editing_filter_can_save, notify=filterEditorChanged)

