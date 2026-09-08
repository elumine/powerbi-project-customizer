import QtQuick
import ui.styles 1.0
import "DiffChipLogic.js" as Logic

Rectangle {
    id: chip
    DiffChipStyle { id: style }

    property string value: ""
    property color chipColor: style.defaultColor
    property color chipTextColor: Theme.contrastText(chipColor)
    property bool active: false

    implicitHeight: Math.max(Geometry.controlHeight - Spacing.xs, chipText.implicitHeight + Spacing.sm)
    implicitWidth: Math.min(260, chipText.implicitWidth + Spacing.lg)
    radius: style.radius
    color: chip.chipColor
    border.color: chip.active ? style.activeBorder : "transparent"
    border.width: chip.active ? Geometry.borderWidth : 0
    scale: chip.active ? Motion.hoverScale : 1.0

    Behavior on color { ColorAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }
    Behavior on scale { NumberAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }

    Text {
        id: chipText
        anchors.fill: parent
        anchors.margins: Spacing.xs
        text: Logic.coalesce(chip.value, "")
        color: chip.chipTextColor
        font.family: Typography.dataFamily
        font.pixelSize: Typography.bodySize
        elide: Text.ElideRight
        verticalAlignment: Text.AlignVCenter
    }
}
