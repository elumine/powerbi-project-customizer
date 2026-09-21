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
    property string editorView: "text"
    readonly property var filterOperationOptions: ["equals", "includes", "notEquals", "notIncludes"]
    readonly property var filterTargetOptions: ["All", "Page", "Visual"]
    readonly property var visualEditorCategories: ["General", "Specific"]

    readonly property color appBackground: Theme.appBackground
    readonly property color activityBackground: Theme.activityBackground
    readonly property color panelBackground: Theme.panelBackground
    readonly property color editorBackground: Theme.editorBackground
    readonly property color headerBackground: Theme.headerBackground
    readonly property color statusBackground: Theme.statusBackground
    readonly property color cardBackground: Theme.cardBackground
    readonly property color cardRaised: Theme.cardRaised
    readonly property color cardHover: Theme.cardHover
    readonly property color controlBackground: Theme.controlBackground
    readonly property color controlHover: Theme.controlHover
    readonly property color borderColor: Theme.borderColor
    readonly property color borderSubtle: Theme.borderSubtle
    readonly property color listHover: Theme.listHover
    readonly property color listActive: Theme.listActive
    readonly property color textColor: Theme.textColor
    readonly property color mutedText: Theme.mutedText
    readonly property color dimText: Theme.dimText
    readonly property color accentBlue: Theme.accentBlue
    readonly property color accentBlueHover: Theme.accentBlueHover
    readonly property color accentGreen: Theme.accentGreen
    readonly property color accentGreenHover: Theme.accentGreenHover
    readonly property color accentRed: Theme.accentRed
    readonly property color accentRedHover: Theme.accentRedHover
    readonly property color inputBackground: Theme.inputBackground
    readonly property color inputFocus: Theme.inputFocus
    readonly property color warningColor: Theme.warningColor
    readonly property color okColor: Theme.okColor
    readonly property color selectionColor: Theme.selectionColor
    property bool dashboardReady: false
    opacity: dashboardReady ? 1.0 : 0.0

    Component.onCompleted: dashboardReady = true
    Behavior on opacity { NumberAnimation { duration: Motion.relaxed; easing.type: Easing.OutCubic } }

    function callController(action) { if (root.controller) action(root.controller) }
    Connections {
        target: root.controller
        function onPanelRequested(panelName) { root.activePanel = panelName }
        function onEditorViewRequested(viewName) { root.editorView = viewName }
        function onSessionResetRequested() { root.pageName = "picker"; root.activePanel = "explorer"; root.editorView = "text" }
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

    ImportedFilesChangedDialog { anchors.fill: parent; app: root }

    FilterEditorDialog { anchors.fill: parent; app: root }

    StartAgainDialog { id: startAgainDialog; app: root }
}
