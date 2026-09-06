from __future__ import annotations

import html
import re


class SearchService:
    PREVIEW_RADIUS = 42
    MAX_PREVIEWS = 200

    @staticmethod
    def count(text: str, needle: str, case_sensitive: bool = False) -> int:
        if needle == "":
            return 0

        flags = 0 if case_sensitive else re.IGNORECASE
        return len(re.findall(re.escape(needle), text, flags))

    @staticmethod
    def replace(
        text: str,
        needle: str,
        replacement: str,
        case_sensitive: bool = False,
    ) -> tuple[str, int]:
        if needle == "":
            return text, 0

        flags = 0 if case_sensitive else re.IGNORECASE
        return re.subn(re.escape(needle), lambda _match: replacement, text, flags=flags)

    @classmethod
    def match_span(cls, text: str, needle: str, match_index: int, case_sensitive: bool = False) -> tuple[int, int] | None:
        if needle == "" or match_index < 0:
            return None
        flags = 0 if case_sensitive else re.IGNORECASE
        for index, match in enumerate(re.finditer(re.escape(needle), text, flags)):
            if index == match_index:
                return match.start(), match.end()
        return None

    @classmethod
    def replace_span(cls, text: str, start: int, end: int, replacement: str) -> str:
        if start < 0 or end < start or end > len(text):
            return text
        return text[:start] + replacement + text[end:]

    @classmethod
    def previews(
        cls,
        text: str,
        needle: str,
        replacement: str = "",
        case_sensitive: bool = False,
    ) -> list[dict[str, str | int]]:
        if needle == "":
            return []

        flags = 0 if case_sensitive else re.IGNORECASE
        previews: list[dict[str, str | int]] = []
        for match_index, match in enumerate(re.finditer(re.escape(needle), text, flags)):
            if match_index >= cls.MAX_PREVIEWS:
                break
            start = max(0, match.start() - cls.PREVIEW_RADIUS)
            end = min(len(text), match.end() + cls.PREVIEW_RADIUS)
            before = text[start:match.start()]
            after = text[match.end():end]
            previews.append(
                {
                    "before": cls._compact(before, prefix=start > 0),
                    "match": match.group(0),
                    "after": cls._compact(after, suffix=end < len(text)),
                    "replacement": replacement,
                    "index": match_index,
                    "line": text.count("\n", 0, match.start()) + 1,
                    "start": match.start(),
                    "end": match.end(),
                }
            )
        return previews

    @classmethod
    def highlighted_html(
        cls,
        text: str,
        needle: str,
        replacement: str = "",
        case_sensitive: bool = False,
    ) -> str:
        escaped_font = "Consolas, 'Courier New', monospace"
        if needle == "":
            body = html.escape(text)
            return f"<pre style=\"font-family:{escaped_font}; font-size:14px; color:#d4d4d4;\">{body}</pre>"

        flags = 0 if case_sensitive else re.IGNORECASE
        parts: list[str] = []
        last_end = 0
        for match in re.finditer(re.escape(needle), text, flags):
            parts.append(html.escape(text[last_end:match.start()]))
            matched = html.escape(match.group(0))
            if replacement:
                replaced = html.escape(replacement)
                parts.append(
                    '<span style="background-color:#6f2424;color:#ffd7d7;">'
                    + matched
                    + '</span><span style="background-color:#183f2a;color:#c6f6d5;">'
                    + replaced
                    + '</span>'
                )
            else:
                parts.append('<span style="background-color:#5a4a00;color:#fff4b8;">' + matched + '</span>')
            last_end = match.end()
        parts.append(html.escape(text[last_end:]))
        body = "".join(parts)
        return f"<pre style=\"font-family:{escaped_font}; font-size:14px; color:#d4d4d4;\">{body}</pre>"

    @staticmethod
    def _compact(value: str, prefix: bool = False, suffix: bool = False) -> str:
        compacted = " ".join(value.split())
        if prefix and compacted:
            compacted = "... " + compacted
        if suffix and compacted:
            compacted = compacted + " ..."
        return compacted
