# App Version 6 Development Specification

Source request date: 2026-09-05

Related documents:

- [app-version-5-development-specification.md](app-version-5-development-specification.md)
- [app-version-5-development-results.md](app-version-5-development-results.md)

# Purpose

Version 6 expands the PBIR visual editor beyond the v5 "Specific" category coverage and adds an application history panel that can move the current session backward and forward through file-content operations.

The app should remain a focused Power BI PBIR JSON editor. v6 should keep the current Python, PySide6, and QML architecture, preserve deterministic JSON output, and avoid unsupported edits to semantic model, cache, local, and generated files.

# Research Summary

Microsoft documents Power BI Desktop projects as source-control-friendly folders where report and semantic model metadata are saved as individual text files. PBIR report definitions store report parts under a `definition/` folder, including one `visual.json` per visual and one `page.json` per page. Microsoft also documents that each PBIR JSON file declares a public schema URL, and those schemas can be used by code editors for validation and IntelliSense.

Useful references:

- [Power BI Desktop projects](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview)
- [Power BI Desktop project report folder](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report)
- [Create a Power BI report in enhanced report format](https://learn.microsoft.com/en-us/power-bi/developer/embedded/projects-enhanced-report-format)
- [Fabric REST report definition parts](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/report-definition)
- [Microsoft JSON schemas repository, visualContainer folder](https://github.com/microsoft/json-schemas/tree/main/fabric/item/report/definition/visualContainer)
- [visualContainer 2.9.0 schema](https://raw.githubusercontent.com/microsoft/json-schemas/main/fabric/item/report/definition/visualContainer/2.9.0/schema.json)
- [visualConfiguration 2.3.0 embedded schema](https://raw.githubusercontent.com/microsoft/json-schemas/main/fabric/item/report/definition/visualConfiguration/2.3.0/schema-embedded.json)
- [Power BI optimization guide](https://learn.microsoft.com/en-us/power-bi/guidance/power-bi-optimization)
- [Power BI implementation planning: deploy content](https://learn.microsoft.com/en-us/power-bi/guidance/powerbi-implementation-planning-content-lifecycle-management-deploy)

Notes from schema research:

- The user-requested schema URLs are:
  - `https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.10.0/schema.json`
  - `https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.11.0/schema.json`
- Those exact URLs were not fetchable during this research pass, but the local test PBIR files reference both versions through `$schema`.
- The public GitHub schema folder currently exposes visualContainer versions through `2.9.0`; v6 should treat later schema versions as valid input even if the schema cannot be downloaded.
- The 2.9.0 visualContainer schema defines a visual container with `$schema`, `name`, `position`, optional `visual`, optional `visualGroup`, `parentGroupName`, `filterConfig`, `isHidden`, `annotations`, and `howCreated`.
- The visualConfiguration embedded schema defines `visual.visualType`, `visual.objects`, `visual.visualContainerObjects`, and visual query state. v6 should continue to edit formatting/configuration properties only, not query bindings.

Power BI best-practice implications:

- Keep edits small, explicit, and source-control friendly.
- Preserve `$schema`, `name`, folder names, query structures, and data bindings unless a control explicitly owns a safe formatting property.
- Validate JSON after every generated change before updating document text.
- Prefer operation history that makes accidental bulk edits reversible within the app before the user saves to disk.
- Power BI report performance guidance recommends limiting unnecessary visuals and applying restrictive filters early. v6 should not render every loaded JSON file body at once; it should continue rendering only the currently selected JSON file content.

# Current v5 Baseline

The v5 implementation already includes:

- PBIR page and visual document classification.
- Project tree model with page-to-visual hierarchy.
- Current-document JSON rendering instead of rendering all file contents.
- Visuals Editor MVP with general controls and a small Specific category.
- Filters with file-type targeting and dynamic filters.
- Macro import/export and visual-editor-change macro steps.
- Start Again reset flow.

Key existing files:

- `src/app/features/visual_editor/visual_property_catalog.py`
- `src/app/features/visual_editor/visual_editor_service.py`
- `src/app/features/visual_editor/visual_edit_types.py`
- `src/app/features/visual_editor/visual_editor_controller.py`
- `src/app/ui/visual_editor_models.py`
- `src/app/shell/app_controller.py`
- `src/app/ui/qml/App.qml`
- `src/app/ui/file_list_model.py`
- `src/app/ui/project_tree_model.py`

# Sample Visual Coverage

The sample page `test/data/test-project/definitions/pages/p1/` contains seven visual files. v6 must support all visual types present there:

| Visual type | Schema version in sample | `visual.objects` groups | `visual.visualContainerObjects` groups |
| --- | --- | --- | --- |
| `shape` | `2.10.0` | `shape`, `rotation`, `outline`, `fill` | `title`, `subTitle`, `background`, `border`, `dropShadow`, `visualTooltip`, `visualHeader`, `visualHeaderTooltip` |
| `gauge` | `2.10.0` | `axis`, `labels`, `target`, `calloutValue`, `dataPoint` | `title`, `subTitle`, `spacing`, `background`, `border`, `visualTooltip`, `visualHeader`, `visualHeaderTooltip`, `divider`, `padding` |
| `textbox` | `2.10.0` | `general` | `title`, `subTitle`, `background`, `general`, `border`, `dropShadow`, `visualTooltip`, `visualHeader`, `visualHeaderTooltip` |
| `slicer` | `2.11.0` | `data`, `selection`, `items`, `header`, `general` | `border`, `dropShadow`, `title`, `subTitle`, `background`, `visualTooltip`, `visualHeader`, `visualHeaderTooltip` |
| `cardVisual` | `2.11.0` | `fillCustom`, `outline`, `padding`, `label`, `value`, `layout`, `spacing`, `image`, `referenceLabelLayout`, `referenceLabel`, `referenceLabelTitle`, `divider`, `border` | `background`, `title`, `spacing`, `border`, `visualHeader`, `visualTooltip`, `visualHeaderTooltip` |
| `image` | `2.10.0` | `general` | `visualLink` |
| `barChart` | `2.10.0` | `valueAxis`, `labels`, `legend`, `layout`, `dataPoint`, `categoryAxis`, `totals` | `title`, `background`, `border`, `visualHeader`, `visualTooltip` |

# Feature 1: Expanded Visual Editor Specific Coverage

## Goals

- Add Specific category controls for every visual type found in the sample `p1` page.
- Keep controls allowlisted and safe.
- Make it easier to add future schema-derived controls without editing service logic for every single property.
- Avoid broad recursive edits that update unrelated properties with the same name in unrelated visual sections.

## Non-Goals

- No Power BI visual rendering.
- No query, projection, measure, filterConfig, or semantic model editing.
- No automatic schema download requirement at runtime.
- No attempt to edit every possible property in every Microsoft schema.

## Visual Editor Control Model Updates

Extend `VisualEditorControl` with explicit path support:

```python
@dataclass(slots=True)
class VisualEditorControl:
    id: str
    label: str
    category: str
    control: str
    value_type: str
    visual_types: list[str] = field(default_factory=lambda: ["*"])
    paths: list[list[str | int]] = field(default_factory=list)
    options: list[str] = field(default_factory=list)
    creates_missing_path: bool = False
```

Rules:

- `paths` are preferred over hard-coded `control.id` handling.
- Path controls must update only existing paths by default.
- `creates_missing_path` is allowed only for simple formatting objects where a default object can be created safely.
- Existing v5 controls keep working through compatibility mapping.

Example content-file control:

```json
{
  "id": "gauge-callout-color",
  "label": "Callout color",
  "category": "Specific",
  "control": "color",
  "valueType": "hexColor",
  "visualTypes": ["gauge"],
  "paths": [
    ["visual", "objects", "calloutValue", 0, "properties", "color", "expr", "Literal", "Value"],
    ["visual", "objects", "calloutValue", 0, "properties", "color", "solid", "color"]
  ]
}
```

## Value Conversion Updates

Add converters for common PBIR formatting forms:

- `hexColor`: accepts `#RRGGBB`, writes the form expected at the target path.
- `powerBiLiteralString`: wraps using existing Power BI literal string encoder.
- `powerBiLiteralNumber`: writes either number or literal expression depending on path context.
- `boolean`: accepts QML booleans and string fallbacks.
- `enum`: validates against `options`.
- `integer`: rounds or rejects fractional values.
- `percentage`: clamps to `0..100`.

The service should detect path context:

- Paths ending in `solid.color` receive `#RRGGBB`.
- Paths ending in `expr.Literal.Value` receive encoded literal values.
- Plain scalar paths receive plain scalar values.

## Specific Controls to Add

Add built-in controls or JSON catalog entries for these groups. Prefer JSON files under `content/visual-editor/` for data-only additions and keep Python only for generic path application.

### Shape

- Shape type: `visual.objects.shape[].properties.tileShape`
- Rotation angle: `visual.objects.rotation[].properties.shapeAngle`
- Fill color: `visual.objects.fill[].properties.fillColor`
- Fill transparency: `visual.objects.fill[].properties.transparency`
- Outline enabled: `visual.objects.outline[].properties.show`
- Border color/radius/width through container border paths.
- Drop shadow enabled/preset where present.

### Gauge

- Axis minimum and maximum.
- Label visibility, color, font size, display units, precision, bold.
- Target visibility, color, font size, display units, precision.
- Callout visibility, color, display units, precision, dynamic labels, bold.
- Data point fill and target colors.
- Divider visibility/color and container padding.

### Textbox

- Paragraph text editing should be read-only in v6 unless a safe PBIR text helper is added.
- Border visibility/width.
- Background visibility/transparency.
- Keep layer order toggle.
- Header visibility/foreground.
- Tooltip colors and font family.

### Slicer

- Mode: `visual.objects.data[].properties.mode`.
- Single select toggle.
- Select all checkbox toggle.
- Items font family, text size, font color, background.
- Header text, font family, text size.
- Background color/transparency.
- Border visibility/color/radius/width.

### Card Visual

- Fill custom enabled.
- Outline enabled.
- Padding selection and margins.
- Label visibility, font size, font color, position, text wrap.
- Value font size, bold, font color, horizontal alignment.
- Layout alignment, column count, cell padding.
- Image visibility, position, padding, size, vertical alignment.
- Reference label layout properties.
- Divider visibility.
- Border visibility/color/radius.

### Image

- Image URL: `visual.objects.general[].properties.imageUrl`.
- Visual link enabled, type, bookmark.
- Position and visibility still use General controls.

### Bar Chart

- Value axis visibility and axis title visibility.
- Category axis visibility, axis title visibility, font size, label color, inner padding, max margin factor, preferred category width.
- Labels visibility, color, font size, detail font size, precision, background toggle/transparency, bold.
- Legend visibility and position.
- Data point fill.
- Totals visibility.
- Visual header pin/filter-restatement buttons.

## Category Behavior

Specific category should be driven by the active visual set:

- If one visual type is active, show controls for that type.
- If multiple active visual types are selected through filters, show controls that apply to at least one active type, grouped by visual type.
- Each control row should show how many active visuals it can affect.
- Applying a control should skip nonmatching visuals and report changed/skipped counts.

## Schema-Aware Discovery

Implement an offline schema/sample analyzer to assist future control additions:

- Input: local loaded `visual.json` documents plus optional schema files if present in a local cache.
- Output: discovered visual types, object groups, property names, inferred primitive kinds, and candidate control records.
- The analyzer should not automatically enable new controls. It should generate reviewable catalog JSON.
- Store generated draft catalogs in a developer-only path such as `.codex/generated/visual-editor-candidates/` or expose the data through tests only.

Implementation file suggestion:

- `src/app/features/visual_editor/visual_schema_analyzer.py`

Candidate output shape:

```json
{
  "visualType": "gauge",
  "object": "calloutValue",
  "property": "color",
  "candidateControl": "color",
  "paths": [
    ["visual", "objects", "calloutValue", 0, "properties", "color"]
  ]
}
```

## Visual Editor Service Refactor

Refactor `VisualEditorService._apply_to_data`:

1. Load the selected control.
2. Convert input once using `value_type`.
3. If `control.paths` is present, apply path-specific writes.
4. If no paths exist, use existing v5 compatibility behavior.
5. Validate the mutated JSON by serializing and parsing.
6. Mark only changed documents dirty.
7. Emit history events for each changed document.

Add path helper methods:

- `_get_path(data, path)`
- `_set_path(data, path, value)`
- `_set_existing_paths(data, paths, value, control)`
- `_convert_for_path(value, path, value_type)`

## Visual Editor UI Updates

Update `App.qml` Visuals Editor panel:

- Add a type group label for Specific controls when multiple visual types are visible.
- Add count metadata per control, for example `3 matching`.
- Use the existing compact dark app style.
- Keep the right editor area rendering only the selected JSON document.

## Visual Editor Tests

Add smoke/unit coverage for:

- Catalog loads all new Specific controls.
- Each sample `p1` visual type has at least one applicable Specific control.
- Path-based controls update only intended paths.
- Color controls preserve valid PBIR color structures.
- Invalid JSON documents are skipped.
- Mixed active visual types show applicable controls and skip nonmatching documents.
- No query/projection/filterConfig path is mutated by Specific controls.

# Feature 2: History Panel and Rollback

## Goals

- Record all app operations that change file content or operation state important to PBIR editing.
- Show history in a left sidebar panel.
- Allow clicking earlier rows to rollback changes from the current row to the clicked row.
- Allow clicking later rows to reapply changes from the current row to the clicked row.
- Make file-content changes reversible before save and after save within the same app session.

## History Scope

Record these operation types:

- `file-open`: document added to session.
- `file-remove`: document removed from session.
- `content-edit`: text editor changed the current document.
- `format-json`: JSON formatting changed document text.
- `search-replace-one`: one search result replaced.
- `search-replace-all`: batch replace changed one or more documents.
- `visual-editor-change`: visual editor changed one or more visual documents.
- `filter-apply`: active saved filter changed.
- `filter-clear`: saved/dynamic filter cleared.
- `dynamic-filter-apply`: dynamic filter changed.
- `macro-run`: macro started.
- `macro-step`: macro step applied.
- `macro-complete`: macro completed or stopped.
- `macro-import`: macro imported.
- `filter-import`: filter imported.
- `filter-create`: user filter created.
- `filter-update`: user filter edited.
- `filter-delete`: user filter deleted.
- `start-again`: session cleared.
- `save-file`: a document was saved.
- `save-all`: one or more documents were saved.

Content rollback is required for operations that change file text. Metadata-only operations should still appear in the history but can define no file patch.

## History Data Model

Create a new feature package:

- `src/app/features/history/history_entry.py`
- `src/app/features/history/history_service.py`
- `src/app/features/history/history_controller.py`
- `src/app/ui/history_model.py`

Suggested data classes:

```python
@dataclass(slots=True)
class FileSnapshot:
    document_id: str
    path: str
    before_text: str
    after_text: str
    before_dirty: bool
    after_dirty: bool

@dataclass(slots=True)
class HistoryEntry:
    index: int
    timestamp: datetime
    operation_type: str
    display_name: str
    metadata: dict[str, Any]
    file_changes: list[FileSnapshot] = field(default_factory=list)
```

`HistoryService` owns:

- `entries: list[HistoryEntry]`
- `current_index: int`
- `record(entry)`
- `rollback_to(index, files)`
- `rollforward_to(index, files)`
- `clear()`

History index semantics:

- `current_index == -1` means no operation has been applied.
- When recording a new operation after rolling back, discard entries after `current_index` before appending the new entry.
- The newly appended entry becomes current.
- Rollback from current index `N` to clicked index `K` applies `before_text` for entries `N, N-1, ..., K+1`.
- Rollforward from current index `N` to clicked index `K` applies `after_text` for entries `N+1, N+2, ..., K`.

This makes the clicked row become the current row.

## History Row Format

Each row displays:

```text
[ index ] [ time ] [ operation type ] Display name ( metadata of what changed )
```

Example:

```text
[ 12 ] [ 19:42:08 ] [ visual-editor-change ] Gauge ( 1 file, callout color #00AEEF )
```

Required row background states:

- Current row: cyan background.
- Rows above current row: light green background.
- Rows below current row: light red background.

Use app-theme-compatible colors, for example:

- Current: `#0e7490`
- Previous: `#1f5f46`
- Next: `#6b2d35`

If these read too saturated in the current dark theme, use lower-opacity variants while preserving the requested cyan/green/red meaning.

## Sidebar UI

Add a left sidebar button:

- Text/icon: `H`
- Tooltip: `History`
- Active when `root.activePanel === "history"`.

Add history panel:

- Header: `History`.
- Small count and current index summary.
- Optional compact operation-type filter field after MVP.
- `ListView` backed by `historyModel`.
- Clicking a row calls `controller.goToHistoryIndex(index)`.
- Disable click when row is current.
- Keep keyboard/mouse interactions consistent with filter and macro panels.

Update `App.qml` active panel sizing:

- Add `history` to panel width logic.
- Do not hide the project tree permanently when history is open unless existing panel layout requires it.

## Controller Integration

Add to `AppController`:

- `_history = HistoryListModel()`
- `self.history = HistoryController(self._history, HistoryService())`
- `historyChanged = Signal()`
- `get_history_model`
- `get_history_count`
- `get_history_current_index`
- `goToHistoryIndex(index)`

Expose QML properties:

- `historyModel`
- `historyCount`
- `historyCurrentIndex`

Refresh after history jumps:

1. Update affected `JsonDocument` text and dirty state.
2. Refresh `FileListModel` rows.
3. Refresh `ProjectTreeModel`.
4. Refresh search results for current search text.
5. Reapply active filters or clear stale filter states.
6. Refresh suggestions.
7. Refresh visual editor applicable controls.
8. Emit `currentDocumentChanged`, `filesChanged`, `historyChanged`, and `statusChanged`.

## Recording File Text Changes

Wrap existing mutation points so history gets accurate before/after snapshots:

- `FileListModel.set_document_text`
- JSON formatter action.
- Replace one and replace all.
- Visual editor changes.
- Macro step execution.
- Start Again.

Prefer recording at feature-controller boundaries, not inside low-level model setters, to avoid duplicate history entries. Low-level model setters can return enough data to make recording easier but should not decide operation semantics.

For direct text editor typing, coalesce changes:

- Start a pending `content-edit` entry when the user edits current text.
- Debounce for about 700 ms after the last keystroke.
- Commit one history entry per editing burst.
- Commit immediately when changing current document, saving, formatting, running replace, applying visual editor changes, or starting a macro.

## File Remove and Start Again

For removed documents, snapshots must include enough data to restore the document in memory:

- document id
- path
- display name
- file type metadata
- previous text
- dirty state
- hierarchy metadata

MVP option:

- Record `file-remove` and `start-again` rows as non-reversible metadata entries.
- Display them with a `not reversible` metadata marker.
- Do not allow rollback across non-reversible entries.

Recommended v6 implementation:

- Make `file-remove` reversible.
- Treat `start-again` as a hard boundary: clear history or record a boundary entry and disable rollback across it.

## Save Semantics

Saving to disk should be recorded but must not prevent rollback in memory:

- `save-file` captures dirty state transition from true to false.
- Rollback to before a save can mark a document dirty again if in-memory text differs from saved text.
- The app should never silently write rollback changes to disk. Disk writes still require Save File or Save All.

## Macros and History

Macro behavior:

- Record `macro-run` at start.
- Record each mutating step as `macro-step` with file snapshots.
- Record `macro-complete` or stopped state.

Undo granularity:

- Clicking before a macro step rolls back that step.
- Clicking before `macro-run` rolls back all completed mutating macro steps after it.
- A future option can add grouped macro rollback, but v6 should keep one history row per step for transparency.

## History Model Roles

`HistoryListModel` roles:

- `index`
- `timeText`
- `operationType`
- `displayName`
- `metadataText`
- `rowState`: `previous`, `current`, `next`
- `reversible`
- `affectedFileCount`
- `changedValueCount`

## Tests for History

Unit tests:

- Recording appends entries and advances current index.
- Recording after rollback truncates future entries.
- Rollback applies before snapshots in reverse order.
- Rollforward applies after snapshots in forward order.
- Current, previous, and next row states are computed correctly.
- Non-reversible boundary behavior is enforced.

Integration smoke tests:

- Edit current file, format JSON, rollback to pre-format row, roll forward to formatted row.
- Apply visual editor change to gauge and card visual, rollback and roll forward.
- Replace all across filtered documents, rollback all affected documents.
- Run a macro with visual editor change, rollback through macro steps.
- Save file, rollback edit in memory, confirm disk file is unchanged until Save File.

# Implementation Plan

## Phase 1: Visual Editor Path Controls

1. Extend `VisualEditorControl` and catalog loader with `paths` and `createsMissingPath`.
2. Add generic path-based write support to `VisualEditorService`.
3. Keep all v5 controls working.
4. Add tests for value conversion and path writes.

## Phase 2: Sample Visual Specific Controls

1. Add catalog entries for `shape`.
2. Add catalog entries for `gauge`.
3. Add catalog entries for `textbox`.
4. Add catalog entries for `slicer`.
5. Add catalog entries for `cardVisual`.
6. Add catalog entries for `image`.
7. Expand existing `barChart` controls.
8. Add coverage checks that every `p1` visual type has Specific controls.

## Phase 3: Visual Editor UI Metadata

1. Extend control model roles with matching visual count and visual type group.
2. Update Specific category UI to show grouped controls cleanly.
3. Ensure mixed visual selections are understandable.
4. Verify the current-document editor remains single-document rendering.

## Phase 4: History Core

1. Add history data classes.
2. Add `HistoryService`.
3. Add `HistoryListModel`.
4. Add rollback and rollforward unit tests.
5. Add operation metadata formatting.

## Phase 5: History Integration

1. Add `HistoryController` to `AppController`.
2. Record text edits with debounce/coalescing.
3. Record format, replace, visual editor, filter, macro, save, import, and remove operations.
4. Implement `goToHistoryIndex`.
5. Refresh all dependent models after jumps.

## Phase 6: History UI

1. Add left sidebar History button.
2. Add history panel and row colors.
3. Add click behavior for rollback/rollforward.
4. Add empty and boundary states.

## Phase 7: Smoke Test and Results

1. Run Python syntax checks.
2. Run existing automated tests.
3. Run targeted visual-editor tests against `test/data/test-project/definitions/pages/p1/`.
4. Run history rollback/rollforward smoke tests.
5. Start the app if a manual UI smoke test is needed.
6. Write `ai/docs/app-version-6-development-results.md` after implementation.

# Acceptance Criteria

- All seven visual types in `test/data/test-project/definitions/pages/p1/` have Specific category controls.
- Specific controls only mutate allowlisted formatting paths.
- Visual editor changes keep JSON valid.
- Query/projection/filterConfig structures are not changed by visual editor controls.
- The right-side JSON editor renders only the currently selected JSON file content.
- History button appears in the left sidebar.
- History panel displays rows in the required format.
- Current row has cyan background, previous rows light green, next rows light red.
- Clicking a previous row rolls back intervening file-content changes.
- Clicking a next row reapplies intervening file-content changes.
- Recording a new operation after rollback truncates future history.
- Save operations are recorded without automatically writing rollback changes to disk.
- Smoke test results are documented in `app-version-6-development-results.md` after implementation.

# Risks and Mitigations

- PBIR schema versions are moving targets. Mitigation: preserve schema URLs and use sample/schema discovery as an assistive tool, not a runtime dependency.
- Different visuals can reuse property names with different meanings. Mitigation: use explicit paths instead of recursive key updates for v6 Specific controls.
- Power BI literal expression shapes vary. Mitigation: path-context conversion and round-trip JSON validation.
- History can consume memory for large files. Mitigation: store full before/after snapshots for MVP, then add diff storage if needed. Add a future cap or warning for very large documents.
- Rollback across structural operations can be complex. Mitigation: treat Start Again as a boundary and implement file-remove restoration separately from simple content rollback.
