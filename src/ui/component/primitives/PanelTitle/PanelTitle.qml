import QtQuick
import ui.styles 1.0
import "PanelTitleLogic.js" as Logic

Text {
    id: control
    PanelTitleStyle { id: style }

    text: Logic.coalesce(control.text, "")
    color: style.textColor
    font.family: Typography.uiFamily
    font.pixelSize: Typography.captionSize
    font.weight: Font.DemiBold
    elide: Text.ElideRight
    opacity: enabled ? 1.0 : 0.55
}
