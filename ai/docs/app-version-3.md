This file describes application v3 features.

# Application
- based on application v1 and v2 features
- target platform is Windows
- uses Python, PySide6, QML and QStyle for UI
- keeps VS Code dark theme style

# New Features
- files can be filtered by JSON content
  - filter is a JSON object
    - has display name for UI
    - has unique random color for UI display
    - has rules array
  - rule is JSON pattern matcher
    - has key text
    - has operation type
      - equals
      - includes
      - notEquals
      - notIncludes
    - has value text
  - example rule
    - somewhere in JSON key "a" should equal value "b"
  - filter can have multiple rules
    - file matches filter only when all filter rules match
    - each rule can match any occurrence of the key anywhere in JSON
    - nested objects and arrays should be searched recursively
  - rule matchers should not be case sensitive
    - key matching is case insensitive
    - value matching is case insensitive
    - string comparison should normalize both sides before matching
  - non-string JSON values should be supported
    - convert value to string for text comparison
    - null should be compared as "null"
    - boolean values should be compared as "true" or "false"
    - numbers should be compared by their string representation

- create 2 default filters
  - "Table"
    - color is generated once and stored with filter
    - rules
      - key "visualType"
      - operation equals
      - value "table"
  - "Chart"
    - color is generated once and stored with filter
    - rules
      - key "visualType"
      - operation includes
      - value "chart"

- create filter sidebar tab button
  - button is displayed in left side panel near file explorer and search buttons
  - onclick opens filters panel
  - active button state should match existing sidebar tab style

- create filters panel
  - panel displays list of already created filters
    - each filter item displays color marker
    - each filter item displays filter display name
    - each filter item has apply/deactivate toggle
    - each filter item has edit button
    - each filter item has delete button
  - panel has "New filter" button
    - onclick opens filter editor UI for new filter
  - user can apply one filter at a time
    - applying another filter deactivates previously applied filter
    - deactivating current filter returns all files to active state

- create filter editor UI
  - editor is used for creating and editing filters
  - user can change filter display name
  - user can see and change filter color
    - color is random by default for new filters
    - color should remain stable after filter is saved
  - user can add rule
  - user can remove rule
  - each rule constructor has 3 items
    - text input for key
    - select for operation type
      - equals
      - includes
      - notEquals
      - notIncludes
    - text input for value
  - user can save filter
    - display name is required
    - at least 1 rule is required
    - every rule must have non-empty key
    - saved filter appears in filters list
  - user can cancel editor changes

- filter apply behavior
  - when user applies filter
    - evaluate every loaded JSON file against selected filter rules
    - matching files become active
    - not matching files become inactive
  - if file JSON cannot be parsed
    - file does not match content filters
    - file becomes inactive while filter is applied
    - UI should show parse error indicator near file name
  - filter state should be recalculated when file content changes
    - if active filter exists and user edits file JSON, update file active/inactive state after debounce
    - if JSON becomes invalid, mark file inactive for current filter

- file explorer behavior
  - all loaded files are visible in file explorer
  - active files display normally
  - inactive files have opacity 0.25
  - inactive files cannot be selected for editor display
  - active filter color can be displayed near matching active files

- files editor behavior
  - files editor displays only active files
  - inactive files are not displayed in files editor
  - if currently opened file becomes inactive
    - close/collapse it in files editor
    - select first active file if available
    - show empty editor state if no files are active

- search and replace behavior
  - search works only on active files
  - replace all works only on active files
  - replace in single file is available only for active files
  - inactive files are not included in match count
  - inactive files are not displayed in search results
  - when filter is deactivated
    - search and replace returns to using all loaded files

# Data Model
- File item
  - id
  - original path
  - display name from v2 name detection logic
  - raw text content
  - parsed JSON content if valid
  - parse error if invalid
  - isActive boolean

- Filter item
  - id
    - unique generated id
  - displayName
  - color
    - unique random color for UI display
  - rules
    - array of filter rules

- Filter rule
  - id
    - unique generated id for UI editing
  - key
  - operation
    - equals
    - includes
    - notEquals
    - notIncludes
  - value

# Matching Logic
- recursively search JSON content for matching keys
  - object keys should be checked at every nested level
  - array items should be recursively checked
  - first matching key/value pair can satisfy a rule
- rule result
  - equals
    - true when any matching key has value equal to rule value
  - includes
    - true when any matching key has value that contains rule value
  - notEquals
    - true when matching key exists and all matching key values are not equal to rule value
  - notIncludes
    - true when matching key exists and all matching key values do not contain rule value
- missing key behavior
  - equals returns false
  - includes returns false
  - notEquals returns false
  - notIncludes returns false
- filter result
  - all rules must return true
  - if rules array is empty, filter is invalid and cannot be saved

# Persistence
- saved filters should be persisted between app sessions
  - default filters should be created only when no saved filters exist
  - user-created filters should keep ids, names, colors and rules
  - deleting filter removes it from persisted filters
- active filter state can be session-only
  - after app restart, no filter needs to be active by default

# Edge Cases
- filter display name duplicates
  - allow duplicates but keep ids unique
- random color duplicates
  - avoid using same color for filters in current list when possible
- empty value in rule
  - allowed for includes and notIncludes
  - equals can match empty string
- whitespace
  - trim key text before saving
  - keep value text as entered, but comparisons should be case insensitive
- invalid JSON file
  - still visible in file explorer
  - hidden from files editor while content filter is active
  - searchable only when no content filter is active
