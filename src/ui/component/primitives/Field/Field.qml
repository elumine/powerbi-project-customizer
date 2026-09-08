import QtQuick
import QtQuick.Controls
import ui.styles 1.0
import "FieldLogic.js" as Logic

TextField {
    id: control
    FieldStyle { id: style }

    implicitHeight: Geometry.controlHeight
    color: Theme.textColor
    placeholderTextColor: Theme.dimText
    selectedTextColor: style.selectedTextColor
    selectionColor: style.selectionColor
    font.family: Typography.uiFamily
    font.pixelSize: Typography.bodySize
    leftPadding: Spacing.md
    rightPadding: Spacing.md

    background: Rectangle {
        radius: Geometry.radiusSm
        color: control.activeFocus ? style.focusedBackground : style.background
        border.width: Geometry.borderWidth
        border.color: control.activeFocus ? style.focusedBorder : style.border

        Behavior on color { ColorAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }
    }

    onTextChanged: {
        // Touch the local logic contract while normalizing text input remains caller-owned.
        Logic.coalesce(text, "")
    }
}
