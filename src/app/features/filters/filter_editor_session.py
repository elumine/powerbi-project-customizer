from __future__ import annotations

from dataclasses import dataclass

from app.core.content_filter import ContentFilter, FilterRule, generate_filter_color
from app.core.json_file_type import FILTER_TARGET_ALL, normalize_filter_target


@dataclass(slots=True)
class FilterEditorSession:
    filter_id: str = ""
    name: str = ""
    color: str = ""
    target_json_file_type: str = FILTER_TARGET_ALL
    visible: bool = False

    @classmethod
    def new_filter(cls, used_colors: set[str]) -> "FilterEditorSession":
        return cls(color=generate_filter_color(used_colors), visible=True)

    @classmethod
    def edit_filter(cls, content_filter: ContentFilter) -> "FilterEditorSession":
        return cls(
            filter_id=content_filter.id,
            name=content_filter.display_name,
            color=content_filter.color,
            target_json_file_type=content_filter.target_json_file_type,
            visible=True,
        )

    def to_filter(self, rules: list[FilterRule], used_colors: set[str]) -> ContentFilter:
        color = self.color or generate_filter_color(used_colors)
        target = normalize_filter_target(self.target_json_file_type)
        if self.filter_id:
            return ContentFilter(
                id=self.filter_id,
                display_name=self.name.strip(),
                color=color,
                rules=rules,
                target_json_file_type=target,
            )
        return ContentFilter.create(self.name.strip(), rules, color=color, used_colors=used_colors, target_json_file_type=target)
