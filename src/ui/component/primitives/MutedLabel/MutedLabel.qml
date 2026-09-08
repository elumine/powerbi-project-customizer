import QtQuick
import ui.styles 1.0
import "MutedLabelLogic.js" as Logic

Text {
    id: control
    MutedLabelStyle { id: style }

    text: Logic.coalesce(control.text, "")
    color: enabled ? style.textColor : style.disabledColor
    font.family: Typography.uiFamily
    font.pixelSize: Typography.bodySize
    wrapMode: Text.WordWrap
}
