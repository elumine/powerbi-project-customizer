import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property color contentColor: Theme.textColor
    readonly property color idleBackground: "transparent"
    readonly property color hoverBackground: Theme.controlHover
    readonly property color pressedBackground: Theme.listActive
}
