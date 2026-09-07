import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "FilterEditorDialogLogic.js" as Logic

Item {
    FilterEditorDialogStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    id: dialog
    anchors.fill: parent
    required property var app
    Rectangle { anchors.fill: parent; visible: app.controller.filterEditorVisible; color: style.scrim; z: 30
        MouseArea { anchors.fill: parent }
        Rectangle { width: Math.min(parent.width - 80, 860); height: Math.min(parent.height - 80, 660); anchors.centerIn: parent; color: app.panelBackground; border.color: app.borderColor; radius: 4
            ColumnLayout { anchors.fill: parent; anchors.margins: 16; spacing: 12
                RowLayout {
                    Layout.fillWidth: true
                    PanelTitle { text: "FILTER EDITOR"; Layout.fillWidth: true }
                    IconButton { text: "x"; contentColor: app.accentRed; onClicked: app.callController(function(c) { c.cancelFilterEditor() }) }
                }
                RowLayout { Layout.fillWidth: true; spacing: 10
                    Field { Layout.fillWidth: true; placeholderText: "Filter name"; text: app.controller.editingFilterName; onTextEdited: app.callController(function(c) { c.editingFilterName = text }) }
                    DarkCombo { Layout.preferredWidth: 130; model: app.filterTargetOptions; currentIndex: Math.max(0, app.filterTargetOptions.indexOf(app.controller.editingFilterTarget)); onActivated: app.callController(function(c) { c.editingFilterTarget = currentText }) }
                    Rectangle { Layout.preferredWidth: 32; Layout.preferredHeight: 32; radius: 3; color: app.controller.editingFilterColor.length > 0 ? app.controller.editingFilterColor : app.accentBlue; border.color: app.borderColor }
                    Text { text: app.controller.editingFilterColor; color: app.mutedText; font.family: "Consolas"; font.pixelSize: 12; Layout.preferredWidth: 76; elide: Text.ElideRight }
                    IconButton { text: "R"; ToolTip.visible: hovered; ToolTip.text: "Random color"; onClicked: app.callController(function(c) { c.randomizeEditingFilterColor() }) }
                }
                RowLayout {
                    Layout.fillWidth: true
                    PanelTitle { text: "RULES"; Layout.fillWidth: true }
                    Text { text: app.controller.editingRuleCount + " rule(s)"; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                }
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: app.editorBackground; border.color: app.borderColor; radius: 3
                    ListView { id: ruleList; anchors.fill: parent; anchors.margins: 8; clip: true; spacing: 6; model: app.controller.editingRuleModel
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                        delegate: Rectangle { width: ruleList.width; height: 42; color: ruleMouse.containsMouse ? app.listHover : "transparent"; radius: 2
                            MouseArea { id: ruleMouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }
                            RowLayout { anchors.fill: parent; anchors.leftMargin: 4; anchors.rightMargin: 4; spacing: 8
                                Field { Layout.preferredWidth: 160; placeholderText: "Key"; text: key; onTextEdited: app.callController(function(c) { c.updateEditingRuleKey(index, text) }) }
                                DarkCombo { Layout.preferredWidth: 145; model: app.filterOperationOptions; currentIndex: Math.max(0, app.filterOperationOptions.indexOf(operation)); onActivated: app.callController(function(c) { c.updateEditingRuleOperation(index, currentText) }) }
                                Field { Layout.fillWidth: true; placeholderText: "Value"; text: value; onTextEdited: app.callController(function(c) { c.updateEditingRuleValue(index, text) }) }
                                IconButton { text: "x"; contentColor: app.accentRed; ToolTip.visible: hovered; ToolTip.text: "Remove rule"; onClicked: app.callController(function(c) { c.removeEditingRule(index) }) }
                            }
                        }
                    }
                }
                RowLayout { Layout.fillWidth: true; spacing: 10
                    ChromeButton { text: "Add rule"; onClicked: app.callController(function(c) { c.addEditingRule() }) }
                    MutedLabel { Layout.fillWidth: true; text: app.controller.statusMessage; elide: Text.ElideRight }
                    ChromeButton { text: "Cancel"; normalColor: "#3c3c3c"; hoverColor: "#4a4a4a"; onClicked: app.callController(function(c) { c.cancelFilterEditor() }) }
                    ChromeButton { text: "Save"; normalColor: app.accentGreen; hoverColor: app.accentGreenHover; pressedColor: "#126a4d"; enabled: app.controller.editingFilterCanSave; onClicked: app.callController(function(c) { c.saveFilterEditor() }) }
                }
            }
        }
    }
}
