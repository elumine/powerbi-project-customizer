import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property bool enabled: true
    readonly property int minimumWidth: Geometry.sidebarWidth
    readonly property color background: Theme.activityBackground
    readonly property color border: Theme.borderSubtle
}
