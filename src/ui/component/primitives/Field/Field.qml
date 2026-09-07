import QtQuick
import QtQuick.Controls
import ui.styles 1.0
import "FieldLogic.js" as Logic
TextField {
    id: control
    FieldStyle { id: style }
    color: Theme.textColor; placeholderTextColor: Theme.mutedText; selectedTextColor: style.selectedTextColor; selectionColor: style.selectionColor
    font.family: "Segoe UI"; font.pixelSize: 12; leftPadding: 8; rightPadding: 8
    background: Rectangle { color: Theme.inputBackground; border.color: control.activeFocus ? Theme.statusBackground : Theme.borderColor; radius: 2 }
}
