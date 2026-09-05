# JSON Multi Editor

Desktop JSON multi-file editor built with Python, PySide6, QML, and Qt styling.

## Features

- Open multiple JSON files by picker or drag and drop.
- Import folders recursively through a modal scan that includes only files named `visual.json`.
- Display friendly file names from JSON content keys: `name`, `Name`, `Title`, or `title`.
- Edit files in vertical expand/collapse accordions.
- Search and replace across JSON text, including both keys and values.
- Click search result previews to open the matching file accordion and scroll to the matched line.
- Navigate matches inside the file editor with a compact search widget and active match count.
- Import read-only content filters from `content/filters` and keep user-created filters persisted separately.
- Create, edit, delete, persist, apply, and deactivate user JSON content filters.
- Match filters recursively by key with `equals`, `includes`, `notEquals`, and `notIncludes` operations.
- View duplicate JSON key/value suggestions from loaded valid JSON files and open search from a suggestion.
- Import and run ordered macros from `content/macros` for filter, search, and search-and-replace workflows.
- Keep invalid JSON visible in the explorer while excluding it from active filtered editing/search.
- Limit search, replace-all, and single-file replace to active files while a content filter is applied.
- Save one file or all dirty files.

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

## Build

```cmd
tools\build.cmd
```