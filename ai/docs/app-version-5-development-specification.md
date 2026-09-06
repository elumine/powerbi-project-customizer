# App Version 5 Development Specification

Source ideas document: [app-version-5-ideas.md](app-version-5-ideas.md)

Research date: 2026-09-05

# Purpose

Version 5 changes the app from a general JSON multi-file editor into a focused Power BI PBIR report definition editor. The app should still preserve the fast text-editing workflows from v1-v4, but the primary domain is now:

- `page.json` files from Power BI report pages.
- `visual.json` files from Power BI report visuals.
- Page-to-visual folder hierarchy from Power BI Project / PBIR report definitions.
- Safe batch editing for visuals, filters, search/replace, and macros.

The target platform remains Windows. The implementation should continue using Python, PySide6, QML, and the current VS Code dark theme style.

# Power BI Development Research Summary

These findings should guide implementation choices:

- Power BI Desktop Projects (`.pbip`) store report and semantic model metadata as text files in source-control-friendly folders. Microsoft describes PBIP files as publicly documented, human readable, Git-friendly, and suitable for programmatic generation/editing of item definition files.
- PBIR is still preview, so the app should avoid unsupported assumptions and should treat schema URLs and schema versions as data read from the files.
- PBIR report definitions store pages, visuals, bookmarks, and report settings as separate JSON files under a `definition/` folder. The relevant v5 structure is `definition/pages/[pageName]/page.json` and `definition/pages/[pageName]/visuals/[visualName]/visual.json`.
- Microsoft warns that some report-folder files do not support external editing during preview. v5 should only edit files it explicitly supports: `page.json` and `visual.json`.
- PBIR file and folder names can be user-friendly, but changing object `name` values can break internal or external references. v5 should display friendly names but should not rename `name` values or folders by default.
- Each PBIR JSON file can declare a public `$schema` URL. v5 should preserve that URL, use it for validation when available, and avoid hard-coding only one schema version.
- Power BI development best practice favors source control, isolated branches/workspaces, small coherent commits, validation before deployment, and formal Dev/Test/Prod promotion. v5 should create deterministic, minimal JSON diffs and never touch generated local files such as `.pbi/localSettings.json` or `.pbi/cache.abf`.
- Power BI report performance guidance recommends limiting unnecessary visuals and filtering visual data as early as possible. v5 should make it easy to find visuals by type and batch-update visual-level settings, but should avoid silent edits to query or data-binding structures.
- Power BI accessibility guidance emphasizes alt text, titles, labels, tab order, contrast, and consistent visual design. v5 visual editor controls should prioritize these common report-quality properties.

# Product Scope

## In Scope

- Import loose JSON files, PBIR report folders, and folders containing nested PBIR page/visual definitions.
- Classify imported JSON files as Page or Visual.
- Preserve parent-child relationships between pages and visuals based on the file system.
- Display pages and visuals in a collapsible hierarchy.
- Search and replace across the active document set.
- Add a single-match Replace action.
- Upgrade filters with file-type targeting, import/export, predefined filters, and dynamic filters.
- Add a Visuals Editor panel for safe UI-based edits to common visual properties and supported visual-type-specific properties.
- Upgrade macros with filter, search, replace, filter-clear, and visual-editor-change actions.
- Add a Start Again flow that clears the loaded project/session state.
- Fix the save bug related to enabling/disabling filters.

## Out of Scope

- Editing `.pbix` binary files.
- Editing semantic model metadata, TMDL, measures, relationships, or Power Query.
- Publishing or deploying to Power BI Service or Fabric.
- Editing PBIR-Legacy `report.json`.
- Editing `mobileState.json`, `semanticModelDiagramLayout.json`, `.platform`, `.pbi/*`, or cache files.
- Renaming PBIR folders or object `name` values from the UI.
- Rendering Power BI visuals inside the app.

# Architecture Direction

The current app already has useful boundaries:

- `JsonDocument` in `src/app/core/file_document.py`
- `FileListModel` in `src/app/ui/file_list_model.py`
- folder import in `src/app/features/folder_import`
- file management in `src/app/features/file_management`
- filters in `src/app/features/filters`
- search/replace in `src/app/features/search_replace`
- suggestions in `src/app/features/suggestions`
- macros in `src/app/features/macros`
- top-level QML facade in `src/app/shell/app_controller.py`
- main UI in `src/app/ui/qml/App.qml`

