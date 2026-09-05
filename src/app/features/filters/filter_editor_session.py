from __future__ import annotations

from dataclasses import dataclass

from app.core.content_filter import ContentFilter, FilterRule, generate_filter_color


@dataclass(slots=True)
class FilterEditorSession:
    filter_id: str = ""
    name: str = ""
    color: str = ""
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
            visible=True,
        )

    def to_filter(self, rules: list[FilterRule], used_colors: set[str]) -> ContentFilter:
        color = self.color or generate_filter_color(used_colors)
        if self.filter_id:
            return ContentFilter(
                id=self.filter_id,
                display_name=self.name.strip(),
                color=color,
                rules=rules,
            )
        return ContentFilter.create(self.name.strip(), rules, color=color, used_colors=used_colors)
