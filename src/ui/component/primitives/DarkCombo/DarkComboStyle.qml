import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property int itemHeight: Geometry.controlHeight
    readonly property color background: Theme.inputBackground
    readonly property color hoverBackground: Theme.controlHover
    readonly property color border: Theme.borderSubtle
    readonly property color focusBorder: Theme.accentBlue
}
