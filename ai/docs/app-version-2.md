This files describes application v2 features.

# New Features
- ability to select/drag-and-drop folder
  - in this case we should open modal window overlay
    - scan folder recursively for json files
    - filter only files that have "visual.json" names
    - display them as file tree
    - display continue green button
      - onclick user should proceed with files import
- in search and replace
  - if user enters search
    - for each file with matches
      - we should display matched text for each match in file as list (matched text with yellow bg)
      - if user has replace text entered
        - we should display matched text with red bg and display replaced text with green bg near match text
          - this should look like git diff
- in file editor
  - files display should be as vertical list of collapse/expand accordions instead of tabs
    - user can toggle file content expand/collapse
  - if user has search entered we should display searches in file editor view as they are displayed in VS Code
    - in file content hightlight searched match should have yellow bg
    - if user has replace entered we should display matched text with red bg and display replaced text with green bg near match text
        - this should look like git diff
- json file names may be random symbols, create module to get file name by its json content
  - try to find property "name", "Name", "Title", "title" in file and use it as name
  - use it to display file names on ui
- bugs
  - when using search and replace we can only search/replace by json values - not by keys
