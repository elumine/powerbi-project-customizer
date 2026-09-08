import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property bool enabled: true
    readonly property int height: Geometry.toolbarHeight
    readonly property color background: Theme.headerBackground
    readonly property color border: Theme.borderSubtle
    readonly property color activeTab: Theme.accentBlue
    readonly property color idleTab: Theme.mutedText
}
