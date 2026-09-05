# Feature Slices

The app is split into feature-oriented modules. QML still talks to
`app.shell.AppController`, but that class is now a facade over these slices:

- `file_management`: load, track, edit, format, save, remove, and select JSON documents.
- `folder_import`: scan selected folders and stage matching `visual.json` files for import.
- `search_replace`: search state, highlighted previews, replacement, and match navigation.
- `filters`: imported and persisted content filters, active/inactive document state, and filter editor workflow.
- `suggestions`: duplicate key/value detection for valid loaded JSON documents.
- `macros`: imported macro loading, validation, running state, and ordered execution.

Keep feature business rules inside these packages. The shell facade should only
translate QML calls into feature methods and emit Qt notifications.