from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ThemeTokens:
    activity_background: str = "#333333"
    panel_background: str = "#252526"
    editor_background: str = "#1e1e1e"
    header_background: str = "#2d2d30"
    status_background: str = "#007acc"
    border_color: str = "#3c3c3c"
    list_hover: str = "#2a2d2e"
    list_active: str = "#37373d"
    text_color: str = "#d4d4d4"
    muted_text: str = "#858585"
    accent_blue: str = "#0e639c"
    accent_blue_hover: str = "#1177bb"
    accent_green: str = "#16825d"
    accent_green_hover: str = "#1f9d72"
    accent_red: str = "#c44242"
    input_background: str = "#1b1b1c"
    warning_color: str = "#cca700"
    ok_color: str = "#3fb950"
    syntax_key: str = "#9cdcfe"
    syntax_string: str = "#ce9178"
    syntax_number: str = "#b5cea8"
    syntax_literal: str = "#569cd6"
    syntax_punctuation: str = "#d4d4d4"


DEFAULT_THEME = ThemeTokens()
