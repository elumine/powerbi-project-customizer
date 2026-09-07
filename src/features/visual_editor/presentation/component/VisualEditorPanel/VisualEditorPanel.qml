import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "VisualEditorPanelLogic.js" as Logic

ColumnLayout {
    VisualEditorPanelStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    required property var app
    spacing: style.panelSpacing
                            RowLayout {
                                Layout.fillWidth: true
                                PanelTitle { text: "VISUALS EDITOR"; Layout.fillWidth: true }
                                Text { text: app.controller.activeVisualCount + " active"; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                            }
                            DarkCombo { id: categoryCombo; Layout.fillWidth: true; model: app.controller.visualEditorCategoryOptions; currentIndex: Logic.optionIndex(app.controller.visualEditorCategoryOptions, app.controller.visualEditorCategory); onActivated: { var option = app.controller.visualEditorCategoryOptions[index]; if (categoryCombo.optionEnabled(option)) app.callController(function(c) { c.setVisualEditorCategory(categoryCombo.optionValue(option)) }) } }
                            MutedLabel { Layout.fillWidth: true; text: app.controller.visualEditorStatus }
                            ListView { id: visualControlList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 6; model: app.controller.visualEditorControlModel
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                                section.property: "groupLabel"
                                section.criteria: ViewSection.FullString
                                section.delegate: Rectangle { width: visualControlList.width; height: section.length > 0 ? 24 : 0; color: app.panelBackground; Text { anchors.fill: parent; anchors.leftMargin: 8; text: section; color: app.mutedText; font.family: "Consolas"; font.pixelSize: 10; font.bold: true; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight } }
                                delegate: Rectangle {
                                    id: visualControlRow
                                    width: visualControlList.width
                                    height: matchesOpen ? 196 : 126
                                    color: app.editorBackground
                                    border.color: app.borderColor
                                    radius: 3
                                    property bool matchesOpen: false
                                    property var propertyMatches: model.matches || []
                                    property var propertyGroupPath: model.groupPath || []
                                    function inputValue() {
                                        if (control === "boolean") return visualBoolean.checked
                                        if (control === "slider" || valueType === "percentage") return Math.round(visualSlider.value)
                                        return visualValue.text
                                    }
                                    ColumnLayout { anchors.fill: parent; anchors.topMargin: 7; anchors.rightMargin: 7; anchors.bottomMargin: 7; anchors.leftMargin: 7 + (visualControlRow.propertyGroupPath.length > 0 ? 10 : 0); spacing: 4
                                        RowLayout { Layout.fillWidth: true; spacing: 8
                                            ColumnLayout { Layout.fillWidth: true; spacing: 2
                                                Text { Layout.fillWidth: true; text: label; color: app.textColor; font.family: "Segoe UI"; font.pixelSize: 12; font.bold: true; elide: Text.ElideRight }
                                                Text { Layout.fillWidth: true; text: (propertyGroupPath.length > 0 ? propertyGroupPath.join(" > ") + " - " : "") + (visualTypeGroup.length > 0 ? visualTypeGroup + " - " : "") + valueType + (matchingCount > 0 ? " - " + matchingCount + " matching" : ""); color: app.mutedText; font.family: "Consolas"; font.pixelSize: 10; elide: Text.ElideRight }
                                                Text { visible: description.length > 0; Layout.fillWidth: true; text: description; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideRight }
                                            }
                                            ChromeButton { text: "Apply"; enabled: app.controller.activeVisualCount > 0; onClicked: app.callController(function(c) { c.applyVisualEditorChange(model.id, visualControlRow.inputValue()) }) }
                                        }
                                        RowLayout { Layout.fillWidth: true; spacing: 8
                                            Rectangle { visible: control === "color"; Layout.preferredWidth: 24; Layout.preferredHeight: 24; radius: 2; color: visualValue.text.length > 0 ? visualValue.text : defaultValue; border.color: app.borderColor }
                                            Field { id: visualValue; visible: control !== "boolean" && control !== "slider" && valueType !== "percentage"; Layout.fillWidth: true; text: defaultValue; placeholderText: control === "color" ? "#3B82F6" : "Value" }
                                            CheckBox { id: visualBoolean; visible: control === "boolean"; checked: defaultValue === "True" || defaultValue === "true"; text: "" }
                                            Slider { id: visualSlider; visible: control === "slider" || valueType === "percentage"; Layout.fillWidth: true; from: 0; to: 100; value: Number(defaultValue) || 0 }
                                            Text { visible: control === "slider" || valueType === "percentage"; text: Math.round(visualSlider.value); color: app.mutedText; font.family: "Consolas"; font.pixelSize: 11; Layout.preferredWidth: 36 }
                                        }
                                        RowLayout { Layout.fillWidth: true; spacing: 6
                                            ChromeButton { text: visualControlRow.matchesOpen ? "Hide matches" : "Matches"; normalColor: "#3c3c3c"; hoverColor: "#4a4a4a"; enabled: visualControlRow.propertyMatches.length > 0; onClicked: visualControlRow.matchesOpen = !visualControlRow.matchesOpen }
                                            Text { Layout.fillWidth: true; text: visualControlRow.propertyMatches.length + " existing"; color: app.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideRight }
                                        }
                                        ListView { visible: visualControlRow.matchesOpen; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; model: visualControlRow.propertyMatches
                                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOn }
                                            delegate: Text { width: visualControlList.width - 20; text: "- " + modelData.text; color: app.mutedText; font.family: "Consolas"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                        }
                                    }
                                }
                            }
                            MutedLabel { visible: app.controller.visualEditorControlCount === 0; Layout.fillWidth: true; text: "No controls for the active visual scope." }
                        }