v5 should keep these boundaries and add a small Power BI domain layer instead of moving Power BI-specific behavior into QML.

# Data Model

## JsonFileType

Create `JsonFileType` in a core module, for example `src/app/core/json_file_type.py`.

```python
from enum import Enum

class JsonFileType(str, Enum):
    PAGE = "Page"
    VISUAL = "Visual"
```

For filter scope only, use the string value `"All"` as a target option. Do not make `"All"` a real document type.

## JsonDocument Updates

Extend `JsonDocument` with Power BI metadata:

- `file_type: JsonFileType | None`
- `project_root: Path | None`
- `relative_path: str`
- `schema_url: str`
- `pbir_name: str`
- `parent_page_id: str`
- `display_name_source: str`

Rules:

- Existing loose JSON behavior should continue.
- `file_type` is `Page` for `page.json`.
- `file_type` is `Visual` for `visual.json`.
- Invalid JSON can still be loaded and displayed, but Power BI metadata should fall back to path-based values.
- `$schema` must be preserved exactly when saving.

## PageFile

Create a Power BI-specific page object.

```python
@dataclass(slots=True)
class PageFile(JsonDocument):
    visual_ids: list[str] = field(default_factory=list)
    collapsed: bool = False
```

Required behavior:

- `display_name` comes from the `displayName` property in `page.json`.
- `pbir_name` comes from the `name` property when valid.
- `visual_ids` stores document ids for child visuals in stable folder order.
- `collapsed` is UI state only and should not be saved into JSON.

## VisualFile

Create a Power BI-specific visual object.

```python
@dataclass(slots=True)
class VisualFile(JsonDocument):
    parent_page_id: str = ""
    visual_type: str = ""
```

Required behavior:

- `parent_page_id` points to the containing `PageFile`.
- `visual_type` comes from `visual.visualType` when present.
- Visual display name priority:
  1. `visual.visualContainerObjects.title[0].properties.text.expr.Literal.Value`
  2. `visual.visualType`
  3. `name`
  4. file or folder name fallback

Literal title values in PBIR commonly include expression quoting. Display-name extraction should strip surrounding Power BI literal quotes for UI display only.

## Project Tree Model

Add a QML-facing model for hierarchy, for example `ProjectTreeModel`.

Suggested roles:

- `id`
- `path`
- `name`
- `fileName`
- `fileType`
- `directory`
- `relativePath`
- `parentPageId`
- `depth`
- `expanded`
- `visibleInTree`
- `operationActive`
- `dirty`
- `validJson`
- `jsonError`
- `matchCount`
- `activeFilterColor`

Keep `FileListModel` as the flat operational list if that keeps search, save, and editor code simpler. The tree model can be derived from the flat documents and folder relationships.

# File Import and Project Scanning

## Supported Entry Points

The user can import:

- Loose `.json` files.
- A folder that contains only visual folders.
- A PBIR `definition` folder.
- A `.Report` folder containing `definition/`.
- A broader project folder containing one or more `.Report/definition` folders.

## Scanner Behavior

Replace the current scanner that hard-codes `visual.json` with a Power BI report scanner.

The scanner should collect:

- `definition/pages/*/page.json`
- `definition/pages/*/visuals/*/visual.json`
- loose `page.json`
- loose `visual.json`
- any manually selected `.json` file that can be classified as Page or Visual

The scanner should skip:

- `.pbi/*`
- `cache.abf`
- `localSettings.json`
- `report.json`
- `mobileState.json`
- `semanticModelDiagramLayout.json`
- `.platform`
- files larger than an agreed safety limit unless the user explicitly selects them

## Classification Rules

Path name is the strongest signal:

- `page.json` => Page
- `visual.json` => Visual

Content can be used as a fallback:

- Page-like if object has `displayName`, `height`, `width`, and no `visual`.
- Visual-like if object has `visual`, `visualGroup`, or `visual.visualType`.

When classification fails:

