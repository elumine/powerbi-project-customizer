from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ui.component.shell.workspace_components import WorkspaceComponents
from features.editor.public import SyntaxHighlighterBridge
from features.file_management.public import FileListModel, FileManagementController, FileManagementService, FileRepository, ProjectTreeModel
from features.filters.public import FilterController, FilterListModel, FilterRepository, FilterScopeService, ImportedFilterRepository, RuleListModel
from features.folder_import.public import FolderImportController, FolderScanModel, FolderScanner
from features.history.public import HistoryController, HistoryListModel, HistoryService
from features.changes.public import ChangesListModel
from features.macros.public import MacroController, MacroListModel, MacroRepository
from features.search_replace.public import SearchController, SearchProjectionService, SearchResultListModel
from features.suggestions.public import SuggestionController, SuggestionListModel
from features.visual_editor.public import VisualEditorControlModel, VisualEditorController, VisualEditorService, VisualPropertyCatalog
from infrastructure.filesystem.local_text_files import LocalTextFileReader
from infrastructure.packaging.resource_locator import ResourceLocator
from infrastructure.qt.dialog_gateway import QtDialogGateway
from services.configuration.runtime_paths import RuntimePaths
from services.documents.collection import DocumentCollection
from ui.component.shell.shell_adapter import ShellAdapter
from ui.styles.theme_tokens import DEFAULT_THEME, ThemeTokens


@dataclass(slots=True)
class ApplicationGraph:
    """Objects retained for the Qt/QML engine lifetime."""

    resource_locator: ResourceLocator
    runtime_paths: RuntimePaths
    documents: DocumentCollection
    dialogs: QtDialogGateway
    theme: ThemeTokens
    workspace: WorkspaceComponents
    shell_adapter: ShellAdapter
    editor_adapter: SyntaxHighlighterBridge

    def qml_initial_properties(self) -> dict[str, object]:
        return {"shellAdapter": self.shell_adapter, "editorAdapter": self.editor_adapter}


class DependencyContainer:
    """The only runtime composition root; it is never used as a service locator."""

    def __init__(self, resource_locator: ResourceLocator | None = None, runtime_paths: RuntimePaths | None = None, theme: ThemeTokens = DEFAULT_THEME) -> None:
        self._resource_locator = resource_locator or ResourceLocator.discover()
        self._runtime_paths = runtime_paths or RuntimePaths.discover()
        self._theme = theme

    def build(self, filter_storage_path: Path | None = None, content_root: Path | None = None) -> ApplicationGraph:
        content = content_root or self._resource_locator.content_root()
        storage_path = filter_storage_path or self._runtime_paths.filter_storage_path
        documents = DocumentCollection()
        dialogs = QtDialogGateway()
        workspace = self._build_workspace(documents, content, storage_path)
        shell_adapter = ShellAdapter(
            content_root=content,
            dialogs=dialogs,
            runtime_paths=self._runtime_paths,
            documents=documents,
            components=workspace,
        )
        editor_adapter = SyntaxHighlighterBridge(self._theme)
        return ApplicationGraph(
            resource_locator=self._resource_locator,
            runtime_paths=self._runtime_paths,
            documents=documents,
            dialogs=dialogs,
            theme=self._theme,
            workspace=workspace,
            shell_adapter=shell_adapter,
            editor_adapter=editor_adapter,
        )

    @staticmethod
    def _build_workspace(documents: DocumentCollection, content_root: Path, filter_storage_path: Path) -> WorkspaceComponents:
        files = FileListModel(documents)
        project_tree = ProjectTreeModel()
        folder_scan = FolderScanModel()
        filters_model = FilterListModel()
        editing_rules = RuleListModel()
        suggestion_keys, suggestion_values = SuggestionListModel(), SuggestionListModel()
        macros_model, history_model = MacroListModel(), HistoryListModel()
        changes_model = ChangesListModel(documents)
        search_results, visual_editor_controls = SearchResultListModel(), VisualEditorControlModel()

        file_management = FileManagementController(files, FileManagementService(documents, FileRepository()))
        folder_import = FolderImportController(folder_scan, FolderScanner(LocalTextFileReader()))
        search_replace = SearchController(files, SearchProjectionService())
        imported_filter_repository = ImportedFilterRepository(content_root)
        imported = imported_filter_repository.list_filters()
        filters = FilterController(
            filters_model,
            editing_rules,
            FilterRepository(filter_storage_path),
            imported_filters=imported.filters,
            scope_service=FilterScopeService(),
        )
        suggestions = SuggestionController(suggestion_keys, suggestion_values)
        macros = MacroController(macros_model, MacroRepository(content_root))
        macros.refresh_validation(filters_model.filters())
        history = HistoryController(history_model, HistoryService())
        visual_editor = VisualEditorController(
            visual_editor_controls,
            VisualEditorService(VisualPropertyCatalog(content_root).list_controls()),
        )
        return WorkspaceComponents(
            files=files, project_tree=project_tree, folder_scan=folder_scan,
            filters_model=filters_model, editing_rules=editing_rules,
            suggestion_keys=suggestion_keys, suggestion_values=suggestion_values,
            macros_model=macros_model, history_model=history_model, changes_model=changes_model,
            search_results=search_results, visual_editor_controls=visual_editor_controls,
            file_management=file_management, folder_import=folder_import, search_replace=search_replace,
            imported_filter_repository=imported_filter_repository, imported_filter_errors=imported.errors,
            filters=filters, suggestions=suggestions, macros=macros, history=history,
            visual_editor=visual_editor,
        )

    def create_shell_adapter(self, filter_storage_path: Path | None = None, content_root: Path | None = None) -> ShellAdapter:
        """Factory for integration tests that need the shell adapter only."""
        return self.build(filter_storage_path, content_root).shell_adapter
