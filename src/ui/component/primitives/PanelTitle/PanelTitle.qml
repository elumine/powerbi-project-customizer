import QtQuick
import ui.styles 1.0
import "PanelTitleLogic.js" as Logic
Text {
    PanelTitleStyle { id: style }
    color: style.textColor
    font.family: "Segoe UI"
    font.pixelSize: 11
    font.bold: true
    elide: Text.ElideRight
}