- Keep loose manual imports only if existing v4 behavior requires it.
- Otherwise show a skipped-file message.
- Do not attach unclassified files to a Power BI hierarchy.

## Relationship Rules

When both page and visual files are present:

- A visual belongs to the nearest ancestor page folder that contains `page.json`.
- Expected shape: `pages/<pageFolder>/visuals/<visualFolder>/visual.json`.
- Page order should follow `definition/pages/pages.json` when available. If unavailable, sort by page display name, then relative path.
- Visual order should use `position.z` when available, then visual display name, then relative path.

When only visual files are present:

- Preserve the existing flat behavior.
- Display visuals as a flat list.
- Parent page fields remain empty.

# Naming

## Page Names

If imported JSON is Page:

- UI name = `displayName`.
- Fallback = `name`.
- Fallback = page folder name.
- Fallback = `page.json`.

## Visual Names

If imported JSON is Visual:

- First try title text at `visual.visualContainerObjects.title[0].properties.text.expr.Literal.Value`.
- Then try `visual.visualType`.
- Then try `name`.
- Then try visual folder name.
- Then fallback to `visual.json`.

Do not mutate `name` properties as part of display-name generation.

# Save Behavior and Filter Save Bug

The reported bug is that users cannot save files after enabling/disabling filters. v5 should make save behavior independent from filter visibility.

Rules:

- Dirty state belongs to documents, not filter state.
- `Save All` saves every dirty loaded document, including inactive or hidden documents.
- `Save File` saves the selected document even if it became inactive after filter changes, provided the UI still has a valid selection.
- If the selected document is hidden by a filter, the app should either keep it in the tree as a dimmed row or move selection to a visible row while preserving the dirty document for `Save All`.
- Deactivating filters must not clear dirty state, parsed JSON, match state, or document ids.

Tests:

- Edit a visual, apply a filter that hides it, deactivate the filter, then save.
- Edit a visual, apply a filter that hides it, then use `Save All`.
- Toggle filters repeatedly and confirm dirty count remains correct.

# Search and Replace

## Remove Replace File

Remove the current "Replace File" action from the search UI and QML controller surface.

## Add Replace

Add a "Replace" button that replaces the current active match only.

Behavior:

- If no match is selected, replace the first match in the active document set.
- If a match is selected, replace that exact match.
- After replacement, refresh search results and move to the next available match.
- If replacement text is empty, deletion is valid.
- If the current match became stale because the document changed, refresh and retry the first match.

Implementation:

- Add `SearchController.replace_current_match()`.
- Extend `SearchService` with a span-based replacement helper.
- Keep `replace_all()` unless there is a separate decision to remove it.
- Search should operate only on documents active for operations, not merely visible as hierarchy containers.

Tests:

- Replace first match across multiple active files.
- Replace currently selected match in the second file.
- Replace with empty string.
- Replace after filter target changes.

# Filter System

## Operation Selector Bug

Fix the bug where created filters can only select `equals`.

Likely implementation areas:

- Verify `filterOperationOptions` in QML.
- Verify `DarkCombo.onActivated` uses the selected operation, not stale text.
- Verify `FilterController.update_rule_operation()` receives `includes`, `notEquals`, and `notIncludes`.
- Add a controller/unit test for all `FILTER_OPERATIONS`.

## Filter Target

Add `targetJsonFileType` to `ContentFilter`.

Allowed values:

- `All`
- `Page`
- `Visual`

Default: `All`

Matching behavior:

- `All`: evaluate every classified document.
- `Page`: evaluate pages. Matching pages are active, and their child visuals are active for visual workflows.
- `Visual`: evaluate visuals. Matching visuals are active. Parent pages remain visible as containers but are not active for text operations unless they separately match another active rule.

This may require separating:

- `visibleInTree`: row should be visible in the explorer hierarchy.
- `operationActive`: row participates in search, replace, save-current, suggestions opened as search, macro actions, and visual editor.

If implementation keeps only `is_active` in v5, document this limitation and choose behavior that supports page-scoped visual edits.

## Import Filters

Existing imported filters from `content/filters` should continue. Extend schema:

