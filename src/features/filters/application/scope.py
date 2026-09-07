from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from entities.document.models import JsonDocument
from entities.filter.models import FILTER_OPERATIONS, ContentFilter, FilterRule
from entities.filter.rules import ContentFilterMatcher
from entities.powerbi.file_types import FILTER_TARGET_ALL, JsonFileType, normalize_filter_target


@dataclass(frozen=True, slots=True)
class DocumentScopeState:
    document_id: str
    is_active: bool
    is_visible: bool
    filter_color: str = ""


class FilterScopeService:
    """Pure filter-to-document scope projection with PBIR parent visibility rules."""

    def project(self, documents: Iterable[JsonDocument], active_filter: ContentFilter | None) -> tuple[DocumentScopeState, ...]:
        values = tuple(documents)
        if active_filter is None:
            return tuple(DocumentScopeState(document.id, True, True) for document in values)

        matched_ids: set[str] = set()
        visible_ids: set[str] = set()
        pages_by_id = {document.id: document for document in values if document.file_type == JsonFileType.PAGE}
        target = normalize_filter_target(active_filter.target_json_file_type)
        visual_name_filter = self._is_visual_name_filter(active_filter)

        for document in values:
            if not document.is_valid_json and not visual_name_filter:
                continue
            if not self._matches_target(document, target):
                continue
            if self._matches(document, active_filter, visual_name_filter):
                matched_ids.add(document.id)
                visible_ids.add(document.id)

        if target == JsonFileType.PAGE.value:
            for document in values:
                if document.parent_page_id in matched_ids:
                    matched_ids.add(document.id)
                    visible_ids.add(document.id)
        elif target == JsonFileType.VISUAL.value:
            for document in values:
                if document.id in matched_ids and document.parent_page_id in pages_by_id:
                    visible_ids.add(document.parent_page_id)
        else:
            for document in values:
                if document.id in matched_ids and document.file_type == JsonFileType.VISUAL and document.parent_page_id in pages_by_id:
                    visible_ids.add(document.parent_page_id)

        return tuple(
            DocumentScopeState(
                document_id=document.id,
                is_active=document.id in matched_ids,
                is_visible=document.id in visible_ids,
                filter_color=active_filter.color if document.id in matched_ids else "",
            )
            for document in values
        )

    @staticmethod
    def _matches_target(document: JsonDocument, target: str) -> bool:
        return target == FILTER_TARGET_ALL or document.file_type_text == target

    @staticmethod
    def _is_visual_name_filter(content_filter: ContentFilter) -> bool:
        return any(rule.key.strip().casefold() == "visualname" for rule in content_filter.rules)

    @classmethod
    def _matches(cls, document: JsonDocument, content_filter: ContentFilter, visual_name_filter: bool) -> bool:
        if visual_name_filter:
            return all(cls._matches_visual_name_rule(document, rule) for rule in content_filter.rules)
        return ContentFilterMatcher.matches_filter(document.parsed_json, content_filter)

    @staticmethod
    def _matches_visual_name_rule(document: JsonDocument, rule: FilterRule) -> bool:
        if rule.operation not in FILTER_OPERATIONS:
            return False
        values = [
            str(value).casefold()
            for value in (document.display_name, document.pbir_name, document.path.parent.name, document.path.name, document.relative_path)
            if str(value).strip()
        ]
        needle = rule.value.casefold()
        if rule.operation == "equals":
            return any(value == needle for value in values)
        if rule.operation == "includes":
            return any(needle in value for value in values)
        if rule.operation == "notEquals":
            return all(value != needle for value in values)
        return all(needle not in value for value in values)
