from __future__ import annotations

from weakref import WeakKeyDictionary

from PySide6.QtCore import QObject, QRegularExpression, Slot
from PySide6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat

from ui.styles.theme_tokens import DEFAULT_THEME, ThemeTokens


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document, theme: ThemeTokens = DEFAULT_THEME) -> None:
        super().__init__(document)
        self._formats = {
            "key": self._make_format(theme.syntax_key),
            "string": self._make_format(theme.syntax_string),
            "number": self._make_format(theme.syntax_number),
            "literal": self._make_format(theme.syntax_literal),
            "punctuation": self._make_format(theme.syntax_punctuation),
        }
        self._rules = [
            (QRegularExpression(r'"(?:\\.|[^"\\])*"'), self._formats["string"]),
            (QRegularExpression(r'"(?:\\.|[^"\\])*"(?=\s*:)'), self._formats["key"]),
            (QRegularExpression(r"\b-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?\b"), self._formats["number"]),
            (QRegularExpression(r"\b(?:true|false|null)\b"), self._formats["literal"]),
            (QRegularExpression(r"[\{\}\[\],:]"), self._formats["punctuation"]),
        ]

    def highlightBlock(self, text: str) -> None:
        for pattern, text_format in self._rules:
            matches = pattern.globalMatch(text)
            while matches.hasNext():
                match = matches.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), text_format)

    @staticmethod
    def _make_format(color: str) -> QTextCharFormat:
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        return text_format


class SyntaxHighlighterBridge(QObject):
    """Owns at most one highlighter per live Qt text document."""

    def __init__(self, theme: ThemeTokens = DEFAULT_THEME) -> None:
        super().__init__()
        self._theme = theme
        self._highlighters: WeakKeyDictionary[object, JsonSyntaxHighlighter] = WeakKeyDictionary()

    @Slot(QObject)
    def attach(self, quick_text_document: QObject) -> None:
        if quick_text_document is None or not hasattr(quick_text_document, "textDocument"):
            return
        text_document = quick_text_document.textDocument()
        if text_document is None or text_document in self._highlighters:
            return
        self._highlighters[text_document] = JsonSyntaxHighlighter(text_document, self._theme)

    @Slot(QObject)
    def dispose(self, quick_text_document: QObject) -> None:
        if quick_text_document is None or not hasattr(quick_text_document, "textDocument"):
            return
        text_document = quick_text_document.textDocument()
        highlighter = self._highlighters.pop(text_document, None)
        if highlighter is not None:
            highlighter.setDocument(None)
            highlighter.deleteLater()

    def dispose_all(self) -> None:
        for highlighter in tuple(self._highlighters.values()):
            highlighter.setDocument(None)
            highlighter.deleteLater()
        self._highlighters.clear()
