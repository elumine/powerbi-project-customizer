from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from entities.document.models import JsonDocument
from services.text.search_engine import SearchService

from features.search_replace.application.query import SearchQuery


@dataclass(frozen=True, slots=True)
class SearchDocumentView:
    document_id: str
    match_count: int
    previews: tuple[dict[str, str | int], ...]
    highlighted_html: str


class SearchProjectionService:
    """Pure search projection and text replacement algorithms for feature presenters."""

    def __init__(self, engine: type[SearchService] = SearchService) -> None:
        self._engine = engine

    def project(self, documents: Iterable[JsonDocument], query: SearchQuery) -> tuple[SearchDocumentView, ...]:
        views: list[SearchDocumentView] = []
        for document in documents:
            if document.is_active:
                match_count = self._engine.count(document.text, query.needle, query.case_sensitive)
                previews = tuple(self._engine.previews(document.text, query.needle, query.replacement, query.case_sensitive))
                highlighted = self._engine.highlighted_html(document.text, query.needle, query.replacement, query.case_sensitive)
            else:
                match_count = 0
                previews = ()
                highlighted = self._engine.highlighted_html(document.text, "")
            views.append(SearchDocumentView(document.id, match_count, previews, highlighted))
        return tuple(views)

    def match_span(self, text: str, query: SearchQuery, match_index: int) -> tuple[int, int] | None:
        return self._engine.match_span(text, query.needle, match_index, query.case_sensitive)

    def replace_span(self, text: str, start: int, end: int, query: SearchQuery) -> str:
        return self._engine.replace_span(text, start, end, query.replacement)

    def replace(self, text: str, query: SearchQuery) -> tuple[str, int]:
        return self._engine.replace(text, query.needle, query.replacement, query.case_sensitive)