```json
{
  "id": "visual-type-bar",
  "displayName": "Bar visuals",
  "targetJsonFileType": "Visual",
  "color": "#4ec9b0",
  "rules": [
    {
      "key": "visualType",
      "operation": "includes",
      "value": "Bar"
    }
  ]
}
```

Validation:

- `targetJsonFileType` defaults to `All`.
- Unknown target values are invalid for imported filters.
- User-created filters can coerce unknown target values to `All`.

## Export Filters

Add export action for each filter row.

Behavior:

- User-created filters can be exported.
- Imported read-only filters can also be exported as a copy.
- Export writes a `.json` file selected by the user.
- Export payload includes `id`, `displayName`, `targetJsonFileType`, `color`, and `rules`.
- Export should use `ensure_ascii=False` and deterministic indentation.

## Import User Filters

Add "Import filter" button to the filters panel.

Behavior:

- User selects a filter `.json`.
- Validate using the same schema as content filters.
- Imported user filter becomes editable and persisted in user filter storage.
- If an imported id conflicts with an existing user filter, assign a new id and preserve display name.

## Predefined Filters

Create new JSON files under `content/filters`:

- `visual-type-bar.json`
- `visual-type-pie.json`
- `visual-type-line.json`
- `visual-type-chart.json`
- `visual-type-table.json`
- `visual-type-slicer.json`

Each should use:

- `targetJsonFileType`: `Visual`
- `key`: `visualType`
- `operation`: `includes`
- `value`: `Bar`, `Pie`, `Line`, `Chart`, `Table`, or `Slicer`

## Dynamic Filters

Add a dynamic filter section in the filters panel. Dynamic filters are session-only and cannot be imported/exported.

Controls:

- `PageNameDynamicFilter`
  - target: `Page`
  - key: `displayName`
  - operation: `includes`
  - value: text input
- `VisualTypeDynamicFilter`
  - target: `Visual`
  - key: `visualType`
  - operation: `includes`
  - value: text input

The ideas document mentions three sections but defines two. Implement the two defined filters unless a third is specified later.

Behavior:

- Each section has label, text input, and Apply button.
- Empty text disables Apply.
- Applying a dynamic filter clears any currently active saved filter.
- Dynamic filters should not appear in import/export lists.
- Status message should identify the active dynamic filter.

# Start Again / Reinitialization

Add a top bar button named "Start Again".

Behavior:

- If there are dirty files, show a confirmation modal before clearing state.
- Clear loaded files.
- Clear folder scan state.
- Clear current file selection.
- Clear active filter and active dynamic filter.
- Clear search and replace text.
- Clear match navigation.
- Clear suggestions.
- Stop any running macro.
- Keep imported content filters and macros loaded.
- Return to the first screen with file/folder selection.
- Set active panel to Explorer.
- Set status to `Ready`.

Implementation:

- Add `AppController.startAgain()`.
- Add reset methods on feature controllers where needed.
- Avoid recreating the entire `AppController` unless QML binding stability becomes difficult.

Tests:

- Start again with clean state.
- Start again with dirty files and confirm.
- Start again with dirty files and cancel.
- Start again while a macro is running.

# File Hierarchy UI

Update the current files panel to show pages and visuals as hierarchy.

Required UI behavior:

- Page rows show page display name, file type, dirty state, match count, active filter marker, and valid/invalid JSON state.
- Visual rows are indented below parent pages.
- Page rows have expand/collapse control.
- Collapsed pages hide child visual rows.
- A visual row click selects and opens that visual JSON editor.
- A page row click selects and opens that page JSON editor.
- If a visual filter is active, parent pages for matching visuals remain visible as hierarchy containers.
- If a page filter is active, matching pages and their child visuals remain visible.
- Flat visual-only imports keep the old list-like behavior.

Implementation options:

- Preferred: create a dedicated `ProjectTreeModel` that emits only visible tree rows.
- Alternative: extend `FileListModel` with hierarchy roles and let QML filter/collapse rows.

The preferred option keeps QML simpler and keeps hierarchy rules testable in Python.

# Performance

The current accordion-style editor can render many loaded JSON files with their full text content. v5 should not render every JSON document body in the list. Large PBIR reports can contain many pages and visuals, and rendering every editor at once creates avoidable UI cost.

