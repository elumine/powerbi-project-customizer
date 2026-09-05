from __future__ import annotations

import re

from app.core.search_service import SearchService
from app.features.search_replace.search_query import SearchQuery
from app.ui.file_list_model import FileListModel


class SearchController:
    """Feature controller for search, replace, previews, and match navigation."""

    def __init__(self, file_model: FileListModel, service: type[SearchService] = SearchService) -> None:
        self._files = file_model
        self._service = service
        self._query = SearchQuery()
        self._total_matches = 0
        self._active_match_file_index = -1
        self._active_match_index = -1
        self._active_match_line = 0

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
    def active_match_display_index(self) -> int:
        return self._active_match_index + 1 if self._active_match_index >= 0 else 0

    def active_match_file_count(self) -> int:
        document = self._files.document_at(self._active_match_file_index)
        return document.match_count if document is not None and document.is_active else 0

    def set_search_text(self, text: str) -> bool:
        value = text or ""
        if value == self._query.needle:
            return False
        self._query.needle = value
        self.refresh()
        return True

    def set_replace_text(self, text: str) -> bool:
        value = text or ""
        if value == self._query.replacement:
            return False
        self._query.replacement = value
        self.refresh()
        return True

    def set_case_sensitive(self, value: bool) -> bool:
        normalized = bool(value)
        if normalized == self._query.case_sensitive:
            return False
        self._query.case_sensitive = normalized
        self.refresh()
        return True

    def refresh(self) -> None:
        self._total_matches = 0
        for row, document in enumerate(self._files.documents()):
            if document.is_active:
                match_count = self._service.count(document.text, self._query.needle, self._query.case_sensitive)
                previews = self._service.previews(
                    document.text,
                    self._query.needle,
                    self._query.replacement,
                    self._query.case_sensitive,
                )
                highlighted_html = self._service.highlighted_html(
                    document.text,
                    self._query.needle,
                    self._query.replacement,
                    self._query.case_sensitive,
                )
            else:
                match_count = 0
                previews = []
                highlighted_html = self._service.highlighted_html(document.text, "")

            self._files.refresh_search_view(row, match_count, previews, highlighted_html)
            self._total_matches += match_count

        self._ensure_active_match_is_valid()

    def replace_current_file(self, row: int) -> int:
        document = self._files.document_at(row)
        if document is None or not document.is_active or self._query.is_empty:
            return 0

        new_text, replacement_count = self._service.replace(
            document.text,
            self._query.needle,
            self._query.replacement,
            self._query.case_sensitive,
        )
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
            new_text, replacement_count = self._service.replace(
                document.text,
                self._query.needle,
                self._query.replacement,
                self._query.case_sensitive,
            )
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

        self._active_match_file_index = file_index
        self._active_match_index = match_index
        self._active_match_line = self._line_for_match_index(document.text, match_index)
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

    def _reset_active_match(self) -> None:
        self._active_match_file_index = -1
        self._active_match_index = -1
        self._active_match_line = 0

    def _line_for_match_index(self, text: str, match_index: int) -> int:
        if self._query.is_empty:
            return 0
        flags = 0 if self._query.case_sensitive else re.IGNORECASE
        for index, match in enumerate(re.finditer(re.escape(self._query.needle), text, flags)):
            if index == match_index:
                return text.count("\n", 0, match.start()) + 1
        return 0
