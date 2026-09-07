import QtQuick
import QtQuick.Controls
import ui.styles 1.0
import "PanelButtonLogic.js" as Logic
Button {
    id: control
    PanelButtonStyle { id: style }
    property bool active: false
    property string tooltipText: ""
    implicitWidth: 52; implicitHeight: 52; padding: 0
    ToolTip.visible: hovered; ToolTip.delay: 450; ToolTip.text: tooltipText
    background: Rectangle { color: control.active ? style.activeBackground : control.hovered ? style.hoverBackground : "transparent"; border.width: control.active ? 3 : 0; border.color: style.activeBorder }
    contentItem: Text { text: control.text; color: control.active ? "#ffffff" : Theme.mutedText; font.family: "Segoe UI"; font.pixelSize: 17; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
}
