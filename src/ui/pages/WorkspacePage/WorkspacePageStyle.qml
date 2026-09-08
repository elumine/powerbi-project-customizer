import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property bool enabled: true
    readonly property color background: Theme.appBackground
    readonly property color panel: Theme.cardBackground
    readonly property color editor: Theme.editorBackground
    readonly property real sidebarRatio: 0.10
    readonly property int sidebarMinimumWidth: Geometry.sidebarWidth
    readonly property int panelMinimumWidth: 240
}
