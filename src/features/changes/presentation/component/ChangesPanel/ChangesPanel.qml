import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "ChangesPanelLogic.js" as Logic

ColumnLayout {
    id: panel
    ChangesPanelStyle { id: style }

    required property var app
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    spacing: style.panelSpacing

    RowLayout {
        Layout.fillWidth: true
        PanelTitle { text: "Changes"; Layout.fillWidth: true }
        DiffChip {
            value: String(app.controller.changeCount)
            chipColor: Theme.okColor
            chipTextColor: Theme.contrastText(Theme.okColor)
        }
    }

    MutedLabel {
        Layout.fillWidth: true
        text: "Files changed since the workspace was imported."
        wrapMode: Text.WordWrap
    }

    ListView {
        id: changesList
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        spacing: Spacing.xs
        model: app.controller.changesModel
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

        delegate: Rectangle {
            required property string documentId
            required property string name
            required property string relativePath
            required property int addedLines
            required property int removedLines
            width: changesList.width
            height: 68
            radius: Geometry.radiusSm
            color: changeMouse.containsMouse ? Theme.cardHover : Theme.cardBackground
            border.width: Geometry.borderWidth
            border.color: Theme.borderSubtle
            scale: changeMouse.containsMouse ? Motion.hoverScale : 1.0
            Behavior on color { ColorAnimation { duration: Motion.quick } }
            Behavior on scale { NumberAnimation { duration: Motion.quick } }

            MouseArea {
                id: changeMouse
                anchors.fill: parent
                hoverEnabled: true
                onClicked: app.callController(function(controller) {
                    controller.openChanges(documentId)
                })
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Spacing.sm
                spacing: Spacing.xxs
                Text {
                    Layout.fillWidth: true
                    text: name
                    color: Theme.textColor
                    font.family: Typography.uiFamily
                    font.pixelSize: Typography.bodySize
                    font.weight: Font.DemiBold
                    elide: Text.ElideRight
                }
                RowLayout {
                    Layout.fillWidth: true
                    Text {
                        Layout.fillWidth: true
                        text: relativePath
                        color: Theme.dimText
                        font.family: Typography.dataFamily
                        font.pixelSize: Typography.microSize
                        elide: Text.ElideMiddle
                    }
                    RowLayout {
                        spacing: Spacing.xs
                        Text {
                            text: "+" + addedLines
                            color: Theme.okColor
                            font.family: Typography.dataFamily
                            font.pixelSize: Typography.captionSize
                            font.weight: Font.DemiBold
                        }
                        Text {
                            text: "-" + removedLines
                            color: Theme.accentRed
                            font.family: Typography.dataFamily
                            font.pixelSize: Typography.captionSize
                            font.weight: Font.DemiBold
                        }
                    }
                }
            }
        }
    }

    MutedLabel {
        visible: app.controller.changeCount === 0
        Layout.fillWidth: true
        text: "No changes yet. Edit a file to see its diff here."
        wrapMode: Text.WordWrap
    }
}
