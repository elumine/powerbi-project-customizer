from __future__ import annotations


def register_qml_types() -> None:
    """Reserve a single registration boundary for future Python-backed QML types.

    The theme is a QML singleton declared in ``ui.styles/qmldir`` so every engine
    can import it safely. Runtime feature collaborators are supplied only through
    root initial properties, never global context properties or singletons.
    """
