import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property color normalColor: Theme.actionExecute
    readonly property color hoverColor: Theme.actionExecuteHover
    readonly property color pressedColor: Theme.actionExecutePressed
    readonly property color disabledColor: Theme.controlBackground
    readonly property color contentColor: Theme.white
    readonly property color disabledContentColor: Theme.dimText
    readonly property int radius: Geometry.radiusSm
    readonly property int horizontalPadding: Spacing.md
}
