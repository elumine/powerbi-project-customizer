from __future__ import annotations

import re

from features.search_replace.application.query import SearchQuery
from features.search_replace.application.service import SearchProjectionService
from services.documents.workspace_port import DocumentWorkspacePort


class SearchController:
    """Feature controller for search, replace, previews, and match navigation."""

    def __init__(self, file_model: DocumentWorkspacePort, projection: SearchProjectionService | None = None) -> None:
        self._files = file_model
        self._projection = projection or SearchProjectionService()
        self._query = SearchQuery()
        self._total_matches = 0
        self._active_match_file_index = -1
        self._active_match_index = -1
        self._active_match_line = 0
        self._active_match_start = -1
        self._active_match_end = -1

    @property
    def search_text(self) -> str:
        return self._query.needle

    @property
    def replace_text(self) -> str:
        return self._query.replacement

    @property
    def case_sensitive(self) -> bool:
        return self._query.case_sensitive

    @property
    def total_matches(self) -> int:
        return self._total_matches

    @property
    def active_match_file_index(self) -> int:
        return self._active_match_file_index

    @property
    def active_match_index(self) -> int:
        return self._active_match_index

    @property
    def active_match_line(self) -> int:
        return self._active_match_line

    @property
    def active_match_start(self) -> int:
        return self._active_match_start

    @property
    def active_match_end(self) -> int:
        return self._active_match_end

    @property
    def active_match_display_index(self) -> int:
        return self._active_match_index + 1 if self._active_match_index >= 0 else 0

    def active_match_file_count(self) -> int:
        document = self._files.document_at(self._active_match_file_index)
        return document.match_count if document is not None and document.is_active else 0

    def reset(self) -> None:
        self._query = SearchQuery()
        self._total_matches = 0
        self._reset_active_match()
        self.refresh()

    def set_search_text(self, text: str) -> bool:
        value = text or ""
        if value == self._query.needle:
            return False
        self._query.needle = value
        return True

    def set_replace_text(self, text: str) -> bool:
        value = text or ""
        if value == self._query.replacement:
            return False
        self._query.replacement = value
        return True

    def set_case_sensitive(self, value: bool) -> bool:
        normalized = bool(value)
        if normalized == self._query.case_sensitive:
            return False
        self._query.case_sensitive = normalized
        return True

    def execute_search(self) -> bool:
        """Run the currently drafted query only when the user explicitly requests it."""
        self.refresh()
        return not self._query.is_empty

    def refresh(self) -> None:
        self._total_matches = 0
        for view in self._projection.project(self._files.collection.documents(), self._query):
            row = self._files.document_index_by_id(view.document_id)
            self._files.refresh_search_view(row, view.match_count, list(view.previews), view.highlighted_html)
            self._total_matches += view.match_count
        self._ensure_active_match_is_valid()

    def replace_current_match(self) -> int:
        if self._query.is_empty:
            return 0

        locations = self._match_locations()
        if not locations:
            self._reset_active_match()
            return 0

        current = (self._active_match_file_index, self._active_match_index)
        if current not in locations:
            current = locations[0]
        row, match_index = current
        document = self._files.document_at(row)
        if document is None or not document.is_active:
            return 0

        span = self._projection.match_span(document.text, self._query, match_index)
        if span is None:
            self.refresh()
            return self.replace_current_match()

        start, end = span
        new_text = self._projection.replace_span(document.text, start, end, self._query)
        if new_text == document.text:
            return 0

        self._files.set_document_text(row, new_text)
        self.refresh()
        self.navigate_next()
        return 1

    def replace_current_file(self, row: int) -> int:
        document = self._files.document_at(row)
        if document is None or not document.is_active or self._query.is_empty:
            return 0

        new_text, replacement_count = self._projection.replace(document.text, self._query)
        if replacement_count > 0:
            self._files.set_document_text(row, new_text)
        self.refresh()
        return replacement_count

    def replace_all(self) -> int:
        if self._query.is_empty:
            return 0

        total = 0
        for row, document in enumerate(self._files.documents()):
            if not document.is_active:
                continue
            new_text, replacement_count = self._projection.replace(document.text, self._query)
            if replacement_count > 0:
                self._files.set_document_text(row, new_text)
                total += replacement_count

        self.refresh()
        return total

    def navigate_to_match(self, file_index: int, match_index: int) -> bool:
        document = self._files.document_at(file_index)
        if document is None or not document.is_active:
            return False
        if not 0 <= match_index < document.match_count:
            return False
        span = self._projection.match_span(document.text, self._query, match_index)
        if span is None:
            self.refresh()
            return False

        self._active_match_file_index = file_index
        self._active_match_index = match_index
        self._active_match_start, self._active_match_end = span
        self._active_match_line = document.text.count("\n", 0, self._active_match_start) + 1
        return True

    def navigate_next(self) -> bool:
        locations = self._match_locations()
        if not locations:
            self._reset_active_match()
            return False

        current = (self._active_match_file_index, self._active_match_index)
        try:
            next_index = locations.index(current) + 1
        except ValueError:
            next_index = 0
        return self.navigate_to_match(*locations[next_index % len(locations)])

    def navigate_previous(self) -> bool:
        locations = self._match_locations()
        if not locations:
            self._reset_active_match()
            return False

        current = (self._active_match_file_index, self._active_match_index)
        try:
            previous_index = locations.index(current) - 1
        except ValueError:
            previous_index = len(locations) - 1
        return self.navigate_to_match(*locations[previous_index])

    def _match_locations(self) -> list[tuple[int, int]]:
        locations: list[tuple[int, int]] = []
        for row, document in enumerate(self._files.documents()):
            if not document.is_active:
                continue
            locations.extend((row, match_index) for match_index in range(document.match_count))
        return locations

    def _ensure_active_match_is_valid(self) -> None:
        if self._query.is_empty or self._total_matches == 0:
            self._reset_active_match()
            return
        document = self._files.document_at(self._active_match_file_index)
        valid_match = document is not None and 0 <= self._active_match_index < document.match_count
        if document is None or not document.is_active or not valid_match:
            self.navigate_next()
            return
        self.navigate_to_match(self._active_match_file_index, self._active_match_index)

    def _reset_active_match(self) -> None:
        self._active_match_file_index = -1
        self._active_match_index = -1
        self._active_match_line = 0
        self._active_match_start = -1
        self._active_match_end = -1

    def _line_for_match_index(self, text: str, match_index: int) -> int:
        if self._query.is_empty:
            return 0
        flags = 0 if self._query.case_sensitive else re.IGNORECASE
        for index, match in enumerate(re.finditer(re.escape(self._query.needle), text, flags)):
            if index == match_index:
                return text.count("\n", 0, match.start()) + 1
        return 0
