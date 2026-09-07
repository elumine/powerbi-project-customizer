import QtQuick
import ui.styles 1.0
import "MutedLabelLogic.js" as Logic
Text {
    MutedLabelStyle { id: style }
    color: style.textColor
    font.family: "Segoe UI"
    font.pixelSize: 12
    wrapMode: Text.WordWrap
}
