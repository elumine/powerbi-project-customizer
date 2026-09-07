from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.document.models import JsonDocument


class DocumentChangeKind(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    CONTENT_CHANGED = "content_changed"
    SAVE_STATE_CHANGED = "save_state_changed"
    PRESENTATION_CHANGED = "presentation_changed"
    RESET = "reset"


@dataclass(frozen=True, slots=True)
class DocumentChange:
    """A collection event expressed with stable document identity, never a UI row."""

    kind: DocumentChangeKind
    document_id: str = ""
    index: int = -1
    previous_index: int = -1
    document: JsonDocument | None = None


@dataclass(frozen=True, slots=True)
class DocumentSnapshot:
    document_id: str
    text: str
    original_text: str
    is_dirty: bool


@dataclass(frozen=True, slots=True)
class CommittedChangeSet:
    """The exact state changes committed by a document operation."""

    operation: str
    snapshots: tuple[DocumentSnapshot, ...]

    @property
    def changed_count(self) -> int:
        return len(self.snapshots)

    @property
    def is_empty(self) -> bool:
        return not self.snapshots
