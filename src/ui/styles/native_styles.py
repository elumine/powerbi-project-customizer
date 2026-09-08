from __future__ import annotations

from ui.styles.theme_tokens import ThemeTokens


def build_native_styles(theme: ThemeTokens) -> str:
    """Create the Qt Widgets dialog stylesheet from the shared palette constants."""

    return f'''
QWidget {{
    background-color: {theme.editor_background};
    color: {theme.text_color};
    font-family: "Segoe UI Variable";
    font-size: 12pt;
}}
QFileDialog, QMessageBox {{
    background-color: {theme.panel_background};
    color: {theme.text_color};
}}
QLineEdit, QPlainTextEdit, QTextEdit, QListView, QTreeView {{
    background-color: {theme.input_background};
    border: 1px solid {theme.border_color};
    border-radius: 7px;
    color: {theme.text_color};
    selection-background-color: {theme.selection_color};
}}
QPushButton {{
    background-color: {theme.action_execute};
    border: 1px solid {theme.action_execute_hover};
    border-radius: 7px;
    color: {theme.white};
    padding: 7px 12px;
}}
QPushButton:hover {{ background-color: {theme.action_execute_hover}; }}
QPushButton:pressed {{ background-color: {theme.action_execute_pressed}; }}
QPushButton:disabled {{
    background-color: {theme.control_background};
    border-color: {theme.border_subtle};
    color: {theme.dim_text};
}}
'''.strip()
