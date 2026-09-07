import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.component.shell 1.0
import "WorkspacePageLogic.js" as Logic
import ui.styles 1.0
import features.file_management.presentation 1.0
import features.search_replace.presentation 1.0
import features.filters.presentation 1.0
import features.suggestions.presentation 1.0
import features.visual_editor.presentation 1.0
import features.history.presentation 1.0
import features.macros.presentation 1.0
import features.editor.presentation 1.0

Item {
    WorkspacePageStyle { id: style }
    readonly property bool componentReady: Logic.isReady(app)
    enabled: style.enabled && componentReady
    id: page
    required property var app

    function openFind() {
        jsonEditor.openFind()
    }

            RowLayout { anchors.fill: parent; spacing: 0
                PanelsSidebar { app: page.app }

                Rectangle { Layout.preferredWidth: Math.max(420, Math.min(680, app.width * 0.50)); Layout.fillHeight: true; color: app.panelBackground; border.color: app.borderColor
                    StackLayout { anchors.fill: parent; anchors.margins: 10; currentIndex: Logic.panelIndex(app.activePanel)
                        ProjectExplorerPanel { app: page.app }

                        SearchPanel { app: page.app }

                        FilterPanel { app: page.app }

                        SuggestionsPanel { app: page.app }

                        VisualEditorPanel { app: page.app }


                        HistoryPanel { app: page.app }
                        MacrosPanel { app: page.app }
                    }
                }

                JsonEditor { id: jsonEditor; app: page.app }
            }
        
}
