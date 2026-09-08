import QtQuick
import QtQuick.Controls
import ui.styles 1.0
import "PanelButtonLogic.js" as Logic

Button {
    id: control
    PanelButtonStyle { id: style }

    property bool active: false
    property string tooltipText: ""
    property url iconSource: ""

    implicitWidth: Geometry.sidebarWidth
    implicitHeight: Geometry.sidebarWidth
    padding: 0
    scale: control.down ? Motion.pressScale : control.hovered ? Motion.hoverScale : 1.0

    ToolTip.visible: control.hovered && tooltipText.length > 0
    ToolTip.delay: Motion.standard
    ToolTip.text: tooltipText

    Behavior on scale {
        NumberAnimation { duration: Motion.quick; easing.type: Easing.OutCubic }
    }

    background: Rectangle {
        radius: Geometry.radiusSm
        color: control.active ? style.activeBackground : control.hovered ? style.hoverBackground : "transparent"
        border.width: Geometry.borderWidth
        border.color: control.active ? Theme.borderColor : "transparent"

        Rectangle {
            width: style.indicatorWidth
            height: parent.height - Spacing.lg
            anchors.left: parent.left
            anchors.verticalCenter: parent.verticalCenter
            radius: width / 2
            color: style.activeBorder
            opacity: control.active ? 1.0 : 0.0
            Behavior on opacity { NumberAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }
        }

        Behavior on color { ColorAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }
    }

    contentItem: Item {
        Image {
            anchors.centerIn: parent
            width: Math.min(parent.width - Spacing.lg, 36)
            height: width
            source: control.iconSource
            visible: control.iconSource.toString().length > 0
            fillMode: Image.PreserveAspectFit
            opacity: control.active ? 1.0 : 0.62
            Behavior on opacity { NumberAnimation { duration: Motion.quick } }
        }
        Text {
            anchors.centerIn: parent
            visible: control.iconSource.toString().length === 0
            text: Logic.coalesce(control.text, "")
            color: control.active ? style.activeContent : style.idleContent
            font.family: Typography.uiFamily
            font.pixelSize: Math.max(Typography.sectionSize * 2 - 2, 28)
            font.weight: Font.DemiBold
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }
}
