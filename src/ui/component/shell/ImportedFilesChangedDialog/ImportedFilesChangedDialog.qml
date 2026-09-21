import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "ImportedFilesChangedDialogLogic.js" as Logic

Item {
    id: dialog
    required property var app
    ImportedFilesChangedDialogStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady

    Rectangle {
        id: overlay
        anchors.fill: parent
        visible: opacity > 0
        z: 30
        color: style.scrim
        opacity: app.controller.externalChangesPending ? style.scrimOpacity : 0
        Behavior on opacity { NumberAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }
        MouseArea { anchors.fill: parent }

        Rectangle {
            width: Math.min(parent.width - Spacing.xxl * 2, style.preferredWidth)
            height: Math.min(parent.height - Spacing.xxl * 2, style.preferredHeight)
            anchors.centerIn: parent
            color: app.panelBackground
            border.color: app.borderColor
            radius: Geometry.radiusLg
            scale: app.controller.externalChangesPending ? 1.0 : 0.96
            Behavior on scale { NumberAnimation { duration: Motion.standard; easing.type: Easing.OutBack } }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Spacing.lg
                spacing: Spacing.md
                PanelTitle { text: "IMPORTED FILES CHANGED"; Layout.fillWidth: true }
                MutedLabel {
                    Layout.fillWidth: true
                    text: "The following files were modified outside the editor. Re-importing replaces their in-memory contents."
                    wrapMode: Text.WordWrap
                }
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: app.editorBackground
                    border.color: app.borderColor
                    ListView {
                        id: changedFiles
                        anchors.fill: parent
                        anchors.margins: Spacing.sm
                        clip: true
                        spacing: 2
                        model: app.controller.importChangeModel
                        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                        delegate: Rectangle {
                            width: changedFiles.width
                            height: 48
                            color: "transparent"
                            Column {
                                anchors.verticalCenter: parent.verticalCenter
                                width: parent.width
                                spacing: 2
                                Text { text: name; color: app.textColor; font.family: Typography.uiFamily; font.pixelSize: Typography.labelSize; elide: Text.ElideMiddle; width: parent.width }
                                Text { text: path; color: app.mutedText; font.family: Typography.uiFamily; font.pixelSize: Typography.captionSize; elide: Text.ElideMiddle; width: parent.width }
                            }
                        }
                    }
                }
                RowLayout {
                    Layout.fillWidth: true
                    Item { Layout.fillWidth: true }
                    ChromeButton { text: "Cancel"; actionType: "cancel"; onClicked: app.callController(function(c) { c.cancelExternalChanges() }) }
                    ChromeButton { text: "Re-import"; actionType: "save"; onClicked: app.callController(function(c) { c.reimportChangedFiles() }) }
                }
            }
        }
    }
}
