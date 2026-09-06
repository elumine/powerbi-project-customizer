# App Version 5 Development Results

Implementation date: 2026-09-05

Source specification: [app-version-5-development-specification.md](app-version-5-development-specification.md)

# Summary

Version 5 implementation has been added to the Python/PySide6/QML app. The app now treats Power BI `page.json` and `visual.json` files as typed documents, preserves page-to-visual hierarchy, renders only the currently selected JSON document body, supports targeted filters, adds a single-match Replace action, includes a Visuals Editor MVP, expands macro actions, and provides a Start Again reset flow.

# Implemented Features

## Power BI Document Model

- Added `JsonFileType` with `Page` and `Visual` values.
- Added Power BI metadata extraction for `$schema`, PBIR `name`, visual type, display name, relative path, and parent page id.
- Added `PageFile` and `VisualFile` document classes.
- Updated loaded documents to classify `page.json` and `visual.json` by path first, then by content fallback.
- Updated display name logic:
  - Pages use `displayName`, then `name`, then folder/file fallback.
  - Visuals use visual title literal, then `visualType`, then `name`, then folder/file fallback.

## PBIR Folder Import

- Updated folder scanning to include both `page.json` and `visual.json` files.
- Preserved visual parent relationships by detecting the nearest ancestor folder containing `page.json`.
- Added skip behavior for unsupported Power BI support files and folders, including `.pbi`, cache files, `report.json`, and local settings.
- Kept flat visual-only import behavior when no pages are present.

## Performance-Oriented UI

- Replaced the accordion editor list with a lightweight project tree plus one selected-document editor.
- Project tree rows show metadata only: file type, name, visual type, match count, dirty state, and validation state.
- The full JSON `TextArea` / highlighted `TextEdit` is instantiated only once for the currently selected document.
- Page expand/collapse no longer creates editor instances for child visuals.

## Filter System

- Added `targetJsonFileType` to filters with `All`, `Page`, and `Visual` targets.
- Updated imported filter schema, persisted user filter schema, and QML roles.
- Added filter import/export controller slots.
- Added predefined visual-type filters under `content/filters` for Bar, Pie, Line, Chart, Table, and Slicer.
- Added dynamic Page Name and Visual Type filters.
- Fixed filter operation handling so `includes`, `notEquals`, and `notIncludes` are preserved.
- Split filtered state into operation-active behavior and tree visibility behavior.

## Search and Replace

- Removed the visible `Replace file` UI action.
- Added `Replace`, which replaces the current selected match or first available match.
- Kept `Replace all` for existing workflows.
- Search and replace continue to operate only on active documents.

## Start Again

- Added a top-bar `Start Again` action.
- Added dirty-state confirmation in QML.
- Reset clears loaded files, folder scan state, active filters, search/replace state, suggestions, current selection, macro runtime state, visual editor state, and project tree state.
- Imported content filters and macros remain available after reset.

## Visuals Editor MVP

- Added a new `visual_editor` feature package.
- Added allowlisted visual editor controls and a catalog loader.
- Added General controls for title text/color, background color/transparency, hidden state, and position values.
- Added initial Specific controls for bar, pie, line, table, and slicer-like visuals.
- Added value adapters for strings, booleans, numbers, percentages, hex colors, and Power BI literal strings.
- Added batch-edit behavior over active visual files only.
- Invalid JSON files are skipped by structured visual editor changes.

## Macros

- Added support for v5 macro step types:
  - `filter-apply`
  - `filter-clear`
  - `search`
  - `search-replace`
  - `replace-current`
  - `replace-all`
  - `visual-editor-change`
- Preserved compatibility with v4 `filter` and `search-and-replace` step names.
- Added macro import/export controller slots.
- Added sample v5 macro files for clearing filters and applying a visual editor change.

## Smoke Test

- Reworked the offscreen smoke test to cover v5 workflows:
  - QML startup.
  - imported content filters/macros.
  - PBIR folder scan.
  - page/visual hierarchy.
  - dynamic page and visual filters.
  - single-match Replace.
  - Visuals Editor title update.
  - Visuals Editor macro color update.
  - save-all while filters hide a dirty file.
  - targeted filter persistence.
  - Start Again reset.

