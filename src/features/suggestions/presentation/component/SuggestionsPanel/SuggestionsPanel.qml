import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "SuggestionsPanelLogic.js" as Logic

ColumnLayout {
    id: panel
    SuggestionsPanelStyle { id: style }

    required property var app
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    spacing: style.panelSpacing

    RowLayout {
        Layout.fillWidth: true
        PanelTitle { text: "Data signals"; Layout.fillWidth: true }
        DiffChip {
            value: (app.controller.suggestionKeyCount + app.controller.suggestionValueCount) + " signals"
            chipColor: Theme.visualPie
        }
    }

    Text {
        Layout.fillWidth: true
        text: "Repeated keys and values worth inspecting across the active JSON workspace."
        color: Theme.mutedText
        font.family: Typography.uiFamily
        font.pixelSize: Typography.captionSize
        wrapMode: Text.WordWrap
    }

    PanelTitle { text: "Repeated keys" }
    ListView {
        id: keyList
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        spacing: Spacing.xs
        model: app.controller.suggestionKeyModel
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
        delegate: Rectangle {
            required property string duplicationValue
            required property int duplicationCount
            required property color suggestionColor
            required property int index
            width: keyList.width
            height: Geometry.controlHeight
            radius: Geometry.radiusSm
            color: suggestionColor
            scale: keyMouse.containsMouse ? Motion.hoverScale : 1.0
            Behavior on scale { NumberAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }
            MouseArea { id: keyMouse; anchors.fill: parent; hoverEnabled: true; onClicked: app.callController(function(controller) { controller.openSuggestionSearch("key", index) }) }
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Spacing.sm
                anchors.rightMargin: Spacing.sm
                Text {
                    Layout.fillWidth: true
                    text: duplicationValue
                    color: Theme.contrastText(suggestionColor)
                    font.family: Typography.dataFamily
                    font.pixelSize: Typography.captionSize
                    elide: Text.ElideRight
                }
                DiffChip { value: duplicationCount + "×"; chipColor: Theme.black; chipTextColor: Theme.white }
            }
        }
    }

    PanelTitle { text: "Repeated values" }
    ListView {
        id: valueList
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        spacing: Spacing.xs
        model: app.controller.suggestionValueModel
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
        delegate: Rectangle {
            required property string duplicationValue
            required property int duplicationCount
            required property color suggestionColor
            required property int index
            width: valueList.width
            height: Geometry.controlHeight
            radius: Geometry.radiusSm
            color: suggestionColor
            scale: valueMouse.containsMouse ? Motion.hoverScale : 1.0
            Behavior on scale { NumberAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }
            MouseArea { id: valueMouse; anchors.fill: parent; hoverEnabled: true; onClicked: app.callController(function(controller) { controller.openSuggestionSearch("value", index) }) }
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Spacing.sm
                anchors.rightMargin: Spacing.sm
                Text {
                    Layout.fillWidth: true
                    text: duplicationValue
                    color: Theme.contrastText(suggestionColor)
                    font.family: Typography.dataFamily
                    font.pixelSize: Typography.captionSize
                    elide: Text.ElideRight
                }
                DiffChip { value: duplicationCount + "×"; chipColor: Theme.black; chipTextColor: Theme.white }
            }
        }
    }
}
