import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "FilterPanelLogic.js" as Logic

ColumnLayout {
    id: panel
    FilterPanelStyle { id: style }

    required property var app
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    spacing: style.panelSpacing

    RowLayout {
        Layout.fillWidth: true
        PanelTitle { text: "Rules & filters"; Layout.fillWidth: true }
        IconButton {
            text: "+"
            tooltipText: "New filter"
            contentColor: Theme.accentBlue
            onClicked: app.callController(function(controller) { controller.openNewFilterEditor() })
        }
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: Spacing.xs
        ChromeButton {
            Layout.fillWidth: true
            text: "Import"
            actionType: "save"
            onClicked: app.callController(function(controller) { controller.importFilter() })
        }
        ChromeButton {
            Layout.fillWidth: true
            text: "Clear filters"
            actionType: "cancel"
            enabled: app.controller.hasActiveFilter
            onClicked: app.callController(function(controller) { controller.deactivateFilter() })
        }
    }

    PanelTitle { text: "Quick filters" }

    Rectangle {
        Layout.fillWidth: true
        radius: Geometry.radiusMd
        color: Theme.controlBackground
        border.width: Geometry.borderWidth
        border.color: Theme.borderSubtle
        implicitHeight: quickFilters.implicitHeight + Spacing.md * 2

        ColumnLayout {
            id: quickFilters
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: Spacing.sm
            spacing: Spacing.xs

            RowLayout {
                Layout.fillWidth: true
                Field {
                    id: visualNameFilterField
                    Layout.fillWidth: true
                    placeholderText: "Filter by visual name"
                    onAccepted: app.callController(function(controller) { controller.applyDynamicVisualNameFilter(text) })
                }
                ChromeButton {
                    text: "Apply"
                    actionType: "execute"
                    onClicked: app.callController(function(controller) { controller.applyDynamicVisualNameFilter(visualNameFilterField.text) })
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Field {
                    id: visualTypeFilterField
                    Layout.fillWidth: true
                    placeholderText: "Filter by visual type"
                    onAccepted: app.callController(function(controller) { controller.applyDynamicVisualTypeFilter(text) })
                }
                ChromeButton {
                    text: "Apply"
                    actionType: "execute"
                    onClicked: app.callController(function(controller) { controller.applyDynamicVisualTypeFilter(visualTypeFilterField.text) })
                }
            }

            RowLayout {
                Layout.fillWidth: true
                Field {
                    id: pageNameFilterField
                    Layout.fillWidth: true
                    placeholderText: "Filter by page name"
                    onAccepted: app.callController(function(controller) { controller.applyDynamicPageNameFilter(text) })
                }
                ChromeButton {
                    text: "Apply"
                    actionType: "execute"
                    onClicked: app.callController(function(controller) { controller.applyDynamicPageNameFilter(pageNameFilterField.text) })
                }
            }
        }
    }

    ListView {
        id: filterList
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true
        spacing: Spacing.sm
        model: app.controller.filterModel
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }

        add: Transition {
            NumberAnimation { properties: "opacity"; from: 0; to: 1; duration: Motion.relaxed }
            NumberAnimation { properties: "y"; from: Spacing.sm; duration: Motion.relaxed; easing.type: Easing.OutCubic }
        }
        remove: Transition { NumberAnimation { properties: "opacity"; to: 0; duration: Motion.quick } }
        displaced: Transition { NumberAnimation { properties: "y"; duration: Motion.standard; easing.type: Easing.OutCubic } }

        delegate: Rectangle {
            id: filterCard
            required property string filterId
            required property string displayName
            required property color filterColor
            property color filterHue: Theme.safeColor(filterColor, Theme.filterSky)
            required property string ruleSummary
            required property bool active
            required property bool readOnly
            required property string targetJsonFileType
            required property int index

            width: filterList.width
            height: 106
            radius: Geometry.radiusMd
            color: active ? Qt.lighter(filterHue, 1.05) : filterMouse.containsMouse ? style.cardHover : style.cardBackground
            border.width: active ? 2 : Geometry.borderWidth
            border.color: active ? filterHue : Theme.borderSubtle
            scale: filterMouse.containsMouse ? Motion.hoverScale : 1.0

            Behavior on color { ColorAnimation { duration: Motion.standard; easing.type: Easing.OutCubic } }
            Behavior on scale { NumberAnimation { duration: Motion.quick; easing.type: Easing.OutCubic } }

            MouseArea { id: filterMouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }

            RowLayout {
                anchors.fill: parent
                anchors.margins: Geometry.cardPadding
                spacing: Spacing.sm

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: Spacing.xxs
                    RowLayout {
                        Layout.fillWidth: true
                        Text {
                            Layout.fillWidth: true
                            text: displayName
                            color: active ? Theme.contrastText(filterHue) : Theme.textColor
                            font.family: Typography.uiFamily
                            font.pixelSize: Typography.labelSize
                            font.weight: Font.DemiBold
                            elide: Text.ElideRight
                        }
                        DiffChip {
                            value: targetJsonFileType
                            chipColor: filterHue
                            chipTextColor: Theme.contrastText(filterHue)
                            active: active
                        }
                    }
                    Text {
                        Layout.fillWidth: true
                        text: ruleSummary
                        color: active ? Theme.contrastText(filterHue) : Theme.mutedText
                        font.family: Typography.dataFamily
                        font.pixelSize: Typography.microSize
                        elide: Text.ElideRight
                    }
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Spacing.xs
                        ChromeButton {
                            text: active ? "Applied" : "Apply"
                            enabled: !active
                            actionType: "execute"
                            onClicked: app.callController(function(controller) { controller.applyFilter(index) })
                        }
                        IconButton {
                            text: "⇩"
                            tooltipText: "Export filter"
                            onClicked: app.callController(function(controller) { controller.exportFilter(index) })
                        }
                        IconButton {
                            text: "✎"
                            tooltipText: "Edit filter"
                            enabled: !readOnly
                            onClicked: app.callController(function(controller) { controller.openEditFilterEditor(index) })
                        }
                        IconButton {
                            text: "×"
                            tooltipText: "Delete filter"
                            enabled: !readOnly
                            contentColor: Theme.accentRed
                            onClicked: app.callController(function(controller) { controller.deleteFilter(index) })
                        }
                        Item { Layout.fillWidth: true }
                    }
                }
            }
        }
    }

    MutedLabel {
        visible: app.controller.filterCount === 0
        Layout.fillWidth: true
        text: "No filters yet. Create one to focus a visual or page subset."
    }
}
