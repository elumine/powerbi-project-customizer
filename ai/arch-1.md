# Architecture Refactor Plan

## Context

The current application is a Python desktop app using PySide6, QML, and Qt models for multi-file JSON editing. It already has a useful first split between:

- `src/app/core`: JSON document, file service, search service, content filters.
- `src/app/ui`: Qt application bootstrap, QML controller, Qt list models, syntax highlighter, widgets/pages placeholders.

The main architectural problem is that the app still behaves like one large app controller and one large view:

- `src/app/ui/app_controller.py` owns file state, current selection, search/replace state, folder import state, filter editor state, filter persistence, timers, and UI signals.
- `src/app/ui/qml/App.qml` is a single large QML screen containing picker, explorer, search, editor, filter, modal, and shared component definitions.
- `src/app/ui/application.py` has smoke-test workflow logic mixed into the UI bootstrap module.
- Some folders such as `src/app/file-system` use a hyphenated package name, which is not Python-import friendly.
- `src/app/json/json.py` and `src/app/file-system/file-system.py` look like early experimental modules and overlap with `core`.

Important current correctness issue: the checked-in `AppController` exposes many getters, but the current QML and smoke test call slots/properties such as `openFileDialog`, `addFiles`, `scan_folder_paths`, `confirmFolderImport`, `replaceAll`, `saveAll`, `fileModel`, `searchText`, and others. In the current source tree, those are not defined as Qt `Property` or `Slot` members in `app_controller.py`. Before or during the refactor, the controller contract must be restored and tested.

## Target Architecture

Use a feature-sliced architecture similar to a Svelte or React app, adapted for a Python/PySide desktop app. The goal is not to copy frontend folder names blindly, but to separate the application into vertical features with explicit public APIs.

Recommended high-level layout:

```text
src/app/
  main.py
  bootstrap/
    application.py
    dependency_container.py
    qml_registry.py
  shared/
    filesystem/
      file_reader.py
      file_writer.py
      path_service.py
    json/
      json_parser.py
      json_formatter.py
    qt/
      list_model_base.py
      signal_bus.py
    errors.py
  entities/
    document/
      json_document.py
      document_id.py
    filter/
      content_filter.py
      filter_rule.py
  features/
    file_management/
      file_repository.py
      file_collection.py
      file_management_service.py
      file_management_controller.py
      file_list_model.py
      qml/
        FileExplorer.qml
        FilePicker.qml
    search_replace/
      search_query.py
      search_result.py
      search_service.py
      replace_service.py
      search_controller.py
      qml/
        SearchPanel.qml
        MatchPreviewList.qml
    folder_import/
      folder_scanner.py
      folder_import_session.py
      folder_import_controller.py
      folder_scan_model.py
      qml/
        FolderImportDialog.qml
    filters/
      filter_repository.py
      filter_matcher.py
      filter_editor_session.py
      filter_controller.py
      filter_models.py
      qml/
        FilterPanel.qml
        FilterEditorDialog.qml
    editor/
      editor_controller.py
      syntax_highlighter.py
      qml/
        JsonEditor.qml
  shell/
    app_shell_controller.py
    navigation_state.py
    qml/
      App.qml
      Sidebar.qml
      Toolbar.qml
      StatusBar.qml
```

## OOP Style

Move toward a Java-like object model while staying idiomatic Python:

- Use constructor injection instead of creating every dependency inside controllers.
- Prefer service classes with clear responsibilities: `FolderScanner`, `SearchService`, `ReplaceService`, `FilterMatcher`, `FileRepository`.
- Use repository classes for persistence: `FileRepository`, `FilterRepository`.
- Use session/state objects for multi-step UI flows: `FolderImportSession`, `FilterEditorSession`, `SearchSession`.
- Keep Qt `QObject` controllers thin. They should translate QML calls into application use cases, expose Qt properties/signals, and avoid business rules.
- Use `typing.Protocol` or abstract base classes where a dependency has multiple implementations or needs easy test doubles.
- Keep domain entities free from Qt imports. `JsonDocument`, `ContentFilter`, and `FilterRule` should not depend on UI models or signals.

Example class split:

```text
FileManagementController
  depends on FileManagementService, FileListModel
  exposes Qt slots/properties for QML

FileManagementService
  depends on FileRepository, JsonParser, DisplayNameService
  owns open/add/remove/save/format use cases

FileRepository
  depends on FileReader, FileWriter
  owns filesystem persistence details

JsonDocument
  pure domain entity with text, path, dirty state, parse status
```

## Feature Boundaries

### File Management

Owns adding files, removing files, current selection, saving, save-all, formatting, dirty state, and duplicate path handling.

Should not own search, filtering, or folder scan modal behavior.

### Folder Import

Owns recursive folder scanning, `visual.json` selection rules, import preview state, cancel/confirm lifecycle, and folder import errors.

