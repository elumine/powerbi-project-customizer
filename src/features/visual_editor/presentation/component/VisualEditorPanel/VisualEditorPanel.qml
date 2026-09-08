import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "VisualEditorPanelLogic.js" as Logic

ColumnLayout {
    id: panel
    VisualEditorPanelStyle { id: style }

    required property var app
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    spacing: style.panelSpacing

    RowLayout {
        Layout.fillWidth: true
        PanelTitle { text: "Visual controls"; Layout.fillWidth: true }
        DiffChip {
            value: app.controller.activeVisualCount + " active"
            chipColor: Theme.visualTable
        }
    }

    DarkCombo {
        id: categoryCombo
        Layout.fillWidth: true
        model: app.controller.visualEditorCategoryOptions
        currentIndex: Logic.optionIndex(app.controller.visualEditorCategoryOptions, app.controller.visualEditorCategory)
        onActivated: {
            const option = app.controller.visualEditorCategoryOptions[index]
            if (categoryCombo.optionEnabled(option)) {
                app.callController(function(controller) {
                    controller.setVisualEditorCategory(categoryCombo.optionValue(option))
                })
            }
        }
    }

    Rectangle {
        Layout.fillWidth: true
        Layout.preferredHeight: 30
        radius: Geometry.radiusSm
        color: Theme.controlBackground
        border.width: Geometry.borderWidth
        border.color: Theme.borderSubtle
        Text {
            anchors.fill: parent
            anchors.leftMargin: Spacing.sm
            anchors.rightMargin: Spacing.sm
            text: app.controller.visualEditorStatus.length > 0 ? app.controller.visualEditorStatus : "Choose a visual type to expose matching controls."
            color: Theme.mutedText
            font.family: Typography.uiFamily
            font.pixelSize: Typography.captionSize
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }
    }

    ListView {
        id: visualControlList
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        spacing: Spacing.sm
        model: app.controller.visualEditorControlModel
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
        section.property: "groupLabel"
        section.criteria: ViewSection.FullString
        section.delegate: Rectangle {
            width: visualControlList.width
            height: section.length > 0 ? 30 : 0
            radius: Geometry.radiusSm
            color: Theme.controlBackground
            border.width: Geometry.borderWidth
            border.color: Theme.borderSubtle
            Rectangle {
                width: 4
                height: parent.height - Spacing.sm
                anchors.left: parent.left
                anchors.leftMargin: Spacing.xs
                anchors.verticalCenter: parent.verticalCenter
                radius: width / 2
                color: Theme.visualTypeColor(section)
            }
            Text {
                anchors.left: parent.left
                anchors.leftMargin: Spacing.lg
                anchors.right: parent.right
                anchors.rightMargin: Spacing.xs
                anchors.verticalCenter: parent.verticalCenter
                text: section.length > 0 ? section : "All visuals"
                color: Theme.mutedText
                font.family: Typography.dataFamily
                font.pixelSize: Typography.microSize
                font.weight: Font.DemiBold
                elide: Text.ElideRight
            }
        }

        add: Transition {
            NumberAnimation { properties: "opacity"; from: 0; to: 1; duration: Motion.relaxed }
            NumberAnimation { properties: "y"; from: Spacing.sm; duration: Motion.relaxed; easing.type: Easing.OutCubic }
        }
        displaced: Transition { NumberAnimation { properties: "y"; duration: Motion.standard; easing.type: Easing.OutCubic } }

        delegate: Rectangle {
            id: controlCard
            property string controlId: model.id
            property string controlLabel: model.label
            property string controlKind: model.control
            property string controlValueType: model.valueType
            property var controlOptions: model.options || []
            property string controlVisualType: model.visualTypeGroup
            property string controlDescription: model.description
            property string controlDefaultValue: model.defaultValue
            property int controlMatchingCount: model.matchingCount
            property var controlMatches: model.matches || []
            property var controlGroupPath: model.groupPath || []
            property bool matchesOpen: false
            readonly property color accent: Theme.controlTypeColor(controlKind, controlValueType)

            width: visualControlList.width
            height: matchesOpen ? 178 : 108
            radius: Geometry.radiusMd
            color: controlMouse.containsMouse ? style.cardHover : style.cardBackground
            border.width: Geometry.borderWidth
            border.color: accent
            scale: controlMouse.containsMouse ? Motion.hoverScale : 1.0

            Behavior on height { NumberAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }
            Behavior on color { ColorAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }
            Behavior on scale { NumberAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }

            MouseArea { id: controlMouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }

            Rectangle {
                width: 4
                height: parent.height - Spacing.md
                anchors.left: parent.left
                anchors.leftMargin: Spacing.xs
                anchors.verticalCenter: parent.verticalCenter
                radius: width / 2
                color: controlCard.accent
                Behavior on color { ColorAnimation { duration: Motion.standard } }
            }

            function inputValue() {
                if (controlKind === "boolean") return visualBoolean.checked
                if (controlKind === "slider" || controlValueType === "percentage") return Math.round(visualSlider.value)
                if (controlOptions.length > 0) return visualEnum.currentText
                return visualValue.text
            }

            ColumnLayout {
                anchors.fill: parent
                anchors.leftMargin: Spacing.lg
                anchors.rightMargin: Spacing.sm
                anchors.topMargin: Spacing.sm
                anchors.bottomMargin: Spacing.sm
                spacing: Spacing.xs

                RowLayout {
                    Layout.fillWidth: true
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Spacing.xxs
                        Text {
                            Layout.fillWidth: true
                            text: controlLabel
                            color: Theme.textColor
                            font.family: Typography.uiFamily
                            font.pixelSize: Typography.labelSize
                            font.weight: Font.DemiBold
                            elide: Text.ElideRight
                        }
                    }
                    DiffChip {
                        value: controlKind
                        chipColor: controlCard.accent
                    }
                    ChromeButton {
                        text: "Apply"
                        actionType: "execute"
                        enabled: app.controller.activeVisualCount > 0
                        onClicked: app.callController(function(controller) {
                            controller.applyVisualEditorChange(controlId, controlCard.inputValue())
                        })
                    }
                    IconButton {
                        Layout.preferredWidth: 20
                        Layout.preferredHeight: 20
                        text: matchesOpen ? "⌃" : "⌄"
                        tooltipText: matchesOpen ? "Hide matches" : "Show matches"
                        contentColor: controlCard.accent
                        enabled: controlMatches.length > 0
                        onClicked: matchesOpen = !matchesOpen
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Spacing.sm
                    Rectangle {
                        id: colorPreview
                        visible: controlKind === "color"
                        Layout.preferredWidth: 32
                        Layout.preferredHeight: 32
                        radius: width / 2
                        color: Theme.safeColor(visualValue.text, controlCard.accent)
                        border.width: 2
                        border.color: Theme.white
                        ToolTip.visible: colorPreviewMouse.containsMouse
                        ToolTip.delay: Motion.standard
                        ToolTip.text: "Open color picker"
                        MouseArea {
                            id: colorPreviewMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            onClicked: colorPicker.openFor(visualValue.text)
                        }
                    }
                    ColorPickerPopup {
                        id: colorPicker
                        onColorSelected: visualValue.text = color
                    }
                    DarkCombo {
                        id: visualEnum
                        visible: controlOptions.length > 0
                        Layout.fillWidth: true
                        model: controlOptions
                        currentIndex: Logic.optionIndex(controlOptions, controlDefaultValue)
                    }
                    Field {
                        id: visualValue
                        visible: controlOptions.length === 0 && controlKind !== "color" && controlKind !== "boolean" && controlKind !== "slider" && controlValueType !== "percentage"
                        Layout.fillWidth: true
                        text: controlDefaultValue
                        placeholderText: "Value"
                    }
                    Flow {
                        visible: controlKind === "color"
                        Layout.fillWidth: true
                        spacing: Spacing.xs
                        Repeater {
                            model: [
                                Theme.accentRed, Theme.visualChart, Theme.visualTable,
                                Theme.visualLine, Theme.visualPie, Theme.visualSlicer,
                                Theme.white, Theme.black
                            ]
                            delegate: Rectangle {
                                required property color modelData
                                width: 22
                                height: 22
                                radius: Geometry.radiusXs
                                color: modelData
                                border.width: visualValue.text === modelData ? 2 : Geometry.borderWidth
                                border.color: visualValue.text === modelData ? Theme.white : Theme.borderColor
                                scale: paletteMouse.containsMouse ? Motion.hoverScale : 1.0
                                Behavior on scale { NumberAnimation { duration: Motion.quick } }
                                MouseArea {
                                    id: paletteMouse
                                    anchors.fill: parent
                                    hoverEnabled: true
                                    onClicked: visualValue.text = modelData
                                }
                            }
                        }
                    }
                    CheckBox {
                        id: visualBoolean
                        visible: controlKind === "boolean"
                        checked: controlDefaultValue === "True" || controlDefaultValue === "true"
                        text: "Enabled"
                        contentItem: Text {
                            text: visualBoolean.text
                            color: Theme.textColor
                            font.family: Typography.uiFamily
                            font.pixelSize: Typography.bodySize
                            leftPadding: visualBoolean.indicator.width + Spacing.sm
                            verticalAlignment: Text.AlignVCenter
                        }
                        indicator: Rectangle {
                            implicitWidth: 20
                            implicitHeight: 20
                            radius: Geometry.radiusXs
                            color: visualBoolean.checked ? controlCard.accent : Theme.inputBackground
                            border.width: Geometry.borderWidth
                            border.color: visualBoolean.checked ? controlCard.accent : Theme.borderColor
                            Text {
                                anchors.centerIn: parent
                                text: visualBoolean.checked ? "✓" : ""
                                color: Theme.contrastText(parent.color)
                                font.family: Typography.uiFamily
                                font.weight: Font.DemiBold
                            }
                            Behavior on color { ColorAnimation { duration: Motion.quick } }
                        }
                    }
                    Slider {
                        id: visualSlider
                        visible: controlKind === "slider" || controlValueType === "percentage"
                        Layout.fillWidth: true
                        from: 0
                        to: 100
                        value: Number(controlDefaultValue) || 0
                        background: Rectangle {
                            x: visualSlider.leftPadding
                            y: visualSlider.topPadding + visualSlider.availableHeight / 2 - height / 2
                            width: visualSlider.availableWidth
                            height: 5
                            radius: height / 2
                            color: Theme.inputBackground
                            Rectangle {
                                width: visualSlider.visualPosition * parent.width
                                height: parent.height
                                radius: parent.radius
                                color: controlCard.accent
                            }
                        }
                        handle: Rectangle {
                            x: visualSlider.leftPadding + visualSlider.visualPosition * (visualSlider.availableWidth - width)
                            y: visualSlider.topPadding + visualSlider.availableHeight / 2 - height / 2
                            width: 16
                            height: 16
                            radius: width / 2
                            color: controlCard.accent
                            border.width: Geometry.borderWidth
                            border.color: Theme.white
                        }
                    }
                    Text {
                        visible: controlKind === "slider" || controlValueType === "percentage"
                        text: Math.round(visualSlider.value)
                        color: controlCard.accent
                        font.family: Typography.dataFamily
                        font.pixelSize: Typography.captionSize
                        Layout.preferredWidth: 40
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Spacing.xs
                    Text {
                        Layout.fillWidth: true
                        text: controlMatches.length + " existing values"
                        color: Theme.dimText
                        font.family: Typography.uiFamily
                        font.pixelSize: Typography.microSize
                        elide: Text.ElideRight
                    }
                }

                ListView {
                    visible: matchesOpen
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    clip: true
                    model: controlMatches
                    ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
                    delegate: Text {
                        required property var modelData
                        width: visualControlList.width - Spacing.xl
                        text: "• " + modelData.text
                        color: Theme.mutedText
                        font.family: Typography.dataFamily
                        font.pixelSize: Typography.microSize
                        elide: Text.ElideMiddle
                    }
                }
            }
        }
    }

    MutedLabel {
        visible: app.controller.visualEditorControlCount === 0
        Layout.fillWidth: true
        text: "No controls are available for the current visual selection."
    }
}
