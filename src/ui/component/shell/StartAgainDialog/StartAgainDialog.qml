import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "StartAgainDialogLogic.js" as Logic

    Popup {
    StartAgainDialogStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
        required property var app
        id: dialog
        modal: true
        focus: true
        width: Math.min(app.width - 80, style.preferredWidth)
        height: 170
        anchors.centerIn: parent
        background: Rectangle { color: app.panelBackground; border.color: app.borderColor; radius: 4 }
        ColumnLayout { anchors.fill: parent; anchors.margins: 16; spacing: 12
            PanelTitle { text: "START AGAIN" }
            MutedLabel { Layout.fillWidth: true; text: "Unsaved changes will remain only in memory until this session is cleared." }
            Item { Layout.fillHeight: true }
            RowLayout { Layout.fillWidth: true; spacing: 10
                Item { Layout.fillWidth: true }
                ChromeButton { text: "Cancel"; normalColor: "#3c3c3c"; hoverColor: "#4a4a4a"; onClicked: dialog.close() }
                ChromeButton { text: "Clear"; normalColor: app.accentRed; hoverColor: "#d65252"; onClicked: { dialog.close(); app.callController(function(c) { c.startAgain() }) } }
            }
        }
    }
