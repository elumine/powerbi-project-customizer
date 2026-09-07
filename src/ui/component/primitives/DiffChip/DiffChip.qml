import QtQuick
import ui.styles 1.0
import "DiffChipLogic.js" as Logic
Rectangle {
    id: chip
    DiffChipStyle { id: style }
    property string value: ""
    property color chipColor: style.defaultColor
    property color chipTextColor: style.textColor
    property bool active: false
    implicitHeight: Math.max(24, chipText.implicitHeight + 8); implicitWidth: Math.min(260, chipText.implicitWidth + 14); radius: 2; color: chip.chipColor; border.color: chip.active ? "#ffffff" : "transparent"; border.width: chip.active ? 1 : 0
    Text { id: chipText; anchors.fill: parent; anchors.margins: 4; text: chip.value; color: chip.chipTextColor; font.family: "Consolas"; font.pixelSize: 12; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter }
}
