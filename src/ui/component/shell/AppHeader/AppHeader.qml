import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "AppHeaderLogic.js" as Logic

Rectangle {
    id: header
    AppHeaderStyle { id: style }

    required property var app
    signal startAgainRequested()
    readonly property bool componentReady: Logic.isReady(app)
    readonly property string recordingLabel: Logic.recordingAction(app.controller.anyMacroRunning, app.controller.macroRecording)
    enabled: style.enabled && componentReady
    height: style.height
    color: style.background
    border.width: Geometry.borderWidth
    border.color: style.border

    Behavior on color { ColorAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: Spacing.lg
        anchors.rightMargin: Spacing.lg
        spacing: Spacing.lg

        ColumnLayout {
            Layout.preferredWidth: 210
            Layout.alignment: Qt.AlignVCenter
            spacing: Spacing.xxs
            Text {
                text: "PBIR Control Room"
                color: app.textColor
                font.family: Typography.uiFamily
                font.pixelSize: Typography.sectionSize
                font.weight: Font.DemiBold
            }
            Text {
                text: "JSON workspace"
                color: app.dimText
                font.family: Typography.uiFamily
                font.pixelSize: Typography.microSize
            }
        }

        RowLayout {
            visible: app.controller.fileCount > 0
            Layout.fillWidth: true
            spacing: Spacing.md
            Repeater {
                model: [
                    { "label": "Workspace", "panel": "explorer" },
                    { "label": "Search", "panel": "search" },
                    { "label": "Rules", "panel": "filters" },
                    { "label": "Automations", "panel": "macros" }
                ]
                delegate: Item {
                    required property var modelData
                    readonly property bool active: app.pageName === "management" && app.activePanel === modelData.panel
                    implicitWidth: tabLabel.implicitWidth + Spacing.sm
                    implicitHeight: header.height
                    property bool hovered: tabMouse.containsMouse
                    Rectangle {
                        anchors.fill: parent
                        anchors.topMargin: Spacing.xs
                        anchors.bottomMargin: Spacing.xs
                        radius: Geometry.radiusSm
                        color: active ? Theme.controlBackground : hovered ? Theme.cardHover : "transparent"
                        Behavior on color { ColorAnimation { duration: Motion.quick } }
                    }
                    Text {
                        id: tabLabel
                        anchors.centerIn: parent
                        text: modelData.label
                        color: Theme.white
                        opacity: active ? 1.0 : 0.82
                        font.family: Typography.uiFamily
                        font.pixelSize: Typography.captionSize
                        font.weight: active ? Font.DemiBold : Font.Medium
                        Behavior on color { ColorAnimation { duration: Motion.quick } }
                    }
                    Rectangle {
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: parent.bottom
                        width: parent.width
                        height: 2
                        radius: 1
                        color: Theme.accentRed
                        opacity: active ? 1.0 : hovered ? 0.45 : 0.0
                        Behavior on opacity { NumberAnimation { duration: Motion.quick } }
                    }
                    MouseArea {
                        id: tabMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            app.pageName = "management"
                            app.activePanel = modelData.panel
                        }
                    }
                }
            }
        }

        Rectangle {
            visible: app.controller.hasActiveFilter
            Layout.maximumWidth: 220
            Layout.preferredWidth: Math.min(220, filterChipLabel.implicitWidth + Spacing.lg)
            Layout.preferredHeight: Geometry.controlHeight - Spacing.xs
            radius: Geometry.radiusSm
            color: Theme.safeColor(app.controller.activeFilterColor, Theme.filterSky)
            border.width: Geometry.borderWidth
            border.color: Qt.lighter(color, 1.12)
            scale: filterChipMouse.containsMouse ? Motion.hoverScale : 1.0
            Behavior on color { ColorAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }
            Behavior on scale { NumberAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }
            Text {
                id: filterChipLabel
                anchors.fill: parent
                anchors.leftMargin: Spacing.sm
                anchors.rightMargin: Spacing.sm
                text: app.controller.activeFilterName + " · " + app.controller.activeFilterTarget
                color: Theme.contrastText(parent.color)
                font.family: Typography.uiFamily
                font.pixelSize: Typography.captionSize
                font.weight: Font.DemiBold
                verticalAlignment: Text.AlignVCenter
                elide: Text.ElideRight
            }
            MouseArea { id: filterChipMouse; anchors.fill: parent; hoverEnabled: true }
        }

        Rectangle {
            Layout.preferredWidth: 108
            Layout.preferredHeight: Geometry.controlHeight - Spacing.xs
            radius: Geometry.radiusSm
            color: app.cardBackground
            border.width: Geometry.borderWidth
            border.color: app.borderSubtle
            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: Spacing.sm
                anchors.rightMargin: Spacing.sm
                spacing: Spacing.xs
                Rectangle {
                    Layout.preferredWidth: 7
                    Layout.preferredHeight: 7
                    radius: width / 2
                    color: app.controller.hasDirtyFiles ? app.warningColor : app.okColor
                    scale: app.controller.hasDirtyFiles ? 1.0 : 0.82
                    Behavior on color { ColorAnimation { duration: Motion.standard } }
                    Behavior on scale { NumberAnimation { duration: Motion.standard; easing.type: Easing.InOutSine } }
                }
                Text {
                    Layout.fillWidth: true
                    text: app.controller.hasDirtyFiles ? "Unsaved" : "Synced"
                    color: app.mutedText
                    font.family: Typography.uiFamily
                    font.pixelSize: Typography.captionSize
                    elide: Text.ElideRight
                }
            }
        }

        Button {
            id: recordingButton
            readonly property bool recording: app.controller.anyMacroRunning || app.controller.macroRecording
            implicitWidth: recording ? Geometry.controlHeight : 132
            implicitHeight: Geometry.controlHeight
            padding: 0
            scale: down ? Motion.pressScale : hovered ? Motion.hoverScale : 1.0
            Behavior on implicitWidth { NumberAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }
            Behavior on scale { NumberAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }
            ToolTip.visible: hovered
            ToolTip.delay: Motion.standard
            ToolTip.text: recording ? "Stop recording" : "Start recording"
            background: Rectangle {
                radius: height / 2
                color: Theme.accentRed
                border.width: Geometry.borderWidth
                border.color: Theme.accentRedHover
                Behavior on color { ColorAnimation { duration: Motion.quick } }
            }
            contentItem: RowLayout {
                anchors.fill: parent
                anchors.leftMargin: recordingButton.recording ? Spacing.sm : Spacing.md
                anchors.rightMargin: recordingButton.recording ? Spacing.sm : Spacing.md
                spacing: Spacing.sm
                Rectangle {
                    Layout.preferredWidth: 14
                    Layout.preferredHeight: 14
                    radius: recordingButton.recording ? Geometry.radiusXs : width / 2
                    color: Theme.white
                    Behavior on radius { NumberAnimation { duration: Motion.quick } }
                }
                Text {
                    visible: !recordingButton.recording
                    Layout.fillWidth: true
                    text: header.recordingLabel
                    color: Theme.white
                    font.family: Typography.uiFamily
                    font.pixelSize: Typography.captionSize
                    font.weight: Font.DemiBold
                    verticalAlignment: Text.AlignVCenter
                }
            }
            onClicked: app.controller.anyMacroRunning
                ? app.callController(function(c) { c.stopMacro() })
                : app.controller.macroRecording
                    ? app.callController(function(c) { c.stopMacroRecording() })
                    : app.callController(function(c) { c.startMacroRecording() })
        }

        IconButton {
            text: "↺"
            tooltipText: "Start again"
            implicitWidth: Geometry.controlHeight + Spacing.sm
            implicitHeight: Geometry.controlHeight + Spacing.sm
            contentColor: Theme.white
            onClicked: app.controller.hasDirtyFiles ? startAgainRequested() : app.callController(function(c) { c.startAgain() })
        }
    }
}
