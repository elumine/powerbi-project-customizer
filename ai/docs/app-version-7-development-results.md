# App Version 7 Development Results

Implementation date: 2026-09-06

Specification: [app-version-7-development-specification.md](app-version-7-development-specification.md)

# Summary

Version 7 has been implemented on top of the v6 PBIR editor. This release adds default flat JSON import, visual-name dynamic filtering, richer visual-editor inspection data, line-aware per-match search results, a line-numbered no-wrap JSON editor with local find/replace controls, history scroll preservation, and macro recording from history.

# Implemented Features

## Flat JSON Import

Added a JSON transform package:

- `src/app/features/json_transform/flat_json.py`
- `src/app/features/json_transform/__init__.py`

The transform converts hierarchical JSON into flat key-value JSON using dot-separated object paths and `[n]` array index segments.

Example:

```json
{
  "a": 1,
  "b.c": 2,
  "b.d.[0].e": "f"
}
```

Reserved path characters in source keys are escaped, empty objects/arrays are preserved as leaf values, and key collisions fail cleanly instead of overwriting values. File and folder imports now flatten JSON on read by default. The separate `Add flat JSON` action was removed because `Add JSON files` and folder import already use the flat transform.

## Dynamic Filter by Visual Name

Added dynamic visual-name filtering next to the existing page-name and visual-type filters.

Matching includes:

- visual display name
- PBIR `name`
- visual folder name
- `visual.json` file name
- relative path

The filter is case-insensitive and scoped to visual documents. Visual-type filters use the flattened `visual.visualType` key after default flatten-on-read import. Visual-name matching still includes filename/path metadata, including `visual.json` paths. Applying it records `dynamic-filter-apply` history metadata with `kind: visual-name`.

## Visual Editor Control Inspectability

Extended visual-editor data classes and Qt model roles with:

- `description`
- `defaultValue`
- `matches`
- `groupPath`

The visual editor service enriches applicable controls with generated descriptions, default values from the first active matching visual property, up to 20 existing property matches, and a hierarchy path derived from the controlled JSON path. Known controls resolve both nested PBIR paths and flattened long keys such as `visual.objects.labels.[0].properties.fontSize`.

Each match is exposed in this format:

```text
[{file}] [{line}] {property}: {value}
```

Added a lightweight JSON navigation helper:

- `src/app/features/json_navigation/json_line_index.py`
- `src/app/features/json_navigation/__init__.py`

The QML visual-editor delegate shows descriptions, hierarchy metadata, defaults, typed boolean/slider inputs, color swatches, and collapsed match lists.

## Search and Editor Navigation

Search previews now include line numbers, line text, display text, and exact start/end offsets. Added:

- `src/app/ui/search_result_model.py`

The global search panel now renders one row per match in `[file] [line] [text]` format and calls `navigateToMatch(fileIndex, matchIndex)`. Search navigation stores exact match offsets and line numbers, refreshes positions after text changes, and exposes `activeMatchStart` / `activeMatchEnd` for QML selection.

## JSON Editor Upgrade

The JSON editor now includes:

- line-number gutter beside the current document
- `TextEdit.NoWrap` editing
- horizontal scrolling for long lines
- editor-local find/replace bar opened by `Ctrl+F`
- next/previous/replace/current-file replace actions from the editor bar
- selection of the exact active global/editor search match when navigation changes

## History Scroll Stability

History row clicks preserve `historyList.contentY` around rollback/rollforward calls, preventing the list from jumping back to the top after selecting a visible history row.

## Macro Transparency and Recording

Macro rows in QML have an expandable `Steps` view showing step index, step type, and step summary from the macro model.

Added macro creation from applied history rows through:

- `HistoryController.entries`
- `MacroController.create_from_history_entries(...)`
- `AppController.createMacroFromHistory()`
- History panel `Record macro` button

Supported history-to-macro conversions:

- `search-replace-one`
- `search-replace-current-file`
- `search-replace-all`
- `visual-editor-change`
- `filter-apply`
- `filter-clear`
- `dynamic-filter-apply`
- `format-json`

Unsupported history rows are skipped and reported in the status message. Recorded macros preserve `sourceHistoryIndex` in JSON export, validate imported recorded steps, and replay the recorded step types.

# Verification

## Python Compile Check

Passed:

```powershell
python -m py_compile src\app\features\json_transform\flat_json.py src\app\features\json_navigation\json_line_index.py src\app\ui\search_result_model.py src\app\features\file_management\file_repository.py src\app\features\file_management\file_management_service.py src\app\features\file_management\file_management_controller.py src\app\features\filters\filter_controller.py src\app\features\visual_editor\visual_edit_types.py src\app\ui\visual_editor_models.py src\app\features\visual_editor\visual_editor_service.py src\app\features\visual_editor\visual_property_catalog.py src\app\features\macros\macro_types.py src\app\features\macros\macro_repository.py src\app\features\macros\macro_controller.py src\app\features\history\history_controller.py src\app\shell\app_controller.py src\app\features\search_replace\search_controller.py
```

## App Smoke Test

Passed in offscreen mode:

```powershell
$env:PYTHONPATH='src'; $env:QT_QPA_PLATFORM='offscreen'; python -m app.ui.application --smoke-test
```

## Targeted v7 Smoke Test

Passed with an in-memory/temp-file smoke test covering:

- flat JSON transform output including `b.d.[0].e`
- per-match search result model rows
- exact-offset match navigation
- invalid `visual.json` matching by visual-name path metadata
- macro creation from history producing replayable recorded steps

# Notes and Limitations

- Flat import is the default for JSON file and folder imports. Imported `page.json` and `visual.json` files are flattened into generic JSON documents on read.
- The editor-local find bar shares the existing search/replace state with the global search panel instead of maintaining a second independent query.
- Visual color input currently uses a swatch plus text field rather than a native color dialog.
- Visual-editor match line discovery is conservative. If a precise key line cannot be found, the model reports `0` and the UI displays `?`.
- History model updates still reset internally; QML preserves scroll position around history clicks to address the observed jump.
- Macro recording uses applied history rows from the start of the current history branch through the current row. Explicit multi-row history selection remains a future enhancement.