Required behavior:

- The explorer/tree renders only lightweight rows for pages and visuals.
- The main editor renders only the currently selected JSON file.
- Search result previews, match counts, dirty state, file type, and validation state can appear in lists, but full JSON text editors must not be instantiated per row.
- Switching selection updates the single editor content.
- Hidden or filtered documents remain in memory and can still be saved through Save All.
- Expanding/collapsing page rows must not create text editors for child visuals.

Implementation:

- Keep `FileListModel` as the source of loaded document state.
- Use `ProjectTreeModel` for lightweight tree rows.
- Add selected-document properties to `AppController` for the single editor surface.
- Move full `TextArea` / highlighted `TextEdit` rendering out of the file list delegate.
- Refresh the single editor when `currentIndex`, search state, or document text changes.
# Visuals Editor

## Feature Boundary

Create a new feature package:

```text
src/app/features/visual_editor/
  __init__.py
  visual_editor_controller.py
  visual_editor_service.py
  visual_edit_types.py
  visual_property_catalog.py
```

Create QML-facing models as needed:

```text
src/app/ui/visual_editor_models.py
```

## UI

Add a left sidebar button and panel for Visuals Editor.

Panel layout:

- Active visual count.
- Current filter/scope summary.
- Category tabs:
  - `General`
  - `Specific`
- Control list for selected category.
- Status/errors area.

Control types:

- Boolean: checkbox/toggle.
- Number: spin box or slider depending on range.
- Opacity/transparency: slider with 0-100 range.
- String: text input.
- Long string / alt text: multiline text input.
- Color: color picker and hex text input.
- Enum: combo box.

## General Controls

Initial General controls should focus on PBIR visual-container properties that are broadly useful:

- Visual title show/hide.
- Visual title text.
- Visual title font size.
- Visual title font color.
- Background show/hide.
- Background color.
- Background transparency.
- Border show/hide if supported.
- Visual hidden state (`isHidden`).
- Position values (`x`, `y`, `width`, `height`, `z`) with numeric inputs.
- Tab order when available in position metadata.
- Alt text when discoverable in visual or container objects.

Exact JSON paths vary by schema version and visual type, so controls should be catalog-driven and validated against the current document shape.

## Specific Controls

Initial Specific controls:

- Bar/column charts: data color where discoverable, labels show/hide, axis titles.
- Pie/donut charts: detail labels, legend, slice colors where discoverable.
- Line charts: line color, marker show/hide, axis titles.
- Tables/matrices: grid style, text size, row/column header styling where discoverable.
- Slicers: header/title, selection style, background transparency.

Because Power BI visual formatting structures can differ by visual type and schema version, specific controls should be additive. Unsupported controls should be hidden for a visual rather than shown disabled across all visuals.

## Property Catalog

Use a catalog instead of hard-coded UI logic.

Example:

```json
{
  "id": "general-title-text",
  "label": "Title text",
  "category": "General",
  "targetFileType": "Visual",
  "visualTypes": ["*"],
  "match": {
    "mode": "keyName",
    "key": "text",
    "ancestorPathIncludes": ["visualContainerObjects", "title"]
  },
  "valueType": "powerBiLiteralString",
  "control": "text"
}
```

Catalog rules:

- Controls are allowlisted. The user should not be able to mass-change arbitrary keys from the Visuals Editor.
- Prefer exact paths when stable.
- Use key-name matching only with ancestor constraints.
- Each control defines a value adapter.
- Each control defines supported file type and visual type.

## Change Engine

When a user changes a value:

1. Collect active visual documents.
2. Skip invalid JSON.
3. Resolve applicable controls for each visual.
4. Find matching JSON nodes.
5. Convert the UI value through the control adapter.
6. Update all matched nodes.
7. Serialize using deterministic JSON formatting.
8. Mark changed documents dirty.
9. Refresh search, filters, suggestions, and visual editor state.

This implements the ideas-document requirement to update all active `visual.json` files by finding matching keys, but adds an allowlist so broad names such as `color`, `text`, or `show` do not update unrelated locations.

## Value Adapters

Implement adapters for common PBIR value shapes:

