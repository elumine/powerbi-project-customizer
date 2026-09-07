from __future__ import annotations

from collections.abc import Iterable

from entities.document.models import JsonDocument
from features.history.domain.models import FileSnapshot


class HistoryRecorder:
    """Captures and compares document state outside the shell presentation facade."""

    @staticmethod
    def capture(documents: Iterable[JsonDocument]) -> dict[str, tuple[str, str, bool]]:
        return {
            document.id: (document.text, document.original_text or "", document.is_dirty)
            for document in documents
        }

    @staticmethod
    def changes(before: dict[str, tuple[str, str, bool]], documents: Iterable[JsonDocument]) -> list[FileSnapshot]:
        changes: list[FileSnapshot] = []
        for document in documents:
            previous = before.get(document.id)
            if previous is None:
                continue
            before_text, before_original_text, before_dirty = previous
            after = (document.text, document.original_text or "", document.is_dirty)
            if previous == after:
                continue
            changes.append(FileSnapshot(
                document_id=document.id,
                path=str(document.path),
                before_text=before_text,
                after_text=after[0],
                before_original_text=before_original_text,
                after_original_text=after[1],
                before_dirty=before_dirty,
                after_dirty=after[2],
            ))
        return changes
