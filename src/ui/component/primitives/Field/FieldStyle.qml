import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property color selectedTextColor: Theme.white
    readonly property color selectionColor: Theme.selectionColor
    readonly property color background: Theme.inputBackground
    readonly property color focusedBackground: Theme.inputFocus
    readonly property color border: Theme.borderSubtle
    readonly property color focusedBorder: Theme.accentBlue
}
