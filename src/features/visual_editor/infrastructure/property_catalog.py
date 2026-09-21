from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from features.visual_editor.domain.models import VisualEditorControl


class VisualPropertyCatalog:
    """Loads allowlisted visual editor controls from content files and built-ins."""

    BUILTIN_CONTROLS = [
        VisualEditorControl("general-title-text", "Title text", "General", "text", "powerBiLiteralString", paths=[["visual", "visualContainerObjects", "title", 0, "properties", "text", "expr", "Literal", "Value"], ["Title"], ["title"]]),
        VisualEditorControl("general-title-font-color", "Title font color", "General", "color", "hexColor", paths=[["visual", "visualContainerObjects", "title", 0, "properties", "fontColor", "solid", "color"]]),
        VisualEditorControl("general-background-color", "Background color", "General", "color", "hexColor", paths=[["visual", "visualContainerObjects", "background", 0, "properties", "color", "solid", "color"]]),
        VisualEditorControl("general-background-transparency", "Background transparency", "General", "slider", "percentage", paths=[["visual", "visualContainerObjects", "background", 0, "properties", "transparency"]]),
        VisualEditorControl("general-hidden", "Hidden", "General", "boolean", "boolean", paths=[["isHidden"]]),
        VisualEditorControl("bar-data-color", "Bar color", "General", "color", "hexColor", ["bar", "barChart", "clusteredBarChart", "columnChart", "clusteredColumnChart"], paths=[
            ["visual", "objects", "dataPoint", 0, "properties", "fill"],
        ]),
        VisualEditorControl("bar-value-axis-show", "Value axis", "General", "boolean", "boolean", ["barChart"], paths=[
            ["visual", "objects", "valueAxis", 0, "properties", "show"],
        ]),
        VisualEditorControl("bar-category-axis-color", "Category label color", "General", "color", "hexColor", ["barChart"], paths=[
            ["visual", "objects", "categoryAxis", 0, "properties", "labelColor"],
        ]),
        VisualEditorControl("bar-label-font-size", "Label font size", "General", "number", "number", ["barChart"], paths=[
            ["visual", "objects", "labels", 0, "properties", "fontSize"],
        ]),
        VisualEditorControl("bar-legend-show", "Legend", "General", "boolean", "boolean", ["barChart"], paths=[
            ["visual", "objects", "legend", 0, "properties", "show"],
        ]),
        VisualEditorControl("bar-totals-show", "Totals", "General", "boolean", "boolean", ["barChart"], paths=[
            ["visual", "objects", "totals", 0, "properties", "show"],
        ]),
        VisualEditorControl("pie-slice-color", "Pie slice color", "General", "color", "hexColor", ["pieChart", "donutChart"]),
        VisualEditorControl("line-color", "Line color", "General", "color", "hexColor", ["lineChart"]),
        VisualEditorControl("table-text-size", "Table text size", "General", "number", "number", ["table", "pivotTable", "matrix"], paths=[["visual", "objects", "values", 0, "properties", "fontSize"], ["visual", "objects", "values", 0, "properties", "textSize"], ["visual", "objects", "columnHeaders", 0, "properties", "fontSize"], ["visual", "objects", "columnHeaders", 0, "properties", "textSize"]]),
        VisualEditorControl("slicer-background-transparency", "Slicer background transparency", "General", "slider", "percentage", ["slicer"], paths=[
            ["visual", "visualContainerObjects", "background", 0, "properties", "transparency"],
        ]),
        VisualEditorControl("slicer-mode", "Mode", "General", "text", "string", ["slicer"], paths=[
            ["visual", "objects", "data", 0, "properties", "mode"],
        ]),
        VisualEditorControl("slicer-single-select", "Single select", "General", "boolean", "boolean", ["slicer"], paths=[
            ["visual", "objects", "selection", 0, "properties", "singleSelect"],
        ]),
        VisualEditorControl("slicer-select-all", "Select all checkbox", "General", "boolean", "boolean", ["slicer"], paths=[
            ["visual", "objects", "selection", 0, "properties", "selectAllCheckboxEnabled"],
        ]),
        VisualEditorControl("slicer-items-font-color", "Items font color", "General", "color", "hexColor", ["slicer"], paths=[
            ["visual", "objects", "items", 0, "properties", "fontColor"],
        ]),
        VisualEditorControl("slicer-items-text-size", "Items text size", "General", "number", "number", ["slicer"], paths=[
            ["visual", "objects", "items", 0, "properties", "textSize"],
        ]),
        VisualEditorControl("slicer-header-text", "Header text", "General", "text", "powerBiLiteralString", ["slicer"], paths=[
            ["visual", "objects", "header", 0, "properties", "text"],
        ]),
        VisualEditorControl("shape-type", "Shape type", "General", "text", "string", ["shape"], paths=[
            ["visual", "objects", "shape", 0, "properties", "tileShape"],
        ]),
        VisualEditorControl("shape-rotation", "Rotation angle", "General", "number", "number", ["shape"], paths=[
            ["visual", "objects", "rotation", 0, "properties", "shapeAngle"],
        ]),
        VisualEditorControl("shape-fill-color", "Fill color", "General", "color", "hexColor", ["shape"], paths=[
            ["visual", "objects", "fill", 0, "properties", "fillColor"],
        ]),
        VisualEditorControl("shape-fill-transparency", "Fill transparency", "General", "slider", "percentage", ["shape"], paths=[
            ["visual", "objects", "fill", 0, "properties", "transparency"],
        ]),
        VisualEditorControl("shape-outline-show", "Outline", "General", "boolean", "boolean", ["shape"], paths=[
            ["visual", "objects", "outline", 0, "properties", "show"],
        ]),
        VisualEditorControl("gauge-axis-min", "Axis minimum", "General", "number", "number", ["gauge"], paths=[
            ["visual", "objects", "axis", 0, "properties", "min"],
        ]),
        VisualEditorControl("gauge-axis-max", "Axis maximum", "General", "number", "number", ["gauge"], paths=[
            ["visual", "objects", "axis", 0, "properties", "max"],
        ]),
        VisualEditorControl("gauge-label-color", "Label color", "General", "color", "hexColor", ["gauge"], paths=[
            ["visual", "objects", "labels", 0, "properties", "color"],
        ]),
        VisualEditorControl("gauge-label-font-size", "Label font size", "General", "number", "number", ["gauge"], paths=[
            ["visual", "objects", "labels", 0, "properties", "fontSize"],
        ]),
        VisualEditorControl("gauge-target-show", "Target", "General", "boolean", "boolean", ["gauge"], paths=[
            ["visual", "objects", "target", 0, "properties", "show"],
        ]),
        VisualEditorControl("gauge-callout-color", "Callout color", "General", "color", "hexColor", ["gauge"], paths=[
            ["visual", "objects", "calloutValue", 0, "properties", "color"],
        ]),
        VisualEditorControl("gauge-callout-show", "Callout", "General", "boolean", "boolean", ["gauge"], paths=[
            ["visual", "objects", "calloutValue", 0, "properties", "show"],
        ]),
        VisualEditorControl("textbox-border-show", "Border", "General", "boolean", "boolean", ["textbox"], paths=[
            ["visual", "visualContainerObjects", "border", 0, "properties", "show"],
        ]),
        VisualEditorControl("textbox-border-width", "Border width", "General", "number", "number", ["textbox"], paths=[
            ["visual", "visualContainerObjects", "border", 0, "properties", "width"],
        ]),
        VisualEditorControl("textbox-keep-layer-order", "Keep layer order", "General", "boolean", "boolean", ["textbox"], paths=[
            ["visual", "visualContainerObjects", "general", 0, "properties", "keepLayerOrder"],
        ]),
        VisualEditorControl("textbox-header-show", "Header", "General", "boolean", "boolean", ["textbox"], paths=[
            ["visual", "visualContainerObjects", "visualHeader", 0, "properties", "show"],
        ]),
        VisualEditorControl("card-fill-custom-show", "Custom fill", "General", "boolean", "boolean", ["cardVisual"], paths=[
            ["visual", "objects", "fillCustom", 0, "properties", "show"],
        ]),
        VisualEditorControl("card-label-show", "Label", "General", "boolean", "boolean", ["cardVisual"], paths=[
            ["visual", "objects", "label", 0, "properties", "show"],
        ]),
        VisualEditorControl("card-label-color", "Label color", "General", "color", "hexColor", ["cardVisual"], paths=[
            ["visual", "objects", "label", 0, "properties", "fontColor"],
        ]),
        VisualEditorControl("card-value-color", "Value color", "General", "color", "hexColor", ["cardVisual"], paths=[
            ["visual", "objects", "value", 0, "properties", "fontColor"],
        ]),
        VisualEditorControl("card-value-font-size", "Value font size", "General", "number", "number", ["cardVisual"], paths=[
            ["visual", "objects", "value", 0, "properties", "fontSize"],
        ]),
        VisualEditorControl("card-value-bold", "Value bold", "General", "boolean", "boolean", ["cardVisual"], paths=[
            ["visual", "objects", "value", 0, "properties", "bold"],
        ]),
        VisualEditorControl("card-column-count", "Column count", "General", "number", "integer", ["cardVisual"], paths=[
            ["visual", "objects", "layout", 0, "properties", "columnCount"],
        ]),
        VisualEditorControl("card-image-show", "Image", "General", "boolean", "boolean", ["cardVisual"], paths=[
            ["visual", "objects", "image", 0, "properties", "show"],
        ]),
        VisualEditorControl("card-divider-show", "Divider", "General", "boolean", "boolean", ["cardVisual"], paths=[
            ["visual", "objects", "divider", 0, "properties", "show"],
        ]),
        VisualEditorControl("image-url", "Image URL", "General", "text", "string", ["image"], paths=[
            ["visual", "objects", "general", 0, "properties", "imageUrl"],
        ]),
        VisualEditorControl("image-link-show", "Visual link", "General", "boolean", "boolean", ["image"], paths=[
            ["visual", "visualContainerObjects", "visualLink", 0, "properties", "show"],
        ]),
        VisualEditorControl("image-link-type", "Link type", "General", "text", "string", ["image"], paths=[
            ["visual", "visualContainerObjects", "visualLink", 0, "properties", "type"],
        ]),
    ]

    def __init__(self, content_root: Path | None = None) -> None:
        self._content_root = content_root

    def list_controls(self) -> list[VisualEditorControl]:
        controls = list(self.BUILTIN_CONTROLS)
        if self._content_root is None:
            return controls
        folder = self._content_root / "visual-editor"
        if not folder.exists() or not folder.is_dir():
            return controls
        for path in sorted(folder.rglob("*.json"), key=lambda item: str(item).casefold()):
            controls.extend(self._load_file(path))
        return self._dedupe(controls)

    def _load_file(self, path: Path) -> list[VisualEditorControl]:
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            return []
        raw_controls: list[Any]
        if isinstance(data, list):
            raw_controls = data
        elif isinstance(data, dict) and isinstance(data.get("controls"), list):
            raw_controls = data["controls"]
        else:
            return []
        controls: list[VisualEditorControl] = []
        for item in raw_controls:
            if not isinstance(item, dict):
                continue
            control_id = str(item.get("id", "")).strip()
            label = str(item.get("label", "")).strip()
            # The UI has one unified General category; type-specific controls are
            # grouped and collapsed by visual type in the presentation layer.
            category = "General"
            control = str(item.get("control", "text")).strip() or "text"
            value_type = str(item.get("valueType", "string")).strip() or "string"
            if not control_id or not label:
                continue
            visual_types = item.get("visualTypes", ["*"])
            options = item.get("options", [])
            paths = item.get("paths", [])
            controls.append(
                VisualEditorControl(
                    id=control_id,
                    label=label,
                    category=category,
                    control=control,
                    value_type=value_type,
                    visual_types=[str(value) for value in visual_types] if isinstance(visual_types, list) else ["*"],
                    options=[str(value) for value in options] if isinstance(options, list) else [],
                    paths=self._normalize_paths(paths),
                    creates_missing_path=bool(item.get("createsMissingPath", False)),
                    description=str(item.get("description", "")),
                    group_path=[str(value) for value in item.get("groupPath", [])] if isinstance(item.get("groupPath", []), list) else [],
                    selector_id=str(item.get("selectorId", "")).strip(),
                )
            )
        return controls

    @staticmethod
    def _normalize_paths(paths: Any) -> list[list[str | int]]:
        if not isinstance(paths, list):
            return []
        normalized: list[list[str | int]] = []
        for raw_path in paths:
            if not isinstance(raw_path, list):
                continue
            parts: list[str | int] = []
            for part in raw_path:
                if isinstance(part, int):
                    parts.append(part)
                elif isinstance(part, str):
                    parts.append(part)
            if parts:
                normalized.append(parts)
        return normalized

    @staticmethod
    def _dedupe(controls: list[VisualEditorControl]) -> list[VisualEditorControl]:
        by_id: dict[str, VisualEditorControl] = {}
        for control in controls:
            by_id[control.id] = control
        return list(by_id.values())


