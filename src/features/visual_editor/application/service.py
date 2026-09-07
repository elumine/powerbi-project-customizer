from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, replace
from typing import Any, Iterable

from entities.document.models import JsonDocument
from entities.powerbi.file_types import JsonFileType
from entities.powerbi.literals import decode_powerbi_literal_string, encode_powerbi_literal_string
from features.visual_editor.application.line_lookup import line_for_json_path
from features.visual_editor.application.value_conversion import VisualValueConverter
from features.visual_editor.domain.models import VisualEditorControl, VisualEditorPropertyMatch
from services.documents.ports import MutableDocuments


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
            controls.append(self._enriched_control(control, scoped_documents, matching_count, group))

        self._dynamic_controls = {}
        if include_specific:
            dynamic_documents = scoped_documents if selected_visual_type is not None else active_documents
            dynamic_controls = self._dynamic_document_controls(dynamic_documents)
            builtin_paths = {self._flat_key_for_path(path) for control in controls for path in control.paths}
            enriched_dynamic_controls: list[VisualEditorControl] = []
            for control in dynamic_controls:
                if all(self._flat_key_for_path(path) in builtin_paths for path in control.paths):
                    continue
                matching_count = control.matching_count or sum(1 for document in dynamic_documents if self._control_matches_document(control, document))
                enriched_dynamic_controls.append(self._enriched_control(control, dynamic_documents, matching_count, control.visual_type_group or self._control_group(control)))
            self._dynamic_controls = {control.id: control for control in enriched_dynamic_controls}
            controls.extend(enriched_dynamic_controls)
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

    def apply_change(self, documents: MutableDocuments, control_id: str, raw_value: Any) -> VisualEditResult:
        """Apply only validated changes through the document collection boundary.

        The mutation is calculated against a detached JSON copy. Invalid generated
        content never changes the live document, and every committed replacement
        publishes a stable-ID collection event for other feature projections.
        """
        control = self.control(control_id)
        result = VisualEditResult()
        if control is None:
            result.warnings.append(f"Unknown visual editor control '{control_id}'.")
            return result

        changed_document_ids: set[str] = set()
        for document in documents.documents():
            if not self._is_active_visual(document):
                continue
            if self._selected_visual_type is not None and not self._document_matches_selected_type(document, self._selected_visual_type):
                result.skipped_files += 1
                continue
            if not document.is_valid_json or not self._control_matches_document(control, document):
                result.skipped_files += 1
                continue
            try:
                data = json.loads(json.dumps(document.parsed_json, ensure_ascii=False))
                changed = self._apply_to_data(data, control, raw_value)
                if changed <= 0:
                    result.skipped_files += 1
                    continue
                new_text = json.dumps(data, ensure_ascii=False, indent=2)
                json.loads(new_text)
            except (TypeError, ValueError, json.JSONDecodeError) as error:
                result.skipped_files += 1
                result.warnings.append(f"{document.name}: generated JSON failed validation: {error}")
                continue
            documents.set_document_text_by_id(document.id, new_text, operation="visual-editor-change")
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
            type_matches = True
        else:
            visual_type = document.visual_type.casefold()
            type_matches = any(visual_type == candidate.casefold() or candidate.casefold() in visual_type for candidate in control.visual_types)
        if not type_matches:
            return False
        if control.paths and isinstance(document.parsed_json, dict):
            return any(self._path_exists(document.parsed_json, path, control) for path in control.paths)
        return True

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
        mapped = self._category_visual_types.get(category)
        if mapped is not None:
            return mapped
        for visual_type in self._supported_specific_visual_types():
            if self._visual_type_label(visual_type).casefold() == category.casefold():
                return visual_type
        return None

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
    def _dynamic_document_controls(self, documents: list[JsonDocument]) -> list[VisualEditorControl]:
        controls_by_id: dict[str, VisualEditorControl] = {}
        for document in documents:
            visual_type = document.visual_type or "unknown"
            if not isinstance(document.parsed_json, dict):
                continue
            for control in self._controls_for_document(document, visual_type):
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

    def _controls_for_document(self, document: JsonDocument, visual_type: str) -> list[VisualEditorControl]:
        data = document.parsed_json
        if not isinstance(data, dict):
            return []
        discovered = self._controls_for_flat_unknown_document(data, visual_type)
        if discovered:
            return discovered
        visual = data.get("visual")
        if not isinstance(visual, dict):
            return []
        discovered = []
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
                                visual_type_group=self._visual_type_label(visual_type),
                            )
                        )
        return discovered

    def _controls_for_flat_unknown_document(self, data: dict[str, Any], visual_type: str) -> list[VisualEditorControl]:
        discovered: list[VisualEditorControl] = []
        for flat_key, property_value in data.items():
            path = self._path_from_flat_key(flat_key)
            property_index = self._properties_index(path)
            if property_index < 0 or len(path) <= property_index + 1:
                continue
            if len(path) < 5 or path[0] != "visual" or path[1] not in {"objects", "visualContainerObjects"}:
                continue
            object_name = str(path[2])
            property_name = str(path[property_index + 1])
            inferred = self._infer_dynamic_control(property_name, property_value)
            if inferred is None:
                continue
            control_type, value_type = inferred
            if self._is_flat_literal_value_path(path) and value_type == "string":
                value_type = "powerBiLiteralString"
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
                    visual_type_group=self._visual_type_label(visual_type),
                )
            )
        return discovered

    @staticmethod
    def _properties_index(path: list[str | int]) -> int:
        for index, part in enumerate(path):
            if part == "properties":
                return index
        return -1

    @staticmethod
    def _is_flat_literal_value_path(path: list[str | int]) -> bool:
        tail = [str(part) for part in path[-3:]]
        return tail == ["expr", "Literal", "Value"]
    @staticmethod
    def _path_from_flat_key(key: str) -> list[str | int]:
        path: list[str | int] = []
        for part in str(key).split("."):
            match = re.fullmatch(r"\[(\d+)\]", part)
            path.append(int(match.group(1)) if match else part)
        return path
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

        return f"Detected: {title(object_name)} {title(property_name)}"

    def _enriched_control(
        self,
        control: VisualEditorControl,
        documents: list[JsonDocument],
        matching_count: int,
        group: str,
    ) -> VisualEditorControl:
        matches = self._matches_for_control(control, documents)
        default_value = matches[0].value if matches else None
        return replace(
            control,
            matching_count=matching_count,
            visual_type_group=group,
            description=control.description or self._description_for_control(control),
            default_value=default_value,
            matches=matches,
            group_path=control.group_path or self._group_path_for_control(control),
        )

    def _matches_for_control(self, control: VisualEditorControl, documents: list[JsonDocument]) -> list[VisualEditorPropertyMatch]:
        matches: list[VisualEditorPropertyMatch] = []
        for document in documents:
            if not self._control_matches_document(control, document):
                continue
            if not isinstance(document.parsed_json, dict):
                continue
            for path in control.paths:
                if len(matches) >= 20:
                    return matches
                resolved_path = self._resolved_path_for_control(document.parsed_json, path, control)
                if resolved_path is None:
                    continue
                value = self._get_path(document.parsed_json, resolved_path)
                matches.append(
                    VisualEditorPropertyMatch(
                        document_id=document.id,
                        file_path=document.name,
                        line=line_for_json_path(document.text, resolved_path),
                        property_path=self._format_path(resolved_path),
                        value=self._display_value(value),
                    )
                )
        return matches

    @staticmethod
    def _description_for_control(control: VisualEditorControl) -> str:
        if control.paths:
            return "Controls " + ", ".join(VisualEditorService._format_path(path) for path in control.paths[:2])
        return f"Controls allowlisted {control.category.casefold()} property '{control.id}'."

    @staticmethod
    def _group_path_for_control(control: VisualEditorControl) -> list[str]:
        if not control.paths:
            return [control.category]
        path = control.paths[0]
        if "properties" in path:
            property_index = path.index("properties")
            return [str(part) for part in path[:property_index]]
        return [str(part) for part in path[:-1]]

    @staticmethod
    def _format_path(path: list[str | int]) -> str:
        return VisualEditorService._flat_key_for_path(path)

    @staticmethod
    def _flat_key_for_path(path: list[str | int]) -> str:
        return ".".join(f"[{part}]" if isinstance(part, int) else str(part) for part in path)

    @staticmethod
    def _flat_descendant_key(data: dict[str, Any], flat_key: str, control: VisualEditorControl | None = None) -> str | None:
        prefix = flat_key + "."
        if control is not None:
            preferred_suffixes = []
            if control.value_type in {"powerBiLiteralString", "powerBiLiteralNumber"} or control.control == "text":
                preferred_suffixes.append("expr.Literal.Value")
            if control.value_type == "hexColor" or control.control == "color":
                preferred_suffixes.append("solid.color")
            for suffix in preferred_suffixes:
                candidate = prefix + suffix
                if candidate in data:
                    return candidate
        descendants = [key for key in data if key.startswith(prefix)]
        if len(descendants) == 1:
            return descendants[0]
        return None

    @staticmethod
    def _display_value(value: Any) -> Any:
        if isinstance(value, dict):
            literal = value.get("expr", {}).get("Literal")
            if isinstance(literal, dict) and "Value" in literal:
                return decode_powerbi_literal_string(literal.get("Value"))
            solid = value.get("solid")
            if isinstance(solid, dict) and "color" in solid:
                return solid.get("color")
        if isinstance(value, str):
            return decode_powerbi_literal_string(value)
        return value

    def _resolved_path_for_control(self, data: Any, path: list[str | int], control: VisualEditorControl | None = None) -> list[str | int] | None:
        if not isinstance(data, dict):
            return path if self._path_exists(data, path, control) else None
        flat_key = self._flat_key_for_path(path)
        if flat_key in data:
            return path
        descendant_key = self._flat_descendant_key(data, flat_key, control)
        if descendant_key is not None:
            return self._path_from_flat_key(descendant_key)
        return None

    @staticmethod
    def _get_path(data: Any, path: list[str | int]) -> Any:
        if isinstance(data, dict):
            flat_key = VisualEditorService._flat_key_for_path(path)
            if flat_key in data:
                return data.get(flat_key)
            descendant_key = VisualEditorService._flat_descendant_key(data, flat_key)
            if descendant_key is not None:
                return data.get(descendant_key)
        current = data
        for part in path:
            if isinstance(part, int):
                if not isinstance(current, list) or not 0 <= part < len(current):
                    return None
                current = current[part]
            else:
                if not isinstance(current, dict) or part not in current:
                    return None
                current = current[part]
        return current

    def _apply_to_data(self, data: Any, control: VisualEditorControl, raw_value: Any) -> int:
        value = VisualValueConverter.convert(control.value_type, raw_value, control.options)
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
        if isinstance(data, dict):
            flat_key = self._flat_key_for_path(path)
            if flat_key in data:
                return self._set_leaf_value(data, flat_key, value, path, control)
            descendant_key = self._flat_descendant_key(data, flat_key, control)
            if descendant_key is not None:
                return self._set_leaf_value(data, descendant_key, value, self._path_from_flat_key(descendant_key), control)
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

    def _path_exists(self, data: Any, path: list[str | int], control: VisualEditorControl | None = None) -> bool:
        if isinstance(data, dict):
            flat_key = self._flat_key_for_path(path)
            if flat_key in data or self._flat_descendant_key(data, flat_key, control) is not None:
                return True
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
                flat_leaf = current_key.rsplit(".", 1)[-1]
                if (current_key == key or flat_leaf == key) and current_value != value:
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
                flat_path = self._flat_path_parts(current_key)
                effective_path = path + flat_path
                effective_leaf = flat_path[-1] if flat_path else current_key
                effective_ancestor_match = ancestor_match or self._ancestor_match(effective_path[:-1], ancestors)
                if effective_ancestor_match and effective_leaf in keys and not isinstance(current_value, (dict, list)):
                    if data[current_key] != value:
                        data[current_key] = value
                        changed += 1
                else:
                    changed += self._walk_and_update(current_value, value, ancestors, keys, effective_path)
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
    def _flat_path_parts(key: str) -> list[str]:
        return [part for part in str(key).split(".") if part]

    @staticmethod
    def _ancestor_match(path: list[str], ancestors: list[str]) -> bool:
        lowered_path = [part.casefold() for part in path]
        return any(any(ancestor.casefold() in part for part in lowered_path) for ancestor in ancestors)