- `string`: plain JSON string.
- `number`: int/float.
- `boolean`: JSON boolean.
- `hexColor`: string normalized to `#RRGGBB`.
- `percentage`: integer 0-100.
- `powerBiLiteralString`: update `expr.Literal.Value` while preserving Power BI literal quoting.
- `powerBiLiteralNumber`: update numeric literal values in expression wrappers.
- `powerBiSolidColor`: update known solid color expression wrappers when the existing shape matches.

If an adapter cannot safely update an existing node shape, skip that node and include a warning count in the status message.

## Validation

Minimum validation:

- JSON parse after every visual editor change.
- Do not save if parse fails after a generated edit.
- Preserve `$schema`.
- Preserve `name`.
- Preserve unknown properties.

Preferred validation:

- Use the document `$schema` URL when available.
- Bundle or cache known schemas for offline use.
- Validate edited Page and Visual files with `jsonschema` if the dependency is available.
- Report schema warnings without blocking save in the first v5 release, unless the generated edit produced invalid JSON.

# Macros System

## Macro Imports and Exports

Add import/export capability similar to filters.

Import:

- User selects a macro `.json`.
- Validate against macro schema.
- Imported macro becomes available in the macro list.
- User-imported macros can be persisted if a user macro storage file exists. Otherwise import for current session only and document the limitation.

Export:

- Each macro row has Export action.
- Export writes a deterministic JSON file.
- Imported read-only macros can be exported as copies.

## Macro Step Types

Support these step types:

- `filter-apply`
- `filter-clear`
- `search`
- `search-replace`
- `replace-current`
- `replace-all`
- `visual-editor-change`

Backward compatibility:

- Existing `filter` steps should map to `filter-apply`.
- Existing `search-and-replace` steps should map to `search-replace` or `replace-all` based on current behavior.

## Macro Schema

Example:

```json
{
  "id": "set-bar-titles-blue",
  "name": "Set bar titles blue",
  "steps": [
    {
      "type": "filter-apply",
      "filterName": "Bar visuals"
    },
    {
      "type": "visual-editor-change",
      "controlId": "general-title-font-color",
      "value": "#3B82F6"
    },
    {
      "type": "filter-clear"
    }
  ]
}
```

Validation:

- Macro name is required.
- Steps array must have at least one item.
- `filter-apply` requires `filterName` or `filterId`.
- `search` requires `searchValue`.
- `search-replace` requires `searchValue`; empty `replaceValue` is allowed.
- `replace-current` requires active search text at runtime.
- `replace-all` requires active search text at runtime.
- `visual-editor-change` requires `controlId` and `value`.
- Unknown step types are invalid.

Execution:

- Execute steps in order.
- Use existing controllers rather than duplicating logic.
- Stop on first validation or runtime failure.
- Do not revert already completed steps.
- Keep UI responsive with the existing timer-based macro execution pattern.

# Content Folder Updates

Expected content structure:

```text
content/
  filters/
    visual-type-bar.json
    visual-type-pie.json
    visual-type-line.json
    visual-type-chart.json
    visual-type-table.json
    visual-type-slicer.json
  macros/
    example-apply-visual-filter.json
    example-title-replace.json
    example-visual-editor-change.json
  visual-editor/
    controls-general.json
    controls-bar.json
    controls-pie.json
    controls-line.json
    controls-table.json
    controls-slicer.json
```

Content files shipped with the app should be read-only from the app UI unless the user exports a copy elsewhere.

# QML and Controller Updates

## AppController

Add or update:

- `projectTreeModel`
- `visualEditorControlModel`
- `visualEditorCategory`
- `activeDynamicFilterName`
- `operationActiveFileCount`
- `activeVisualCount`
- `startAgain()`
- `replaceCurrentMatch()`
- `importFilter()`
- `exportFilter(index)`
- `applyDynamicPageNameFilter(value)`
- `applyDynamicVisualTypeFilter(value)`
- `importMacro()`
- `exportMacro(index)`
- `applyVisualEditorChange(controlId, value)`
- `setPageExpanded(pageId, expanded)`

Existing signals can stay, but v5 likely needs:

- `projectTreeChanged`
- `visualEditorChanged`
- `sessionResetRequested` or direct QML state update after `startAgain()`

