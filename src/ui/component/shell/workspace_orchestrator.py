from __future__ import annotations

from ui.component.shell.workspace_components import WorkspaceComponents
from entities.powerbi.relationships import PageVisualLinker


class WorkspaceViewOrchestrator:
    """Coordinates derived workspace projections after an explicit use-case result."""

    def __init__(self, components: WorkspaceComponents, linker: PageVisualLinker | None = None) -> None:
        self._components = components
        self._linker = linker or PageVisualLinker()

    def refresh_documents(self, *, reapply_filter: bool = True) -> None:
        components = self._components
        self._linker.rebuild(components.files.collection.documents())
        if reapply_filter:
            components.filters.apply_to_files(components.files)
        components.file_management.ensure_current_index()
        components.search_replace.refresh()
        components.search_results.reset_from_files(components.files)
        components.visual_editor.refresh(components.files)
        components.project_tree.reset_from_files(components.files)

    def refresh_suggestions_now(self) -> None:
        self._components.suggestions.refresh_now(self._components.files)

    def schedule_suggestions_refresh(self) -> None:
        self._components.suggestions.schedule_refresh(self._components.files)

    def refresh_macro_validation(self) -> None:
        components = self._components
        components.macros.refresh_validation(components.filters_model.filters())
