import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "MacrosPanelLogic.js" as Logic

ColumnLayout {
    id: panel
    MacrosPanelStyle { id: style }

    required property var app
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    spacing: style.panelSpacing

    RowLayout {
        Layout.fillWidth: true
        PanelTitle { text: "MACROS"; Layout.fillWidth: true }
        Text {
            text: app.controller.macroCount + " macro(s)"
            color: app.mutedText
            font.family: Typography.uiFamily
            font.pixelSize: Typography.captionSize
        }
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: Spacing.xs
        Field {
            id: macroNameSearch
            Layout.fillWidth: true
            placeholderText: "Search macros by name"
            text: app.controller.macroSearchText
            onTextEdited: macroSearchDebounce.restart()
        }
        IconButton {
            text: "×"
            tooltipText: "Clear macro search"
            contentColor: Theme.accentRed
            visible: macroNameSearch.text.length > 0
            onClicked: {
                macroNameSearch.text = ""
                macroSearchDebounce.restart()
            }
        }
    }

    Timer {
        id: macroSearchDebounce
        interval: 200
        repeat: false
        onTriggered: app.callController(function(c) { c.setMacroSearchText(macroNameSearch.text) })
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: Spacing.sm
        ChromeButton {
            Layout.fillWidth: true
            text: "Import"
            actionType: "save"
            onClicked: app.callController(function(c) { c.importMacro() })
        }
        ChromeButton {
            Layout.fillWidth: true
            text: "Reload"
            actionType: "neutral"
            onClicked: app.callController(function(c) { c.reloadContent() })
        }
    }

    ScrollView {
        id: macroScroll
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

        GridLayout {
            id: macroGrid
            width: macroScroll.availableWidth
            columns: 1
            rowSpacing: Spacing.sm
            implicitHeight: childrenRect.height

            Repeater {
                model: app.controller.macroModel

                delegate: Rectangle {
                    id: macroRow
                    property int macroIndex: index
                    property bool stepsOpen: false
                    property var macroGroups: groups || []
                    property int stepsHeight: Math.min(style.maxStepsHeight, Math.max(0, (steps ? steps.length : 0) * style.stepRowHeight))

                    Layout.column: 0
                    Layout.row: macroIndex
                    Layout.fillWidth: true
                    Layout.minimumWidth: 0
                    Layout.preferredWidth: macroGrid.width
                    Layout.preferredHeight: implicitHeight
                    implicitHeight: stepsOpen ? style.cardOpenBaseHeight + stepsHeight : style.cardClosedHeight
                    height: implicitHeight
                    radius: Geometry.radiusMd
                    color: macroMouse.containsMouse ? app.listHover : app.editorBackground
                    border.width: Geometry.borderWidth
                    border.color: validationText.length > 0 ? app.warningColor : app.borderColor

                    Behavior on height { NumberAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }

                    MouseArea {
                        id: macroMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        acceptedButtons: Qt.NoButton
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Spacing.sm
                        spacing: Spacing.xs

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                Layout.fillWidth: true
                                text: name
                                color: app.textColor
                                font.family: Typography.uiFamily
                                font.pixelSize: Typography.bodySize
                                font.weight: Font.DemiBold
                                elide: Text.ElideRight
                            }
                            Text {
                                text: stepCount + " step(s)"
                                color: app.mutedText
                                font.family: Typography.uiFamily
                                font.pixelSize: Typography.microSize
                            }
                        }

                        Text {
                            Layout.fillWidth: true
                            text: statusText
                            color: validationText.length > 0 ? app.warningColor : app.mutedText
                            font.family: Typography.uiFamily
                            font.pixelSize: Typography.microSize
                            elide: Text.ElideRight
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Spacing.sm
                            ChromeButton {
                                text: running ? "Running" : "Run"
                                actionType: "execute"
                                enabled: canRun
                                onClicked: app.callController(function(c) { c.runMacro(macroIndex) })
                            }
                            ChromeButton {
                                text: "Export"
                                actionType: "save"
                                onClicked: app.callController(function(c) { c.exportMacro(macroIndex) })
                            }
                            ChromeButton {
                                text: macroRow.stepsOpen ? "Hide steps" : "Steps"
                                actionType: "neutral"
                                enabled: stepCount > 0
                                onClicked: macroRow.stepsOpen = !macroRow.stepsOpen
                            }
                            Item { Layout.fillWidth: true }
                        }

                        ListView {
                            visible: macroRow.stepsOpen && macroRow.macroGroups.length > 0
                            Layout.fillWidth: true
                            Layout.preferredHeight: macroRow.stepsHeight
                            Layout.maximumHeight: style.maxStepsHeight
                            clip: true
                            model: macroRow.macroGroups
                            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

                            delegate: ColumnLayout {
                                width: macroRow.width - Spacing.xl
                                spacing: Spacing.xxs
                                property var groupData: modelData

                                Text {
                                    Layout.fillWidth: true
                                    text: groupData["name"] || ""
                                    color: app.textColor
                                    font.family: Typography.uiFamily
                                    font.pixelSize: Typography.microSize
                                    font.weight: Font.DemiBold
                                    elide: Text.ElideRight
                                }
                                Repeater {
                                    model: groupData["steps"] || []
                                    delegate: Text {
                                        property var stepData: modelData
                                        Layout.fillWidth: true
                                        text: "  " + (stepData["type"] || "") + " - " + (stepData["summary"] || "")
                                        color: app.mutedText
                                        font.family: Typography.dataFamily
                                        font.pixelSize: Typography.microSize
                                        elide: Text.ElideMiddle
                                    }
                                }
                            }
                        }

                        ListView {
                            visible: macroRow.stepsOpen && macroRow.macroGroups.length === 0
                            Layout.fillWidth: true
                            Layout.preferredHeight: macroRow.stepsHeight
                            Layout.maximumHeight: style.maxStepsHeight
                            clip: true
                            model: steps
                            ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                            delegate: Text {
                                width: macroRow.width - Spacing.xl
                                text: (index + 1) + ". " + modelData.type + " - " + modelData.summary
                                color: app.mutedText
                                font.family: Typography.dataFamily
                                font.pixelSize: Typography.microSize
                                elide: Text.ElideMiddle
                            }
                        }
                    }
                }
            }
        }
    }

    MutedLabel {
        visible: app.controller.macroCount === 0
        Layout.fillWidth: true
        text: macroNameSearch.text.length > 0
            ? "No macros match this name."
            : "No macros yet. Import a JSON macro to automate repeatable work."
    }
}
