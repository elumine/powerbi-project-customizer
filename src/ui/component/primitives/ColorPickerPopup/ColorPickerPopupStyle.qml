import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property color background: Theme.panelBackground
    readonly property color surface: Theme.cardBackground
    readonly property color fieldBackground: Theme.inputBackground
    readonly property color border: Theme.borderColor
    readonly property color selection: Theme.actionExecute
    readonly property color muted: Theme.mutedText
    readonly property int pickerSize: 228
}
