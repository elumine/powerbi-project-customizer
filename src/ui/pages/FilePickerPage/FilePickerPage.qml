import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "FilePickerPageLogic.js" as Logic

Item {
    FilePickerPageStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    id: page
    required property var app

            DropArea { id: pickerDropArea; anchors.fill: parent; keys: ["text/uri-list"]; onDropped: function(drop) { if (drop.hasUrls) { app.callController(function(c) { if (c.addFiles(drop.urls) > 0) app.pageName = "management" }); drop.acceptProposedAction() } } }
            Rectangle { anchors.fill: parent; color: pickerDropArea.containsDrag ? "#242b32" : style.background }
            ColumnLayout { anchors.fill: parent; anchors.margins: 36; spacing: 22
                ColumnLayout { Layout.fillWidth: true; spacing: 8
                    Text { text: "Open Power BI report JSON"; color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 28; font.bold: true }
                    MutedLabel { Layout.maximumWidth: 760; text: "Drop a PBIR report folder, page.json, or visual.json. Folder import scans pages and visuals while preserving their hierarchy." }
                }
                Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 180; color: app.panelBackground; border.color: pickerDropArea.containsDrag ? app.statusBackground : app.borderColor; radius: 4
                    ColumnLayout { anchors.centerIn: parent; width: Math.min(parent.width - 48, 560); spacing: 14
                        Text { Layout.fillWidth: true; text: pickerDropArea.containsDrag ? "Release to scan or add" : "Drag Power BI JSON files or folders here"; color: pickerDropArea.containsDrag ? "#ffffff" : app.textColor; font.family: "Segoe UI"; font.pixelSize: 18; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                        RowLayout { Layout.alignment: Qt.AlignHCenter; spacing: 10
                            ChromeButton { text: "Add JSON files"; onClicked: app.callController(function(c) { if (c.openFileDialog() > 0) app.pageName = "management" }) }
                            ChromeButton { text: "Add folder"; onClicked: app.callController(function(c) { c.openFolderDialog() }) }
                        }
                    }
                }
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: app.panelBackground; border.color: app.borderColor; radius: 4
                    ColumnLayout { anchors.fill: parent; anchors.margins: 12; spacing: 8
                        RowLayout {
                            Layout.fillWidth: true
                            PanelTitle { text: "OPEN DOCUMENTS"; Layout.fillWidth: true }
                            Text { text: app.controller.fileCount + " file(s)"; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 12 }
                        }
                        ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 1; model: app.controller.fileModel
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                            delegate: Rectangle { width: parent ? parent.width : 0; height: 44; color: "transparent"; opacity: visibleInTree ? 1.0 : 0.4
                                RowLayout { anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 4; spacing: 8
                                    Rectangle { Layout.preferredWidth: 8; Layout.preferredHeight: 8; radius: 4; color: activeFilterColor.length > 0 ? activeFilterColor : "transparent" }
                                    ColumnLayout { Layout.fillWidth: true; spacing: 1
                                        Text { Layout.fillWidth: true; text: (dirty ? "* " : "") + name; color: validJson ? app.textColor : app.warningColor; font.family: "Segoe UI"; font.pixelSize: 13; font.bold: true; elide: Text.ElideMiddle }
                                        Text { Layout.fillWidth: true; text: fileType + " - " + relativePath; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        
}
