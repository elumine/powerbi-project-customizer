import QtQuick
import QtQuick.Controls
import ui.styles 1.0
import "IconButtonLogic.js" as Logic

Button {
    id: control
    IconButtonStyle { id: style }

    property color contentColor: style.contentColor
    property string tooltipText: ""
    implicitWidth: Geometry.controlHeight
    implicitHeight: Geometry.controlHeight
    padding: 0
    scale: control.down ? Motion.pressScale : control.hovered ? Motion.hoverScale : 1.0

    ToolTip.visible: control.hovered && tooltipText.length > 0
    ToolTip.delay: Motion.standard
    ToolTip.text: tooltipText

    Behavior on scale { NumberAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }

    background: Rectangle {
        radius: Geometry.radiusSm
        color: control.down ? style.pressedBackground : control.hovered ? style.hoverBackground : style.idleBackground
        Behavior on color { ColorAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }
    }

    contentItem: Text {
        text: Logic.coalesce(control.text, "")
        color: control.enabled ? control.contentColor : Theme.dimText
        font.family: Typography.uiFamily
        font.pixelSize: Math.max(Typography.sectionSize * 2 - 2, 26)
        font.weight: Font.DemiBold
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }
}
