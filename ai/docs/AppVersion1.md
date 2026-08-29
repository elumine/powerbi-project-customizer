This files describes application v1 features.

# Application
- uses python
- uses PySide6, QML and QStyle for UI. https://doc.qt.io/qtforpython-6/index.html
- taget platform is windows

# Idea
- app is used to multi edit json files.
- open multiple json files
- search and replace text in files

# Features
- Looks lik VSCode dark theme

- File picker to open files
  - use drag and drop or button to add files
  - files are displayed in list
  - file can be removed from list (using red x button)
  - green continue button to proceed to file management (disabled if there are no files)

- File editor to search and replace text
  - has left side panel
    - with file explorer button
      - onclick opens file explorer panel
        - looks like vscode file explorer
    - with search button
      - onclick opens search panel
        - looks like vscode search panel
          - user can search in files
          - user can replace text in all files
          - user can replace text in single file
  - has files editor panel
    - with tabs for each file
      - each tab is file editor
        - user can edit text in file
        - file can be saved using save button (near file tab and in file explorer panel)
