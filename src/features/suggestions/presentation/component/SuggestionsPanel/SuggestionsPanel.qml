import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "SuggestionsPanelLogic.js" as Logic

ColumnLayout {
    SuggestionsPanelStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    required property var app
    spacing: style.panelSpacing
                            PanelTitle { text: "SUGGESTIONS" }
                            Text { Layout.fillWidth: true; text: app.controller.suggestionKeyCount + " key duplicate(s), " + app.controller.suggestionValueCount + " value duplicate(s)"; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 12 }
                            ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; model: app.controller.suggestionKeyModel; spacing: 4
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                                delegate: Rectangle { width: parent ? parent.width : 0; height: 36; color: suggestionColor; radius: 3
                                    MouseArea { anchors.fill: parent; onClicked: app.callController(function(c) { c.openSuggestionSearch("key", index) }) }
                                    Text { anchors.fill: parent; anchors.margins: 7; text: duplicationValue + " : " + duplicationCount; color: "#ffffff"; font.family: "Consolas"; font.pixelSize: 12; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter }
                                }
                            }
                            ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; model: app.controller.suggestionValueModel; spacing: 4
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                                delegate: Rectangle { width: parent ? parent.width : 0; height: 36; color: suggestionColor; radius: 3
                                    MouseArea { anchors.fill: parent; onClicked: app.callController(function(c) { c.openSuggestionSearch("value", index) }) }
                                    Text { anchors.fill: parent; anchors.margins: 7; text: duplicationValue + " : " + duplicationCount; color: "#ffffff"; font.family: "Consolas"; font.pixelSize: 12; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter }
                                }
                            }
                        }
