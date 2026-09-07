from __future__ import annotations

from dataclasses import dataclass

from features.file_management.public import FileListModel, FileManagementController, ProjectTreeModel
from features.filters.public import FilterController, FilterListModel, ImportedFilterRepository, RuleListModel
from features.folder_import.public import FolderImportController, FolderScanModel
from features.history.public import HistoryController, HistoryListModel
from features.macros.public import MacroController, MacroListModel
from features.search_replace.public import SearchController, SearchResultListModel
from features.suggestions.public import SuggestionController, SuggestionListModel
from features.visual_editor.public import VisualEditorControlModel, VisualEditorController


@dataclass(slots=True)
class WorkspaceComponents:
    """Already-constructed feature presenters and models injected into the shell."""

    files: FileListModel
    project_tree: ProjectTreeModel
    folder_scan: FolderScanModel
    filters_model: FilterListModel
    editing_rules: RuleListModel
    suggestion_keys: SuggestionListModel
    suggestion_values: SuggestionListModel
    macros_model: MacroListModel
    history_model: HistoryListModel
    search_results: SearchResultListModel
    visual_editor_controls: VisualEditorControlModel
    file_management: FileManagementController
    folder_import: FolderImportController
    search_replace: SearchController
    imported_filter_repository: ImportedFilterRepository
    imported_filter_errors: list[str]
    filters: FilterController
    suggestions: SuggestionController
    macros: MacroController
    history: HistoryController
    visual_editor: VisualEditorController
