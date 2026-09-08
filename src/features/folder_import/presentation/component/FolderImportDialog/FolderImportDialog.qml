import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "FolderImportDialogLogic.js" as Logic

Item {
    FolderImportDialogStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    id: dialog
    anchors.fill: parent
    required property var app
    Rectangle {
        id: overlay
        anchors.fill: parent
        property bool open: app.controller.folderImportVisible
        visible: opacity > 0
        color: style.scrim
        opacity: open ? style.scrimOpacity : 0
        z: 20
        Behavior on opacity { NumberAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }
        MouseArea { anchors.fill: parent }
        Rectangle {
            width: Math.min(parent.width - Spacing.xxl * 2, 760)
            height: Math.min(parent.height - Spacing.xxl * 2, 560)
            anchors.centerIn: parent
            color: style.dialogBackground
            border.width: Geometry.borderWidth
            border.color: Theme.borderColor
            radius: Geometry.radiusLg
            scale: overlay.open ? 1.0 : 0.96
            Behavior on scale { NumberAnimation { duration: Motion.standard; easing.type: Easing.OutBack } }
            ColumnLayout { anchors.fill: parent; anchors.margins: 16; spacing: 12
                RowLayout {
                    Layout.fillWidth: true
                    PanelTitle { text: "FOLDER IMPORT"; Layout.fillWidth: true }
                    IconButton { text: "x"; contentColor: app.accentRed; onClicked: app.callController(function(c) { c.cancelFolderImport() }) }
                }
                MutedLabel { Layout.fillWidth: true; text: app.controller.folderScanRoot; elide: Text.ElideMiddle }
                Text { Layout.fillWidth: true; text: app.controller.folderScanCount + " Power BI JSON file(s) found"; color: app.controller.folderScanCount > 0 ? app.okColor : app.warningColor; font.family: Typography.uiFamily; font.pixelSize: Typography.labelSize }
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: app.editorBackground; border.color: app.borderColor
                    ListView { id: folderTree; anchors.fill: parent; anchors.margins: 8; clip: true; spacing: 1; model: app.controller.folderScanModel
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                        delegate: Rectangle { width: folderTree.width; height: 42; color: folderMouse.containsMouse ? app.listHover : "transparent"
                            MouseArea { id: folderMouse; anchors.fill: parent; hoverEnabled: true }
                            RowLayout { anchors.fill: parent; anchors.leftMargin: 8 + depth * 16; anchors.rightMargin: 8; spacing: 8
                                Text { text: displayName; color: app.textColor; font.family: Typography.uiFamily; font.pixelSize: Typography.labelSize; Layout.fillWidth: true; elide: Text.ElideMiddle }
                                Text { text: fileType; color: app.okColor; font.family: Typography.uiFamily; font.pixelSize: Typography.captionSize }
                                Text { text: relativePath; color: app.mutedText; font.family: Typography.uiFamily; font.pixelSize: Typography.captionSize; Layout.maximumWidth: 360; elide: Text.ElideMiddle }
                            }
                        }
                    }
                }
                RowLayout { Layout.fillWidth: true; spacing: 10
                    MutedLabel { Layout.fillWidth: true; text: app.controller.statusMessage; elide: Text.ElideRight }
                    ChromeButton { text: "Cancel"; actionType: "cancel"; onClicked: app.callController(function(c) { c.cancelFolderImport() }) }
                    ChromeButton { text: "Continue"; actionType: "save"; enabled: app.controller.folderScanCount > 0; onClicked: { app.callController(function(c) { c.confirmFolderImport() }); app.pageName = "management" } }
                }
            }
        }
    }
}
