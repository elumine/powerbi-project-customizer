import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import features.changes.presentation 1.0
import "JsonEditorLogic.js" as Logic

Rectangle {
    id: editorRoot
    JsonEditorStyle { id: style }

    required property var app
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    property string displayMode: "raw"
    property bool findOpen: false
    color: style.editorBackground
    radius: Geometry.radiusMd
    border.width: Geometry.borderWidth
    border.color: Theme.borderSubtle
    clip: true

    function openFind() {
        findOpen = true
        editorFindField.forceActiveFocus()
    }

    function focusCurrentFlatMatch() {
        if (app.controller.activeMatchStart >= 0 && app.controller.activeMatchEnd >= app.controller.activeMatchStart) {
            editorArea.cursorPosition = app.controller.activeMatchStart
            editorArea.select(app.controller.activeMatchStart, app.controller.activeMatchEnd)
            editorArea.forceActiveFocus()
        } else if (app.controller.activeMatchLine > 0) {
            const position = Logic.lineOffset(app.controller.currentText, app.controller.activeMatchLine)
            editorArea.cursorPosition = position
            editorArea.select(position, Math.min(app.controller.currentText.length, position + Math.max(1, app.controller.searchText.length)))
            editorArea.forceActiveFocus()
        }
    }

    SequentialAnimation {
        id: statusFlash
        NumberAnimation { target: statusBar; property: "opacity"; to: 1.0; duration: Motion.quick }
        NumberAnimation { target: statusBar; property: "scale"; to: Motion.hoverScale; duration: Motion.quick }
        NumberAnimation { target: statusBar; property: "scale"; to: 1.0; duration: Motion.standard; easing.type: Easing.OutCubic }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: Geometry.toolbarHeight
            color: style.toolbarBackground
            border.width: Geometry.borderWidth
            border.color: Theme.borderSubtle

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Geometry.cardPadding
                anchors.rightMargin: Geometry.cardPadding
                spacing: Spacing.sm

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: Spacing.xxs
                    Text {
                        Layout.fillWidth: true
                        text: app.controller.currentName
                        color: Theme.textColor
                        font.family: Typography.uiFamily
                        font.pixelSize: Typography.sectionSize
                        font.weight: Font.DemiBold
                        elide: Text.ElideMiddle
                    }
                    Text {
                        Layout.fillWidth: true
                        text: app.controller.currentFileType + " · " + app.controller.currentRelativePath
                        color: Theme.dimText
                        font.family: Typography.dataFamily
                        font.pixelSize: Typography.microSize
                        elide: Text.ElideMiddle
                    }
                }
                DiffChip {
                    value: app.controller.currentDirty ? "dirty" : "saved"
                    chipColor: app.controller.currentDirty ? Theme.warningColor : Theme.okColor
                    chipTextColor: Theme.contrastText(chipColor)
                }
                DiffChip {
                    value: app.controller.currentValidJson ? "valid" : "invalid"
                    chipColor: app.controller.currentValidJson ? Theme.visualTable : Theme.accentRed
                    chipTextColor: Theme.contrastText(chipColor)
                }
                RowLayout {
                    spacing: Spacing.xxs
                    ChromeButton {
                        text: "Text editor"
                        actionType: app.editorView === "text" ? "execute" : "neutral"
                        onClicked: app.callController(function(controller) { controller.openTextEditor() })
                    }
                    ChromeButton {
                        text: "Changes"
                        actionType: app.editorView === "changes" ? "execute" : "neutral"
                        enabled: app.controller.currentDiffLines.length > 0
                        onClicked: app.callController(function(controller) { controller.openCurrentChanges() })
                    }
                }
                ChromeButton {
                    text: editorRoot.displayMode === "flat" ? "Flat" : "Hierarchical preview"
                    actionType: "neutral"
                    ToolTip.visible: hovered
                    ToolTip.text: editorRoot.displayMode === "flat" ? "Editable flat JSON" : "Read-only hierarchical preview"
                    contentColor: Theme.textColor
                    onClicked: editorRoot.displayMode = editorRoot.displayMode === "flat" ? "raw" : "flat"
                }
                IconButton {
                    text: "⌁"
                    tooltipText: "Format flattened JSON"
                    enabled: app.controller.currentIndex >= 0
                    contentColor: Theme.visualChart
                    onClicked: app.callController(function(controller) { controller.formatCurrentJson() })
                }
                IconButton {
                    text: "⇩"
                    tooltipText: "Save"
                    enabled: app.controller.currentIndex >= 0 && app.controller.currentDirty
                    contentColor: Theme.okColor
                    onClicked: app.callController(function(controller) { controller.saveFile(app.controller.currentIndex) })
                }
            }
        }

        Rectangle {
            visible: app.controller.currentIndex < 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: style.editorBackground
            ColumnLayout {
                anchors.centerIn: parent
                width: Math.min(parent.width - Spacing.xxl * 2, 440)
                spacing: Spacing.sm
                Text {
                    Layout.fillWidth: true
                    text: app.controller.hasActiveFilter ? "No matching document selected" : "Select a document to inspect"
                    color: Theme.textColor
                    font.family: Typography.uiFamily
                    font.pixelSize: Typography.titleSize
                    font.weight: Font.DemiBold
                    horizontalAlignment: Text.AlignHCenter
                }
                MutedLabel {
                    Layout.fillWidth: true
                    text: app.controller.hasActiveFilter ? "Adjust or clear the active filter to reveal additional documents." : "Choose an item from the workspace panel to edit its JSON."
                    horizontalAlignment: Text.AlignHCenter
                }
            }
        }

        ColumnLayout {
            visible: app.controller.currentIndex >= 0
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            Rectangle {
                id: editorFindBar
                visible: editorRoot.findOpen && app.editorView === "text"
                Layout.fillWidth: true
                Layout.preferredHeight: Geometry.controlHeight + Spacing.xs
                color: Theme.controlBackground
                border.width: Geometry.borderWidth
                border.color: Theme.borderSubtle
                opacity: visible ? 1.0 : 0.0
                Behavior on opacity { NumberAnimation { duration: Motion.quick } }
                RowLayout {
                    anchors.fill: parent
                    anchors.margins: Spacing.xs
                    spacing: Spacing.xs
                    Field {
                        id: editorFindField
                        Layout.fillWidth: true
                        placeholderText: "Find"
                        text: app.controller.searchText
                        onTextEdited: app.callController(function(controller) { controller.searchText = text })
                        Keys.onReturnPressed: function(event) {
                            app.callController(function(controller) {
                                controller.runSearch()
                                controller.navigateNextMatch()
                            })
                            event.accepted = true
                        }
                    }
                    Field {
                        id: editorReplaceField
                        Layout.fillWidth: true
                        placeholderText: "Replace"
                        text: app.controller.replaceText
                        onTextEdited: app.callController(function(controller) { controller.replaceText = text })
                    }
                    ChromeButton {
                        text: "Search"
                        actionType: "execute"
                        enabled: app.controller.searchText.length > 0
                        onClicked: app.callController(function(controller) { controller.runSearch() })
                    }
                    IconButton { text: "↑"; tooltipText: "Previous match"; enabled: app.controller.totalMatches > 0; onClicked: app.callController(function(controller) { controller.navigatePreviousMatch() }) }
                    IconButton { text: "↓"; tooltipText: "Next match"; enabled: app.controller.totalMatches > 0; onClicked: app.callController(function(controller) { controller.navigateNextMatch() }) }
                    ChromeButton { text: "Replace"; actionType: "execute"; enabled: app.controller.searchText.length > 0; onClicked: app.callController(function(controller) { controller.replaceCurrentMatch() }) }
                    ChromeButton {
                        text: "File"
                        actionType: "execute"
                        enabled: app.controller.searchText.length > 0
                        onClicked: app.callController(function(controller) { controller.replaceCurrentFile() })
                    }
                    IconButton { text: "×"; tooltipText: "Close find"; contentColor: Theme.accentRed; onClicked: editorRoot.findOpen = false }
                }
            }

            ScrollView {
                id: editorScroll
                visible: app.editorView === "text"
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                Row {
                    id: editorRow
                    spacing: 0
                    Rectangle {
                        id: lineGutter
                        width: Math.max(48, lineText.implicitWidth + Spacing.lg)
                        height: Math.max(editorScroll.availableHeight, editorArea.height)
                        color: style.gutterBackground
                        border.width: Geometry.borderWidth
                        border.color: Theme.borderSubtle
                        Text {
                            id: lineText
                            anchors.top: parent.top
                            anchors.right: parent.right
                            anchors.topMargin: Geometry.cardPadding
                            anchors.rightMargin: Spacing.sm
                            text: Logic.lineNumbers(editorRoot.displayMode === "raw" ? app.controller.currentRawText : app.controller.currentText)
                            color: Theme.dimText
                            font.family: Typography.dataFamily
                            font.pixelSize: Typography.labelSize
                            horizontalAlignment: Text.AlignRight
                        }
                    }
                    TextArea {
                        id: editorArea
                        text: editorRoot.displayMode === "raw" ? app.controller.currentRawText : app.controller.currentText
                        textFormat: TextEdit.PlainText
                        wrapMode: TextEdit.NoWrap
                        // Hierarchical source is a preview only; only flat JSON is editable.
                        readOnly: editorRoot.displayMode !== "flat"
                        selectByMouse: true
                        persistentSelection: true
                        color: Theme.textColor
                        selectedTextColor: Theme.white
                        selectionColor: Theme.selectionColor
                        font.family: Typography.dataFamily
                        font.pixelSize: Typography.labelSize
                        leftPadding: Geometry.cardPadding
                        topPadding: Geometry.cardPadding
                        rightPadding: Geometry.cardPadding
                        bottomPadding: Geometry.cardPadding
                        background: Rectangle { color: style.editorBackground }
                        width: Math.max(editorScroll.availableWidth - lineGutter.width, contentWidth + leftPadding + rightPadding + Spacing.xl)
                        height: Math.max(editorScroll.availableHeight, contentHeight + topPadding + bottomPadding + Spacing.xl)
                        onTextChanged: {
                            if (editorRoot.displayMode === "flat" && activeFocus && text !== app.controller.currentText) {
                                app.callController(function(controller) { controller.updateFileText(app.controller.currentIndex, text) })
                            }
                        }
                        Component.onCompleted: app.editorAdapter.attach(textDocument)
                        Component.onDestruction: app.editorAdapter.dispose(textDocument)
                        Keys.onPressed: function(event) {
                            if ((event.modifiers & Qt.ControlModifier) && event.key === Qt.Key_F) {
                                editorRoot.openFind()
                                event.accepted = true
                            }
                        }
                    }
                }
            }

            Rectangle {
                id: statusBar
                visible: app.editorView === "text"
                Layout.fillWidth: true
                Layout.preferredHeight: 28
                color: style.statusBackground
                border.width: Geometry.borderWidth
                border.color: Theme.borderSubtle
                opacity: 1.0
                transformOrigin: Item.Center
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Geometry.cardPadding
                    anchors.rightMargin: Geometry.cardPadding
                    spacing: Spacing.md
                    Rectangle {
                        Layout.preferredWidth: 7
                        Layout.preferredHeight: 7
                        radius: width / 2
                        color: app.controller.hasDirtyFiles ? Theme.warningColor : Theme.okColor
                        Behavior on color { ColorAnimation { duration: Motion.standard } }
                    }
                    Text {
                        Layout.fillWidth: true
                        text: app.controller.statusMessage
                        color: Theme.textColor
                        font.family: Typography.uiFamily
                        font.pixelSize: Typography.captionSize
                        elide: Text.ElideRight
                    }
                    Text {
                        text: app.controller.activeFileCount + "/" + app.controller.fileCount + " active"
                        color: Theme.mutedText
                        font.family: Typography.dataFamily
                        font.pixelSize: Typography.microSize
                    }
                }
            }

            ChangesView {
                visible: app.controller.currentIndex >= 0 && app.editorView === "changes"
                Layout.fillWidth: true
                Layout.fillHeight: true
                app: editorRoot.app
            }
        }
    }

    Connections {
        target: app.controller
        function onCurrentDocumentChanged() {
            // A document selection always opens the original imported source first.
            editorRoot.displayMode = "raw"
        }
        function onMatchNavigationChanged() {
            // Search offsets belong to the flattened working representation.
            // Switch source view back to Flat before selecting the match.
            if (editorRoot.displayMode === "raw") {
                editorRoot.displayMode = "flat"
                Qt.callLater(editorRoot.focusCurrentFlatMatch)
                return
            }
            editorRoot.focusCurrentFlatMatch()
        }
        function onStatusChanged() { statusFlash.restart() }
    }
}
