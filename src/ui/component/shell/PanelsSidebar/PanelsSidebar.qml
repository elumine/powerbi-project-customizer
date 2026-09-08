import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "PanelsSidebarLogic.js" as Logic

Rectangle {
    id: sidebar
    PanelsSidebarStyle { id: style }

    required property var app
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    // The workspace row owns the 10% responsive width for this rail.
    Layout.fillHeight: true
    color: style.background
    border.width: Geometry.borderWidth
    border.color: style.border

    ColumnLayout {
        anchors.fill: parent
        anchors.topMargin: Spacing.sm
        anchors.bottomMargin: Spacing.sm
        spacing: Spacing.xs

        Repeater {
            model: [
                { "icon": Qt.resolvedUrl("../../../assets/icons/workspace.svg"), "panel": "explorer", "label": "Workspace" },
                { "icon": Qt.resolvedUrl("../../../assets/icons/changes.svg"), "panel": "changes", "label": "Changes" },
                { "icon": Qt.resolvedUrl("../../../assets/icons/search.svg"), "panel": "search", "label": "Search" },
                { "icon": Qt.resolvedUrl("../../../assets/icons/filters.svg"), "panel": "filters", "label": "Filters" },
                { "icon": Qt.resolvedUrl("../../../assets/icons/visuals.svg"), "panel": "visuals", "label": "Visuals" },
                { "icon": Qt.resolvedUrl("../../../assets/icons/history.svg"), "panel": "history", "label": "History" },
                { "icon": Qt.resolvedUrl("../../../assets/icons/macros.svg"), "panel": "macros", "label": "Macros" }
            ]
            delegate: PanelButton {
                required property var modelData
                Layout.alignment: Qt.AlignHCenter
                iconSource: modelData.icon
                tooltipText: modelData.label
                active: app.activePanel === modelData.panel
                onClicked: app.activePanel = modelData.panel
            }
        }

        Item { Layout.fillHeight: true }

        PanelButton {
            Layout.alignment: Qt.AlignHCenter
            iconSource: Qt.resolvedUrl("../../../assets/icons/insights.svg")
            tooltipText: "Insights"
            active: app.activePanel === "suggestions"
            onClicked: app.activePanel = "suggestions"
        }

        Rectangle {
            Layout.alignment: Qt.AlignHCenter
            Layout.preferredWidth: 28
            Layout.preferredHeight: 28
            radius: Geometry.radiusSm
            color: app.cardBackground
            border.width: Geometry.borderWidth
            border.color: app.borderSubtle
            Text {
                anchors.centerIn: parent
                text: app.controller.fileCount
                color: app.mutedText
                font.family: Typography.dataFamily
                font.pixelSize: Typography.captionSize
            }
        }
    }
}
