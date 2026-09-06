from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, replace
from typing import Any, Iterable

from app.core.file_document import JsonDocument
from app.core.json_file_type import JsonFileType
from app.core.powerbi_metadata import encode_powerbi_literal_string
from app.features.visual_editor.visual_edit_types import VisualEditorControl


@dataclass(slots=True)
class VisualEditResult:
    changed_files: int = 0
    changed_values: int = 0
    skipped_files: int = 0
    warnings: list[str] = field(default_factory=list)

    @property
    def summary(self) -> str:
        if self.changed_values == 0:
            return "No visual values changed."
        skipped = f", skipped {self.skipped_files} file(s)" if self.skipped_files else ""
        return f"Changed {self.changed_values} value(s) in {self.changed_files} visual file(s){skipped}."


class VisualEditorService:
    def __init__(self, controls: Iterable[VisualEditorControl]) -> None:
        self._controls = {control.id: control for control in controls}
        self._dynamic_controls: dict[str, VisualEditorControl] = {}
        self._category_visual_types: dict[str, str] = {}
        self._selected_visual_type: str | None = None

    def controls(self) -> list[VisualEditorControl]:
        return list(self._controls.values()) + list(self._dynamic_controls.values())

    def control(self, control_id: str) -> VisualEditorControl | None:
        return self._controls.get(control_id) or self._dynamic_controls.get(control_id)

    def applicable_controls(self, documents: Iterable[JsonDocument], category: str = "General") -> list[VisualEditorControl]:
        active_documents = [document for document in documents if self._is_active_visual(document)]
        selected_visual_type = self._visual_type_from_category(category)
        self._selected_visual_type = selected_visual_type
        scoped_documents = [
            document for document in active_documents
            if selected_visual_type is None or self._document_matches_selected_type(document, selected_visual_type)
        ]
        visual_types = {document.visual_type.casefold() for document in scoped_documents}
        controls: list[VisualEditorControl] = []
        include_general = category == "General" or selected_visual_type is not None
        include_specific = category == "Specific" or selected_visual_type is not None
        for control in self._controls.values():
            if control.category == "General" and not include_general:
                continue
            if control.category == "Specific" and not include_specific:
                continue
            if control.category not in {"General", "Specific"}:
                continue
            if selected_visual_type is not None and control.category == "Specific" and not self._control_matches_visual_type(control, selected_visual_type):
                continue
            if category in {"General", "Specific"} and not self._control_matches_visual_types(control, visual_types):
                continue
            if selected_visual_type is not None and control.category == "General" and not scoped_documents:
                continue
            matching_count = sum(1 for document in scoped_documents if self._control_matches_document(control, document))
            if matching_count <= 0:
                continue
            group = "All visuals" if control.category == "General" else self._control_group(control)
            controls.append(replace(control, matching_count=matching_count, visual_type_group=group))

        self._dynamic_controls = {}
        if include_specific:
            dynamic_documents = scoped_documents if selected_visual_type is not None else active_documents
            dynamic_controls = self._dynamic_other_controls(dynamic_documents)
            self._dynamic_controls = {control.id: control for control in dynamic_controls}
            controls.extend(dynamic_controls)
        return controls

    def visual_type_category_options(self, documents: Iterable[JsonDocument]) -> list[dict[str, Any]]:
        active_counts: dict[str, int] = {}
        for document in documents:
            if not self._is_active_visual(document) or not document.visual_type:
                continue
            active_counts[document.visual_type] = active_counts.get(document.visual_type, 0) + 1

        supported_types = self._supported_specific_visual_types()
        supported_type_keys = {visual_type.casefold() for visual_type in supported_types}
        unknown_count = sum(count for visual_type, count in active_counts.items() if visual_type.casefold() not in supported_type_keys)
        ordered_types = sorted(supported_types, key=str.casefold)
        self._category_visual_types = {self._visual_type_label(visual_type): visual_type for visual_type in ordered_types}

        options: list[dict[str, Any]] = []
        for label, visual_type in self._category_visual_types.items():
            count = active_counts.get(visual_type, 0)
            options.append({"label": f"{count} {label}", "value": label, "enabled": count > 0, "count": count})
        options.append({"label": f"{unknown_count} Other", "value": "Other", "enabled": unknown_count > 0, "count": unknown_count})
        if unknown_count > 0:
            self._category_visual_types["Other"] = "__other__"
        return options

    def apply_change(self, documents: Iterable[JsonDocument], control_id: str, raw_value: Any) -> VisualEditResult:
        control = self.control(control_id)
        result = VisualEditResult()
        if control is None:
            result.warnings.append(f"Unknown visual editor control '{control_id}'.")
            return result

        changed_document_ids: set[str] = set()
        for document in documents:
            if not self._is_active_visual(document):
                continue
            if self._selected_visual_type is not None and not self._document_matches_selected_type(document, self._selected_visual_type):
                result.skipped_files += 1
                continue
            if not document.is_valid_json:
                result.skipped_files += 1
                continue
            if not self._control_matches_document(control, document):
                result.skipped_files += 1
                continue
            data = document.parsed_json
            changed = self._apply_to_data(data, control, raw_value)
            if changed <= 0:
                result.skipped_files += 1
                continue
            try:
                new_text = json.dumps(data, ensure_ascii=False, indent=2)
                json.loads(new_text)
            except (TypeError, ValueError, json.JSONDecodeError) as error:
                result.skipped_files += 1
                result.warnings.append(f"{document.name}: generated JSON failed validation: {error}")
                continue
            document.set_text(new_text)
            changed_document_ids.add(document.id)
            result.changed_values += changed

        result.changed_files = len(changed_document_ids)
        return result

    @staticmethod
    def _is_active_visual(document: JsonDocument) -> bool:
        return document.file_type == JsonFileType.VISUAL and document.is_active

    def _document_matches_selected_type(self, document: JsonDocument, selected_visual_type: str) -> bool:
        if selected_visual_type == "__other__":
            return document.visual_type.casefold() not in self._known_specific_visual_types()
        return document.visual_type.casefold() == selected_visual_type.casefold()
    def _control_matches_document(self, control: VisualEditorControl, document: JsonDocument) -> bool:
        if "*" in control.visual_types:
            return True
        visual_type = document.visual_type.casefold()
        return any(visual_type == candidate.casefold() or candidate.casefold() in visual_type for candidate in control.visual_types)

    def _control_matches_visual_types(self, control: VisualEditorControl, visual_types: set[str]) -> bool:
        if "*" in control.visual_types:
            return True
        if not visual_types:
            return False
        return any(
            visual_type == candidate.casefold() or candidate.casefold() in visual_type
            for visual_type in visual_types
            for candidate in control.visual_types
        )

    def _supported_specific_visual_types(self) -> set[str]:
        supported: set[str] = set()
        for control in self._controls.values():
            if control.category != "Specific":
                continue
            for visual_type in control.visual_types:
                if visual_type != "*":
                    supported.add(visual_type)
        return supported

    def _visual_type_from_category(self, category: str) -> str | None:
        if category in {"General", "Specific"}:
            return None
        return self._category_visual_types.get(category)

    def _control_matches_visual_type(self, control: VisualEditorControl, visual_type: str) -> bool:
        if "*" in control.visual_types:
            return True
        lowered = visual_type.casefold()
        return any(lowered == candidate.casefold() or candidate.casefold() in lowered for candidate in control.visual_types)

    def _control_group(self, control: VisualEditorControl) -> str:
        if "*" in control.visual_types:
            return "All visuals"
        labels = [self._visual_type_label(visual_type) for visual_type in control.visual_types]
        return ", ".join(labels)

    @staticmethod
    def _visual_type_label(visual_type: str) -> str:
        value = re.sub(r"(?<!^)([A-Z])", r" \1", visual_type).replace("_", " ").replace("-", " ")
        value = re.sub(r"\s+", " ", value).strip()
        return value[:1].upper() + value[1:].lower()
    def _dynamic_other_controls(self, documents: list[JsonDocument]) -> list[VisualEditorControl]:
        known_specific_types = self._known_specific_visual_types()
        controls_by_id: dict[str, VisualEditorControl] = {}
        for document in documents:
            visual_type = document.visual_type or "unknown"
            if visual_type.casefold() in known_specific_types:
                continue
            if not isinstance(document.parsed_json, dict):
                continue
            for control in self._controls_for_unknown_document(document, visual_type):
                existing = controls_by_id.get(control.id)
                if existing is None:
                    controls_by_id[control.id] = control
                else:
                    existing.matching_count += 1
        return sorted(controls_by_id.values(), key=lambda item: (item.visual_type_group.casefold(), item.label.casefold(), item.id))

    def _known_specific_visual_types(self) -> set[str]:
        known: set[str] = set()
        for control in self._controls.values():
            if control.category != "Specific":
                continue
            for visual_type in control.visual_types:
                if visual_type != "*":
                    known.add(visual_type.casefold())
        return known

    def _controls_for_unknown_document(self, document: JsonDocument, visual_type: str) -> list[VisualEditorControl]:
        data = document.parsed_json
        if not isinstance(data, dict):
            return []
        visual = data.get("visual")
        if not isinstance(visual, dict):
            return []
        discovered: list[VisualEditorControl] = []
        for container_name in ("objects", "visualContainerObjects"):
            container = visual.get(container_name)
            if not isinstance(container, dict):
                continue
            for object_name, raw_entries in container.items():
                entries = raw_entries if isinstance(raw_entries, list) else [raw_entries]
                for entry_index, entry in enumerate(entries):
                    if not isinstance(entry, dict):
                        continue
                    properties = entry.get("properties")
                    if not isinstance(properties, dict):
                        continue
                    for property_name, property_value in properties.items():
                        inferred = self._infer_dynamic_control(property_name, property_value)
                        if inferred is None:
                            continue
                        control_type, value_type = inferred
                        path = ["visual", container_name, object_name, entry_index, "properties", property_name]
                        control_id = self._dynamic_control_id(visual_type, path)
                        label = self._dynamic_control_label(object_name, property_name)
                        discovered.append(
                            VisualEditorControl(
                                id=control_id,
                                label=label,
                                category="Specific",
                                control=control_type,
                                value_type=value_type,
                                visual_types=[visual_type],
                                paths=[path],
                                matching_count=1,
                                visual_type_group="Other",
                            )
                        )
        return discovered

    @staticmethod
    def _infer_dynamic_control(property_name: str, value: Any) -> tuple[str, str] | None:
        lowered = property_name.casefold()
        if isinstance(value, bool):
            return "boolean", "boolean"
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return ("slider", "percentage") if "transparency" in lowered else ("number", "number")
        if isinstance(value, str):
            if re.fullmatch(r"#[0-9A-Fa-f]{6}", value) or any(token in lowered for token in ("color", "fill", "foreground", "background")):
                return "color", "hexColor"
            return "text", "string"
        if isinstance(value, dict):
            literal = value.get("expr", {}).get("Literal")
            if isinstance(literal, dict) and "Value" in literal:
                literal_value = str(literal.get("Value", ""))
                if re.fullmatch(r"[-+]?\d+(\.\d+)?", literal_value):
                    return "number", "powerBiLiteralNumber"
                return "text", "powerBiLiteralString"
            solid = value.get("solid")
            if isinstance(solid, dict) and isinstance(solid.get("color"), str):
                return "color", "hexColor"
        return None

    @staticmethod
    def _dynamic_control_id(visual_type: str, path: list[str | int]) -> str:
        normalized_type = re.sub(r"[^A-Za-z0-9]+", "-", visual_type).strip("-").casefold() or "unknown"
        normalized_path = "-".join(str(part) for part in path[2:])
        normalized_path = re.sub(r"[^A-Za-z0-9]+", "-", normalized_path).strip("-").casefold()
        return f"other-{normalized_type}-{normalized_path}"

    @staticmethod
    def _dynamic_control_label(object_name: str, property_name: str) -> str:
        def title(value: str) -> str:
            value = re.sub(r"(?<!^)([A-Z])", r" \1", value)
            value = value.replace("_", " ").replace("-", " ")
            return value[:1].upper() + value[1:].lower()

        return f"Other: {title(object_name)} {title(property_name)}"

    def _apply_to_data(self, data: Any, control: VisualEditorControl, raw_value: Any) -> int:
        value = self._convert_value(control.value_type, raw_value, control.options)
        if control.paths:
            return self._set_existing_paths(data, control.paths, value, control)
        if control.id == "general-title-text":
            return self._set_first_existing_path(
                data,
                [
                    (["visual", "visualContainerObjects", "title", 0, "properties", "text", "expr", "Literal", "Value"], encode_powerbi_literal_string(str(raw_value))),
                    (["Title"], str(raw_value)),
                    (["title"], str(raw_value)),
                ],
            )
        if control.id == "general-title-font-color":
            return self._set_color_by_ancestor(data, value, ["title"], ["fontColor", "titleFontColor", "color"])
        if control.id == "general-background-color":
            return self._set_color_by_ancestor(data, value, ["background"], ["color", "backgroundColor"])
        if control.id == "general-background-transparency":
            return self._set_key_by_ancestor(data, "transparency", value, ["background"])
        if control.id == "general-hidden":
            return self._set_exact_key(data, "isHidden", value)
        if control.id.startswith("general-position-"):
            key = control.id.removeprefix("general-position-")
            return self._set_path(data, ["position", key], value, control)
        if control.id in {"bar-data-color", "pie-slice-color", "line-color"}:
            return self._set_color_by_ancestor(data, value, ["data", "color"], ["color", "fill", "foreground", "backgroundColor"])
        if control.id == "table-text-size":
            return self._set_exact_key(data, "fontSize", value) + self._set_exact_key(data, "textSize", value)
        if control.id == "slicer-background-transparency":
            return self._set_key_by_ancestor(data, "transparency", value, ["background", "slicer"])
        return self._set_exact_key(data, control.id, value)

    @staticmethod
    def _convert_value(value_type: str, raw_value: Any, options: list[str] | None = None) -> Any:
        if value_type in {"number", "percentage", "powerBiLiteralNumber", "integer"}:
            try:
                numeric = float(raw_value)
            except (TypeError, ValueError):
                numeric = 0
            if value_type == "percentage":
                numeric = max(0, min(100, numeric))
            if value_type == "integer":
                return int(round(numeric))
            return int(numeric) if numeric.is_integer() else numeric
        if value_type == "boolean":
            if isinstance(raw_value, bool):
                return raw_value
            return str(raw_value).strip().casefold() in {"1", "true", "yes", "on"}
        if value_type == "hexColor":
            value = str(raw_value or "").strip()
            if re.fullmatch(r"[0-9A-Fa-f]{6}", value):
                return "#" + value.upper()
            if re.fullmatch(r"#[0-9A-Fa-f]{6}", value):
                return value.upper()
            return "#000000"
        if value_type == "enum" and options:
            value = str(raw_value or "").strip()
            return value if value in options else options[0]
        return str(raw_value)

    def _set_existing_paths(self, data: Any, paths: list[list[str | int]], value: Any, control: VisualEditorControl) -> int:
        changed = 0
        for path in paths:
            if self._path_exists(data, path):
                changed += self._set_path(data, path, value, control)
        return changed

    def _set_first_existing_path(self, data: Any, candidates: list[tuple[list[str | int], Any]]) -> int:
        for path, value in candidates:
            if self._path_exists(data, path):
                return self._set_path(data, path, value, None)
        return 0

    def _set_path(self, data: Any, path: list[str | int], value: Any, control: VisualEditorControl | None = None) -> int:
        current = data
        for part in path[:-1]:
            if isinstance(part, int):
                if not isinstance(current, list) or not 0 <= part < len(current):
                    return 0
                current = current[part]
            else:
                if not isinstance(current, dict) or part not in current:
                    return 0
                current = current[part]
        leaf = path[-1]
        if isinstance(leaf, int):
            if not isinstance(current, list) or not 0 <= leaf < len(current):
                return 0
            return self._set_leaf_value(current, leaf, value, path, control)
        if not isinstance(current, dict) or leaf not in current:
            return 0
        return self._set_leaf_value(current, leaf, value, path, control)

    def _set_leaf_value(self, container: dict[Any, Any] | list[Any], leaf: Any, value: Any, path: list[str | int], control: VisualEditorControl | None) -> int:
        current_value = container[leaf]
        updated = self._value_for_existing_leaf(current_value, value, path, control)
        if updated == current_value:
            return 0
        container[leaf] = updated
        return 1

    def _value_for_existing_leaf(self, current_value: Any, value: Any, path: list[str | int], control: VisualEditorControl | None) -> Any:
        value_type = control.value_type if control is not None else ""
        if isinstance(current_value, dict):
            copied = json.loads(json.dumps(current_value))
            literal = copied.get("expr", {}).get("Literal")
            if isinstance(literal, dict) and "Value" in literal:
                literal["Value"] = self._literal_value(value, value_type)
                return copied
            solid = copied.get("solid")
            if isinstance(solid, dict) and "color" in solid:
                solid["color"] = str(value)
                return copied
            return current_value
        if str(path[-1]).casefold() == "value" and "Literal" in [str(part) for part in path]:
            return self._literal_value(value, value_type)
        return value

    @staticmethod
    def _literal_value(value: Any, value_type: str) -> str:
        if value_type in {"number", "percentage", "powerBiLiteralNumber", "integer"}:
            return str(value)
        if value_type == "boolean":
            return "true" if value else "false"
        return encode_powerbi_literal_string(str(value))

    def _path_exists(self, data: Any, path: list[str | int]) -> bool:
        current = data
        for part in path:
            if isinstance(part, int):
                if not isinstance(current, list) or not 0 <= part < len(current):
                    return False
                current = current[part]
            else:
                if not isinstance(current, dict) or part not in current:
                    return False
                current = current[part]
        return True

    def _set_exact_key(self, data: Any, key: str, value: Any) -> int:
        changed = 0
        if isinstance(data, dict):
            for current_key, current_value in data.items():
                if current_key == key and current_value != value:
                    data[current_key] = value
                    changed += 1
                else:
                    changed += self._set_exact_key(current_value, key, value)
        elif isinstance(data, list):
            for item in data:
                changed += self._set_exact_key(item, key, value)
        return changed

    def _set_key_by_ancestor(self, data: Any, key: str, value: Any, ancestors: list[str]) -> int:
        return self._walk_and_update(data, value, ancestors, {key})

    def _set_color_by_ancestor(self, data: Any, value: Any, ancestors: list[str], keys: list[str]) -> int:
        changed = self._walk_and_update(data, value, ancestors, set(keys))
        changed += self._set_solid_color_by_ancestor(data, value, ancestors)
        return changed

    def _walk_and_update(self, data: Any, value: Any, ancestors: list[str], keys: set[str], path: list[str] | None = None) -> int:
        path = path or []
        changed = 0
        if isinstance(data, dict):
            ancestor_match = self._ancestor_match(path, ancestors)
            for current_key, current_value in data.items():
                if ancestor_match and current_key in keys and not isinstance(current_value, (dict, list)):
                    if data[current_key] != value:
                        data[current_key] = value
                        changed += 1
                else:
                    changed += self._walk_and_update(current_value, value, ancestors, keys, path + [current_key])
        elif isinstance(data, list):
            for index, item in enumerate(data):
                changed += self._walk_and_update(item, value, ancestors, keys, path + [str(index)])
        return changed

    def _set_solid_color_by_ancestor(self, data: Any, value: str, ancestors: list[str], path: list[str] | None = None) -> int:
        path = path or []
        changed = 0
        if isinstance(data, dict):
            if self._ancestor_match(path, ancestors):
                solid = data.get("solid")
                if isinstance(solid, dict) and isinstance(solid.get("color"), str) and solid.get("color") != value:
                    solid["color"] = value
                    changed += 1
            for current_key, current_value in data.items():
                changed += self._set_solid_color_by_ancestor(current_value, value, ancestors, path + [current_key])
        elif isinstance(data, list):
            for index, item in enumerate(data):
                changed += self._set_solid_color_by_ancestor(item, value, ancestors, path + [str(index)])
        return changed

    @staticmethod
    def _ancestor_match(path: list[str], ancestors: list[str]) -> bool:
        lowered_path = [part.casefold() for part in path]
        return any(any(ancestor.casefold() in part for part in lowered_path) for ancestor in ancestors)