# Verification Results

Commands run:

```cmd
python -m py_compile src\app\core\json_file_type.py src\app\core\powerbi_metadata.py src\app\core\file_document.py src\app\core\content_filter.py src\app\core\search_service.py src\app\features\file_management\file_repository.py src\app\features\file_management\file_management_controller.py src\app\features\folder_import\folder_scanner.py src\app\features\filters\filter_editor_session.py src\app\features\filters\filter_import_repository.py src\app\features\filters\filter_controller.py src\app\features\macros\macro_types.py src\app\features\macros\macro_repository.py src\app\features\macros\macro_controller.py src\app\features\visual_editor\visual_edit_types.py src\app\features\visual_editor\visual_property_catalog.py src\app\features\visual_editor\visual_editor_service.py src\app\features\visual_editor\visual_editor_controller.py src\app\ui\file_list_model.py src\app\ui\folder_scan_model.py src\app\ui\project_tree_model.py src\app\ui\visual_editor_models.py src\app\shell\app_controller.py src\app\ui\application.py
```

Result: passed.

```cmd
tools\dev.cmd --smoke-test
```

Result: passed.

Smoke output:

```text
Smoke test passed: v5 PBIR import, hierarchy, filters, search replace, visual editor, macros, save, and reset worked.
```

# New Files

- `src/app/core/json_file_type.py`
- `src/app/core/powerbi_metadata.py`
- `src/app/ui/project_tree_model.py`
- `src/app/ui/visual_editor_models.py`
- `src/app/features/visual_editor/__init__.py`
- `src/app/features/visual_editor/visual_edit_types.py`
- `src/app/features/visual_editor/visual_property_catalog.py`
- `src/app/features/visual_editor/visual_editor_service.py`
- `src/app/features/visual_editor/visual_editor_controller.py`
- `content/filters/visual-type-bar.json`
- `content/filters/visual-type-pie.json`
- `content/filters/visual-type-line.json`
- `content/filters/visual-type-chart.json`
- `content/filters/visual-type-table.json`
- `content/filters/visual-type-slicer.json`
- `content/macros/example-clear-filter.json`
- `content/macros/example-visual-editor-change.json`
- `ai/docs/app-version-5-development-results.md`

# Updated Files

- `ai/docs/app-version-5-development-specification.md`
- `src/app/core/content_filter.py`
- `src/app/core/file_document.py`
- `src/app/core/search_service.py`
- `src/app/features/file_management/file_management_controller.py`
- `src/app/features/file_management/file_repository.py`
- `src/app/features/filters/filter_controller.py`
- `src/app/features/filters/filter_editor_session.py`
- `src/app/features/filters/filter_import_repository.py`
- `src/app/features/folder_import/folder_scanner.py`
- `src/app/features/macros/macro_controller.py`
- `src/app/features/macros/macro_repository.py`
- `src/app/features/macros/macro_types.py`
- `src/app/features/search_replace/search_controller.py`
- `src/app/shell/app_controller.py`
- `src/app/ui/application.py`
- `src/app/ui/file_list_model.py`
- `src/app/ui/filter_models.py`
- `src/app/ui/folder_scan_model.py`
- `src/app/ui/qml/App.qml`

# Known Limitations

- JSON Schema validation against remote `$schema` URLs is not implemented yet. The app validates generated edits by parsing JSON and preserving existing schema fields.
- Visuals Editor controls are intentionally allowlisted and conservative. They update existing known shapes rather than creating new Power BI formatting structures from scratch.
- User-imported macros are session-only unless a later persistence layer is added for user macro storage.
- Page ordering from `pages.json` is not implemented yet; current tree order is deterministic by display name and relative path.
- Visual-specific controls are MVP-level and should be expanded with real PBIR fixtures for each supported visual type.

# Worktree Notes

Before and after implementation, the worktree included unrelated/pre-existing content changes:

- `ai/docs/app-version-5-ideas.md` was already modified.
- Some old `content/` fixture files appeared deleted while replacement/sample content folders appeared untracked.

Those unrelated changes were not reverted.
