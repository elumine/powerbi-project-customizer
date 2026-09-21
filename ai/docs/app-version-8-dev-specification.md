# App Version 8 Development Specification

Source request date: 2026-09-21

# Purpose

Version 8 keeps an imported JSON workspace in sync with deliberate user decisions when files are changed on disk, and makes the top-bar restart command a true session reinitialization.

# Feature 1: Watch Imported JSON Files

## Goals

- Watch every JSON file successfully imported into the current workspace.
- Detect modifications made outside the application, including edits performed by another editor or tool.
- Do not report the application?s own successful save operations as external changes.
- Stop watching files when they are removed from the workspace or when the session is restarted.

## Change Detection

- Use a file-system watcher for each imported JSON path.
- Maintain a content fingerprint captured at import, successful save, re-import, or user cancellation.
- Ignore duplicate filesystem notifications whose content matches the current fingerprint.
- Treat a deleted/unreadable file as a change so the user can see and decide on it.
- Re-establish a watch after a file replacement when the file still exists, because some editors save by replacing the original file.

# Feature 2: External-Change Modal

When one or more imported files change on disk, display a modal overlay above the workspace.

The overlay must:

- List every changed file by name and full path.
- State that re-import will replace the in-memory contents of those files.
- Block ordinary workspace interaction until a choice is made.
- Provide `Re-import` and `Cancel` actions.

`Re-import` reloads each listed file from disk, retains its stable session identity when possible, resets its dirty/import baseline, and refreshes document-dependent projections such as search, filters, suggestions, project tree, changes, and visual-editor controls.

`Cancel` keeps the current in-memory document versions and acknowledges the observed disk version. The same disk content must not immediately reopen the modal; a later external modification must.

If an individual file cannot be re-imported, show the first error in the status text and leave the successful files refreshed.

# Feature 3: Full Restart

The top-bar restart action must restore the application to a fresh picker-session state. It must clear:

- Imported documents, current selection, project tree, folder-import preview, and file-change watcher state.
- Pending external-change notifications.
- Search query, replacement text, active match navigation, active filter, and filter editor draft.
- Suggestions, visual-editor category/result state, history, and macro-recording state.
- Macro runtime flags and macro search text.

Persisted user filters and bundled macros remain available because they are application content rather than session state.

# Acceptance Criteria

- Editing an imported JSON file manually produces one modal listing that file.
- Multiple external edits before a decision appear together in the same modal.
- Re-import shows disk content and removes the corresponding pending notification.
- Cancel keeps in-memory content and does not repeat for the already acknowledged disk content.
- Saving from the app does not open the external-change modal.
- Restart leaves no imported file rows, pending file-change dialog, history rows, folder-import rows, active filter, or residual visual-editor selection.
