# Macros Feature

# Macros Step Types
Each macros step has unique step type.
```
MACRO_STEP_TYPES = (
    "filter-apply",
    "filter-clear",
    "dynamic-filter-apply",
    "format-json",
    "search",
    "search-replace-all",
    "search-replace-one",
    "visual-editor-change",
)
```

## filter-apply
Applies filter based on filter.json file.
Step actions:
- finds filter json file by name or id
- applies it
Required params:
- filterId: "id" in filter.json file
- or filterName: "displayName" in in filter.json file
Example by id:
```json
{
    "type": "filter-apply",
    "filterId": "builtin.filter.visual-type-table"
}
```
Example by name:
```json
{
    "type": "filter-apply",
    "filterName": "Table visuals"
}
```

## filter-clear
Step actions:
- deactivate current filter
```json
{
    "type": "filter-clear"
}
```

## dynamic-filter-apply
Applies filter without json file, by provided filter string.
Step actions:
- uses provided value as filter value
- executes filter by name with provided value
Example filter by page name:
```json
{
    "value": "Overview",
    "type": "dynamic-filter-apply",
    "filterName": "page-name"
}
```

Example filter by visual name:
```json
{
    "value": "Sales",
    "type": "dynamic-filter-apply",
    "filterName": "visual-name"
}
```

Example filter by visual type:
```json
{
    "value": "table",
    "type": "dynamic-filter-apply",
    "filterName": "visual-type"
}
```

## format-json
Step actions:
- format json document into "pretty" format
```json
{
    "type": "format-json"
}
```

## search
Step actions:
- open search panel
- set value as search input value
- execute search
```json
{
    "type": "search",
    "searchValue": "targetKey"
}

```
## search-replace-all, search-replace-one
Step actions:
- open search panel
- set value as search input value
- execute search
- execute replace
```json
{
    "searchValue": "properties.fontSize.expr.Literal.Value",
    "replaceValue": "14D",
    "type": "search-replace-all"
}
```

## visual-editor-change
Step actions:
- for each active (not filtered out) visual.json
    - if active visual json type doesnt match "" - skip it
    - apply change to visual.json base on "controlId" and "value"

# Visual Editor Macro Steps

Each formatting operation uses a `visual-editor-change` step:

```json
{
    "controlId": "<ControlID>",
    "value": <VALUE>,
    "type": "visual-editor-change"
}
```
Value rules:
- Use real JSON Booleans: `true` and `false`, without quotes.
- Use real JSON numbers, without quotes.
- Use quoted strings for colors, text, font names, URLs, modes, and enum values.
- Hex colors should use the `#RRGGBB` form unless the target property explicitly supports another form.
- A control is intended only for the visual types listed under **Applies to**.
- Controls with a selector are written to that selector state automatically.

## Available control IDs

## Available control IDs

### general-title-text

Actions:
- Sets **Title text**.
- Applies to: all visual types.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.

