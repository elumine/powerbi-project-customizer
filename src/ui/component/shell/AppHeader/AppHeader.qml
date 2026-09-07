import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "AppHeaderLogic.js" as Logic

Rectangle {
    AppHeaderStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    required property var app
    signal startAgainRequested()
    height: style.height
        color: app.headerBackground
        border.color: app.borderColor
        RowLayout { anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 10
            Text { text: "Power BI PBIR Editor"; color: app.textColor; font.family: "Segoe UI"; font.pixelSize: 13; font.bold: true; Layout.fillWidth: true; elide: Text.ElideRight }
            Text { text: app.controller.hasActiveFilter ? app.controller.activeFilterName + " (" + app.controller.activeFilterTarget + ")" : ""; color: app.controller.activeFilterColor.length > 0 ? app.controller.activeFilterColor : app.mutedText; font.family: "Segoe UI"; font.pixelSize: 12; visible: app.controller.hasActiveFilter }
            Text { text: app.controller.hasDirtyFiles ? "Unsaved changes" : "All saved"; color: app.controller.hasDirtyFiles ? app.warningColor : app.mutedText; font.family: "Segoe UI"; font.pixelSize: 12 }
            ChromeButton { text: app.controller.anyMacroRunning ? "Stop macro" : app.controller.macroRecording ? "Stop recording" : "Start recording"; normalColor: app.controller.anyMacroRunning || app.controller.macroRecording ? app.accentRed : app.accentGreen; hoverColor: app.controller.anyMacroRunning || app.controller.macroRecording ? "#d65252" : app.accentGreenHover; enabled: true; onClicked: app.controller.anyMacroRunning ? app.callController(function(c) { c.stopMacro() }) : app.controller.macroRecording ? app.callController(function(c) { c.stopMacroRecording() }) : app.callController(function(c) { c.startMacroRecording() }) }
            ChromeButton { text: "Start Again"; normalColor: "#3c3c3c"; hoverColor: "#4a4a4a"; onClicked: app.controller.hasDirtyFiles ? startAgainRequested() : app.callController(function(c) { c.startAgain() }) }
        }
    }
