# JSON Multi Editor

Desktop JSON multi-file editor built with Python, PySide6, QML, and Qt styling. The source is organized into entities, feature slices, reusable services, infrastructure adapters, bootstrap composition, and component-based QML modules.

## Features

- Open multiple JSON files by picker or drag and drop.
- Import folders recursively through a modal scan of every supported, non-skipped `.json` file, including pages, visuals, and generic JSON.
- Display friendly file names from JSON content keys: `name`, `Name`, `Title`, or `title`.
- Edit files in vertical expand/collapse accordions.
- Search and replace across JSON text, including both keys and values.
- Click search result previews to open the matching file accordion and scroll to the matched line.
- Navigate matches inside the file editor with a compact search widget and active match count.
- Import read-only content filters from `content/filters` and keep user-created filters persisted separately.
- Create, edit, delete, persist, apply, and deactivate user JSON content filters.
- Match filters recursively by key with `equals`, `includes`, `notEquals`, and `notIncludes` operations.
- View duplicate JSON key/value suggestions from loaded valid JSON files and open search from a suggestion.
- Import and run ordered macros from `content/macros` for filter, search, search-and-replace, and grouped visual-formatting workflows.
- Apply the bundled `powerbi-standard-visual-formatting.json` macro with six named groups covering all visuals, charts, slicers, bookmark navigators, title textboxes, and cards.
- Keep invalid JSON visible in the explorer while excluding it from active filtered editing/search.
- Limit search, replace-all, and single-file replace to active files while a content filter is applied.
- Save one file or all dirty files.
- Review files changed since import in a dedicated Changes panel with VS Code-style red/green diffs.

## Setup

```cmd
pip install PySide6
```

## Run

```cmd
tools\dev.cmd
```

## Smoke test

```cmd
tools\dev.cmd --smoke-test
```

## Unit and architecture checks

```cmd
set PYTHONPATH=src && python -m unittest discover -s test\unit
set PYTHONPATH=src && python -m unittest discover -s test\architecture
```

## Build

```cmd
tools\build.cmd
```