Example:
```json
{
    "controlId": "general-title-text",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### general-title-font-color

Actions:
- Sets **Title font color**.
- Applies to: all visual types.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.

Example:
```json
{
    "controlId": "general-title-font-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### general-background-color

Actions:
- Sets **Background color**.
- Applies to: all visual types.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.

Example:
```json
{
    "controlId": "general-background-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### general-background-transparency

Actions:
- Sets **Background transparency**.
- Applies to: all visual types.
- Accepted value: a JSON number representing a percentage, typically `0` to `100`.

Example:
```json
{
    "controlId": "general-background-transparency",
    "value": 20,
    "type": "visual-editor-change"
}
```
<br>

### general-hidden

Actions:
- Sets **Hidden**.
- Applies to: all visual types.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "general-hidden",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### bar-data-color

Actions:
- Sets **Bar color**.
- Applies to: `bar`, `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.

Example:
```json
{
    "controlId": "bar-data-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### bar-value-axis-show

Actions:
- Sets **Value axis**.
- Applies to: `barChart`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "bar-value-axis-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### bar-category-axis-color

Actions:
- Sets **Category label color**.
- Applies to: `barChart`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.

Example:
```json
{
    "controlId": "bar-category-axis-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### bar-label-font-size

Actions:
- Sets **Label font size**.
- Applies to: `barChart`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.

Example:
```json
{
    "controlId": "bar-label-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### bar-legend-show

Actions:
- Sets **Legend**.
- Applies to: `barChart`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "bar-legend-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### bar-totals-show

Actions:
- Sets **Totals**.
- Applies to: `barChart`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "bar-totals-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### pie-slice-color

Actions:
- Sets **Pie slice color**.
- Applies to: `pieChart`, `donutChart`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.

Example:
```json
{
    "controlId": "pie-slice-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### line-color

Actions:
- Sets **Line color**.
- Applies to: `lineChart`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.

Example:
```json
{
    "controlId": "line-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### text-size

Actions:
- Sets **Table text size**.
- Applies to: `table`, `pivotTable`, `matrix`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.

Example:
```json
{
    "controlId": "text-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### slicer-background-transparency

Actions:
- Sets **Slicer background transparency**.
- Applies to: `slicer`.
- Accepted value: a JSON number representing a percentage, typically `0` to `100`.

Example:
```json
{
    "controlId": "slicer-background-transparency",
    "value": 20,
    "type": "visual-editor-change"
}
```
<br>

### slicer-mode

Actions:
- Sets **Mode**.
- Applies to: `slicer`.
- Accepted value: a quoted JSON string accepted by the target Power BI property.

Example:
```json
{
    "controlId": "slicer-mode",
    "value": "Example",
    "type": "visual-editor-change"
}
```
<br>

### slicer-single-select

Actions:
- Sets **Single select**.
- Applies to: `slicer`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "slicer-single-select",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### slicer-select-all

Actions:
- Sets **Select all checkbox**.
- Applies to: `slicer`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "slicer-select-all",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### slicer-items-font-color

Actions:
- Sets **Items font color**.
- Applies to: `slicer`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.

Example:
```json
{
    "controlId": "slicer-items-font-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### slicer-items-text-size

Actions:
- Sets **Items text size**.
- Applies to: `slicer`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.

Example:
```json
{
    "controlId": "slicer-items-text-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### slicer-header-text

Actions:
- Sets **Header text**.
- Applies to: `slicer`.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.

Example:
```json
{
    "controlId": "slicer-header-text",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### shape-type

Actions:
- Sets **Shape type**.
- Applies to: `shape`.
- Accepted value: a quoted JSON string accepted by the target Power BI property.

Example:
```json
{
    "controlId": "shape-type",
    "value": "Example",
    "type": "visual-editor-change"
}
```
<br>

### shape-rotation

Actions:
- Sets **Rotation angle**.
- Applies to: `shape`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.

Example:
```json
{
    "controlId": "shape-rotation",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### shape-fill-color

Actions:
- Sets **Fill color**.
- Applies to: `shape`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.

Example:
```json
{
    "controlId": "shape-fill-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### shape-fill-transparency

Actions:
- Sets **Fill transparency**.
- Applies to: `shape`.
- Accepted value: a JSON number representing a percentage, typically `0` to `100`.

Example:
```json
{
    "controlId": "shape-fill-transparency",
    "value": 20,
    "type": "visual-editor-change"
}
```
<br>

### shape-outline-show

Actions:
- Sets **Outline**.
- Applies to: `shape`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "shape-outline-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### gauge-axis-min

Actions:
- Sets **Axis minimum**.
- Applies to: `gauge`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.

Example:
```json
{
    "controlId": "gauge-axis-min",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### gauge-axis-max

Actions:
- Sets **Axis maximum**.
- Applies to: `gauge`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.

Example:
```json
{
    "controlId": "gauge-axis-max",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### gauge-label-color

Actions:
- Sets **Label color**.
- Applies to: `gauge`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.

Example:
```json
{
    "controlId": "gauge-label-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### gauge-label-font-size

Actions:
- Sets **Label font size**.
- Applies to: `gauge`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.

Example:
```json
{
    "controlId": "gauge-label-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### gauge-target-show

Actions:
- Sets **Target**.
- Applies to: `gauge`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "gauge-target-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### gauge-callout-color

Actions:
- Sets **Callout color**.
- Applies to: `gauge`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.

Example:
```json
{
    "controlId": "gauge-callout-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### gauge-callout-show

Actions:
- Sets **Callout**.
- Applies to: `gauge`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "gauge-callout-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### textbox-border-show

Actions:
- Sets **Border**.
- Applies to: `textbox`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "textbox-border-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### textbox-border-width

Actions:
- Sets **Border width**.
- Applies to: `textbox`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.

Example:
```json
{
    "controlId": "textbox-border-width",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### textbox-keep-layer-order

Actions:
- Sets **Keep layer order**.
- Applies to: `textbox`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "textbox-keep-layer-order",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### textbox-header-show

Actions:
- Sets **Header**.
- Applies to: `textbox`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "textbox-header-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### card-fill-custom-show

Actions:
- Sets **Custom fill**.
- Applies to: `cardVisual`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "card-fill-custom-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### card-label-show

Actions:
- Sets **Label**.
- Applies to: `cardVisual`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "card-label-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### card-label-color

Actions:
- Sets **Label color**.
- Applies to: `cardVisual`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.

Example:
```json
{
    "controlId": "card-label-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### card-value-color

Actions:
- Sets **Value color**.
- Applies to: `cardVisual`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.

Example:
```json
{
    "controlId": "card-value-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### card-value-font-size

Actions:
- Sets **Value font size**.
- Applies to: `cardVisual`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.

Example:
```json
{
    "controlId": "card-value-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### card-value-bold

Actions:
- Sets **Value bold**.
- Applies to: `cardVisual`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "card-value-bold",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### card-column-count

Actions:
- Sets **Column count**.
- Applies to: `cardVisual`.
- Accepted value: a whole JSON number, for example `1`, `2`, or `3`.

Example:
```json
{
    "controlId": "card-column-count",
    "value": 2,
    "type": "visual-editor-change"
}
```
<br>

### card-image-show

Actions:
- Sets **Image**.
- Applies to: `cardVisual`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "card-image-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### card-divider-show

Actions:
- Sets **Divider**.
- Applies to: `cardVisual`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "card-divider-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### image-url

Actions:
- Sets **Image URL**.
- Applies to: `image`.
- Accepted value: a quoted JSON string accepted by the target Power BI property.

Example:
```json
{
    "controlId": "image-url",
    "value": "Example",
    "type": "visual-editor-change"
}
```
<br>

### image-link-show

Actions:
- Sets **Visual link**.
- Applies to: `image`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).

Example:
```json
{
    "controlId": "image-link-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### image-link-type

Actions:
- Sets **Link type**.
- Applies to: `image`.
- Accepted value: a quoted JSON string accepted by the target Power BI property.

Example:
```json
{
    "controlId": "image-link-type",
    "value": "Example",
    "type": "visual-editor-change"
}
```
<br>

### general-title-alignment

Actions:
- Sets **Title alignment**.
- Applies to: all visual types.
- Accepted value: `left`, `center`, `right`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-title-alignment",
    "value": "left",
    "type": "visual-editor-change"
}
```
<br>

### general-title-font-size

Actions:
- Sets **Title font size**.
- Applies to: all visual types.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-title-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### general-title-font-family

Actions:
- Sets **Title font family**.
- Applies to: all visual types.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-title-font-family",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### general-background-show

Actions:
- Sets **Visual background**.
- Applies to: all visual types.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-background-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### general-border-show

Actions:
- Sets **Visual border**.
- Applies to: all visual types.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-border-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### general-visual-tooltip-font-size

Actions:
- Sets **Tooltip font size**.
- Applies to: all visual types.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-visual-tooltip-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### general-visual-tooltip-font-family

Actions:
- Sets **Tooltip font family**.
- Applies to: all visual types.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-visual-tooltip-font-family",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### general-visual-tooltip-title-color

Actions:
- Sets **Tooltip title color**.
- Applies to: all visual types.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-visual-tooltip-title-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### general-visual-tooltip-value-color

Actions:
- Sets **Tooltip value color**.
- Applies to: all visual types.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-visual-tooltip-value-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### general-header-pin-show

Actions:
- Sets **Pin icon**.
- Applies to: all visual types.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-header-pin-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### general-header-filter-show

Actions:
- Sets **Filter icon**.
- Applies to: all visual types.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-header-filter-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### general-header-smart-narrative-show

Actions:
- Sets **Smart narrative icon**.
- Applies to: all visual types.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-header-smart-narrative-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### general-header-icon-color

Actions:
- Sets **Header icon color**.
- Applies to: all visual types.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-header-icon-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### general-header-background-color

Actions:
- Sets **Header background color**.
- Applies to: all visual types.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-header-background-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### general-header-border-color

Actions:
- Sets **Header border color**.
- Applies to: all visual types.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "general-header-border-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### chart-label-font-size

Actions:
- Sets **Label font size**.
- Applies to: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`, `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`, `areaChart`, `stackedAreaChart`, `waterfallChart`, `ribbonChart`, `scatterChart`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "chart-label-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### chart-label-font-family

Actions:
- Sets **Label font family**.
- Applies to: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`, `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`, `areaChart`, `stackedAreaChart`, `waterfallChart`, `ribbonChart`, `scatterChart`.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "chart-label-font-family",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### chart-label-background-show

Actions:
- Sets **Label background**.
- Applies to: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`, `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`, `areaChart`, `stackedAreaChart`, `waterfallChart`, `ribbonChart`, `scatterChart`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "chart-label-background-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### chart-y-axis-title-show

Actions:
- Sets **Y-axis header**.
- Applies to: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`, `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`, `areaChart`, `stackedAreaChart`, `waterfallChart`, `ribbonChart`, `scatterChart`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "chart-y-axis-title-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### bar-y-axis-values-show

Actions:
- Sets **Bar Y-axis values**.
- Applies to: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bar-y-axis-values-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### line-y-axis-values-show

Actions:
- Sets **Line Y-axis values**.
- Applies to: `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "line-y-axis-values-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### line-y-axis-font-size

Actions:
- Sets **Line Y-axis font size**.
- Applies to: `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "line-y-axis-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### line-y-axis-font-family

Actions:
- Sets **Line Y-axis font family**.
- Applies to: `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "line-y-axis-font-family",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### line-y-axis-color

Actions:
- Sets **Line Y-axis color**.
- Applies to: `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "line-y-axis-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### chart-legend-show

Actions:
- Sets **Legend**.
- Applies to: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`, `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`, `areaChart`, `stackedAreaChart`, `waterfallChart`, `ribbonChart`, `scatterChart`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "chart-legend-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### chart-legend-position

Actions:
- Sets **Legend position**.
- Applies to: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`, `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`, `areaChart`, `stackedAreaChart`, `waterfallChart`, `ribbonChart`, `scatterChart`.
- Accepted value: `TopLeft`, `TopCenter`, `TopRight`, `BottomCenter`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "chart-legend-position",
    "value": "TopLeft",
    "type": "visual-editor-change"
}
```
<br>

### chart-legend-font-size

Actions:
- Sets **Legend font size**.
- Applies to: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`, `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`, `areaChart`, `stackedAreaChart`, `waterfallChart`, `ribbonChart`, `scatterChart`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "chart-legend-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### chart-legend-font-family

Actions:
- Sets **Legend font family**.
- Applies to: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`, `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`, `areaChart`, `stackedAreaChart`, `waterfallChart`, `ribbonChart`, `scatterChart`.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "chart-legend-font-family",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### chart-legend-title-show

Actions:
- Sets **Legend title**.
- Applies to: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`, `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`, `areaChart`, `stackedAreaChart`, `waterfallChart`, `ribbonChart`, `scatterChart`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "chart-legend-title-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### chart-gridlines-show

Actions:
- Sets **Gridlines**.
- Applies to: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`, `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`, `areaChart`, `stackedAreaChart`, `waterfallChart`, `ribbonChart`, `scatterChart`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "chart-gridlines-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### chart-category-gridlines-show

Actions:
- Sets **Category gridlines**.
- Applies to: `barChart`, `clusteredBarChart`, `columnChart`, `clusteredColumnChart`, `hundredPercentStackedBarChart`, `hundredPercentStackedColumnChart`, `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`, `areaChart`, `stackedAreaChart`, `waterfallChart`, `ribbonChart`, `scatterChart`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "chart-category-gridlines-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### line-style

Actions:
- Sets **Line style**.
- Applies to: `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`.
- Accepted value: `solid`, `dashed`, `dotted`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "line-style",
    "value": "solid",
    "type": "visual-editor-change"
}
```
<br>

### line-width

Actions:
- Sets **Line width**.
- Applies to: `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "line-width",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### line-interpolation

Actions:
- Sets **Line interpolation**.
- Applies to: `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`.
- Accepted value: `linear`, `smooth`, `step`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "line-interpolation",
    "value": "linear",
    "type": "visual-editor-change"
}
```
<br>

### line-smooth-type

Actions:
- Sets **Smooth type**.
- Applies to: `lineChart`, `lineStackedColumnComboChart`, `lineClusteredColumnComboChart`.
- Accepted value: `monotoneX`, `cardinal`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "line-smooth-type",
    "value": "monotoneX",
    "type": "visual-editor-change"
}
```
<br>

### slicer-height

Actions:
- Sets **Slicer height**.
- Applies to: `slicer`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-height",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### slicer-padding-top

Actions:
- Sets **Padding top**.
- Applies to: `slicer`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-padding-top",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### slicer-padding-right

Actions:
- Sets **Padding right**.
- Applies to: `slicer`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-padding-right",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### slicer-padding-bottom

Actions:
- Sets **Padding bottom**.
- Applies to: `slicer`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-padding-bottom",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### slicer-padding-left

Actions:
- Sets **Padding left**.
- Applies to: `slicer`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-padding-left",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### slicer-title-show

Actions:
- Sets **Slicer title**.
- Applies to: `slicer`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-title-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### slicer-header-font-size

Actions:
- Sets **Slicer header font size**.
- Applies to: `slicer`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-header-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### slicer-header-font-family

Actions:
- Sets **Slicer header font family**.
- Applies to: `slicer`.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-header-font-family",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### slicer-header-color

Actions:
- Sets **Slicer header color**.
- Applies to: `slicer`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-header-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### slicer-multi-select-without-control

Actions:
- Sets **Multi-select without Control**.
- Applies to: `slicer`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-multi-select-without-control",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### slicer-items-font-size

Actions:
- Sets **Slicer value font size**.
- Applies to: `slicer`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-items-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### slicer-items-font-family

Actions:
- Sets **Slicer value font family**.
- Applies to: `slicer`.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-items-font-family",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### slicer-items-color

Actions:
- Sets **Slicer value color**.
- Applies to: `slicer`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-items-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### slicer-items-background-color

Actions:
- Sets **Slicer value background**.
- Applies to: `slicer`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-items-background-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### slicer-dropdown-border-color

Actions:
- Sets **Dropdown border color**.
- Applies to: `slicer`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-dropdown-border-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### slicer-select-icon-color

Actions:
- Sets **Select icon color**.
- Applies to: `slicer`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "slicer-select-icon-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-height

Actions:
- Sets **Navigator height**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-height",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### bookmark-padding-top

Actions:
- Sets **Navigator padding top**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-padding-top",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### bookmark-padding-right

Actions:
- Sets **Navigator padding right**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-padding-right",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### bookmark-padding-bottom

Actions:
- Sets **Navigator padding bottom**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-padding-bottom",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### bookmark-padding-left

Actions:
- Sets **Navigator padding left**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-padding-left",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### bookmark-background-show

Actions:
- Sets **Navigator background**.
- Applies to: `bookmarkNavigator`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-background-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### bookmark-shape

Actions:
- Sets **Navigator shape**.
- Applies to: `bookmarkNavigator`.
- Accepted value: `rectangle`, `roundedRectangle`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-shape",
    "value": "rectangle",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-corner-radius

Actions:
- Sets **Navigator corner radius**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-corner-radius",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### bookmark-default-text-font-size

Actions:
- Sets **Default text font size**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- Selector/state: `non-selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-default-text-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### bookmark-default-text-font-family

Actions:
- Sets **Default text font family**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.
- Selector/state: `non-selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-default-text-font-family",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-default-text-color

Actions:
- Sets **Default text color**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- Selector/state: `non-selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-default-text-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-default-text-vertical-alignment

Actions:
- Sets **Default vertical alignment**.
- Applies to: `bookmarkNavigator`.
- Accepted value: `middle`, `top`, `bottom`.
- Selector/state: `non-selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-default-text-vertical-alignment",
    "value": "middle",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-default-text-horizontal-alignment

Actions:
- Sets **Default horizontal alignment**.
- Applies to: `bookmarkNavigator`.
- Accepted value: `middle`, `left`, `right`.
- Selector/state: `non-selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-default-text-horizontal-alignment",
    "value": "middle",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-default-fill-color

Actions:
- Sets **Default fill color**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- Selector/state: `non-selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-default-fill-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-default-border-width

Actions:
- Sets **Default border width**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- Selector/state: `non-selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-default-border-width",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### bookmark-default-border-color

Actions:
- Sets **Default border color**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- Selector/state: `non-selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-default-border-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-selected-text-font-size

Actions:
- Sets **Selected text font size**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- Selector/state: `selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-selected-text-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### bookmark-selected-text-font-family

Actions:
- Sets **Selected text font family**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.
- Selector/state: `selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-selected-text-font-family",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-selected-text-color

Actions:
- Sets **Selected text color**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- Selector/state: `selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-selected-text-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-selected-text-vertical-alignment

Actions:
- Sets **Selected vertical alignment**.
- Applies to: `bookmarkNavigator`.
- Accepted value: `middle`, `top`, `bottom`.
- Selector/state: `selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-selected-text-vertical-alignment",
    "value": "middle",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-selected-text-horizontal-alignment

Actions:
- Sets **Selected horizontal alignment**.
- Applies to: `bookmarkNavigator`.
- Accepted value: `middle`, `left`, `right`.
- Selector/state: `selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-selected-text-horizontal-alignment",
    "value": "middle",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-selected-fill-color

Actions:
- Sets **Selected fill color**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- Selector/state: `selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-selected-fill-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### bookmark-selected-border-width

Actions:
- Sets **Selected border width**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- Selector/state: `selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-selected-border-width",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### bookmark-selected-border-color

Actions:
- Sets **Selected border color**.
- Applies to: `bookmarkNavigator`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- Selector/state: `selected`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "bookmark-selected-border-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### textbox-text-font-size

Actions:
- Sets **Text font size**.
- Applies to: `textbox`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "textbox-text-font-size",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### textbox-text-font-family

Actions:
- Sets **Text font family**.
- Applies to: `textbox`.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "textbox-text-font-family",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### textbox-text-color

Actions:
- Sets **Text color**.
- Applies to: `textbox`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "textbox-text-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### textbox-background-show

Actions:
- Sets **Text background**.
- Applies to: `textbox`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "textbox-background-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### card-accent-bar-show

Actions:
- Sets **Accent bar**.
- Applies to: `cardVisual`.
- Accepted value: `true` or `false` (JSON Boolean, not a quoted string).
- Selector/state: `default`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "card-accent-bar-show",
    "value": true,
    "type": "visual-editor-change"
}
```
<br>

### card-accent-bar-position

Actions:
- Sets **Accent bar position**.
- Applies to: `cardVisual`.
- Accepted value: `Left`, `Right`.
- Selector/state: `default`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "card-accent-bar-position",
    "value": "Left",
    "type": "visual-editor-change"
}
```
<br>

### card-accent-bar-width

Actions:
- Sets **Accent bar width**.
- Applies to: `cardVisual`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- Selector/state: `default`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "card-accent-bar-width",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### card-accent-bar-color

Actions:
- Sets **Accent bar color**.
- Applies to: `cardVisual`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- Selector/state: `default`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "card-accent-bar-color",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### card-value-font-size-standard

Actions:
- Sets **Card value font size**.
- Applies to: `cardVisual`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "card-value-font-size-standard",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### card-value-font-family-standard

Actions:
- Sets **Card value font family**.
- Applies to: `cardVisual`.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "card-value-font-family-standard",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### card-value-color-standard

Actions:
- Sets **Card value color**.
- Applies to: `cardVisual`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "card-value-color-standard",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

### card-label-position-bottom

Actions:
- Sets **Card label position**.
- Applies to: `cardVisual`.
- Accepted value: `belowValue`, `aboveValue`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "card-label-position-bottom",
    "value": "belowValue",
    "type": "visual-editor-change"
}
```
<br>

### card-label-font-size-standard

Actions:
- Sets **Card label font size**.
- Applies to: `cardVisual`.
- Accepted value: a JSON number, integer or decimal as appropriate to the property.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "card-label-font-size-standard",
    "value": 12,
    "type": "visual-editor-change"
}
```
<br>

### card-label-font-family-standard

Actions:
- Sets **Card label font family**.
- Applies to: `cardVisual`.
- Accepted value: a quoted text value; the macro implementation serializes it as a Power BI literal string.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "card-label-font-family-standard",
    "value": "Example text",
    "type": "visual-editor-change"
}
```
<br>

### card-label-color-standard

Actions:
- Sets **Card label color**.
- Applies to: `cardVisual`.
- Accepted value: a quoted hexadecimal color string, for example `"#01B8AA"`.
- The catalog allows the target JSON path to be created when it is missing.

Example:
```json
{
    "controlId": "card-label-color-standard",
    "value": "#01B8AA",
    "type": "visual-editor-change"
}
```
<br>

## Catalog behavior notes

- `list_controls()` starts with the built-in controls and, when a content root is configured, also loads `visual-editor/**/*.json`.
- External control files may be either a top-level list or an object containing a `controls` list.
- Duplicate IDs are resolved by ID, with the last loaded definition winning. This means a content-file definition can override a built-in control with the same ID.
- Invalid JSON files and malformed control entries are skipped.
- Paths can contain string keys and integer list indexes. Empty or malformed paths are ignored.
- `createsMissingPath` defaults to `false` for controls loaded from content files. The `_format_control(...)` helper defaults it to `true`.