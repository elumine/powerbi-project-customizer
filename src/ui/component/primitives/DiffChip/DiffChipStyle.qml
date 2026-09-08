import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property color defaultColor: Theme.warningColor
    readonly property color textColor: Theme.black
    readonly property color activeBorder: Theme.white
    readonly property int radius: Geometry.radiusXs
}
