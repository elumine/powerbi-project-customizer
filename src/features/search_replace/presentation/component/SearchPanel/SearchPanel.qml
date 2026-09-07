import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "SearchPanelLogic.js" as Logic

ColumnLayout {
    SearchPanelStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    required property var app
    spacing: style.panelSpacing
                            PanelTitle { text: "SEARCH" }
                            Field { Layout.fillWidth: true; placeholderText: "Find"; text: app.controller.searchText; onTextEdited: app.callController(function(c) { c.searchText = text }) }
                            Field { Layout.fillWidth: true; placeholderText: "Replace with"; text: app.controller.replaceText; onTextEdited: app.callController(function(c) { c.replaceText = text }) }
                            CheckBox { text: "Case sensitive"; checked: app.controller.caseSensitive; onToggled: app.callController(function(c) { c.caseSensitive = checked }); contentItem: Text { text: parent.text; color: app.textColor; font.family: "Segoe UI"; font.pixelSize: 12; leftPadding: parent.indicator.width + 6 } }
                            RowLayout { Layout.fillWidth: true; spacing: 6
                                ChromeButton { Layout.fillWidth: true; text: "Replace"; enabled: app.controller.activeFileCount > 0 && app.controller.searchText.length > 0; onClicked: app.callController(function(c) { c.replaceCurrentMatch() }) }
                                ChromeButton { Layout.fillWidth: true; text: "Replace all"; enabled: app.controller.activeFileCount > 0 && app.controller.searchText.length > 0; onClicked: app.callController(function(c) { c.replaceAll() }) }
                            }
                            RowLayout { Layout.fillWidth: true; spacing: 6
                                IconButton { text: "^"; enabled: app.controller.totalMatches > 0; ToolTip.visible: hovered; ToolTip.text: "Previous match"; onClicked: app.callController(function(c) { c.navigatePreviousMatch() }) }
                                IconButton { text: "v"; enabled: app.controller.totalMatches > 0; ToolTip.visible: hovered; ToolTip.text: "Next match"; onClicked: app.callController(function(c) { c.navigateNextMatch() }) }
                                Text { Layout.fillWidth: true; text: app.controller.totalMatches + " match(es) in active files"; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 12; elide: Text.ElideRight }
                            }
                            ListView { id: searchResultList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; model: app.controller.searchResultModel; spacing: 5
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                                delegate: Rectangle { width: searchResultList.width; height: 44; color: app.editorBackground; border.color: app.borderColor; radius: 3
                                    MouseArea { anchors.fill: parent; onClicked: app.callController(function(c) { c.navigateToMatch(fileIndex, matchIndex) }) }
                                    ColumnLayout { anchors.fill: parent; anchors.margins: 6; spacing: 2
                                        Text { Layout.fillWidth: true; text: displayText; color: app.textColor; font.family: "Segoe UI"; font.pixelSize: 12; elide: Text.ElideMiddle }
                                        Text { Layout.fillWidth: true; text: "match " + (matchIndex + 1) + " at offset " + start; color: app.mutedText; font.family: "Consolas"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                    }
                                }
                            }
                        }
