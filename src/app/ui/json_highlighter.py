from __future__ import annotations

from PySide6.QtCore import QObject, QRegularExpression, Slot
from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document) -> None:
        super().__init__(document)
        self._formats = {
            "key": self._make_format("#9cdcfe"),
            "string": self._make_format("#ce9178"),
            "number": self._make_format("#b5cea8"),
            "literal": self._make_format("#569cd6"),
            "punctuation": self._make_format("#d4d4d4"),
        }
        self._rules = [
            (QRegularExpression(r'"(?:\\.|[^"\\])*"'), self._formats["string"]),
            (QRegularExpression(r'"(?:\\.|[^"\\])*"(?=\s*:)'), self._formats["key"]),
            (
                QRegularExpression(r"\b-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b"),
                self._formats["number"],
            ),
            (QRegularExpression(r"\b(?:true|false|null)\b"), self._formats["literal"]),
            (QRegularExpression(r"[\{\}\[\],:]"), self._formats["punctuation"]),
        ]

    def highlightBlock(self, text: str) -> None:
        for pattern, text_format in self._rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), text_format)

    @staticmethod
    def _make_format(color: str) -> QTextCharFormat:
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        return text_format


class SyntaxHighlighterBridge(QObject):
    def __init__(self) -> None:
        super().__init__()
        self._highlighters: list[JsonSyntaxHighlighter] = []

    @Slot(QObject)
    def attach(self, quick_text_document: QObject) -> None:
        if quick_text_document is None or not hasattr(quick_text_document, "textDocument"):
            return

        highlighter = JsonSyntaxHighlighter(quick_text_document.textDocument())
        self._highlighters.append(highlighter)
