import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property bool enabled: true
    readonly property int panelSpacing: Spacing.sm
    readonly property color resultBackground: Theme.inputBackground
    readonly property color resultHover: Theme.controlBackground
}