Should return selected paths to file management instead of directly mutating the file list.

### Search And Replace

Owns query state, match counting, previews, active match navigation, highlighted HTML, replace-current-file, and replace-all.

Should operate over an explicit document collection interface instead of reaching into `FileListModel` directly.

### Filters

Owns filter storage, filter editor draft state, rule validation, active filter selection, and applying active/inactive state to documents.

Should not persist from the Qt model directly. Persist through a repository.

### Editor

Owns editor-specific behavior: current document text updates, syntax highlighting, validation messages, reveal-line commands, and formatting requests.

Should delegate document mutations to file management or document services.

### Shell

Owns app-level concerns: page name, active side panel, status message, global shortcuts, global modal visibility, and cross-feature wiring.

This becomes the app facade exposed to QML, replacing the current single `AppController`.

## QML Refactor

Split `src/app/ui/qml/App.qml` into composable QML modules:

- `App.qml`: root window, layout shell, feature composition only.
- `components/ChromeButton.qml`, `components/IconButton.qml`, `components/Field.qml`, `components/MutedLabel.qml`.
- `features/file-management/FileExplorer.qml`.
- `features/file-management/FilePicker.qml`.
- `features/search-replace/SearchPanel.qml`.
- `features/editor/JsonEditor.qml`.
- `features/folder-import/FolderImportDialog.qml`.
- `features/filters/FilterPanel.qml`.
- `features/filters/FilterEditorDialog.qml`.

QML should bind to feature controllers, not a god controller. For example:

```qml
FileExplorer {
    model: fileManagementController.fileModel
    currentIndex: fileManagementController.currentIndex
    onSaveRequested: fileManagementController.saveFile(index)
}
```

## Migration Plan

1. Restore and lock the current controller contract.
   - Add tests that assert every QML-called slot/property exists on the controller.
   - Make the smoke test fail fast when a QML/controller contract is missing.

2. Extract pure services first.
   - Move folder scanning into `FolderScanner`.
   - Move file list operations into `FileManagementService`.
   - Move replace workflows into `ReplaceService`.
   - Move filter persistence into `FilterRepository`.

3. Introduce feature controllers.
   - Create `FileManagementController`, `SearchController`, `FolderImportController`, `FilterController`, and `EditorController`.
   - Keep the existing `AppController` temporarily as a facade delegating to those controllers.

4. Split QML by feature.
   - Extract repeated inline QML controls first.
   - Extract panels and dialogs next.
   - Keep behavior stable by binding to the facade until feature controllers are registered.

5. Replace the facade with shell composition.
   - Register feature controllers in `application.py` or `dependency_container.py`.
   - Let `App.qml` consume feature controllers directly.
   - Reduce `AppShellController` to status, navigation, and global orchestration.

6. Remove legacy modules.
   - Delete or migrate `src/app/json/json.py`.
   - Rename `src/app/file-system` to `src/app/shared/filesystem` if still needed.
   - Remove placeholder widgets/pages that are not used by the QML app.

## Refactor Rules

- One feature owns one business capability.
- Controllers expose UI state; services perform use cases; repositories persist data; entities hold domain state.
- No Qt imports in `entities` or most of `shared`.
- No file IO inside QML-facing controllers except through repositories/services.
- No feature imports another feature's controller directly. Share through services, events, or shell orchestration.
- No module should need to know all app state unless it is the shell.

## Risks And Edge Cases To Cover

- Missing Qt `Property`/`Slot` definitions for QML-called controller members.
- Duplicate files added by direct file picker and folder import.
- Invalid JSON during search, replace, format, filter matching, and display-name refresh.
- Search/replace over keys and values, including case-insensitive replacement.
- Replace-all dirty-state updates and save-all persistence.
- Active filter changing while search results or active match navigation is selected.
- Removing the current file, active-match file, or filtered-out file.
- Folder scan with no `visual.json` files, inaccessible folders, symlinks, very deep trees, and duplicate paths.
- Filter storage containing invalid JSON, unknown operations, empty rule keys, duplicate colors, or deleted active filters.
- Large files causing UI freezes because search/highlight runs synchronously.

## Testing Strategy

- Unit tests for pure services: file repository, folder scanner, search/replace, filter matcher, filter repository.
- Contract tests for every QML-exposed controller property and slot.
- Model tests for Qt role names and row updates.
- Integration smoke test for: import folder, select file, search, replace, save, filter, remove file.
- Regression tests for invalid JSON and duplicate path behavior.

## Desired End State

The final app should feel like a feature-sliced web app internally:

- The shell composes features.
- Each feature has its own controller, models, services, state, and QML.
- Domain logic is testable without Qt.
- QML files are small enough to understand without scrolling through the whole product.
- Python classes have clear Java-style responsibilities and constructor-injected dependencies.
- `AppController` either disappears or becomes a very small shell facade.
