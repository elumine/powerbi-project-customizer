import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "PanelsSidebarLogic.js" as Logic

                Rectangle {
    PanelsSidebarStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    required property var app
    Layout.preferredWidth: Math.max(style.minimumWidth, Math.min(110, app.width * 0.10))
    Layout.fillHeight: true
    color: app.activityBackground
                    ColumnLayout { anchors.fill: parent; spacing: 0
                        PanelButton { text: "E"; tooltipText: "Explorer"; active: app.activePanel === "explorer"; onClicked: app.activePanel = "explorer" }
                        PanelButton { text: "S"; tooltipText: "Search"; active: app.activePanel === "search"; onClicked: app.activePanel = "search" }
                        PanelButton { text: "F"; tooltipText: "Filters"; active: app.activePanel === "filters"; onClicked: app.activePanel = "filters" }
                        PanelButton { text: "!"; tooltipText: "Suggestions"; active: app.activePanel === "suggestions"; onClicked: app.activePanel = "suggestions" }
                        PanelButton { text: "V"; tooltipText: "Visuals Editor"; active: app.activePanel === "visuals"; onClicked: app.activePanel = "visuals" }
                        PanelButton { text: "H"; tooltipText: "History"; active: app.activePanel === "history"; onClicked: app.activePanel = "history" }
                        PanelButton { text: "M"; tooltipText: "Macros"; active: app.activePanel === "macros"; onClicked: app.activePanel = "macros" }
                        Item { Layout.fillHeight: true }
                    }
                }
