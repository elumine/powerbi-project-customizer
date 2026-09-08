from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass(frozen=True, slots=True)
class DiffLine:
    kind: str
    text: str
    old_line: int | None
    new_line: int | None
    prefix: str

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "text": self.text,
            "oldLine": self.old_line if self.old_line is not None else "",
            "newLine": self.new_line if self.new_line is not None else "",
            "prefix": self.prefix,
        }


class ChangeDiffService:
    """Builds a deterministic, line-oriented diff for QML presentation."""

    def build(self, before_text: str, after_text: str) -> list[dict[str, object]]:
        before = before_text.splitlines()
        after = after_text.splitlines()
        result: list[DiffLine] = []
        matcher = SequenceMatcher(a=before, b=after, autojunk=False)
        for tag, before_start, before_end, after_start, after_end in matcher.get_opcodes():
            if tag == "equal":
                for offset in range(before_end - before_start):
                    result.append(DiffLine(
                        "context",
                        before[before_start + offset],
                        before_start + offset + 1,
                        after_start + offset + 1,
                        " ",
                    ))
            elif tag == "delete":
                for index in range(before_start, before_end):
                    result.append(DiffLine("removed", before[index], index + 1, None, "-"))
            elif tag == "insert":
                for index in range(after_start, after_end):
                    result.append(DiffLine("added", after[index], None, index + 1, "+"))
            else:  # replace: present deleted lines before inserted lines like VS Code.
                for index in range(before_start, before_end):
                    result.append(DiffLine("removed", before[index], index + 1, None, "-"))
                for index in range(after_start, after_end):
                    result.append(DiffLine("added", after[index], None, index + 1, "+"))
        return [line.to_dict() for line in result]

    def line_counts(self, before_text: str, after_text: str) -> tuple[int, int]:
        before = before_text.splitlines()
        after = after_text.splitlines()
        added = removed = 0
        for tag, before_start, before_end, after_start, after_end in SequenceMatcher(
            a=before, b=after, autojunk=False
        ).get_opcodes():
            if tag in {"insert", "replace"}:
                added += after_end - after_start
            if tag in {"delete", "replace"}:
                removed += before_end - before_start
        return added, removed
