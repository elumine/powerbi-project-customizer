import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "ProjectExplorerPanelLogic.js" as Logic

ColumnLayout {
    ProjectExplorerPanelStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    required property var app
    spacing: style.panelSpacing
                            RowLayout {
                                Layout.fillWidth: true
                                PanelTitle { text: "PROJECT"; Layout.fillWidth: true }
                                Text { text: app.controller.projectTreeCount + " row(s)"; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                            }
                            RowLayout { Layout.fillWidth: true; spacing: 6
                                ChromeButton { Layout.fillWidth: true; text: "Add folder"; onClicked: app.callController(function(c) { c.openFolderDialog() }) }
                                ChromeButton { Layout.fillWidth: true; text: "Add files"; onClicked: app.callController(function(c) { c.openFileDialog() }) }
                            }
                            ChromeButton { Layout.fillWidth: true; text: "Save all"; enabled: app.controller.hasDirtyFiles; onClicked: app.callController(function(c) { c.saveAll() }) }
                            ListView { id: projectTree; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 2; model: app.controller.projectTreeModel
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                                delegate: Rectangle { width: projectTree.width; height: 48; color: fileIndex === app.controller.currentIndex ? app.listActive : rowMouse.containsMouse ? app.listHover : "transparent"; opacity: activeFile || containerOnly ? 1.0 : 0.55
                                    MouseArea { id: rowMouse; anchors.fill: parent; hoverEnabled: true; onClicked: app.callController(function(c) { c.selectTreeRow(index) }) }
                                    RowLayout { anchors.fill: parent; anchors.leftMargin: 6 + depth * 18; anchors.rightMargin: 4; spacing: 6
                                        IconButton { visible: fileType === "Page"; text: expanded ? "v" : ">"; onClicked: app.callController(function(c) { c.setPageExpanded(model.id, !expanded) }) }
                                        Text { visible: fileType !== "Page"; text: fileType === "Visual" && depth > 0 ? "-" : ""; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 12; Layout.preferredWidth: fileType === "Page" ? 0 : 30 }
                                        Rectangle { Layout.preferredWidth: 8; Layout.preferredHeight: 8; radius: 4; color: activeFilterColor.length > 0 ? activeFilterColor : "transparent" }
                                        ColumnLayout { Layout.fillWidth: true; spacing: 1
                                            Text { Layout.fillWidth: true; text: (dirty ? "* " : "") + name; color: validJson ? app.textColor : app.warningColor; font.family: "Segoe UI"; font.pixelSize: 13; font.bold: fileType === "Page"; elide: Text.ElideMiddle }
                                            Text { Layout.fillWidth: true; text: fileType + (visualType.length > 0 ? " - " + visualType : "") + (matchCount > 0 ? " - " + matchCount + " match(es)" : ""); color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                        }
                                        IconButton { text: "x"; contentColor: app.accentRed; ToolTip.visible: hovered; ToolTip.text: "Remove"; onClicked: app.callController(function(c) { c.removeFile(fileIndex) }) }
                                    }
                                }
                            }
                            MutedLabel { visible: app.controller.projectTreeCount === 0; Layout.fillWidth: true; text: "No Power BI JSON files loaded." }
                        }
