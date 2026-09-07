import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.component.shell 1.0
import ui.pages 1.0
import features.folder_import.presentation 1.0
import features.filters.presentation 1.0
import ui.styles 1.0
import "AppLogic.js" as Logic

ApplicationWindow {
    id: root
    AppStyle { id: style }
    width: style.initialWidth
    height: style.initialHeight
    minimumWidth: style.minimumWidth
    minimumHeight: style.minimumHeight
    visible: true
    color: style.background
    title: "Power BI PBIR Editor"

    required property var shellAdapter
    required property var editorAdapter
    property var controller: shellAdapter
    property string pageName: "picker"
    property string activePanel: "explorer"
    readonly property var filterOperationOptions: ["equals", "includes", "notEquals", "notIncludes"]
    readonly property var filterTargetOptions: ["All", "Page", "Visual"]
    readonly property var visualEditorCategories: ["General", "Specific"]

    readonly property color activityBackground: Theme.activityBackground
    readonly property color panelBackground: Theme.panelBackground
    readonly property color editorBackground: Theme.editorBackground
    readonly property color headerBackground: Theme.headerBackground
    readonly property color statusBackground: Theme.statusBackground
    readonly property color borderColor: Theme.borderColor
    readonly property color listHover: Theme.listHover
    readonly property color listActive: Theme.listActive
    readonly property color textColor: Theme.textColor
    readonly property color mutedText: Theme.mutedText
    readonly property color accentBlue: Theme.accentBlue
    readonly property color accentBlueHover: Theme.accentBlueHover
    readonly property color accentGreen: Theme.accentGreen
    readonly property color accentGreenHover: Theme.accentGreenHover
    readonly property color accentRed: Theme.accentRed
    readonly property color inputBackground: Theme.inputBackground
    readonly property color warningColor: Theme.warningColor
    readonly property color okColor: Theme.okColor



    function callController(action) { if (root.controller) action(root.controller) }
    Connections {
        target: root.controller
        function onPanelRequested(panelName) { root.activePanel = panelName }
        function onSessionResetRequested() { root.pageName = "picker"; root.activePanel = "explorer" }
    }

    Shortcut { sequences: [StandardKey.Save]; onActivated: root.callController(function(c) { c.saveFile(root.controller.currentIndex) }) }
    Shortcut { sequence: "Ctrl+Shift+S"; onActivated: root.callController(function(c) { c.saveAll() }) }
    Shortcut { sequences: [StandardKey.Find]; onActivated: workspacePage.openFind() }



    header: AppHeader { app: root; onStartAgainRequested: startAgainDialog.open() }

    StackLayout {
        anchors.fill: parent
        currentIndex: Logic.workspaceIndex(root.pageName)

        FilePickerPage {
            Layout.fillWidth: true
            Layout.fillHeight: true
            app: root
        }

        WorkspacePage {
            id: workspacePage
            Layout.fillWidth: true
            Layout.fillHeight: true
            app: root
        }
    }

    FolderImportDialog { anchors.fill: parent; app: root }

    FilterEditorDialog { anchors.fill: parent; app: root }

    StartAgainDialog { id: startAgainDialog; app: root }
}