## App.qml

Update:

- App title to reflect Power BI report editing, for example `Power BI PBIR Editor`.
- First screen copy to mention Power BI report folders, `page.json`, and `visual.json`.
- Sidebar with new Visuals Editor button.
- Explorer panel to use hierarchy.
- Search panel Replace button.
- Filters panel target dropdown, import/export buttons, dynamic filter inputs.
- Macros panel import/export buttons and new step summaries.
- Top bar Start Again button.

Keep the UI compact and utility-focused. v5 is an operational editor, not a landing page.

# Implementation Plan

## Phase 0: Safety Baseline and Bug Fixes

Deliverables:

- Add unit tests around current save behavior, filter operation updates, search replace behavior, and imported content loading.
- Fix filter operation selector bug.
- Fix save-after-filter toggle bug.

Acceptance criteria:

- Users can select all four filter operations.
- Dirty files can be saved after filters are applied and cleared.
- Existing v4 workflows still pass smoke tests.

## Phase 1: Typed Documents and PBIR Scanner

Deliverables:

- Add `JsonFileType`.
- Extend `JsonDocument` metadata.
- Add `PageFile` and `VisualFile`.
- Replace or extend `FolderScanner` to find both `page.json` and `visual.json`.
- Add display-name extraction for PBIR page and visual rules.
- Add tests for PBIR folder examples.

Acceptance criteria:

- Importing a PBIR report folder loads pages and visuals.
- Importing only visuals still works as a flat list.
- Page and visual names follow the v5 rules.
- Unsupported report files are skipped.

## Phase 2: Project Tree UI and Start Again

Deliverables:

- Add `ProjectTreeModel`.
- Update explorer QML to display hierarchy.
- Add expand/collapse state.
- Add Start Again top bar action and dirty confirmation.

Acceptance criteria:

- Pages can collapse and expand.
- Visuals appear under the correct pages.
- Start Again clears session state and returns to picker.
- Dirty confirmation prevents accidental data loss.

## Phase 3: Filter Upgrade

Deliverables:

- Add `targetJsonFileType` to filters.
- Update imported/user filter schema.
- Add filter import/export.
- Add predefined visualType filters.
- Add dynamic page name and visual type filters.
- Add visible/operation-active logic.

Acceptance criteria:

- Page filters narrow to pages and their child visuals.
- Visual filters narrow to matching visuals and keep parent pages visible.
- Imported and exported filters round-trip.
- Dynamic filters work and are not persisted.

## Phase 4: Search Replace Upgrade

Deliverables:

- Remove Replace File action.
- Add Replace current/first match action.
- Keep Replace All if still required.
- Update macros to call the new replace APIs where applicable.

Acceptance criteria:

- Replace changes one match only.
- Replace All still changes all operation-active matches.
- Search respects active filter scope.

## Phase 5: Visuals Editor MVP

Deliverables:

- Add visual editor feature package.
- Add control catalog loader.
- Add General controls.
- Add value adapters.
- Add recursive allowlisted change engine.
- Add Visuals Editor sidebar panel.

Acceptance criteria:

- User can change common properties across active visuals.
- Invalid JSON files are skipped with a visible warning.
- Generated JSON remains parseable.
- `$schema` and `name` values are preserved.
- Dirty state and save work after visual editor changes.

## Phase 6: Visual-Type Specific Controls

Deliverables:

- Add control catalogs for bar, pie, line, table, and slicer visuals.
- Show only controls applicable to active visual types.
- Add warnings for mixed visual-type selections when a control applies only to some active visuals.

Acceptance criteria:

- Specific tab shows relevant controls for active visuals.
- Unsupported visuals are skipped rather than edited incorrectly.
- Status message reports changed/skipped counts.

## Phase 7: Macro Upgrade

Deliverables:

- Add macro import/export.
- Add new macro step types.
- Add backward compatibility for v4 macro step names.
- Add visual-editor-change execution.

Acceptance criteria:

- Existing v4 macros still run.
- New macros can apply filters, run search, replace one/all matches, clear filters, and apply visual editor changes.
- Macro validation reports clear step-level errors.

## Phase 8: Validation, Performance, and Polish

