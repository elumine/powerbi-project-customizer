import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "ChangesViewLogic.js" as Logic

ColumnLayout {
    id: view
    ChangesViewStyle { id: style }

    required property var app
    readonly property bool componentReady: Logic.isReady(app)
    readonly property int lineHeight: style.lineHeight
    readonly property int gutterWidth: style.gutterWidth
    readonly property color addedBackground: style.addedBackground
    readonly property color removedBackground: style.removedBackground
    readonly property color addedGutter: style.addedGutter
    readonly property color removedGutter: style.removedGutter
    readonly property color headerSurface: style.headerSurface
    enabled: style.enabled && componentReady
    spacing: style.panelSpacing

    Rectangle {
        Layout.fillWidth: true
        Layout.preferredHeight: 50
        color: view.headerSurface
        border.width: Geometry.borderWidth
        border.color: style.border

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: Spacing.md
            anchors.rightMargin: Spacing.md
            spacing: Spacing.sm
            ColumnLayout {
                Layout.fillWidth: true
                spacing: Spacing.xxs
                Text {
                    Layout.fillWidth: true
                    text: "Changes"
                    color: Theme.textColor
                    font.family: Typography.uiFamily
                    font.pixelSize: Typography.sectionSize
                    font.weight: Font.DemiBold
                    elide: Text.ElideMiddle
                }
                Text {
                    Layout.fillWidth: true
                    text: "Compared with the initial import"
                    color: Theme.dimText
                    font.family: Typography.uiFamily
                    font.pixelSize: Typography.microSize
                    elide: Text.ElideRight
                }
            }
            DiffChip {
                value: String(app.controller.changeCount)
                chipColor: Theme.okColor
                chipTextColor: Theme.contrastText(Theme.okColor)
            }
        }
    }

    Rectangle {
        Layout.fillWidth: true
        Layout.fillHeight: true
        color: style.surface
        border.width: Geometry.borderWidth
        border.color: style.border
        clip: true

        ListView {
            id: diffList
            anchors.fill: parent
            clip: true
            model: app.controller.currentDiffLines
            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
            ScrollBar.horizontal: ScrollBar { policy: ScrollBar.AsNeeded }

            delegate: Rectangle {
                property var lineData: modelData
                readonly property string lineKind: String(Logic.lineValue(lineData, "kind", "context"))
                width: Math.max(diffList.width, diffText.implicitWidth + view.gutterWidth * 2 + Spacing.xl)
                height: view.lineHeight
                color: lineKind === "added" ? view.addedBackground : lineKind === "removed" ? view.removedBackground : "transparent"

                RowLayout {
                    anchors.fill: parent
                    spacing: 0
                    Rectangle {
                        Layout.preferredWidth: view.gutterWidth
                        Layout.fillHeight: true
                        color: lineKind === "added" ? view.addedGutter : lineKind === "removed" ? view.removedGutter : view.headerSurface
                        Text {
                            anchors.fill: parent
                            anchors.rightMargin: Spacing.xs
                            text: String(Logic.lineValue(lineData, "oldLine", ""))
                            color: lineKind === "context" ? Theme.diffContextText : Theme.white
                            font.family: Typography.dataFamily
                            font.pixelSize: Typography.microSize
                            horizontalAlignment: Text.AlignRight
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    Rectangle {
                        Layout.preferredWidth: view.gutterWidth
                        Layout.fillHeight: true
                        color: lineKind === "added" ? view.addedGutter : lineKind === "removed" ? view.removedGutter : view.headerSurface
                        Text {
                            anchors.fill: parent
                            anchors.rightMargin: Spacing.xs
                            text: String(Logic.lineValue(lineData, "newLine", ""))
                            color: lineKind === "context" ? Theme.diffContextText : Theme.white
                            font.family: Typography.dataFamily
                            font.pixelSize: Typography.microSize
                            horizontalAlignment: Text.AlignRight
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                    Text {
                        id: diffText
                        Layout.fillWidth: true
                        text: String(Logic.lineValue(lineData, "prefix", " ")) + " " + String(Logic.lineValue(lineData, "text", ""))
                        color: lineKind === "added" ? Theme.white : lineKind === "removed" ? Theme.white : Theme.diffContextText
                        font.family: Typography.dataFamily
                        font.pixelSize: Typography.bodySize
                        verticalAlignment: Text.AlignVCenter
                        clip: true
                    }
                }
            }
        }

        MutedLabel {
            anchors.centerIn: parent
            visible: !app.controller.currentDiffLines || app.controller.currentDiffLines.length === 0
            text: "No differences for this file."
        }
    }
}
