import QtQuick
import QtQuick.Controls
import ui.styles 1.0
import "ChromeButtonLogic.js" as Logic
Button {
    id: control
    ChromeButtonStyle { id: style }
    property color normalColor: style.normalColor
    property color hoverColor: style.hoverColor
    property color pressedColor: style.pressedColor
    property color disabledColor: style.disabledColor
    property color contentColor: style.contentColor
    implicitHeight: 32
    padding: 8
    background: Rectangle { radius: 3; color: !control.enabled ? control.disabledColor : control.down ? control.pressedColor : control.hovered ? control.hoverColor : control.normalColor; border.color: Qt.darker(color, 1.15) }
    contentItem: Text { text: control.text; color: control.enabled ? control.contentColor : Theme.mutedText; font.family: "Segoe UI"; font.pixelSize: 12; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
}
