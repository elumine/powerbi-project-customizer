import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "MacrosPanelLogic.js" as Logic

ColumnLayout {
    MacrosPanelStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    required property var app
    spacing: style.panelSpacing
                            RowLayout {
                                Layout.fillWidth: true
                                PanelTitle { text: "MACROS"; Layout.fillWidth: true }
                                Text { text: app.controller.macroCount + " macro(s)"; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                            }
                            RowLayout { Layout.fillWidth: true; spacing: 6
                                ChromeButton { Layout.fillWidth: true; text: "Import"; onClicked: app.callController(function(c) { c.importMacro() }) }
                                ChromeButton { Layout.fillWidth: true; text: "Reload"; onClicked: app.callController(function(c) { c.reloadContent() }) }
                            }
                            ListView { id: macroList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 6; model: app.controller.macroModel
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                                delegate: Rectangle { id: macroRow; width: macroList.width; height: stepsOpen ? 178 : 86; color: macroMouse.containsMouse ? app.listHover : app.editorBackground; border.color: validationText.length > 0 ? app.warningColor : app.borderColor; radius: 4; property bool stepsOpen: false
                                    MouseArea { id: macroMouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }
                                    ColumnLayout { anchors.fill: parent; anchors.margins: 7; spacing: 4
                                        RowLayout {
                                            Layout.fillWidth: true
                                            Text { Layout.fillWidth: true; text: name; color: app.textColor; font.family: "Segoe UI"; font.pixelSize: 12; font.bold: true; elide: Text.ElideRight }
                                            Text { text: stepCount + " step(s)"; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 10 }
                                        }
                                        Text { Layout.fillWidth: true; text: statusText; color: validationText.length > 0 ? app.warningColor : app.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideRight }
                                        RowLayout { Layout.fillWidth: true; spacing: 6
                                            ChromeButton { text: running ? "Running" : "Run"; enabled: canRun; onClicked: app.callController(function(c) { c.runMacro(index) }) }
                                            ChromeButton { text: "Export"; onClicked: app.callController(function(c) { c.exportMacro(index) }) }
                                            ChromeButton { text: macroRow.stepsOpen ? "Hide steps" : "Steps"; normalColor: "#3c3c3c"; hoverColor: "#4a4a4a"; enabled: stepCount > 0; onClicked: macroRow.stepsOpen = !macroRow.stepsOpen }
                                            Item { Layout.fillWidth: true }
                                        }
                                        ListView { visible: macroRow.stepsOpen; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; model: steps
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                                            delegate: Text { width: macroList.width - 20; text: (index + 1) + ". " + modelData.type + " - " + modelData.summary; color: app.mutedText; font.family: "Consolas"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                        }
                                    }
                                }
                            }
                        }
