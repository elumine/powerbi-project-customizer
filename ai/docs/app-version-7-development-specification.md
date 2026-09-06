# App Version 7 Development Specification

Source request date: 2026-09-06

Source idea documents:

- [7.md](7.md)
- [8.md](8.md)
- [9.md](9.md)
- [10.md](10.md)

Related documents:

- [app-version-6-development-specification.md](app-version-6-development-specification.md)
- [app-version-6-development-results.md](app-version-6-development-results.md)

# Purpose

Version 7 improves the day-to-day editing workflow around imported JSON, search, visual-editor controls, history, and macros.

The app should remain a focused Power BI PBIR JSON editor built with Python, PySide6, and QML. v7 should preserve the v6 safety rules: recognized PBIR `page.json` and `visual.json` files stay valid hierarchical PBIR documents, visual-editor mutations stay allowlisted, and the app avoids unsupported edits to semantic model, cache, local, and generated files.

The main product goal is to make every editing surface more inspectable:

- Imported generic JSON can be transformed into a flat key-value shape.
- Dynamic filtering can target visual names.
- Visual-editor controls show what they control, what value they will start with, and where matching properties already exist.
- Search and replace is line-aware and predictable.
- History keeps its scroll position during navigation.
- Macros can be explained, recorded from history, exported, and imported.

# Current v6 Baseline

The v6 implementation already includes:

- PBIR page and visual document classification.
- Page-to-visual hierarchy in the project tree.
- Visual-type selector modes for General, Specific, and supported visual types.
- Path-based visual-editor controls for known visual types.
- Dynamic fallback controls for unknown visual types.
- Matching visual counts and visual type metadata in the visual editor.
- In-session history with rollback and rollforward for reversible content changes.
- History rows with current, previous, and next row states.
- History recording for edits, formatting, replace, visual-editor changes, filter changes, macro operations, save operations, and reset boundaries.
- Macro import and macro execution.

Key existing files:

- `src/app/features/visual_editor/visual_property_catalog.py`
- `src/app/features/visual_editor/visual_editor_service.py`
- `src/app/features/visual_editor/visual_edit_types.py`
- `src/app/features/visual_editor/visual_editor_controller.py`
- `src/app/features/history/history_entry.py`
- `src/app/features/history/history_service.py`
- `src/app/features/history/history_controller.py`
- `src/app/features/macros/`
- `src/app/features/search_replace/`
- `src/app/features/filters/`
- `src/app/ui/history_model.py`
- `src/app/ui/visual_editor_models.py`
- `src/app/ui/file_list_model.py`
- `src/app/ui/project_tree_model.py`
- `src/app/shell/app_controller.py`
- `src/app/ui/qml/App.qml`

# Feature 1: Flat JSON Import

## Goals

- Add an import-time transform that can convert hierarchical JSON into flat key-value JSON.
- Use a structured JSON parser and recursive traversal rather than string manipulation.
- Keep output deterministic and readable.
- Preserve PBIR safety by not flattening recognized PBIR documents when the user imports a Power BI report folder for PBIR editing.

## Non-Goals

- No flattening of recognized PBIR `page.json` or `visual.json` files during normal PBIR folder import.
- No conversion of `.pbix` binary files.
- No flattening of unsupported generated Power BI files such as `.pbi/cache.abf`.
- No lossy key conversion where two source paths would collide.

## Flattening Rules

Given input:

```json
{
  "a": 1,
  "b": {
    "c": 2,
    "d": [
      { "e": "f" }
    ]
  }
}
```

The flat output is:

```json
{
  "a": 1,
  "b.c": 2,
  "b.d.[0].e": "f"
}
```

Rules:

- Object keys are separated with `.`.
- Array indices are represented as `[n]`.
- Array index segments are separated with dots when nested inside an object path, for example `b.d.[0].e`.
- Primitive values, strings, numbers, booleans, and `null` become flat leaf values.
- Empty objects and empty arrays are preserved as leaf values at their current path.
- Key order follows source traversal order.
- Output JSON uses the app's normal deterministic formatting.

## Escaping and Collision Handling

Add escaping for source object keys that contain reserved flat-path characters:

