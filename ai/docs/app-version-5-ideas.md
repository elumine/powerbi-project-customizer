This file describes application v5 features.

# Updates
## Bugs
- user cant save files after enabling/disabling filters
## Json files can have types
- create enum JsonFileTypes { Page, Visual }
- currenly all imported jsons are "visual.json" - those are Visual
- user also can import "page.json" files - those are Page
### File naming updates
- if user imports json of type Page - its name should be value of property "displayName" in that json file
- if user imports json of type Visual - try to get name with this priorities:
  - 1st check property "visual.visualContainerObjects.title.[0].properties.text.expr.Literal.Value"
  - 2st check property "visual.visualType"
  - 3st check property "name"

## Search and replace
- remove Relace File function
- add "Replace" button - this should replace first searched match element

## Filters System
- fix bug: currently when i create filter i cant select any type of operation except "equals"
- filters can be imported (add button) from json files
- filters can be exported (add button for each filter) to json files
- create new pre defined filters (as json files in content folder)
  - filters by visualType key with "includes" operation and following values: Bar, Pie, Line, Chart, Table, Slicer
- filters can be applied to specific json files or to all, add property "targetJsonFileType" default - All
- create new feature: dynamic filters
  - add 3 new input sections (with name, text input and apply button)
    - PageNameDynamicFilter: targetJsonFileType=Page, key=displayName, operation=includes
    - VisualTypeDynamicFilter: targetJsonFileType=Visual, key=visualType, operation=includes
  - they should work as existing filters with "includes operation" but user can specify value via text input
  - dynamic filters cant be imported/exported

## Clearing of application context (re initialization feature)
- I shoul be able to close and remove previously selected folder with json files and select the new one and continue data transformations
- add top bar button "start again" that should clear all existing app state (applied filters, selected files, search state, etc..), and move user to 1st screen of application with files/folders selection

## Files structure updates
- file structure on disk is like this: page_folder with page.json and "visuals" sub folder that has folders for each visual.json
- we should preserve this structure on files import
- if user imports only files of type "visual.json" - they are structured as flat array (as now)
- if use imports Pages and Visuals - we should create tree like hierarchy of page-visuals relations based of file system folders hierarchy
- create class PageFile that has list of visuals
- create class VisualFile that has reference to parent page

### UI updates
- current ui panel should display pages and visuals as hierarchy (ordered list)
- add ability to collapse/expand pages to see their visuals

## New feature "Visuals Editor"
- add left sidebar button and panel for it
- inside panel there should be UI to edit specific json values
- editor is working with Microsoft Office "visualContainer" type (schema https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json)
  - goal is to create ui to edit general properties of all visual types and specific properties per visual type
- editor should have common ui elements to change properties based on their type:
  - opacity: slider
  - string properties: text input
  - colors: color picker
  - etc...
- panel has 2 categories
  - category 1 "General"
    - this category should contain all properties that are shared between visuals, like opacity / backgroundColor
  - category 2 "Specific"
    - for each possible supported visualType we should have unique list of controls for their unique values
    - example: bar chart visual type should have something like "barColor"
- when user changes value in some ui control (bound to some specific key of visual/all_visuals like opacity)
  - 1) for all active visual.json files
  - 2) find all keys with name equal to changed key (opacity)
  - 3) change value of all that keys with new value for ui control

## Macros System
- add import export feature like for filters
- macros should support not only search, search-replace but also filter-apply, filter-clear actions
- add new macros action types to support new visual editor "visual-editor-change"
- update existing macros logic to support other changes made for other features
