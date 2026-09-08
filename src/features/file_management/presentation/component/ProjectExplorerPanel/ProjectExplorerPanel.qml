import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "ProjectExplorerPanelLogic.js" as Logic

ColumnLayout {
    id: panel
    ProjectExplorerPanelStyle { id: style }

    required property var app
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    spacing: style.panelSpacing

    RowLayout {
        Layout.fillWidth: true
        PanelTitle { text: "Workspace files"; Layout.fillWidth: true }
        DiffChip {
            value: app.controller.projectTreeCount + " rows"
            chipColor: Theme.visualLine
        }
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: Spacing.xs
        ChromeButton {
            Layout.fillWidth: true
            text: "Scan folder"
            actionType: "save"
            onClicked: app.callController(function(controller) { controller.openFolderDialog() })
        }
        ChromeButton {
            Layout.fillWidth: true
            text: "Add files"
            actionType: "save"
            onClicked: app.callController(function(controller) { controller.openFileDialog() })
        }
        IconButton {
            text: "⇩"
            tooltipText: "Save all"
            enabled: app.controller.hasDirtyFiles
            contentColor: Theme.okColor
            onClicked: app.callController(function(controller) { controller.saveAll() })
        }
    }

    ListView {
        id: projectTree
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        spacing: Spacing.xs
        model: app.controller.projectTreeModel
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
        displaced: Transition { NumberAnimation { properties: "y"; duration: Motion.standard; easing.type: Easing.OutCubic } }

        delegate: Rectangle {
            id: fileRow
            required property int fileIndex
            required property string documentId
            required property string name
            required property string fileType
            required property string visualType
            required property int depth
            required property bool expanded
            required property bool activeFile
            required property bool containerOnly
            required property bool dirty
            required property bool validJson
            required property int matchCount
            required property string activeFilterColor
            required property int index

            width: projectTree.width
            height: 56
            radius: Geometry.radiusSm
            color: fileIndex === app.controller.currentIndex ? Theme.listActive : fileMouse.containsMouse ? style.rowHover : style.rowBackground
            opacity: activeFile || containerOnly ? 1.0 : 0.50
            scale: fileMouse.containsMouse ? Motion.hoverScale : 1.0
            border.width: Geometry.borderWidth
            border.color: fileIndex === app.controller.currentIndex ? Theme.visualTypeColor(visualType) : Theme.borderSubtle

            Behavior on color { ColorAnimation { duration: Motion.quick } }
            Behavior on scale { NumberAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }

            MouseArea {
                id: fileMouse
                anchors.fill: parent
                hoverEnabled: true
                onClicked: app.callController(function(controller) { controller.selectTreeRow(index) })
            }

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Spacing.sm + depth * Spacing.lg
                anchors.rightMargin: Spacing.sm
                spacing: Spacing.xs
                IconButton {
                    visible: fileType === "Page"
                    text: expanded ? "⌄" : "›"
                    tooltipText: expanded ? "Collapse page" : "Expand page"
                    onClicked: app.callController(function(controller) { controller.setPageExpanded(fileRow.documentId, !expanded) })
                }
                Rectangle {
                    Layout.preferredWidth: 5
                    Layout.preferredHeight: 30
                    radius: width / 2
                    color: Theme.safeColor(activeFilterColor, Theme.visualTypeColor(visualType))
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: Spacing.xxs
                    Text {
                        Layout.fillWidth: true
                        text: (dirty ? "• " : "") + name
                        color: validJson ? Theme.textColor : Theme.warningColor
                        font.family: Typography.uiFamily
                        font.pixelSize: Typography.labelSize
                        font.weight: fileType === "Page" ? Font.DemiBold : Font.Normal
                        elide: Text.ElideMiddle
                    }
                    Text {
                        Layout.fillWidth: true
                        text: fileType + (visualType.length > 0 ? " · " + visualType : "") + (matchCount > 0 ? " · " + matchCount + " matches" : "")
                        color: Theme.dimText
                        font.family: Typography.dataFamily
                        font.pixelSize: Typography.microSize
                        elide: Text.ElideMiddle
                    }
                }
                IconButton {
                    text: "×"
                    tooltipText: "Remove file"
                    contentColor: Theme.accentRed
                    onClicked: app.callController(function(controller) { controller.removeFile(fileIndex) })
                }
            }
        }
    }

    MutedLabel {
        visible: app.controller.projectTreeCount === 0
        Layout.fillWidth: true
        text: "No PBIR JSON files loaded. Scan a folder or add a document to start."
    }
}
