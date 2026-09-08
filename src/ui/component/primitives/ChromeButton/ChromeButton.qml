import QtQuick
import QtQuick.Controls
import ui.styles 1.0
import "ChromeButtonLogic.js" as Logic

Button {
    id: control
    ChromeButtonStyle { id: style }

    // Button intent is explicit; callers can still override colors for rare
    // domain-specific controls, while ordinary actions remain consistent.
    property string actionType: "execute"
    property color normalColor: actionType === "save" ? Theme.actionSave : actionType === "cancel" ? Theme.actionCancel : actionType === "neutral" ? Theme.neutralAction : style.normalColor
    property color hoverColor: actionType === "save" ? Theme.actionSaveHover : actionType === "cancel" ? Theme.actionCancelHover : actionType === "neutral" ? Theme.neutralActionHover : style.hoverColor
    property color pressedColor: actionType === "save" ? Theme.actionSavePressed : actionType === "cancel" ? Theme.actionCancelPressed : actionType === "neutral" ? Theme.neutralActionPressed : style.pressedColor
    property color disabledColor: style.disabledColor
    property color contentColor: style.contentColor

    implicitHeight: Geometry.controlHeight
    leftPadding: style.horizontalPadding
    rightPadding: style.horizontalPadding
    scale: control.down ? Motion.pressScale : control.hovered ? Motion.hoverScale : 1.0

    Behavior on scale {
        NumberAnimation { duration: Motion.quick; easing.type: Easing.OutCubic }
    }

    background: Rectangle {
        radius: style.radius
        color: !control.enabled ? control.disabledColor : control.down ? control.pressedColor : control.hovered ? control.hoverColor : control.normalColor
        border.width: Geometry.borderWidth
        border.color: control.enabled ? Qt.lighter(color, 1.08) : Theme.borderSubtle

        Behavior on color {
            ColorAnimation { duration: Motion.quick; easing.type: Easing.OutCubic }
        }
    }

    contentItem: Text {
        text: Logic.coalesce(control.text, "")
        color: control.enabled ? control.contentColor : style.disabledContentColor
        font.family: Typography.uiFamily
        font.pixelSize: Typography.bodySize
        font.weight: Font.DemiBold
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }
}