# Formatting controls used by the standard visual-formatting macro.  They are
# data-only catalog entries so the same controls are available interactively
# and through a visual-editor-change macro step.
_ALL = ["*"]
_CHARTS = [
    "barChart", "clusteredBarChart", "columnChart", "clusteredColumnChart",
    "hundredPercentStackedBarChart", "hundredPercentStackedColumnChart",
    "lineChart", "lineStackedColumnComboChart", "lineClusteredColumnComboChart",
    "areaChart", "stackedAreaChart", "waterfallChart", "ribbonChart", "scatterChart",
]
_BARS = [
    "barChart", "clusteredBarChart", "columnChart", "clusteredColumnChart",
    "hundredPercentStackedBarChart", "hundredPercentStackedColumnChart",
]
_LINES = ["lineChart", "lineStackedColumnComboChart", "lineClusteredColumnComboChart"]


def _format_control(
    control_id: str,
    label: str,
    control: str,
    value_type: str,
    visual_types: list[str],
    paths: list[list[str | int]],
    *,
    options: list[str] | None = None,
    group: str,
    creates_missing_path: bool = True,
    selector_id: str = "",
) -> VisualEditorControl:
    return VisualEditorControl(
        id=control_id,
        label=label,
        category="General",
        control=control,
        value_type=value_type,
        visual_types=visual_types,
        options=options or [],
        paths=paths,
        creates_missing_path=creates_missing_path,
        group_path=[group],
        selector_id=selector_id,
    )