- `\` becomes `\\`
- `.` becomes `\.`
- `[` becomes `\[`
- `]` becomes `\]`

The app must detect collisions after escaping. If two source paths would produce the same flat key, the import should fail cleanly for that file and show a useful status message. It must not silently overwrite a value.

## Import Behavior

Add one of these user-facing options, choosing the smallest change that fits the existing import UI:

- `Import JSON as flat keys`
- `Flatten generic JSON on import`

Behavior:

- Loose JSON file import may use flat mode.
- Folder import may use flat mode for generic JSON files.
- PBIR report import keeps recognized `page.json` and `visual.json` hierarchical by default.
- If a user explicitly enables flat mode for a PBIR file, the document should be marked as generic JSON and excluded from PBIR visual-editor operations until restored or re-imported hierarchically.

Implementation suggestion:

- Add `src/app/features/json_transform/flat_json.py`.
- Add `flatten_json(data: Any) -> dict[str, Any]`.
- Add focused tests for nested objects, arrays, empty structures, escaped keys, and collision errors.

# Feature 2: Dynamic Filter by Visual Name

## Goals

- Add a third dynamic filter that targets visual names.
- Let users quickly narrow the active document set to visuals whose display name, PBIR `name`, or folder/file name matches text.
- Keep dynamic visual-name filtering compatible with the visual editor, search, replace, macros, and history.

## Filter Semantics

The dynamic visual-name filter should match recognized visual documents using these fields:

- `JsonDocument.display_name`
- `JsonDocument.pbir_name`
- visual folder name
- visual file name
- optional title text if already available from parsed visual metadata

Matching rules:

- Case-insensitive substring match by default.
- Empty input clears the dynamic visual-name filter.
- Invalid JSON files are still matchable by path and display name.
- Page documents do not match unless the UI explicitly includes a future "include parent page" option.

History:

- Applying the filter records `dynamic-filter-apply`.
- Clearing the filter records `filter-clear` or the current v6 equivalent.
- History metadata should identify the dynamic filter as `visual-name`.

UI:

- Add a third dynamic filter input or selector entry labelled `Visual name`.
- Show active filter state clearly in the filter panel.
- Refresh visual-editor applicable controls after the filter changes.

# Feature 3: Visual Editor Control Inspectability

## Goals

- Make each visual-editor control self-explanatory without requiring the user to inspect raw JSON first.
- Show the default value from the first matching property in the active visual set.
- Show an expandable, collapsed-by-default list of existing matches in the loaded `visual.json` files.
- Make Specific controls mirror the underlying JSON structure hierarchically.
- Use real input controls instead of generic text inputs wherever possible.

## Control Metadata

Extend visual-editor control metadata with:

```python
description: str = ""
default_value: Any | None = None
matches: list[VisualEditorPropertyMatch] = field(default_factory=list)
group_path: list[str] = field(default_factory=list)
```

Suggested match data:

```python
@dataclass(slots=True)
class VisualEditorPropertyMatch:
    document_id: str
    file_path: str
    line: int
    property_path: str
    value: Any
```

Rules:

- `description` appears under the control title.
- `default_value` is the first matching value from active documents, using the active file/filter ordering already shown in the UI.
- If no matching value exists, use the catalog default only when one is explicitly defined.
- `matches` is computed from existing paths in active matching visual files.
- Applying a control still skips nonmatching visuals and reports changed/skipped counts.

## Existing Matches UI

For each control, add a collapsed expandable area under the edit input.

Each list item format:

```text
[{file}] [{line}] {property}: {value}
```

Example:

```text
[visual.json] [42] visual.objects.labels[0].properties.color: #00AEEF
```

Rules:

- Keep the list collapsed by default.
- Use unordered list styling.
- Large match sets should be capped initially, with a clear count such as `Showing 20 of 128`.
- Clicking a match should select the corresponding file and scroll the JSON editor to the line when practical.

## Hierarchical Specific Controls

Specific visual-type controls should mirror the JSON structure instead of appearing as a flat list only.

Example hierarchy:

```text
position
  x
  y
  z
  width
  height
