import QtQuick
import QtQuick.Controls
import ui.styles 1.0
import "DarkComboLogic.js" as Logic

ComboBox {
    id: control

    DarkComboStyle { id: style }

    property string textRoleName: "label"
    property string valueRoleName: "value"

    implicitHeight: 32

    function optionText(option) {
        return typeof option === "object" && option !== null && option[textRoleName] !== undefined
            ? option[textRoleName]
            : option
    }

    function optionValue(option) {
        return typeof option === "object" && option !== null && option[valueRoleName] !== undefined
            ? option[valueRoleName]
            : optionText(option)
    }

    function optionEnabled(option) {
        return !(typeof option === "object" && option !== null && option.enabled === false)
    }

    contentItem: Text {
        text: Logic.coalesce(control.optionText(control.currentIndex >= 0 ? control.model[control.currentIndex] : control.displayText), "")
        color: Theme.textColor
        font.family: "Segoe UI"
        font.pixelSize: 12
        verticalAlignment: Text.AlignVCenter
        leftPadding: 8
        rightPadding: 24
        elide: Text.ElideRight
    }

    background: Rectangle {
        color: Theme.inputBackground
        border.color: control.activeFocus ? Theme.statusBackground : Theme.borderColor
        radius: 2
    }

    delegate: ItemDelegate {
        width: control.width
        height: style.itemHeight
        enabled: control.optionEnabled(modelData)
        opacity: enabled ? 1.0 : 0.5

        contentItem: Text {
            text: control.optionText(modelData)
            color: Theme.textColor
            font.family: "Segoe UI"
            font.pixelSize: 12
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }

        background: Rectangle {
            color: highlighted && enabled ? Theme.listActive : Theme.panelBackground
        }
    }

    popup: Popup {
        y: control.height
        width: control.width
        implicitHeight: contentItem.implicitHeight
        padding: 1

        contentItem: ListView {
            clip: true
            implicitHeight: contentHeight
            model: control.popup.visible ? control.delegateModel : null
            currentIndex: control.highlightedIndex
        }

        background: Rectangle {
            color: Theme.panelBackground
            border.color: Theme.borderColor
        }
    }
}
