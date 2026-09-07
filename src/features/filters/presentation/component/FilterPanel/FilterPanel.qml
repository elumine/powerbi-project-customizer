import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "FilterPanelLogic.js" as Logic

ColumnLayout {
    FilterPanelStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    required property var app
    spacing: style.panelSpacing
                            RowLayout {
                                Layout.fillWidth: true
                                PanelTitle { text: "FILTERS"; Layout.fillWidth: true }
                                IconButton { text: "+"; ToolTip.visible: hovered; ToolTip.text: "New filter"; onClicked: app.callController(function(c) { c.openNewFilterEditor() }) }
                            }
                            RowLayout { Layout.fillWidth: true; spacing: 6
                                ChromeButton { Layout.fillWidth: true; text: "Import"; onClicked: app.callController(function(c) { c.importFilter() }) }
                                ChromeButton { Layout.fillWidth: true; text: "Reload"; onClicked: app.callController(function(c) { c.reloadContent() }) }
                                ChromeButton { Layout.fillWidth: true; text: "Clear"; enabled: app.controller.hasActiveFilter; onClicked: app.callController(function(c) { c.deactivateFilter() }) }
                            }
                            ListView { id: filterList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 6; model: app.controller.filterModel
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                                delegate: Rectangle { width: filterList.width; height: 88; color: active ? app.listActive : filterMouse.containsMouse ? app.listHover : app.editorBackground; border.color: active ? color : app.borderColor; radius: 4
                                    MouseArea { id: filterMouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }
                                    ColumnLayout { anchors.fill: parent; anchors.margins: 7; spacing: 4
                                        RowLayout { Layout.fillWidth: true; spacing: 6
                                            Rectangle { Layout.preferredWidth: 10; Layout.preferredHeight: 10; radius: 5; color: color }
                                            Text { Layout.fillWidth: true; text: displayName; color: app.textColor; font.family: "Segoe UI"; font.pixelSize: 12; font.bold: true; elide: Text.ElideRight }
                                            Text { text: targetJsonFileType; color: app.okColor; font.family: "Segoe UI"; font.pixelSize: 10 }
                                        }
                                        Text { Layout.fillWidth: true; text: ruleSummary; color: app.mutedText; font.family: "Consolas"; font.pixelSize: 10; elide: Text.ElideRight }
                                        RowLayout { Layout.fillWidth: true; spacing: 6
                                            ChromeButton { text: active ? "Active" : "Apply"; enabled: !active; onClicked: app.callController(function(c) { c.applyFilter(index) }) }
                                            ChromeButton { text: "Export"; onClicked: app.callController(function(c) { c.exportFilter(index) }) }
                                            ChromeButton { text: "Edit"; enabled: !readOnly; onClicked: app.callController(function(c) { c.openEditFilterEditor(index) }) }
                                            IconButton { text: "x"; enabled: !readOnly; contentColor: app.accentRed; onClicked: app.callController(function(c) { c.deleteFilter(index) }) }
                                            Item { Layout.fillWidth: true }
                                        }
                                    }
                                }
                            }
                            MutedLabel { visible: app.controller.filterCount === 0; Layout.fillWidth: true; text: "No filters." }
                        }
