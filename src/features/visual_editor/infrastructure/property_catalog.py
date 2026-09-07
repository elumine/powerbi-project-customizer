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
        VisualEditorControl("general-position-x", "X", "General", "number", "number", paths=[["position", "x"]]),
        VisualEditorControl("general-position-y", "Y", "General", "number", "number", paths=[["position", "y"]]),
        VisualEditorControl("general-position-width", "Width", "General", "number", "number", paths=[["position", "width"]]),
        VisualEditorControl("general-position-height", "Height", "General", "number", "number", paths=[["position", "height"]]),
        VisualEditorControl("general-position-z", "Z", "General", "number", "number", paths=[["position", "z"]]),
        VisualEditorControl("bar-data-color", "Bar color", "Specific", "color", "hexColor", ["bar", "barChart", "clusteredBarChart", "columnChart", "clusteredColumnChart"], paths=[
            ["visual", "objects", "dataPoint", 0, "properties", "fill"],
        ]),
        VisualEditorControl("bar-value-axis-show", "Value axis", "Specific", "boolean", "boolean", ["barChart"], paths=[
            ["visual", "objects", "valueAxis", 0, "properties", "show"],
        ]),
        VisualEditorControl("bar-category-axis-color", "Category label color", "Specific", "color", "hexColor", ["barChart"], paths=[
            ["visual", "objects", "categoryAxis", 0, "properties", "labelColor"],
        ]),
        VisualEditorControl("bar-label-font-size", "Label font size", "Specific", "number", "number", ["barChart"], paths=[
            ["visual", "objects", "labels", 0, "properties", "fontSize"],
        ]),
        VisualEditorControl("bar-legend-show", "Legend", "Specific", "boolean", "boolean", ["barChart"], paths=[
            ["visual", "objects", "legend", 0, "properties", "show"],
        ]),
        VisualEditorControl("bar-totals-show", "Totals", "Specific", "boolean", "boolean", ["barChart"], paths=[
            ["visual", "objects", "totals", 0, "properties", "show"],
        ]),
        VisualEditorControl("pie-slice-color", "Pie slice color", "Specific", "color", "hexColor", ["pieChart", "donutChart"]),
        VisualEditorControl("line-color", "Line color", "Specific", "color", "hexColor", ["lineChart"]),
        VisualEditorControl("table-text-size", "Table text size", "Specific", "number", "number", ["table", "pivotTable", "matrix"], paths=[["visual", "objects", "values", 0, "properties", "fontSize"], ["visual", "objects", "values", 0, "properties", "textSize"], ["visual", "objects", "columnHeaders", 0, "properties", "fontSize"], ["visual", "objects", "columnHeaders", 0, "properties", "textSize"]]),
        VisualEditorControl("slicer-background-transparency", "Slicer background transparency", "Specific", "slider", "percentage", ["slicer"], paths=[
            ["visual", "visualContainerObjects", "background", 0, "properties", "transparency"],
        ]),
        VisualEditorControl("slicer-mode", "Mode", "Specific", "text", "string", ["slicer"], paths=[
            ["visual", "objects", "data", 0, "properties", "mode"],
        ]),
        VisualEditorControl("slicer-single-select", "Single select", "Specific", "boolean", "boolean", ["slicer"], paths=[
            ["visual", "objects", "selection", 0, "properties", "singleSelect"],
        ]),
        VisualEditorControl("slicer-select-all", "Select all checkbox", "Specific", "boolean", "boolean", ["slicer"], paths=[
            ["visual", "objects", "selection", 0, "properties", "selectAllCheckboxEnabled"],
        ]),
        VisualEditorControl("slicer-items-font-color", "Items font color", "Specific", "color", "hexColor", ["slicer"], paths=[
            ["visual", "objects", "items", 0, "properties", "fontColor"],
        ]),
        VisualEditorControl("slicer-items-text-size", "Items text size", "Specific", "number", "number", ["slicer"], paths=[
            ["visual", "objects", "items", 0, "properties", "textSize"],
        ]),
        VisualEditorControl("slicer-header-text", "Header text", "Specific", "text", "powerBiLiteralString", ["slicer"], paths=[
            ["visual", "objects", "header", 0, "properties", "text"],
        ]),
        VisualEditorControl("shape-type", "Shape type", "Specific", "text", "string", ["shape"], paths=[
            ["visual", "objects", "shape", 0, "properties", "tileShape"],
        ]),
        VisualEditorControl("shape-rotation", "Rotation angle", "Specific", "number", "number", ["shape"], paths=[
            ["visual", "objects", "rotation", 0, "properties", "shapeAngle"],
        ]),
        VisualEditorControl("shape-fill-color", "Fill color", "Specific", "color", "hexColor", ["shape"], paths=[
            ["visual", "objects", "fill", 0, "properties", "fillColor"],
        ]),
        VisualEditorControl("shape-fill-transparency", "Fill transparency", "Specific", "slider", "percentage", ["shape"], paths=[
            ["visual", "objects", "fill", 0, "properties", "transparency"],
        ]),
        VisualEditorControl("shape-outline-show", "Outline", "Specific", "boolean", "boolean", ["shape"], paths=[
            ["visual", "objects", "outline", 0, "properties", "show"],
        ]),
        VisualEditorControl("gauge-axis-min", "Axis minimum", "Specific", "number", "number", ["gauge"], paths=[
            ["visual", "objects", "axis", 0, "properties", "min"],
        ]),
        VisualEditorControl("gauge-axis-max", "Axis maximum", "Specific", "number", "number", ["gauge"], paths=[
            ["visual", "objects", "axis", 0, "properties", "max"],
        ]),
        VisualEditorControl("gauge-label-color", "Label color", "Specific", "color", "hexColor", ["gauge"], paths=[
            ["visual", "objects", "labels", 0, "properties", "color"],
        ]),
        VisualEditorControl("gauge-label-font-size", "Label font size", "Specific", "number", "number", ["gauge"], paths=[
            ["visual", "objects", "labels", 0, "properties", "fontSize"],
        ]),
        VisualEditorControl("gauge-target-show", "Target", "Specific", "boolean", "boolean", ["gauge"], paths=[
            ["visual", "objects", "target", 0, "properties", "show"],
        ]),
        VisualEditorControl("gauge-callout-color", "Callout color", "Specific", "color", "hexColor", ["gauge"], paths=[
            ["visual", "objects", "calloutValue", 0, "properties", "color"],
        ]),
        VisualEditorControl("gauge-callout-show", "Callout", "Specific", "boolean", "boolean", ["gauge"], paths=[
            ["visual", "objects", "calloutValue", 0, "properties", "show"],
        ]),
        VisualEditorControl("textbox-border-show", "Border", "Specific", "boolean", "boolean", ["textbox"], paths=[
            ["visual", "visualContainerObjects", "border", 0, "properties", "show"],
        ]),
        VisualEditorControl("textbox-border-width", "Border width", "Specific", "number", "number", ["textbox"], paths=[
            ["visual", "visualContainerObjects", "border", 0, "properties", "width"],
        ]),
        VisualEditorControl("textbox-keep-layer-order", "Keep layer order", "Specific", "boolean", "boolean", ["textbox"], paths=[
            ["visual", "visualContainerObjects", "general", 0, "properties", "keepLayerOrder"],
        ]),
        VisualEditorControl("textbox-header-show", "Header", "Specific", "boolean", "boolean", ["textbox"], paths=[
            ["visual", "visualContainerObjects", "visualHeader", 0, "properties", "show"],
        ]),
        VisualEditorControl("card-fill-custom-show", "Custom fill", "Specific", "boolean", "boolean", ["cardVisual"], paths=[
            ["visual", "objects", "fillCustom", 0, "properties", "show"],
        ]),
        VisualEditorControl("card-label-show", "Label", "Specific", "boolean", "boolean", ["cardVisual"], paths=[
            ["visual", "objects", "label", 0, "properties", "show"],
        ]),
        VisualEditorControl("card-label-color", "Label color", "Specific", "color", "hexColor", ["cardVisual"], paths=[
            ["visual", "objects", "label", 0, "properties", "fontColor"],
        ]),
        VisualEditorControl("card-value-color", "Value color", "Specific", "color", "hexColor", ["cardVisual"], paths=[
            ["visual", "objects", "value", 0, "properties", "fontColor"],
        ]),
        VisualEditorControl("card-value-font-size", "Value font size", "Specific", "number", "number", ["cardVisual"], paths=[
            ["visual", "objects", "value", 0, "properties", "fontSize"],
        ]),
        VisualEditorControl("card-value-bold", "Value bold", "Specific", "boolean", "boolean", ["cardVisual"], paths=[
            ["visual", "objects", "value", 0, "properties", "bold"],
        ]),
        VisualEditorControl("card-column-count", "Column count", "Specific", "number", "integer", ["cardVisual"], paths=[
            ["visual", "objects", "layout", 0, "properties", "columnCount"],
        ]),
        VisualEditorControl("card-image-show", "Image", "Specific", "boolean", "boolean", ["cardVisual"], paths=[
            ["visual", "objects", "image", 0, "properties", "show"],
        ]),
        VisualEditorControl("card-divider-show", "Divider", "Specific", "boolean", "boolean", ["cardVisual"], paths=[
            ["visual", "objects", "divider", 0, "properties", "show"],
        ]),
        VisualEditorControl("image-url", "Image URL", "Specific", "text", "string", ["image"], paths=[
            ["visual", "objects", "general", 0, "properties", "imageUrl"],
        ]),
        VisualEditorControl("image-link-show", "Visual link", "Specific", "boolean", "boolean", ["image"], paths=[
            ["visual", "visualContainerObjects", "visualLink", 0, "properties", "show"],
        ]),
        VisualEditorControl("image-link-type", "Link type", "Specific", "text", "string", ["image"], paths=[
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
            category = str(item.get("category", "General")).strip() or "General"
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


