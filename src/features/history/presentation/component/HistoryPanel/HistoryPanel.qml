import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "HistoryPanelLogic.js" as Logic

ColumnLayout {
    HistoryPanelStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    required property var app
    spacing: style.panelSpacing
                            RowLayout {
                                Layout.fillWidth: true
                                PanelTitle { text: "HISTORY"; Layout.fillWidth: true }
                                Text { text: app.controller.historyCount + " row(s)"; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                            }
                            MutedLabel { Layout.fillWidth: true; text: app.controller.historyCurrentIndex >= 0 ? "Current row " + app.controller.historyCurrentIndex : "No history yet." }
                            ListView { id: historyList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 5; model: app.controller.historyModel
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                                delegate: Rectangle {
                                    width: historyList.width
                                    height: 64
                                    radius: 3
                                    color: rowState === "current" ? "#0e7490" : rowState === "previous" ? "#1f5f46" : "#6b2d35"
                                    border.color: historyMouse.containsMouse && rowState !== "current" ? "#ffffff" : app.borderColor
                                    opacity: reversible ? 1.0 : 0.65
                                    MouseArea { id: historyMouse; anchors.fill: parent; hoverEnabled: true; enabled: rowState !== "current"; onClicked: { var savedY = historyList.contentY; app.callController(function(c) { c.goToHistoryIndex(historyIndex) }); historyList.contentY = savedY } }
                                    ColumnLayout { anchors.fill: parent; anchors.margins: 7; spacing: 3
                                        Text { Layout.fillWidth: true; text: "[ " + historyIndex + " ] [ " + timeText + " ] [ " + operationType + " ]"; color: "#ffffff"; font.family: "Consolas"; font.pixelSize: 10; elide: Text.ElideRight }
                                        Text { Layout.fillWidth: true; text: displayName + (metadataText.length > 0 ? " ( " + metadataText + " )" : ""); color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 12; font.bold: rowState === "current"; elide: Text.ElideRight }
                                    }
                                }
                            }
                            MutedLabel { visible: app.controller.historyCount === 0; Layout.fillWidth: true; text: "No operations recorded." }
                        }
