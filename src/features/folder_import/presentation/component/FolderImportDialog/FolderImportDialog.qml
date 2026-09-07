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
    Rectangle { anchors.fill: parent; visible: app.controller.folderImportVisible; color: style.scrim; z: 20
        MouseArea { anchors.fill: parent }
        Rectangle { width: Math.min(parent.width - 80, 760); height: Math.min(parent.height - 80, 560); anchors.centerIn: parent; color: app.panelBackground; border.color: app.borderColor; radius: 4
            ColumnLayout { anchors.fill: parent; anchors.margins: 16; spacing: 12
                RowLayout {
                    Layout.fillWidth: true
                    PanelTitle { text: "FOLDER IMPORT"; Layout.fillWidth: true }
                    IconButton { text: "x"; contentColor: app.accentRed; onClicked: app.callController(function(c) { c.cancelFolderImport() }) }
                }
                MutedLabel { Layout.fillWidth: true; text: app.controller.folderScanRoot; elide: Text.ElideMiddle }
                Text { Layout.fillWidth: true; text: app.controller.folderScanCount + " Power BI JSON file(s) found"; color: app.controller.folderScanCount > 0 ? app.okColor : app.warningColor; font.family: "Segoe UI"; font.pixelSize: 13 }
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: app.editorBackground; border.color: app.borderColor
                    ListView { id: folderTree; anchors.fill: parent; anchors.margins: 8; clip: true; spacing: 1; model: app.controller.folderScanModel
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                        delegate: Rectangle { width: folderTree.width; height: 42; color: folderMouse.containsMouse ? app.listHover : "transparent"
                            MouseArea { id: folderMouse; anchors.fill: parent; hoverEnabled: true }
                            RowLayout { anchors.fill: parent; anchors.leftMargin: 8 + depth * 16; anchors.rightMargin: 8; spacing: 8
                                Text { text: displayName; color: app.textColor; font.family: "Segoe UI"; font.pixelSize: 13; Layout.fillWidth: true; elide: Text.ElideMiddle }
                                Text { text: fileType; color: app.okColor; font.family: "Segoe UI"; font.pixelSize: 11 }
                                Text { text: relativePath; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 11; Layout.maximumWidth: 360; elide: Text.ElideMiddle }
                            }
                        }
                    }
                }
                RowLayout { Layout.fillWidth: true; spacing: 10
                    MutedLabel { Layout.fillWidth: true; text: app.controller.statusMessage; elide: Text.ElideRight }
                    ChromeButton { text: "Cancel"; normalColor: "#3c3c3c"; hoverColor: "#4a4a4a"; onClicked: app.callController(function(c) { c.cancelFolderImport() }) }
                    ChromeButton { text: "Continue"; normalColor: app.accentGreen; hoverColor: app.accentGreenHover; pressedColor: "#126a4d"; enabled: app.controller.folderScanCount > 0; onClicked: { app.callController(function(c) { c.confirmFolderImport() }); app.pageName = "management" } }
                }
            }
        }
    }
}
