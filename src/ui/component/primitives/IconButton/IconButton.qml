import QtQuick
import QtQuick.Controls
import ui.styles 1.0
import "IconButtonLogic.js" as Logic
Button {
    id: control
    IconButtonStyle { id: style }
    property color contentColor: style.contentColor
    implicitWidth: 30; implicitHeight: 28; padding: 0
    background: Rectangle { radius: 3; color: control.down ? Theme.listActive : control.hovered ? Theme.listHover : "transparent" }
    contentItem: Text { text: control.text; color: control.enabled ? control.contentColor : Theme.mutedText; font.family: "Segoe UI"; font.pixelSize: 12; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
}
