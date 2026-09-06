# App Version 6 Development Results

Implementation date: 2026-09-05

Specification: [app-version-6-development-specification.md](app-version-6-development-specification.md)

# Summary

Version 6 implementation has been added on top of the v5 PBIR editor. The main changes are expanded Specific visual editor coverage for the sample PBIR visual types and a new in-session History panel with backward/forward history navigation for recorded file-content changes.

# Implemented Features

## Expanded Specific Visual Editor Coverage

The visual editor control model now supports explicit allowlisted PBIR paths through new control metadata:

- `paths`
- `createsMissingPath`
- `matchingCount`
- `visualTypeGroup`

The visual editor service now prefers path-based updates before falling back to v5 compatibility behavior. Path controls can update existing PBIR property objects that use either `expr.Literal.Value` or `solid.color`, and still validate JSON before updating document text.

Added Specific controls for all visual types found in `test/data/test-project/definitions/pages/p1/`:

- `shape`
- `gauge`
- `textbox`
- `slicer`
- `cardVisual`
- `image`
- `barChart`

Representative controls include shape fill/rotation/outline, gauge axis/label/callout settings, textbox border/header settings, slicer mode/selection/items/header settings, card label/value/layout/image/divider settings, image URL/link settings, and expanded bar chart axis/label/legend/totals settings.



## Visual Type Selector Modes

Updated the Visuals Editor selector so it now includes `General`, `Specific`, and visual-type modes such as `Bar chart`, `Gauge`, `Image`, `Slicer`, and `Other`. Visual-type modes show all controls applicable to that type, including General controls and type-specific controls. Applying a General control while a visual-type mode is selected is scoped to active visuals of that selected type only.

## Counted Visual Type Options

Updated visual-type selector options so supported visual types remain visible but unavailable types are disabled. Visual-type option labels now use `{count} {visualTypeName}`, for example `1 Bar chart` or `0 Line chart`. Disabled options render at reduced opacity and cannot be selected from the QML combo. This prevents users from selecting visual-type modes that are not present in the currently active files.
## Dynamic Other Visual Editor Fallback

Added a fallback generator for unknown or marketplace visual types. When the Specific category is opened and an active visual type has no explicit Specific catalog coverage, the visual editor now creates an `Other` group from safe existing formatting properties under:

- `visual.objects.*[].properties`
- `visual.visualContainerObjects.*[].properties`

The generated controls support booleans, numbers, percentages, strings, literal expressions, and solid colors. They are cached in memory so QML can apply them with the same flow as built-in controls. The fallback does not inspect or mutate query, projection, semantic model, or `filterConfig` structures.
## Visual Editor UI Metadata

The Visuals Editor panel now shows control metadata for active visual scope:

- visual type group
- value type
- matching active visual count

This helps users understand which Specific controls apply when filters make one or more visual types active.

## History Feature

Added a new history feature package:

- `src/app/features/history/history_entry.py`
- `src/app/features/history/history_service.py`
- `src/app/features/history/history_controller.py`
- `src/app/features/history/__init__.py`
- `src/app/ui/history_model.py`

History entries include:

- index
- timestamp
- operation type
- display name
- metadata
- affected file snapshots
- reversible flag

File snapshots store before/after text and before/after saved baselines so rollback/rollforward can restore both content and dirty state in memory.

## History Panel

Added a left sidebar `H` button and a History panel in `App.qml`.

Each row displays:

```text
[ index ] [ time ] [ operation type ] Display name ( metadata of what changed )
```

Row colors follow the requested behavior:

- current row: cyan
- previous rows: light green
- next rows: light red

Clicking a previous row rolls back intervening reversible file-content changes. Clicking a next row reapplies them.

## Recorded Operations

The controller now records history for these implemented operations:

- file remove, as a non-reversible boundary row
- content edit
- format JSON
- replace current match
- replace current file
- replace all
- save file
- save all
- filter apply
- filter clear
- dynamic filter apply
- filter import
- filter update/save
- filter delete
- visual editor change
- macro import
- macro run
- macro step file changes
- macro complete
- start again boundary before history is cleared

# Verification

## Python Compile Check

Passed:

```powershell
python -m py_compile src\app\features\visual_editor\visual_edit_types.py src\app\features\visual_editor\visual_property_catalog.py src\app\features\visual_editor\visual_editor_service.py src\app\features\history\history_entry.py src\app\features\history\history_service.py src\app\features\history\history_controller.py src\app\ui\history_model.py src\app\ui\visual_editor_models.py src\app\ui\file_list_model.py src\app\shell\app_controller.py
```

## Targeted Visual Editor and History Smoke Test

Passed in memory against `test/data/test-project/definitions/pages/p1/visuals`.

Results:

- detected visual types: `barChart`, `cardVisual`, `gauge`, `image`, `shape`, `slicer`, `textbox`
- missing Specific coverage: none
- representative edits changed 7 values across the seven visual types
- history rollback moved from row 1 to row 0
- history rollforward moved from row 0 to row 1


## Dynamic Other Fallback Smoke Test

Passed with a synthetic marketplace visual type named `customMarketplaceVisual`.

Results:

- generated 7 `Other` controls from safe formatting properties
- generated labels included `Other: Background Color`, `Other: Settings Font Size`, `Other: Settings Label Color`, and `Other: Settings Show Labels`
- applied a generated color control successfully
- resulting JSON contained the updated color `#00AEEF`
## App Smoke Test

Passed in offscreen mode:

```powershell
$env:PYTHONPATH='src'; $env:QT_QPA_PLATFORM='offscreen'; python -m app.ui.application --smoke-test
```

The command exited with code 0.

# Notes and Limitations

- Text editor history currently records each accepted text update. The v6 specification recommends debounce/coalescing; that can be refined later if typing creates too many rows during manual use.
- `start-again` records a boundary event and then clears app history as part of resetting the session, matching the acceptable boundary behavior from the specification.
- File remove is recorded as non-reversible in this implementation. Full document restoration can be added later if needed.
- The schema-aware candidate generator described in the specification was not implemented as a separate developer tool; the implemented control coverage was based on the local `p1` visual JSON structures.
- Runtime schema download is not required and was not added.