VisualPropertyCatalog.BUILTIN_CONTROLS.extend([
    _format_control("general-title-alignment", "Title alignment", "text", "enum", _ALL,
                    [["visual", "visualContainerObjects", "title", 0, "properties", "alignment"]],
                    options=["left", "center", "right"], group="All visuals"),
    _format_control("general-title-font-size", "Title font size", "number", "number", _ALL,
                    [["visual", "visualContainerObjects", "title", 0, "properties", "fontSize"]], group="All visuals"),
    _format_control("general-title-font-family", "Title font family", "text", "powerBiLiteralString", _ALL,
                    [["visual", "visualContainerObjects", "title", 0, "properties", "fontFamily"]], group="All visuals"),
    _format_control("general-background-show", "Visual background", "boolean", "boolean", _ALL,
                    [["visual", "visualContainerObjects", "background", 0, "properties", "show"]], group="All visuals"),
    _format_control("general-border-show", "Visual border", "boolean", "boolean", _ALL,
                    [["visual", "visualContainerObjects", "border", 0, "properties", "show"]], group="All visuals"),
    _format_control("general-visual-tooltip-font-size", "Tooltip font size", "number", "number", _ALL,
                    [["visual", "visualContainerObjects", "visualTooltip", 0, "properties", "fontSize"]], group="All visuals"),
    _format_control("general-visual-tooltip-font-family", "Tooltip font family", "text", "powerBiLiteralString", _ALL,
                    [["visual", "visualContainerObjects", "visualTooltip", 0, "properties", "fontFamily"]], group="All visuals"),
    _format_control("general-visual-tooltip-title-color", "Tooltip title color", "color", "hexColor", _ALL,
                    [["visual", "visualContainerObjects", "visualTooltip", 0, "properties", "titleFontColor"]], group="All visuals"),
    _format_control("general-visual-tooltip-value-color", "Tooltip value color", "color", "hexColor", _ALL,
                    [["visual", "visualContainerObjects", "visualTooltip", 0, "properties", "valueFontColor"]], group="All visuals"),
    _format_control("general-header-pin-show", "Pin icon", "boolean", "boolean", _ALL,
                    [["visual", "visualContainerObjects", "visualHeader", 0, "properties", "showPinButton"]], group="All visuals"),
    _format_control("general-header-filter-show", "Filter icon", "boolean", "boolean", _ALL,
                    [["visual", "visualContainerObjects", "visualHeader", 0, "properties", "showFilterRestatementButton"]], group="All visuals"),
    _format_control("general-header-smart-narrative-show", "Smart narrative icon", "boolean", "boolean", _ALL,
                    [["visual", "visualContainerObjects", "visualHeader", 0, "properties", "showSmartNarrativeButton"]], group="All visuals"),
    _format_control("general-header-icon-color", "Header icon color", "color", "hexColor", _ALL,
                    [["visual", "visualContainerObjects", "visualHeader", 0, "properties", "foreground"]], group="All visuals"),
    _format_control("general-header-background-color", "Header background color", "color", "hexColor", _ALL,
                    [["visual", "visualContainerObjects", "visualHeader", 0, "properties", "background"]], group="All visuals"),
    _format_control("general-header-border-color", "Header border color", "color", "hexColor", _ALL,
                    [["visual", "visualContainerObjects", "visualHeader", 0, "properties", "border"]], group="All visuals"),

    _format_control("chart-label-font-size", "Label font size", "number", "number", _CHARTS,
                    [["visual", "objects", "labels", i, "properties", "fontSize"] for i in range(3)], group="Charts"),
    _format_control("chart-label-font-family", "Label font family", "text", "powerBiLiteralString", _CHARTS,
                    [["visual", "objects", "labels", i, "properties", "fontFamily"] for i in range(3)], group="Charts"),
    _format_control("chart-label-background-show", "Label background", "boolean", "boolean", _CHARTS,
                    [["visual", "objects", "labels", i, "properties", "enableBackground"] for i in range(3)], group="Charts"),
    _format_control("chart-y-axis-title-show", "Y-axis header", "boolean", "boolean", _CHARTS,
                    [["visual", "objects", "valueAxis", 0, "properties", "showAxisTitle"],
                     ["visual", "objects", "categoryAxis", 0, "properties", "showAxisTitle"]], group="Charts"),
    _format_control("bar-y-axis-values-show", "Bar Y-axis values", "boolean", "boolean", _BARS,
                    [["visual", "objects", "valueAxis", 0, "properties", "show"]], group="Charts"),
    _format_control("line-y-axis-values-show", "Line Y-axis values", "boolean", "boolean", _LINES,
                    [["visual", "objects", "valueAxis", 0, "properties", "show"]], group="Charts"),
    _format_control("line-y-axis-font-size", "Line Y-axis font size", "number", "number", _LINES,
                    [["visual", "objects", "valueAxis", 0, "properties", "fontSize"]], group="Charts"),
    _format_control("line-y-axis-font-family", "Line Y-axis font family", "text", "powerBiLiteralString", _LINES,
                    [["visual", "objects", "valueAxis", 0, "properties", "fontFamily"]], group="Charts"),
    _format_control("line-y-axis-color", "Line Y-axis color", "color", "hexColor", _LINES,
                    [["visual", "objects", "valueAxis", 0, "properties", "labelColor"]], group="Charts"),
    _format_control("chart-legend-show", "Legend", "boolean", "boolean", _CHARTS,
                    [["visual", "objects", "legend", 0, "properties", "show"]], group="Charts"),
    _format_control("chart-legend-position", "Legend position", "text", "enum", _CHARTS,
                    [["visual", "objects", "legend", 0, "properties", "position"]],
                    options=["Top", "Left", "Right", "Bottom", "TopLeft", "TopCenter", "TopRight", "BottomCenter"], group="Charts"),
    _format_control("chart-legend-font-size", "Legend font size", "number", "number", _CHARTS,
                    [["visual", "objects", "legend", 0, "properties", "fontSize"]], group="Charts"),
    _format_control("chart-legend-font-family", "Legend font family", "text", "powerBiLiteralString", _CHARTS,
                    [["visual", "objects", "legend", 0, "properties", "fontFamily"]], group="Charts"),
    _format_control("chart-legend-title-show", "Legend title", "boolean", "boolean", _CHARTS,
                    [["visual", "objects", "legend", 0, "properties", "showTitle"]], group="Charts"),
    _format_control("chart-gridlines-show", "Gridlines", "boolean", "boolean", _CHARTS,
                    [["visual", "objects", "valueAxis", 0, "properties", "showGridlines"]], group="Charts"),
    _format_control("chart-category-gridlines-show", "Category gridlines", "boolean", "boolean", _CHARTS,
                    [["visual", "objects", "categoryAxis", 0, "properties", "showGridlines"]], group="Charts"),
    _format_control("line-style", "Line style", "text", "enum", _LINES,
                    [["visual", "objects", "lineStyles", 0, "properties", "lineStyle"],
                     ["visual", "objects", "dataPoint", 0, "properties", "lineStyle"]],
                    options=["solid", "dashed", "dotted"], group="Charts"),
    _format_control("line-width", "Line width", "number", "number", _LINES,
                    [["visual", "objects", "lineStyles", 0, "properties", "strokeWidth"],
                     ["visual", "objects", "dataPoint", 0, "properties", "strokeWidth"]], group="Charts"),
    _format_control("line-interpolation", "Line interpolation", "text", "enum", _LINES,
                    [["visual", "objects", "lineStyles", 0, "properties", "lineChartType"],
                     ["visual", "objects", "dataPoint", 0, "properties", "lineChartType"]],
                    options=["linear", "smooth", "step"], group="Charts"),
    _format_control("line-smooth-type", "Smooth type", "text", "enum", _LINES,
                    [["visual", "objects", "lineStyles", 0, "properties", "interpolationSmooth"],
                     ["visual", "objects", "dataPoint", 0, "properties", "interpolationSmooth"]],
                    options=["monotoneX", "cardinal"], group="Charts"),

    _format_control("slicer-height", "Slicer height", "number", "number", ["slicer"],
                    [["position", "height"]], group="Slicer"),
    _format_control("slicer-padding-top", "Padding top", "number", "number", ["slicer"],
                    [["visual", "visualContainerObjects", "padding", 0, "properties", "top"],
                     ["visual", "objects", "padding", 0, "properties", "top"]], group="Slicer"),
    _format_control("slicer-padding-right", "Padding right", "number", "number", ["slicer"],
                    [["visual", "visualContainerObjects", "padding", 0, "properties", "right"],
                     ["visual", "objects", "padding", 0, "properties", "right"]], group="Slicer"),
    _format_control("slicer-padding-bottom", "Padding bottom", "number", "number", ["slicer"],
                    [["visual", "visualContainerObjects", "padding", 0, "properties", "bottom"],
                     ["visual", "objects", "padding", 0, "properties", "bottom"]], group="Slicer"),
    _format_control("slicer-padding-left", "Padding left", "number", "number", ["slicer"],
                    [["visual", "visualContainerObjects", "padding", 0, "properties", "left"],
                     ["visual", "objects", "padding", 0, "properties", "left"]], group="Slicer"),
    _format_control("slicer-title-show", "Slicer title", "boolean", "boolean", ["slicer"],
                    [["visual", "visualContainerObjects", "title", 0, "properties", "show"]], group="Slicer"),
    _format_control("slicer-header-font-size", "Slicer header font size", "number", "number", ["slicer"],
                    [["visual", "objects", "header", 0, "properties", "textSize"]], group="Slicer"),
    _format_control("slicer-header-font-family", "Slicer header font family", "text", "powerBiLiteralString", ["slicer"],
                    [["visual", "objects", "header", 0, "properties", "fontFamily"]], group="Slicer"),
    _format_control("slicer-header-color", "Slicer header color", "color", "hexColor", ["slicer"],
                    [["visual", "objects", "header", 0, "properties", "fontColor"]], group="Slicer"),
    _format_control("slicer-multi-select-without-control", "Multi-select without Control", "boolean", "boolean", ["slicer"],
                    [["visual", "objects", "selection", 0, "properties", "multiSelectWithCtrl"],
                     ["visual", "objects", "selection", 0, "properties", "multiSelectWithControl"]], group="Slicer"),
    _format_control("slicer-items-font-size", "Slicer value font size", "number", "number", ["slicer"],
                    [["visual", "objects", "items", 0, "properties", "textSize"]], group="Slicer"),
    _format_control("slicer-items-font-family", "Slicer value font family", "text", "powerBiLiteralString", ["slicer"],
                    [["visual", "objects", "items", 0, "properties", "fontFamily"]], group="Slicer"),
    _format_control("slicer-items-color", "Slicer value color", "color", "hexColor", ["slicer"],
                    [["visual", "objects", "items", 0, "properties", "fontColor"]], group="Slicer"),
    _format_control("slicer-items-background-color", "Slicer value background", "color", "hexColor", ["slicer"],
                    [["visual", "objects", "items", 0, "properties", "background"]], group="Slicer"),
    _format_control("slicer-dropdown-border-color", "Dropdown border color", "color", "hexColor", ["slicer"],
                    [["visual", "visualContainerObjects", "border", 0, "properties", "color"],
                     ["visual", "objects", "dropdown", 0, "properties", "borderColor"]], group="Slicer"),
    _format_control("slicer-select-icon-color", "Select icon color", "color", "hexColor", ["slicer"],
                    [["visual", "objects", "selection", 0, "properties", "selectIconColor"],
                     ["visual", "objects", "general", 0, "properties", "selectIconColor"]], group="Slicer"),

    _format_control("bookmark-height", "Navigator height", "number", "number", ["bookmarkNavigator"],
                    [["position", "height"]], group="Bookmark navigator"),
    _format_control("bookmark-padding-top", "Navigator padding top", "number", "number", ["bookmarkNavigator"],
                    [["visual", "visualContainerObjects", "padding", 0, "properties", "top"]], group="Bookmark navigator"),
    _format_control("bookmark-padding-right", "Navigator padding right", "number", "number", ["bookmarkNavigator"],
                    [["visual", "visualContainerObjects", "padding", 0, "properties", "right"]], group="Bookmark navigator"),
    _format_control("bookmark-padding-bottom", "Navigator padding bottom", "number", "number", ["bookmarkNavigator"],
                    [["visual", "visualContainerObjects", "padding", 0, "properties", "bottom"]], group="Bookmark navigator"),
    _format_control("bookmark-padding-left", "Navigator padding left", "number", "number", ["bookmarkNavigator"],
                    [["visual", "visualContainerObjects", "padding", 0, "properties", "left"]], group="Bookmark navigator"),
    _format_control("bookmark-background-show", "Navigator background", "boolean", "boolean", ["bookmarkNavigator"],
                    [["visual", "visualContainerObjects", "background", 0, "properties", "show"]], group="Bookmark navigator"),
    _format_control("bookmark-shape", "Navigator shape", "text", "enum", ["bookmarkNavigator"],
                    [["visual", "objects", "shape", 0, "properties", "tileShape"]],
                    options=["rectangle", "roundedRectangle"], group="Bookmark navigator"),
    _format_control("bookmark-corner-radius", "Navigator corner radius", "number", "number", ["bookmarkNavigator"],
                    [["visual", "visualContainerObjects", "border", 0, "properties", "radius"]], group="Bookmark navigator"),

    _format_control("bookmark-default-text-font-size", "Default text font size", "number", "number", ["bookmarkNavigator"],
                    [["visual", "objects", "text", 0, "properties", "fontSize"]], group="Bookmark navigator", selector_id="non-selected"),
    _format_control("bookmark-default-text-font-family", "Default text font family", "text", "powerBiLiteralString", ["bookmarkNavigator"],
                    [["visual", "objects", "text", 0, "properties", "fontFamily"]], group="Bookmark navigator", selector_id="non-selected"),
    _format_control("bookmark-default-text-color", "Default text color", "color", "hexColor", ["bookmarkNavigator"],
                    [["visual", "objects", "text", 0, "properties", "fontColor"]], group="Bookmark navigator", selector_id="non-selected"),
    _format_control("bookmark-default-text-vertical-alignment", "Default vertical alignment", "text", "enum", ["bookmarkNavigator"],
                    [["visual", "objects", "text", 0, "properties", "verticalAlignment"]], options=["middle", "top", "bottom"], group="Bookmark navigator", selector_id="non-selected"),
    _format_control("bookmark-default-text-horizontal-alignment", "Default horizontal alignment", "text", "enum", ["bookmarkNavigator"],
                    [["visual", "objects", "text", 0, "properties", "horizontalAlignment"]], options=["middle", "left", "right"], group="Bookmark navigator", selector_id="non-selected"),
    _format_control("bookmark-default-fill-color", "Default fill color", "color", "hexColor", ["bookmarkNavigator"],
                    [["visual", "objects", "fill", 0, "properties", "fillColor"]], group="Bookmark navigator", selector_id="non-selected"),
    _format_control("bookmark-default-border-width", "Default border width", "number", "number", ["bookmarkNavigator"],
                    [["visual", "objects", "outline", 0, "properties", "width"], ["visual", "objects", "border", 0, "properties", "width"]], group="Bookmark navigator", selector_id="non-selected"),
    _format_control("bookmark-default-border-color", "Default border color", "color", "hexColor", ["bookmarkNavigator"],
                    [["visual", "objects", "outline", 0, "properties", "color"], ["visual", "objects", "border", 0, "properties", "color"]], group="Bookmark navigator", selector_id="non-selected"),
    _format_control("bookmark-selected-text-font-size", "Selected text font size", "number", "number", ["bookmarkNavigator"],
                    [["visual", "objects", "text", 0, "properties", "fontSize"]], group="Bookmark navigator", selector_id="selected"),
    _format_control("bookmark-selected-text-font-family", "Selected text font family", "text", "powerBiLiteralString", ["bookmarkNavigator"],
                    [["visual", "objects", "text", 0, "properties", "fontFamily"]], group="Bookmark navigator", selector_id="selected"),
    _format_control("bookmark-selected-text-color", "Selected text color", "color", "hexColor", ["bookmarkNavigator"],
                    [["visual", "objects", "text", 0, "properties", "fontColor"]], group="Bookmark navigator", selector_id="selected"),
    _format_control("bookmark-selected-text-vertical-alignment", "Selected vertical alignment", "text", "enum", ["bookmarkNavigator"],
                    [["visual", "objects", "text", 0, "properties", "verticalAlignment"]], options=["middle", "top", "bottom"], group="Bookmark navigator", selector_id="selected"),
    _format_control("bookmark-selected-text-horizontal-alignment", "Selected horizontal alignment", "text", "enum", ["bookmarkNavigator"],
                    [["visual", "objects", "text", 0, "properties", "horizontalAlignment"]], options=["middle", "left", "right"], group="Bookmark navigator", selector_id="selected"),
    _format_control("bookmark-selected-fill-color", "Selected fill color", "color", "hexColor", ["bookmarkNavigator"],
                    [["visual", "objects", "fill", 0, "properties", "fillColor"]], group="Bookmark navigator", selector_id="selected"),
    _format_control("bookmark-selected-border-width", "Selected border width", "number", "number", ["bookmarkNavigator"],
                    [["visual", "objects", "outline", 0, "properties", "width"], ["visual", "objects", "border", 0, "properties", "width"]], group="Bookmark navigator", selector_id="selected"),
    _format_control("bookmark-selected-border-color", "Selected border color", "color", "hexColor", ["bookmarkNavigator"],
                    [["visual", "objects", "outline", 0, "properties", "color"], ["visual", "objects", "border", 0, "properties", "color"]], group="Bookmark navigator", selector_id="selected"),

    _format_control("textbox-text-font-size", "Text font size", "number", "number", ["textbox"],
                    [["visual", "objects", "general", 0, "properties", "paragraphs", 0, "textRuns", 0, "textStyle", "fontSize"]], group="Text visual"),
    _format_control("textbox-text-font-family", "Text font family", "text", "powerBiLiteralString", ["textbox"],
                    [["visual", "objects", "general", 0, "properties", "paragraphs", 0, "textRuns", 0, "textStyle", "fontFamily"]], group="Text visual"),
    _format_control("textbox-text-color", "Text color", "color", "hexColor", ["textbox"],
                    [["visual", "objects", "general", 0, "properties", "paragraphs", 0, "textRuns", 0, "textStyle", "color"]], group="Text visual"),
    _format_control("textbox-background-show", "Text background", "boolean", "boolean", ["textbox"],
                    [["visual", "visualContainerObjects", "background", 0, "properties", "show"]], group="Text visual"),

    _format_control("card-accent-bar-show", "Accent bar", "boolean", "boolean", ["cardVisual"],
                    [["visual", "objects", "accentBar", 0, "properties", "show"]], group="Card", selector_id="default"),
    _format_control("card-accent-bar-position", "Accent bar position", "text", "enum", ["cardVisual"],
                    [["visual", "objects", "accentBar", 0, "properties", "position"]], options=["Left", "Right"], group="Card", selector_id="default"),
    _format_control("card-accent-bar-width", "Accent bar width", "number", "number", ["cardVisual"],
                    [["visual", "objects", "accentBar", 0, "properties", "width"]], group="Card", selector_id="default"),
    _format_control("card-accent-bar-color", "Accent bar color", "color", "hexColor", ["cardVisual"],
                    [["visual", "objects", "accentBar", 0, "properties", "color"]], group="Card", selector_id="default"),
    _format_control("card-value-font-size-standard", "Card value font size", "number", "number", ["cardVisual"],
                    [["visual", "objects", "value", 0, "properties", "fontSize"]], group="Card"),
    _format_control("card-value-font-family-standard", "Card value font family", "text", "powerBiLiteralString", ["cardVisual"],
                    [["visual", "objects", "value", 0, "properties", "fontFamily"]], group="Card"),
    _format_control("card-value-color-standard", "Card value color", "color", "hexColor", ["cardVisual"],
                    [["visual", "objects", "value", 0, "properties", "fontColor"]], group="Card"),
    _format_control("card-label-position-bottom", "Card label position", "text", "enum", ["cardVisual"],
                    [["visual", "objects", "label", 0, "properties", "position"]], options=["belowValue", "aboveValue"], group="Card"),
    _format_control("card-label-font-size-standard", "Card label font size", "number", "number", ["cardVisual"],
                    [["visual", "objects", "label", 0, "properties", "fontSize"]], group="Card"),
    _format_control("card-label-font-family-standard", "Card label font family", "text", "powerBiLiteralString", ["cardVisual"],
                    [["visual", "objects", "label", 0, "properties", "fontFamily"]], group="Card"),
    _format_control("card-label-color-standard", "Card label color", "color", "hexColor", ["cardVisual"],
                    [["visual", "objects", "label", 0, "properties", "fontColor"]], group="Card"),
])

for _control in VisualPropertyCatalog.BUILTIN_CONTROLS:
    if _control.id == "general-title-font-color":
        _control.group_path = ["All visuals"]
