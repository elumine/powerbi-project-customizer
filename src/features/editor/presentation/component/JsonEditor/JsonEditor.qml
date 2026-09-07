import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "JsonEditorLogic.js" as Logic

                Rectangle {
    JsonEditorStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    required property var app
    function openFind() { editorFindBar.visible = true; editorFindField.forceActiveFocus() } Layout.fillWidth: true; Layout.fillHeight: true; color: app.editorBackground
                    ColumnLayout { anchors.fill: parent; spacing: 0
                        Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 52; color: app.headerBackground; border.color: app.borderColor
                            RowLayout { anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 10
                                ColumnLayout { Layout.fillWidth: true; spacing: 1
                                    Text { Layout.fillWidth: true; text: app.controller.currentName; color: app.textColor; font.family: "Segoe UI"; font.pixelSize: 14; font.bold: true; elide: Text.ElideMiddle }
                                    Text { Layout.fillWidth: true; text: app.controller.currentFileType + " - " + app.controller.currentRelativePath; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                }
                                Text { text: app.controller.currentDirty ? "dirty" : "clean"; color: app.controller.currentDirty ? app.warningColor : app.mutedText; font.family: "Segoe UI"; font.pixelSize: 12 }
                                Text { text: app.controller.currentValidJson ? "Valid JSON" : app.controller.currentJsonError; color: app.controller.currentValidJson ? app.okColor : app.warningColor; font.family: "Segoe UI"; font.pixelSize: 11; Layout.maximumWidth: 280; elide: Text.ElideRight }
                                IconButton { text: "F"; enabled: app.controller.currentIndex >= 0; ToolTip.visible: hovered; ToolTip.text: "Format"; onClicked: app.callController(function(c) { c.formatCurrentJson() }) }
                                IconButton { text: "S"; enabled: app.controller.currentIndex >= 0 && app.controller.currentDirty; ToolTip.visible: hovered; ToolTip.text: "Save"; onClicked: app.callController(function(c) { c.saveFile(app.controller.currentIndex) }) }
                            }
                        }
                        Rectangle { visible: app.controller.currentIndex < 0; Layout.fillWidth: true; Layout.fillHeight: true; color: app.editorBackground
                            ColumnLayout { anchors.centerIn: parent; width: Math.min(parent.width - 64, 420); spacing: 8
                                Text { Layout.fillWidth: true; text: app.controller.hasActiveFilter ? "No visible file selected" : "No file selected"; color: app.textColor; font.family: "Segoe UI"; font.pixelSize: 20; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                                MutedLabel { Layout.fillWidth: true; text: app.controller.hasActiveFilter ? "No loaded document matches the active filter." : "Select a page or visual from the project tree."; horizontalAlignment: Text.AlignHCenter }
                            }
                        }
                        ColumnLayout { visible: app.controller.currentIndex >= 0; Layout.fillWidth: true; Layout.fillHeight: true; spacing: 0
                            Rectangle { id: editorFindBar; visible: false; Layout.fillWidth: true; Layout.preferredHeight: 38; color: app.headerBackground; border.color: app.borderColor
                                RowLayout { anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8; spacing: 6
                                    Field { id: editorFindField; Layout.fillWidth: true; placeholderText: "Find"; text: app.controller.searchText; onTextEdited: app.callController(function(c) { c.searchText = text }); Keys.onReturnPressed: function(event) { app.callController(function(c) { c.navigateNextMatch() }); event.accepted = true } }
                                    Field { id: editorReplaceField; Layout.fillWidth: true; placeholderText: "Replace"; text: app.controller.replaceText; onTextEdited: app.callController(function(c) { c.replaceText = text }) }
                                    ChromeButton { text: "Prev"; enabled: app.controller.totalMatches > 0; onClicked: app.callController(function(c) { c.navigatePreviousMatch() }) }
                                    ChromeButton { text: "Next"; enabled: app.controller.totalMatches > 0; onClicked: app.callController(function(c) { c.navigateNextMatch() }) }
                                    ChromeButton { text: "Replace"; enabled: app.controller.searchText.length > 0; onClicked: app.callController(function(c) { c.replaceCurrentMatch() }) }
                                    ChromeButton { text: "All"; enabled: app.controller.searchText.length > 0; onClicked: app.callController(function(c) { c.replaceCurrentFile() }) }
                                    IconButton { text: "x"; contentColor: app.accentRed; onClicked: editorFindBar.visible = false }
                                }
                            }
                            ScrollView { id: editorScroll; Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                                ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AlwaysOn }
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                                Row {
                                    id: editorRow
                                    spacing: 0
                                    Rectangle {
                                        id: lineGutter
                                        width: Math.max(44, lineText.implicitWidth + 16)
                                        height: Math.max(editorScroll.availableHeight, editorArea.height)
                                        color: style.gutterBackground
                                        Text {
                                            id: lineText
                                            anchors.top: parent.top
                                            anchors.right: parent.right
                                            anchors.topMargin: 12
                                            anchors.rightMargin: 8
                                            text: Logic.lineNumbers(app.controller.currentText)
                                            color: app.mutedText
                                            font.family: "Consolas"
                                            font.pixelSize: 14
                                            horizontalAlignment: Text.AlignRight
                                        }
                                    }
                                    TextArea {
                                        id: editorArea
                                        text: app.controller.currentText
                                        textFormat: TextEdit.PlainText
                                        wrapMode: TextEdit.NoWrap
                                        selectByMouse: true
                                        persistentSelection: true
                                        color: app.textColor
                                        selectedTextColor: "#ffffff"
                                        selectionColor: "#264f78"
                                        font.family: "Consolas"
                                        font.pixelSize: 14
                                        leftPadding: 14
                                        topPadding: 12
                                        rightPadding: 14
                                        bottomPadding: 12
                                        background: Rectangle { color: app.editorBackground }
                                        width: Math.max(editorScroll.availableWidth - lineGutter.width, contentWidth + leftPadding + rightPadding + 24)
                                        height: Math.max(editorScroll.availableHeight, contentHeight + topPadding + bottomPadding + 24)
                                        onTextChanged: if (activeFocus && text !== app.controller.currentText) app.callController(function(c) { c.updateFileText(app.controller.currentIndex, text) })
                                        Component.onCompleted: app.editorAdapter.attach(textDocument)
                                        Component.onDestruction: app.editorAdapter.dispose(textDocument)
                                        Keys.onPressed: function(event) { if ((event.modifiers & Qt.ControlModifier) && event.key === Qt.Key_F) { editorFindBar.visible = true; editorFindField.forceActiveFocus(); event.accepted = true } }
                                    }
                                }
                            }
                            Connections { target: app.controller; function onMatchNavigationChanged() { if (app.controller.activeMatchStart >= 0 && app.controller.activeMatchEnd >= app.controller.activeMatchStart) { editorArea.cursorPosition = app.controller.activeMatchStart; editorArea.select(app.controller.activeMatchStart, app.controller.activeMatchEnd); editorArea.forceActiveFocus() } else if (app.controller.activeMatchLine > 0) { var pos = Logic.lineOffset(app.controller.currentText, app.controller.activeMatchLine); editorArea.cursorPosition = pos; editorArea.select(pos, Math.min(app.controller.currentText.length, pos + Math.max(1, app.controller.searchText.length))); editorArea.forceActiveFocus() } } }
                        }
                        Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 24; color: app.statusBackground
                            RowLayout { anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 10; spacing: 12
                                Text { text: app.controller.statusMessage; color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideRight }
                                Text { text: app.controller.activeFileCount + "/" + app.controller.fileCount + " active"; color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 11 }
                                Text { text: app.controller.hasDirtyFiles ? "dirty" : "clean"; color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 11 }
                            }
                        }
                    }
                }
