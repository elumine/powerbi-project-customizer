from __future__ import annotations

from collections.abc import Iterable

from entities.document.models import JsonDocument
from entities.powerbi.file_types import JsonFileType


class PageVisualLinker:
    """Rebuilds the derived page-to-visual relationship graph deterministically."""

    @staticmethod
    def rebuild(documents: Iterable[JsonDocument]) -> None:
        values = tuple(documents)
        pages_by_folder = {}
        for document in values:
            document.visual_ids.clear()
            if document.file_type == JsonFileType.VISUAL:
                document.parent_page_id = ""
            elif document.file_type == JsonFileType.PAGE:
                pages_by_folder[document.path.parent] = document
        for document in values:
            if document.file_type != JsonFileType.VISUAL:
                continue
            for parent in document.path.parents:
                page = pages_by_folder.get(parent)
                if page is not None:
                    document.parent_page_id = page.id
                    if document.id not in page.visual_ids:
                        page.visual_ids.append(document.id)
                    break