```

Rules:

- Use object group names from the PBIR path as the hierarchy, for example `visual.objects.labels`.
- Use collapsible groups for large sections.
- Preserve the existing General and visual-type selector modes.
- When multiple visual types are active, group first by visual type and then by JSON structure.
- Unknown visual dynamic fallback controls should use the same hierarchy when possible.

## Control Types

Use distinct QML controls by value type:

| Value type | UI control |
| --- | --- |
| `hexColor` | Color picker |
| `boolean` | Checkbox |
| `percentage` / opacity / transparency | Slider with numeric value |
| `string` / text | Text field |
| `integer` / number | Numeric input |
| `enum` | Combo box or segmented selector |
| `url` | Text field with URL validation |

Rules:

- Do not use generic text fields for booleans, colors, opacity, or numbers.
- Validate before applying.
- Keep path-based conversions from v6.
- Preserve JSON validity after every applied change.

## Line Number Discovery

The match list and search features require reliable line numbers.

Add a shared helper that can map known JSON paths to source lines:

- Prefer a lightweight source-map parser if one is already available.
- Otherwise implement a conservative scanner that locates property keys from the formatted document text.
- If a precise line cannot be found, use `?` in the UI and keep the feature usable.

The helper should live outside QML, for example:

- `src/app/features/json_navigation/json_line_index.py`

# Feature 4: Layout and JSON Text Editor Upgrade

## Goals

- Adjust the main layout proportions to make sidebar workflows easier to use.
- Add line numbers to the JSON text editor, similar to Visual Studio Code.
- Add editor-local find and replace using `Ctrl+F`.
- Ensure large JSON text scrolls horizontally instead of wrapping into an unreadable layout.
- Use icon-style sidebar buttons similar to Visual Studio Code.

## Main Layout

When a left panel is open, target these proportions:

- Left sidebar rail: about 10% of total width.
- Open left sidebar panel: about 50% of total width.
- JSON text editor area: about 40% of total width.

Rules:

- Use responsive minimum and maximum widths so the app remains usable on small windows.
- Avoid overlapping UI elements.
- Keep the project tree and open panel behavior consistent with the existing v6 shell.
- If a strict percentage would make the editor too small, clamp to a usable minimum width and allow resizing later.

## JSON Editor

Requirements:

- Display line numbers beside the text.
- Line numbers scroll vertically with the editor.
- JSON text should not soft-wrap by default.
- Long lines should be reachable through horizontal scrolling.
- Current search match should be highlighted or selected.
- Existing document dirty-state behavior must continue working.

Implementation notes:

- If the current QML text editor cannot support stable gutters and horizontal scrolling cleanly, wrap it in a custom editor component.
- Keep rendering limited to the current document, preserving the v5/v6 performance rule.

## Editor Find and Replace

Add `Ctrl+F` support inside the JSON text editor.

Behavior:

- `Ctrl+F` opens or focuses an in-editor find/replace bar.
- Search text is initialized from current selection when useful.
- Enter moves to next match.
- Shift+Enter moves to previous match.
- Replace replaces the selected match.
- Replace all applies to the current document unless the global search panel is explicitly active.
- Match navigation scrolls to the exact line and selection.

History:

- Replace current match records `search-replace-one`.
- Replace all records `search-replace-all` or a current-document-specific operation type if one already exists.
- Plain find navigation does not record history.

# Feature 5: Search and Replace Result Accuracy

## Goals

- Update global search results to show line-aware match rows.
- Fix navigation so up/down buttons scroll to the real match location rather than an unrelated line.

## Search Result Row Format

Each global search result item should display:

```text
[file] [line] [text]
```

Rules:

- `file` should be a short display path when possible.
- `line` is 1-based.
- `text` is the matching line trimmed enough to fit the panel.
- The full line or full path can appear in tooltip text if supported.

## Navigation Bug Fix

The current bug is that clicking up/down search buttons can scroll to a random line instead of the selected match line.

Fix requirements:

- Store both character offsets and line/column information for every match.
- Recompute match locations whenever document text changes.
- When selecting a result, select by document id plus match index, not only by visible row index.
- Scroll the current document editor to the match's exact line.
- Do not reuse stale line offsets after replace, format, rollback, rollforward, or file switch.

Tests:

- Multiple matches in one file navigate in order.
- Matches across multiple files navigate to the correct file and line.
- Replacing one match refreshes subsequent match positions.
- Formatting JSON invalidates and refreshes match offsets.

# Feature 6: History Panel Scroll Stability

## Goals

- Clicking a history item should not reset the history panel scroll position.
- Rollback and rollforward should keep the user oriented in large history lists.

Behavior:

- Preserve `ListView.contentY` around row clicks.
- Updating row states from previous/current/next must not recreate the entire model when row data changes are enough.
- If the clicked row is outside the current viewport because of keyboard navigation, scroll just enough to reveal it.
- Mouse clicks should keep the clicked row visually stable whenever possible.

Tests:

- Create enough history rows to require scrolling.
- Scroll near the bottom.
- Click an older visible row.
- Verify the panel remains near the same scroll position and the clicked row remains visible.

# Feature 7: Macro Transparency and Recording From History

## Goals

- Let users understand exactly what each macro will do before running it.
- Add the ability to create macros from recorded history entries.
- Keep macro export and import JSON-based.
- Preserve safe operation boundaries from v6 history.

## Expandable Macro Steps

Each macro row in the macros panel should include a collapsed expandable steps list.

The expanded list should show:

- Step index.
- Step operation type.
- Target scope, such as current file, filtered files, or matching visuals.
- Main parameters, such as search text, replacement text, filter name, control id, and value.
- Whether the step is reversible through history after it runs.

Rules:

- Keep steps collapsed by default.
- A macro with unsupported or missing fields should display a clear warning on that step.
- Running a macro should still record `macro-run`, mutating `macro-step` rows, and `macro-complete`.

## Record Macro From History

Add a command in the History panel:

- `Create macro from selected history`

MVP selection options:

- Use a contiguous range from the first selected history row to the last selected history row.
- If multi-select is not available yet, use `Create macro from current branch` to capture rows from the first row after the latest rollback branch point through the current row.

History-to-macro conversion:

- Convert supported operation types into macro steps.
- Preserve operation metadata needed to replay the action.
- Exclude non-replayable operations by default and list them in a skipped-steps summary.

Supported initial conversions:

- `search-replace-one`
- `search-replace-all`
- `visual-editor-change`
- `filter-apply`
- `filter-clear`
- `dynamic-filter-apply`
- `format-json`

Optional or deferred conversions:

- `content-edit`, unless the app can safely represent it as an exact text patch.
- `save-file` and `save-all`, because macros should not write to disk without an explicit user action.
- `file-open`, `file-remove`, and `start-again`, because they are session-structure operations.
- `macro-run`, `macro-step`, and `macro-complete`, to avoid accidentally nesting macros.

Generated macro metadata:

- Name defaults to `Recorded macro YYYY-MM-DD HH-mm-ss`.
- Description states the source history index range.
- Each generated step includes the original history index in metadata.

## Macro Import and Export

The app already supports macro import/export from previous versions. v7 should keep this behavior and ensure recorded macros use the same JSON format.

Requirements:

- Export recorded macros to JSON.
- Import exported macros without losing step explanations.
- Validate macro JSON before adding it to the macro list.
- Show validation errors in status text or a compact dialog.
- Imported macros should display expandable steps immediately.

# Feature 8: Operation Refresh Rules

Many v7 features depend on current line numbers, active filters, visual-editor matches, and history state. After these operations, refresh all dependent state:

- File import.
- Flat JSON transform.
- Text edit.
- Format JSON.
- Search replace one.
- Search replace all.
- Visual editor change.
- Dynamic filter apply or clear.
- History rollback.
- History rollforward.
- Macro run.
- Macro step.
- Macro import.

Refresh sequence:

1. Update document text and dirty state.
2. Recompute document line index for changed documents.
3. Refresh search matches for the current query.
4. Refresh dynamic filters.
5. Refresh project tree and file list rows when document set or metadata changes.
6. Refresh visual-editor applicable controls, default values, and match lists.
7. Refresh history row states without resetting history scroll.
8. Emit existing controller signals for current document, files, search, filters, visual editor, history, and status.

# Implementation Plan

## Phase 1: Flat JSON Transform

1. Add flat JSON transform helper and tests.
2. Add import option for generic JSON flattening.
3. Ensure recognized PBIR files remain hierarchical in normal PBIR import.
4. Add collision and escaping validation.

## Phase 2: Shared Line Index

1. Add a JSON/text line-index helper.
2. Store line and offset information for search matches.
3. Store path-to-line information for visual-editor property matches when available.
4. Refresh line indexes after text-changing operations.

## Phase 3: Dynamic Visual Name Filter

1. Add visual-name dynamic filter state.
2. Implement matching against display name, PBIR name, folder name, and file name.
3. Wire the filter into file lists, visual editor scope, search, macros, and history metadata.
4. Add tests for matching and clearing.

## Phase 4: Visual Editor UX

1. Add control descriptions.
2. Compute default values from first matching active property.
3. Compute existing match lists with file, line, property, and value.
4. Render hierarchical Specific controls.
5. Replace generic text inputs with typed controls.
6. Add tests for defaults, matches, hierarchy, and typed value validation.

## Phase 5: Search and Editor Navigation

1. Add line numbers and horizontal scrolling to the JSON editor.
2. Add editor-local `Ctrl+F` find/replace.
3. Update global search result rows to `[file] [line] [text]`.
4. Fix up/down navigation to use stable match offsets.
5. Add navigation regression tests.

## Phase 6: History Scroll Stability

1. Preserve history list scroll position on row clicks.
2. Update row states without unnecessary full model resets.
3. Add a UI smoke test for long history lists.

## Phase 7: Macro Recording and Explanation

1. Add expandable macro step display.
2. Add history-range to macro-step conversion.
3. Add skipped-step reporting for non-replayable history entries.
4. Export recorded macros to JSON.
5. Import recorded macro JSON and preserve step explanations.
6. Add macro replay tests.

## Phase 8: Smoke Test and Results

1. Run Python compile checks.
2. Run existing automated tests.
3. Run targeted flat JSON transform tests.
4. Run search navigation regression tests.
5. Run visual-editor default and match-list tests.
6. Run history scroll stability smoke test.
7. Run recorded macro import/export smoke test.
8. Write `ai/docs/app-version-7-development-results.md` after implementation.

# Acceptance Criteria

- A generic hierarchical JSON file can be imported as flat key-value JSON.
- Flat import outputs paths like `b.d.[0].e`.
- Flat import preserves empty objects and arrays as leaf values.
- Flat import escapes reserved characters and rejects key collisions.
- Normal PBIR folder import keeps `page.json` and `visual.json` hierarchical and editable by PBIR features.
- A third dynamic filter can filter visuals by visual name.
- Visual-name filtering updates file list, project tree, search scope, and visual-editor scope.
- Each visual-editor control can show a description under its title.
- Each visual-editor control initializes from the first matching active value when one exists.
- Each visual-editor control can show a collapsed list of existing matches in `[{file}] [{line}] {property}: {value}` format.
- Specific controls are grouped hierarchically to mirror JSON structure.
- Color, boolean, opacity, text, number, enum, and URL properties use appropriate typed controls.
- The left sidebar rail, open panel, and editor area target about 10%, 50%, and 40% width respectively while remaining responsive.
- The JSON text editor displays line numbers.
- Long JSON lines can be reached through horizontal scrolling.
- `Ctrl+F` opens or focuses editor-local find/replace.
- Global search results display `[file] [line] [text]`.
- Search up/down navigation scrolls to the correct match line.
- History row clicks do not reset the history panel scroll position.
- Macro rows show expandable step explanations.
- Users can create a macro from supported history entries.
- Recorded macros can be exported to JSON and imported again.
- Non-replayable history entries are skipped with a clear summary when recording a macro.
- All text-changing operations refresh line indexes, search matches, visual-editor matches, and history state.

# Risks and Mitigations

- Flattening PBIR files would break PBIR editing. Mitigation: keep normal PBIR import hierarchical and treat explicit flat PBIR import as generic JSON.
- Flat path escaping can confuse users. Mitigation: document the escape rules in code comments and keep the visible format close to the requested dot-path example.
- Line-number mapping for arbitrary JSON can be imprecise after invalid edits. Mitigation: use exact search offsets for text search and show `?` for visual-editor property lines when a structured path cannot be located.
- Visual-editor match lists can become large. Mitigation: collapse by default and cap rendered rows.
- Editor line numbers and horizontal scrolling can be difficult with the current QML component. Mitigation: create a focused reusable editor component and test with large files.
- History-to-macro conversion may capture operations that are not safely replayable. Mitigation: allowlist supported operation types and skip the rest with an explicit summary.
- Layout percentages may not fit small windows. Mitigation: use responsive clamping and minimum widths.
