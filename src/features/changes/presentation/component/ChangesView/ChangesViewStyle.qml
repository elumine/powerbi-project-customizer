import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property bool enabled: true
    readonly property int panelSpacing: Spacing.sm
    readonly property color surface: Theme.editorBackground
    readonly property color headerSurface: Theme.cardBackground
    readonly property color border: Theme.borderSubtle
    readonly property color addedBackground: Qt.rgba(0.16, 0.55, 0.35, 0.24)
    readonly property color removedBackground: Qt.rgba(0.82, 0.25, 0.28, 0.24)
    readonly property color addedGutter: Qt.rgba(0.16, 0.55, 0.35, 0.40)
    readonly property color removedGutter: Qt.rgba(0.82, 0.25, 0.28, 0.40)
    // Diff content sits on a near-black editor surface; never inherit a
    // platform-default black text color here.
    readonly property color contextText: Theme.diffContextText
    readonly property int lineHeight: 24
    readonly property int gutterWidth: 52
}
