import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "SearchPanelLogic.js" as Logic

ColumnLayout {
    id: panel
    SearchPanelStyle { id: style }

    required property var app
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    spacing: style.panelSpacing

    RowLayout {
        Layout.fillWidth: true
        PanelTitle { text: "Search & replace"; Layout.fillWidth: true }
        DiffChip {
            value: app.controller.totalMatches + " hits"
            chipColor: app.controller.totalMatches > 0 ? Theme.visualChart : Theme.controlBackground
            chipTextColor: app.controller.totalMatches > 0 ? Theme.contrastText(Theme.visualChart) : Theme.mutedText
        }
    }

    Field {
        Layout.fillWidth: true
        placeholderText: "Find in active files"
        text: app.controller.searchText
        onTextEdited: app.callController(function(controller) { controller.searchText = text })
    }
    Field {
        Layout.fillWidth: true
        placeholderText: "Replace with"
        text: app.controller.replaceText
        onTextEdited: app.callController(function(controller) { controller.replaceText = text })
    }

    CheckBox {
        id: caseSensitive
        text: "Case sensitive"
        checked: app.controller.caseSensitive
        onToggled: app.callController(function(controller) { controller.caseSensitive = checked })
        contentItem: Text {
            text: caseSensitive.text
            color: Theme.mutedText
            font.family: Typography.uiFamily
            font.pixelSize: Typography.captionSize
            leftPadding: caseSensitive.indicator.width + Spacing.sm
            verticalAlignment: Text.AlignVCenter
        }
        indicator: Rectangle {
            implicitWidth: 18
            implicitHeight: 18
            radius: Geometry.radiusXs
            color: caseSensitive.checked ? Theme.accentBlue : Theme.inputBackground
            border.width: Geometry.borderWidth
            border.color: caseSensitive.checked ? Theme.accentBlue : Theme.borderColor
            Text { anchors.centerIn: parent; text: caseSensitive.checked ? "✓" : ""; color: Theme.white; font.weight: Font.DemiBold }
            Behavior on color { ColorAnimation { duration: Motion.quick } }
        }
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: Spacing.xs
        ChromeButton {
            Layout.fillWidth: true
            text: "Search"
            actionType: "execute"
            enabled: app.controller.searchText.length > 0
            onClicked: app.callController(function(controller) { controller.runSearch() })
        }
        ChromeButton {
            Layout.fillWidth: true
            text: "Replace match"
            actionType: "execute"
            enabled: app.controller.activeFileCount > 0 && app.controller.searchText.length > 0
            onClicked: app.callController(function(controller) { controller.replaceCurrentMatch() })
        }
        ChromeButton {
            Layout.fillWidth: true
            text: "Replace all"
            actionType: "execute"
            enabled: app.controller.activeFileCount > 0 && app.controller.searchText.length > 0
            onClicked: app.callController(function(controller) { controller.replaceAll() })
        }
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: Spacing.xs
        IconButton { text: "↑"; tooltipText: "Previous match"; enabled: app.controller.totalMatches > 0; onClicked: app.callController(function(controller) { controller.navigatePreviousMatch() }) }
        IconButton { text: "↓"; tooltipText: "Next match"; enabled: app.controller.totalMatches > 0; onClicked: app.callController(function(controller) { controller.navigateNextMatch() }) }
        Text {
            Layout.fillWidth: true
            text: "Across " + app.controller.activeFileCount + " active files"
            color: Theme.dimText
            font.family: Typography.uiFamily
            font.pixelSize: Typography.captionSize
            elide: Text.ElideRight
        }
    }

    ListView {
        id: searchResultList
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        spacing: Spacing.xs
        model: app.controller.searchResultModel
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
        add: Transition { NumberAnimation { properties: "opacity"; from: 0; to: 1; duration: Motion.standard } }
        displaced: Transition { NumberAnimation { properties: "y"; duration: Motion.standard; easing.type: Easing.OutCubic } }
        delegate: Rectangle {
            required property int fileIndex
            required property int matchIndex
            required property string displayText
            required property string before
            required property string match
            required property string after
            required property string replacement
            required property int start
            width: searchResultList.width
            height: 56
            radius: Geometry.radiusSm
            color: resultMouse.containsMouse ? style.resultHover : style.resultBackground
            border.width: Geometry.borderWidth
            border.color: Theme.borderSubtle
            scale: resultMouse.containsMouse ? Motion.hoverScale : 1.0
            Behavior on color { ColorAnimation { duration: Motion.quick } }
            Behavior on scale { NumberAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }
            MouseArea {
                id: resultMouse
                anchors.fill: parent
                hoverEnabled: true
                onClicked: app.callController(function(controller) { controller.navigateToMatch(fileIndex, matchIndex) })
            }
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Geometry.cardPadding
                spacing: Spacing.xxs
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 0
                    Text {
                        text: before
                        color: Theme.textColor
                        font.family: Typography.dataFamily
                        font.pixelSize: Typography.captionSize
                        elide: Text.ElideLeft
                    }
                    Rectangle {
                        Layout.preferredHeight: 22
                        Layout.preferredWidth: searchMatchText.implicitWidth + Spacing.sm
                        radius: Geometry.radiusXs
                        color: Theme.accentRed
                        Text {
                            id: searchMatchText
                            anchors.centerIn: parent
                            text: match
                            color: Theme.white
                            font.family: Typography.dataFamily
                            font.pixelSize: Typography.captionSize
                        }
                    }
                    Rectangle {
                        visible: replacement.length > 0
                        Layout.preferredHeight: 22
                        Layout.preferredWidth: visible ? replacementText.implicitWidth + Spacing.sm : 0
                        radius: Geometry.radiusXs
                        color: Theme.okColor
                        Text {
                            id: replacementText
                            anchors.centerIn: parent
                            text: replacement
                            color: Theme.contrastText(Theme.okColor)
                            font.family: Typography.dataFamily
                            font.pixelSize: Typography.captionSize
                        }
                    }
                    Text {
                        Layout.fillWidth: true
                        text: after
                        color: Theme.textColor
                        font.family: Typography.dataFamily
                        font.pixelSize: Typography.captionSize
                        elide: Text.ElideRight
                    }
                }
                Text {
                    Layout.fillWidth: true
                    text: "Match " + (matchIndex + 1) + " · offset " + start
                    color: Theme.dimText
                    font.family: Typography.dataFamily
                    font.pixelSize: Typography.microSize
                    elide: Text.ElideMiddle
                }
            }
        }
    }
}