Deliverables:

- Optional JSON Schema validation using file `$schema`.
- Large-folder scan progress or batching if needed.
- Debounced refresh for filters, suggestions, and visual editor derived state.
- Documentation updates in README.
- Smoke tests for import, filter, search, visual editor, save, and start-again workflows.

Acceptance criteria:

- Large PBIR reports do not freeze the UI for ordinary operations.
- Schema validation warnings are visible but do not block safe text edits.
- README describes v5 Power BI workflow.

# Testing Strategy

## Unit Tests

Add tests for:

- `JsonFileType` classification.
- PBIR page and visual scanning.
- Page-to-visual relationship construction.
- Page display-name extraction.
- Visual display-name extraction.
- Filter operation updates.
- Filter target behavior.
- Dynamic filters.
- Filter import/export validation.
- Replace-current-match behavior.
- Visual editor value adapters.
- Visual editor key matching with ancestor constraints.
- Macro validation for new step types.
- Start Again controller reset.

## Integration / Smoke Tests

Use a fixture PBIR folder:

```text
fixtures/pbir-report/
  Sample.Report/
    definition.pbir
    definition/
      pages/
        Page1/
          page.json
          visuals/
            VisualA/
              visual.json
            VisualB/
              visual.json
```

Smoke flow:

1. Open fixture folder.
2. Confirm pages and visuals appear in tree.
3. Apply VisualTypeDynamicFilter.
4. Search for a title.
5. Replace one match.
6. Use Visuals Editor to update title color.
7. Save all.
8. Start again.

# Risks and Mitigations

- PBIR schema is preview and may change.
  - Mitigation: read `$schema` from files, keep control catalog version-aware, preserve unknown JSON.
- Broad key-name edits can damage unrelated visual settings.
  - Mitigation: use allowlisted controls with ancestor constraints and adapters.
- Power BI object renames can break references.
  - Mitigation: do not rename `name` properties or folders in v5.
- Some report files do not support external editing.
  - Mitigation: only edit `page.json` and `visual.json`.
- Large PBIR reports can cause UI stalls.
  - Mitigation: debounce derived analysis and batch expensive refreshes.
- Invalid JSON should not block the whole project.
  - Mitigation: keep invalid files visible, skip structured features for them, allow manual text correction.
- Filtered-out dirty files can become hard to save.
  - Mitigation: save-all ignores active filter state and dirty indicators remain visible at project level.

# Definition of Done

v5 is complete when:

- A Power BI PBIR report folder can be imported without losing page/visual structure.
- Pages and visuals appear as a collapsible hierarchy.
- Page and visual display names follow the requested priority rules.
- Filters support Page/Visual/All targets, import/export, predefined visualType filters, and dynamic filters.
- Search has a single-match Replace action.
- Start Again resets the session safely.
- Visuals Editor can batch-edit allowlisted common properties across active visuals.
- Macros support new filter/search/replace/visual editor actions.
- Saving works regardless of filter state.
- The app avoids unsupported Power BI files and preserves PBIR identifiers.
- Tests cover all high-risk transformation logic.

# References

- [Power BI Desktop projects (PBIP)](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [Power BI Desktop project report folder](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)
- [Microsoft Fabric report definition](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/report-definition)
- [Fabric lifecycle management best practices](https://learn.microsoft.com/en-us/fabric/cicd/best-practices-cicd)
- [Power BI implementation planning: deploy content](https://learn.microsoft.com/en-us/power-bi/guidance/powerbi-implementation-planning-content-lifecycle-management-deploy)
- [Power BI implementation planning: validate content](https://learn.microsoft.com/en-us/power-bi/guidance/powerbi-implementation-planning-content-lifecycle-management-validate)
- [Power BI optimization guide](https://learn.microsoft.com/en-us/power-bi/guidance/power-bi-optimization)
- [Design Power BI reports for accessibility](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-creating-reports)
- [Understand star schema and the importance for Power BI](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
- [Microsoft JSON schemas visualContainer changelog](https://github.com/microsoft/json-schemas/blob/main/fabric/item/report/definition/visualContainer/CHANGELOG.md)
- [Fabric report visualContainer schema 2.9.0](https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json)


