from __future__ import annotations

import sys
from collections.abc import Sequence

from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtWidgets import QApplication, QStyleFactory

from bootstrap.dependency_container import ApplicationGraph, DependencyContainer
from bootstrap.qml_registration import register_qml_types
from ui.styles.native_styles import build_native_styles


ROOT_MODULE_URI = "ui.component.app"
ROOT_TYPE_NAME = "App"


def run(argv: Sequence[str] | None = None) -> int:
    app, engine, graph = create_app(list(sys.argv if argv is None else argv))
    if not engine.rootObjects():
        destroy_qml(app, engine, graph)
        return 1
    try:
        return app.exec()
    finally:
        destroy_qml(app, engine, graph)


def create_app(
    args: Sequence[str],
    *,
    container: DependencyContainer | None = None,
) -> tuple[QApplication, QQmlApplicationEngine, ApplicationGraph]:
    """Build the process and inject its explicit QML collaborators before loading."""

    QQuickStyle.setStyle("Fusion")
    app = QApplication(list(args))
    fusion = QStyleFactory.create("Fusion")
    if fusion is not None:
        app.setStyle(fusion)

    container = container or DependencyContainer()
    graph = container.build()
    app.setStyleSheet(build_native_styles(graph.theme))

    register_qml_types()
    engine = QQmlApplicationEngine()
    qml_warnings: list[str] = []
    engine.warnings.connect(lambda warnings: qml_warnings.extend(warning.toString() for warning in warnings))
    engine.addImportPath(str(graph.resource_locator.source_root()))
    engine.setInitialProperties(graph.qml_initial_properties())
    engine.loadFromModule(ROOT_MODULE_URI, ROOT_TYPE_NAME)
    if qml_warnings:
        for warning in qml_warnings:
            print(warning)
        destroy_qml(app, engine, graph)
        raise RuntimeError("QML module load emitted warning(s); see diagnostics above.")
    return app, engine, graph


def destroy_qml(app: QApplication, engine: QQmlApplicationEngine, graph: ApplicationGraph | None = None) -> None:
    if graph is not None:
        graph.editor_adapter.dispose_all()
    for root_object in engine.rootObjects():
        root_object.setProperty("visible", False)
        root_object.deleteLater()
    app.processEvents()
