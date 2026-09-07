from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from services.text.stable_values import stable_id
from features.macros.domain.models import MACRO_STEP_TYPES, MacroItem, MacroStep


class MacroRepository:
    def __init__(self, content_root: Path) -> None:
        self._content_root = content_root

    @property
    def macros_path(self) -> Path:
        return self._content_root / "macros"

    def list_macros(self) -> list[MacroItem]:
        folder = self.macros_path
        if not folder.exists() or not folder.is_dir():
            return []

        macros = [self.load_macro_file(path) for path in sorted(folder.rglob("*.json"), key=lambda item: str(item).casefold())]
        return macros

    def load_macro_file(self, path: Path) -> MacroItem:
        macro_id = self._macro_id(path, {})
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as error:
            return MacroItem(
                id=macro_id,
                name=path.stem,
                source_path=str(path),
                load_errors=[f"{path.name}: {error}"],
                validation_errors=[f"{path.name}: {error}"],
            )

        if not isinstance(data, dict):
            return MacroItem(
                id=macro_id,
                name=path.stem,
                source_path=str(path),
                load_errors=["Macro file must contain a JSON object."],
                validation_errors=["Macro file must contain a JSON object."],
            )

        macro_id = self._macro_id(path, data)
        name = str(data.get("name") or path.stem).strip()
        steps_data = data.get("steps")
        load_errors: list[str] = []
        steps: list[MacroStep] = []
        if not isinstance(steps_data, list):
            load_errors.append("Macro steps must be an array.")
        else:
            for index, step_data in enumerate(steps_data):
                step, errors = self._step_from_data(macro_id, index, step_data)
                steps.append(step)
                load_errors.extend(errors)

        return MacroItem(
            id=macro_id,
            name=name,
            steps=steps,
            source_path=str(path),
            load_errors=load_errors,
            validation_errors=list(load_errors),
        )

    @staticmethod
    def export_macro(path: Path, macro: MacroItem) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(macro.to_export_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def _step_from_data(self, macro_id: str, index: int, data: Any) -> tuple[MacroStep, list[str]]:
        step_id = f"{macro_id}.step.{index + 1}"
        if not isinstance(data, dict):
            return MacroStep(id=step_id, type=""), [f"Step {index + 1}: step must be an object."]

        step_type = str(data.get("type", "")).strip()
        errors: list[str] = []
        if step_type not in MACRO_STEP_TYPES:
            errors.append(f"Step {index + 1}: unknown step type '{step_type}'.")
        if step_type == "search-and-replace" and "replaceValue" not in data:
            errors.append(f"Step {index + 1}: replaceValue is required.")
        if step_type in {"visual-editor-change", "dynamic-filter-apply"} and "value" not in data:
            errors.append(f"Step {index + 1}: value is required.")

        source_history_index = -1
        try:
            source_history_index = int(data.get("sourceHistoryIndex", -1) or -1)
        except (TypeError, ValueError):
            errors.append(f"Step {index + 1}: sourceHistoryIndex must be an integer.")

        return (
            MacroStep(
                id=step_id,
                type=step_type,
                filter_name=str(data.get("filterName", "")).strip(),
                filter_id=str(data.get("filterId", "")).strip(),
                search_value=str(data.get("searchValue", "")),
                replace_value=str(data.get("replaceValue", "")),
                has_replace_value="replaceValue" in data,
                control_id=str(data.get("controlId", "")).strip(),
                value=data.get("value", ""),
                source_history_index=source_history_index,
            ),
            errors,
        )

    def _macro_id(self, path: Path, data: dict[str, Any]) -> str:
        explicit_id = str(data.get("id", "")).strip()
        if explicit_id:
            return explicit_id
        return stable_id("macro", self._relative_seed(path))

    def _relative_seed(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self._content_root.resolve())).replace("\\", "/")
        except ValueError:
            return str(path.resolve())
