import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "FilePickerPageLogic.js" as Logic

Item {
    id: page
    FilePickerPageStyle { id: style }

    required property var app
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    opacity: componentReady ? 1.0 : 0.0

    Behavior on opacity { NumberAnimation { duration: Motion.relaxed; easing.type: Easing.OutCubic } }

    DropArea {
        id: pickerDropArea
        anchors.fill: parent
        keys: ["text/uri-list"]
        onDropped: function(drop) {
            if (!drop.hasUrls) return
            app.callController(function(controller) {
                if (controller.addFiles(drop.urls) > 0) app.pageName = "management"
            })
            drop.acceptProposedAction()
        }
    }

    Rectangle {
        anchors.fill: parent
        color: pickerDropArea.containsDrag ? style.dropHoverBackground : style.background
        Behavior on color { ColorAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Spacing.xxl
        spacing: Spacing.xl

        RowLayout {
            Layout.fillWidth: true
            Layout.alignment: Qt.AlignTop
            ColumnLayout {
                Layout.fillWidth: true
                spacing: Spacing.xs
                Text {
                    text: "Bring a PBIR workspace into focus"
                    color: Theme.textColor
                    font.family: Typography.uiFamily
                    font.pixelSize: Typography.heroSize
                    font.weight: Font.DemiBold
                }
                MutedLabel {
                    Layout.maximumWidth: 720
                    text: "Drop a report folder, page.json, or visual.json. The workspace keeps your report structure intact while you inspect and update JSON."
                }
            }
            Rectangle {
                visible: app.controller.fileCount > 0
                Layout.preferredWidth: 112
                Layout.preferredHeight: Geometry.controlHeight
                radius: Geometry.radiusSm
                color: Theme.cardBackground
                border.width: Geometry.borderWidth
                border.color: Theme.borderSubtle
                Text {
                    anchors.centerIn: parent
                    text: app.controller.fileCount + " loaded"
                    color: Theme.mutedText
                    font.family: Typography.dataFamily
                    font.pixelSize: Typography.captionSize
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 224
            radius: Geometry.radiusLg
            color: pickerDropArea.containsDrag ? style.dropHoverBackground : style.dropBackground
            border.width: Geometry.borderWidth
            border.color: pickerDropArea.containsDrag ? Theme.accentBlue : Theme.borderColor
            scale: pickerDropArea.containsDrag ? Motion.hoverScale : 1.0

            Behavior on color { ColorAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }
            Behavior on scale { NumberAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }

            ColumnLayout {
                anchors.centerIn: parent
                width: Math.min(parent.width - Spacing.xxl * 2, 620)
                spacing: Spacing.lg

                Text {
                    Layout.fillWidth: true
                    text: pickerDropArea.containsDrag ? "Release to import" : "Drop report JSON or choose a source"
                    color: pickerDropArea.containsDrag ? Theme.white : Theme.textColor
                    font.family: Typography.uiFamily
                    font.pixelSize: Typography.titleSize
                    font.weight: Font.DemiBold
                    horizontalAlignment: Text.AlignHCenter
                }
                MutedLabel {
                    Layout.fillWidth: true
                    text: "Import files directly or scan a report folder before you commit the selection."
                    horizontalAlignment: Text.AlignHCenter
                }
                RowLayout {
                    Layout.alignment: Qt.AlignHCenter
                    spacing: Spacing.sm
                    ChromeButton {
                        text: "Choose JSON files"
                        actionType: "save"
                        onClicked: app.callController(function(controller) { if (controller.openFileDialog() > 0) app.pageName = "management" })
                    }
                    ChromeButton {
                        text: "Scan folder"
                        actionType: "save"
                        onClicked: app.callController(function(controller) { controller.openFolderDialog() })
                    }
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: Geometry.radiusMd
            color: style.cardBackground
            border.width: Geometry.borderWidth
            border.color: Theme.borderSubtle

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Geometry.cardPadding
                spacing: Spacing.sm
                RowLayout {
                    Layout.fillWidth: true
                    PanelTitle { text: "Loaded documents"; Layout.fillWidth: true }
                    Text {
                        text: app.controller.fileCount + " files"
                        color: Theme.dimText
                        font.family: Typography.dataFamily
                        font.pixelSize: Typography.captionSize
                    }
                }
                ListView {
                    id: documentsList
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    spacing: Spacing.xs
                    model: app.controller.fileModel
                    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                    add: Transition {
                        NumberAnimation { properties: "opacity"; from: 0; to: 1; duration: Motion.relaxed }
                        NumberAnimation { properties: "y"; from: Spacing.sm; duration: Motion.relaxed; easing.type: Easing.OutCubic }
                    }
                    displaced: Transition { NumberAnimation { properties: "y"; duration: Motion.standard; easing.type: Easing.OutCubic } }
                    delegate: Rectangle {
                        required property string activeFilterColor
                        required property bool visibleInTree
                        required property bool dirty
                        required property string name
                        required property bool validJson
                        required property string fileType
                        required property string relativePath
                        width: documentsList.width
                        height: 52
                        radius: Geometry.radiusSm
                        color: documentMouse.containsMouse ? Theme.cardHover : Theme.controlBackground
                        opacity: visibleInTree ? 1.0 : 0.45
                        Behavior on color { ColorAnimation { duration: Motion.quick } }
                        MouseArea { id: documentMouse; anchors.fill: parent; hoverEnabled: true }
                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: Spacing.md
                            anchors.rightMargin: Spacing.md
                            spacing: Spacing.sm
                            Rectangle {
                                Layout.preferredWidth: 8
                                Layout.preferredHeight: 28
                                radius: 4
                                color: Theme.safeColor(activeFilterColor, Theme.borderColor)
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
                                    font.weight: Font.DemiBold
                                    elide: Text.ElideMiddle
                                }
                                Text {
                                    Layout.fillWidth: true
                                    text: fileType + " · " + relativePath
                                    color: Theme.dimText
                                    font.family: Typography.dataFamily
                                    font.pixelSize: Typography.microSize
                                    elide: Text.ElideMiddle
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
