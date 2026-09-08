import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.component.shell 1.0
import ui.styles 1.0
import "WorkspacePageLogic.js" as Logic
import features.file_management.presentation 1.0
import features.changes.presentation 1.0
import features.search_replace.presentation 1.0
import features.filters.presentation 1.0
import features.suggestions.presentation 1.0
import features.visual_editor.presentation 1.0
import features.history.presentation 1.0
import features.macros.presentation 1.0
import features.editor.presentation 1.0

Item {
    id: page
    WorkspacePageStyle { id: style }

    required property var app
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    opacity: componentReady ? 1.0 : 0.0

    function openFind() {
        jsonEditor.openFind()
    }

    Behavior on opacity { NumberAnimation { duration: Motion.relaxed; easing.type: Easing.OutCubic } }

    Rectangle {
        anchors.fill: parent
        color: style.background
    }

    RowLayout {
        id: workspaceLayout
        anchors.fill: parent
        anchors.margins: Spacing.md
        spacing: Spacing.md
        readonly property real contentWidth: Math.max(0, width - spacing * 2)
        readonly property real panelRatio: Logic.panelWidthRatio(app.activePanel)

        PanelsSidebar {
            app: page.app
            Layout.preferredWidth: Math.max(style.sidebarMinimumWidth, workspaceLayout.contentWidth * style.sidebarRatio)
        }

        Rectangle {
            Layout.preferredWidth: Math.max(style.panelMinimumWidth, workspaceLayout.contentWidth * workspaceLayout.panelRatio)
            Layout.fillHeight: true
            radius: Geometry.radiusMd
            color: style.panel
            border.width: Geometry.borderWidth
            border.color: Theme.borderSubtle
            clip: true

            StackLayout {
                anchors.fill: parent
                anchors.margins: Geometry.cardPadding
                currentIndex: Logic.panelIndex(app.activePanel)

                ProjectExplorerPanel { app: page.app }
                ChangesPanel { app: page.app }
                SearchPanel { app: page.app }
                FilterPanel { app: page.app }
                SuggestionsPanel { app: page.app }
                VisualEditorPanel { app: page.app }
                HistoryPanel { app: page.app }
                MacrosPanel { app: page.app }
            }
        }

        JsonEditor {
            id: jsonEditor
            Layout.fillWidth: true
            Layout.fillHeight: true
            app: page.app
        }
    }
}
