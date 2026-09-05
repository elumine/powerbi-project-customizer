import QtQuick
import QtQuick.Controls
import QtQml
import QtQuick.Layouts

ApplicationWindow {
    id: root
    width: 1220
    height: 780
    minimumWidth: 980
    minimumHeight: 640
    visible: true
    color: editorBackground
    title: "JSON Multi Editor"

    property var controller: appController
    property string pageName: "picker"
    property string activePanel: "explorer"
    property int pendingRevealFileIndex: -1
    property int pendingRevealLine: 0
    readonly property var filterOperationOptions: ["equals", "includes", "notEquals", "notIncludes"]

    readonly property color activityBackground: "#333333"
    readonly property color panelBackground: "#252526"
    readonly property color editorBackground: "#1e1e1e"
    readonly property color headerBackground: "#2d2d30"
    readonly property color statusBackground: "#007acc"
    readonly property color borderColor: "#3c3c3c"
    readonly property color listHover: "#2a2d2e"
    readonly property color listActive: "#37373d"
    readonly property color textColor: "#d4d4d4"
    readonly property color mutedText: "#858585"
    readonly property color accentBlue: "#0e639c"
    readonly property color accentBlueHover: "#1177bb"
    readonly property color accentGreen: "#16825d"
    readonly property color accentGreenHover: "#1f9d72"
    readonly property color accentRed: "#c44242"
    readonly property color inputBackground: "#1b1b1c"
    readonly property color warningColor: "#cca700"
    readonly property color okColor: "#3fb950"

    QtObject {
        id: appState
        property string searchText: root.controller ? root.controller.searchText : ""
        property string replaceText: root.controller ? root.controller.replaceText : ""
        property string statusMessage: root.controller ? root.controller.statusMessage : ""
        property string folderScanRoot: root.controller ? root.controller.folderScanRoot : ""
        property string activeFilterName: root.controller ? root.controller.activeFilterName : ""
        property string activeFilterColor: root.controller ? root.controller.activeFilterColor : ""
        property string editingFilterName: root.controller ? root.controller.editingFilterName : ""
        property string editingFilterColor: root.controller ? root.controller.editingFilterColor : ""
        property int fileCount: root.controller ? root.controller.fileCount : 0
        property int activeFileCount: root.controller ? root.controller.activeFileCount : 0
        property int currentIndex: root.controller ? root.controller.currentIndex : -1
        property int activeMatchFileIndex: root.controller ? root.controller.activeMatchFileIndex : -1
        property int activeMatchIndex: root.controller ? root.controller.activeMatchIndex : -1
        property int activeMatchLine: root.controller ? root.controller.activeMatchLine : 0
        property int activeMatchDisplayIndex: root.controller ? root.controller.activeMatchDisplayIndex : 0
        property int activeMatchFileCount: root.controller ? root.controller.activeMatchFileCount : 0
        property int totalMatches: root.controller ? root.controller.totalMatches : 0
        property int folderScanCount: root.controller ? root.controller.folderScanCount : 0
        property int filterCount: root.controller ? root.controller.filterCount : 0
        property int suggestionKeyCount: root.controller ? root.controller.suggestionKeyCount : 0
        property int suggestionValueCount: root.controller ? root.controller.suggestionValueCount : 0
        property int macroCount: root.controller ? root.controller.macroCount : 0
        property int editingRuleCount: root.controller ? root.controller.editingRuleCount : 0
        property bool hasDirtyFiles: root.controller ? root.controller.hasDirtyFiles : false
        property bool caseSensitive: root.controller ? root.controller.caseSensitive : false
        property bool folderImportVisible: root.controller ? root.controller.folderImportVisible : false
        property bool hasActiveFilter: root.controller ? root.controller.hasActiveFilter : false
        property bool filterEditorVisible: root.controller ? root.controller.filterEditorVisible : false
        property bool editingFilterCanSave: root.controller ? root.controller.editingFilterCanSave : false
        property var fileModel: root.controller ? root.controller.fileModel : null
        property var folderScanModel: root.controller ? root.controller.folderScanModel : null
        property var filterModel: root.controller ? root.controller.filterModel : null
        property var suggestionKeyModel: root.controller ? root.controller.suggestionKeyModel : null
        property var suggestionValueModel: root.controller ? root.controller.suggestionValueModel : null
        property var macroModel: root.controller ? root.controller.macroModel : null
        property var editingRuleModel: root.controller ? root.controller.editingRuleModel : null
        property bool anyMacroRunning: root.controller ? root.controller.anyMacroRunning : false
    }

    function callController(action) { if (root.controller) action(root.controller) }
    function panelIndex() {
        if (root.activePanel === "explorer") return 0
        if (root.activePanel === "search") return 1
        if (root.activePanel === "filters") return 2
        if (root.activePanel === "suggestions") return 3
        return 4
    }
    function revealMatch(fileIndex, line) {
        root.pageName = "management"
        root.pendingRevealFileIndex = fileIndex
        root.pendingRevealLine = line
        revealTimer.restart()
    }

    Timer {
        id: revealTimer
        interval: 40
        repeat: false
        onTriggered: if (root.pendingRevealFileIndex >= 0) editorList.positionViewAtIndex(root.pendingRevealFileIndex, ListView.Beginning)
    }

    Shortcut { sequences: [StandardKey.Save]; onActivated: root.callController(function(c) { c.saveFile(appState.currentIndex) }) }
    Shortcut { sequence: "Ctrl+Shift+S"; onActivated: root.callController(function(c) { c.saveAll() }) }

    Connections {
        target: root.controller
        function onPanelRequested(panelName) { root.activePanel = panelName }
    }

    component ChromeButton: Button {
        id: control
        property color normalColor: root.accentBlue
        property color hoverColor: root.accentBlueHover
        property color pressedColor: "#0b5688"
        property color disabledColor: "#3c3c3c"
        property color contentColor: "#ffffff"
        implicitHeight: 32
        padding: 8
        background: Rectangle { radius: 3; color: !control.enabled ? control.disabledColor : control.down ? control.pressedColor : control.hovered ? control.hoverColor : control.normalColor; border.color: Qt.darker(color, 1.15) }
        contentItem: Text { text: control.text; color: control.enabled ? control.contentColor : root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
    }

    component IconButton: Button {
        id: control
        property color contentColor: root.textColor
        implicitWidth: 30
        implicitHeight: 28
        padding: 0
        background: Rectangle { radius: 3; color: control.down ? root.listActive : control.hovered ? root.listHover : "transparent" }
        contentItem: Text { text: control.text; color: control.enabled ? control.contentColor : root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
    }

    component PanelButton: Button {
        id: control
        property bool active: false
        property string tooltipText: ""
        implicitWidth: 52
        implicitHeight: 52
        padding: 0
        ToolTip.visible: hovered
        ToolTip.delay: 450
        ToolTip.text: tooltipText
        background: Rectangle { color: control.active ? root.listActive : control.hovered ? "#3d3d3d" : "transparent"; border.width: control.active ? 3 : 0; border.color: root.statusBackground }
        contentItem: Text { text: control.text; color: control.active ? "#ffffff" : root.mutedText; font.family: "Segoe UI"; font.pixelSize: 17; font.bold: true; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter }
    }

    component PanelTitle: Text { color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 11; font.bold: true; elide: Text.ElideRight }
    component MutedLabel: Text { color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12; wrapMode: Text.WordWrap }

    component Field: TextField {
        id: control
        color: root.textColor
        placeholderTextColor: root.mutedText
        selectedTextColor: "#ffffff"
        selectionColor: "#264f78"
        font.family: "Segoe UI"
        font.pixelSize: 12
        leftPadding: 8
        rightPadding: 8
        background: Rectangle { color: root.inputBackground; border.color: control.activeFocus ? root.statusBackground : root.borderColor; radius: 2 }
    }

    component DarkCombo: ComboBox {
        id: control
        implicitHeight: 32
        contentItem: Text { text: control.displayText; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; verticalAlignment: Text.AlignVCenter; leftPadding: 8; rightPadding: 24; elide: Text.ElideRight }
        background: Rectangle { color: root.inputBackground; border.color: control.activeFocus ? root.statusBackground : root.borderColor; radius: 2 }
        delegate: ItemDelegate {
            width: control.width
            height: 30
            contentItem: Text { text: modelData; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
            background: Rectangle { color: highlighted ? root.listActive : root.panelBackground }
        }
        popup: Popup {
            y: control.height
            width: control.width
            implicitHeight: contentItem.implicitHeight
            padding: 1
            contentItem: ListView { clip: true; implicitHeight: contentHeight; model: control.popup.visible ? control.delegateModel : null; currentIndex: control.highlightedIndex }
            background: Rectangle { color: root.panelBackground; border.color: root.borderColor }
        }
    }

    component DiffChip: Rectangle {
        id: chip
        property string value: ""
        property color chipColor: root.warningColor
        property color chipTextColor: "#111111"
        property bool active: false
        implicitHeight: Math.max(24, chipText.implicitHeight + 8)
        implicitWidth: Math.min(260, chipText.implicitWidth + 14)
        radius: 2
        color: chip.chipColor
        border.color: chip.active ? "#ffffff" : "transparent"
        border.width: chip.active ? 1 : 0
        Text { id: chipText; anchors.fill: parent; anchors.margins: 4; text: chip.value; color: chip.chipTextColor; font.family: "Consolas"; font.pixelSize: 12; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter }
    }

    component SuggestionSection: ColumnLayout {
        id: section
        property string title: ""
        property string suggestionType: "key"
        property var suggestionModel: null
        property int itemCount: 0
        Layout.fillWidth: true
        Layout.fillHeight: true
        spacing: 6

        RowLayout { Layout.fillWidth: true
            PanelTitle { text: section.title; Layout.fillWidth: true }
            Text { text: section.itemCount + " item(s)"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
        }
        ListView { id: suggestionList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 6; model: section.suggestionModel
            delegate: Rectangle {
                id: suggestionRow
                property bool expanded: false
                width: suggestionList.width
                height: 40 + (expanded ? Math.min(190, occurrenceColumn.implicitHeight + 10) : 0)
                color: root.editorBackground
                border.color: suggestionColor
                radius: 4
                clip: true
                ColumnLayout { anchors.fill: parent; anchors.margins: 5; spacing: 5
                    Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 30; color: suggestionColor; radius: 3
                        RowLayout { anchors.fill: parent; anchors.leftMargin: 4; anchors.rightMargin: 8; spacing: 4
                            IconButton { text: suggestionRow.expanded ? "v" : ">"; contentColor: "#ffffff"; onClicked: suggestionRow.expanded = !suggestionRow.expanded }
                            Text { Layout.fillWidth: true; text: duplicationValue + " : " + duplicationCount; color: "#ffffff"; font.family: "Consolas"; font.pixelSize: 12; font.bold: true; elide: Text.ElideRight
                                MouseArea { anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: root.callController(function(c) { c.openSuggestionSearch(section.suggestionType, index) }) }
                            }
                        }
                    }
                    ScrollView { visible: suggestionRow.expanded; Layout.fillWidth: true; Layout.preferredHeight: Math.min(180, occurrenceColumn.implicitHeight + 4); clip: true
                        ColumnLayout { id: occurrenceColumn; width: suggestionList.width - 18; spacing: 4
                            Repeater { model: occurrences
                                delegate: Rectangle { Layout.fillWidth: true; height: 52; color: root.panelBackground; border.color: root.borderColor; radius: 2
                                    ColumnLayout { anchors.fill: parent; anchors.margins: 5; spacing: 1
                                        RowLayout { Layout.fillWidth: true; spacing: 5
                                            Text { Layout.fillWidth: true; text: modelData.fileDisplayName; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 11; elide: Text.ElideMiddle }
                                            Text { text: modelData.occurrenceType; color: root.okColor; font.family: "Segoe UI"; font.pixelSize: 10 }
                                        }
                                        Text { Layout.fillWidth: true; text: modelData.jsonPath; color: root.mutedText; font.family: "Consolas"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                        Text { Layout.fillWidth: true; text: (modelData.key ? modelData.key + " - " : "") + modelData.valuePreview; color: root.mutedText; font.family: "Consolas"; font.pixelSize: 10; elide: Text.ElideRight }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        MutedLabel { visible: section.itemCount === 0; Layout.fillWidth: true; text: "No duplicates." }
    }

    header: Rectangle {
        height: 34
        color: root.headerBackground
        border.color: root.borderColor
        RowLayout { anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 10
            Text { text: "JSON Multi Editor"; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 13; font.bold: true; Layout.fillWidth: true; elide: Text.ElideRight }
            Text { text: appState.hasActiveFilter ? appState.activeFilterName + " filter" : ""; color: appState.activeFilterColor.length > 0 ? appState.activeFilterColor : root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12; visible: appState.hasActiveFilter }
            Text { text: appState.hasDirtyFiles ? "Unsaved changes" : "All saved"; color: appState.hasDirtyFiles ? root.warningColor : root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12 }
        }
    }

    StackLayout {
        anchors.fill: parent
        currentIndex: root.pageName === "picker" ? 0 : 1

        Item {
            DropArea { id: pickerDropArea; anchors.fill: parent; keys: ["text/uri-list"]; onDropped: function(drop) { if (drop.hasUrls) { root.callController(function(c) { c.addFiles(drop.urls) }); drop.acceptProposedAction() } } }
            Rectangle { anchors.fill: parent; color: pickerDropArea.containsDrag ? "#242b32" : root.editorBackground }
            ColumnLayout { anchors.fill: parent; anchors.margins: 36; spacing: 22
                ColumnLayout { Layout.fillWidth: true; spacing: 8
                    Text { text: "Open JSON files"; color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 28; font.bold: true }
                    MutedLabel { Layout.maximumWidth: 720; text: "Drop JSON files or folders here. Folder import scans recursively and offers only files named visual.json." }
                }
                Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 180; color: root.panelBackground; border.color: pickerDropArea.containsDrag ? root.statusBackground : root.borderColor; radius: 4
                    ColumnLayout { anchors.centerIn: parent; width: Math.min(parent.width - 48, 520); spacing: 14
                        Text { Layout.fillWidth: true; text: pickerDropArea.containsDrag ? "Release to scan or add" : "Drag JSON files or folders here"; color: pickerDropArea.containsDrag ? "#ffffff" : root.textColor; font.family: "Segoe UI"; font.pixelSize: 18; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                        RowLayout { Layout.alignment: Qt.AlignHCenter; spacing: 10
                            ChromeButton { text: "Add JSON files"; onClicked: root.callController(function(c) { c.openFileDialog() }) }
                            ChromeButton { text: "Add folder"; onClicked: root.callController(function(c) { c.openFolderDialog() }) }
                        }
                    }
                }
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: root.panelBackground; border.color: root.borderColor; radius: 4
                    ColumnLayout { anchors.fill: parent; anchors.margins: 12; spacing: 8
                        RowLayout {
                            Layout.fillWidth: true
                            PanelTitle { text: "OPEN FILES"; Layout.fillWidth: true }
                            Text { text: appState.fileCount + " file(s)"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12 }
                        }
                        ListView { id: pickerFilesList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 1; model: appState.fileModel
                            delegate: Rectangle { width: pickerFilesList.width; height: 44; color: mouseArea.containsMouse && activeFile ? root.listHover : "transparent"; opacity: activeFile ? 1.0 : 0.25
                                MouseArea { id: mouseArea; anchors.fill: parent; hoverEnabled: true; enabled: activeFile; onClicked: root.callController(function(c) { c.currentIndex = index }) }
                                RowLayout { anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 4; spacing: 8
                                    Rectangle { visible: activeFilterColor.length > 0; Layout.preferredWidth: 8; Layout.preferredHeight: 8; radius: 4; color: activeFilterColor.length > 0 ? activeFilterColor : "transparent" }
                                    ColumnLayout { Layout.fillWidth: true; spacing: 1
                                        Text { Layout.fillWidth: true; text: (dirty ? "* " : "") + name; color: validJson ? root.textColor : root.warningColor; font.family: "Segoe UI"; font.pixelSize: 13; elide: Text.ElideMiddle }
                                        Text { Layout.fillWidth: true; text: fileName + " - " + directory; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                    }
                                    Text { visible: !validJson; text: "JSON"; color: root.warningColor; font.family: "Segoe UI"; font.pixelSize: 10; ToolTip.visible: warningMouse.containsMouse; ToolTip.text: jsonError; MouseArea { id: warningMouse; anchors.fill: parent; hoverEnabled: true } }
                                    IconButton { text: "x"; contentColor: root.accentRed; opacity: 1.0; ToolTip.visible: hovered; ToolTip.text: "Remove"; onClicked: root.callController(function(c) { c.removeFile(index) }) }
                                }
                            }
                        }
                        MutedLabel { visible: appState.fileCount === 0; Layout.fillWidth: true; text: "No files selected." }
                    }
                }
                RowLayout { Layout.fillWidth: true; spacing: 10
                    MutedLabel { text: appState.statusMessage; Layout.fillWidth: true; elide: Text.ElideRight }
                    ChromeButton { text: "Continue"; normalColor: root.accentGreen; hoverColor: root.accentGreenHover; pressedColor: "#126a4d"; enabled: appState.fileCount > 0; onClicked: root.pageName = "management" }
                }
            }
        }

        Item {
            RowLayout { anchors.fill: parent; spacing: 0
                Rectangle { Layout.preferredWidth: 52; Layout.fillHeight: true; color: root.activityBackground
                    ColumnLayout { anchors.top: parent.top; anchors.left: parent.left; anchors.right: parent.right; spacing: 0
                        PanelButton { text: "E"; tooltipText: "Explorer"; active: root.activePanel === "explorer"; onClicked: root.activePanel = "explorer" }
                        PanelButton { text: "S"; tooltipText: "Search"; active: root.activePanel === "search"; onClicked: root.activePanel = "search" }
                        PanelButton { text: "F"; tooltipText: "Filters"; active: root.activePanel === "filters"; onClicked: root.activePanel = "filters" }
                        PanelButton { text: "!"; tooltipText: "Suggestions"; active: root.activePanel === "suggestions"; onClicked: root.activePanel = "suggestions" }
                        PanelButton { text: "M"; tooltipText: "Macros"; active: root.activePanel === "macros"; onClicked: root.activePanel = "macros" }
                    }
                }

                Rectangle { Layout.preferredWidth: 350; Layout.fillHeight: true; color: root.panelBackground; border.color: root.borderColor
                    StackLayout {
                        anchors.fill: parent
                        currentIndex: root.panelIndex()

                        ColumnLayout { Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: 10; spacing: 8
                            RowLayout { Layout.fillWidth: true
                                PanelTitle { text: "EXPLORER"; Layout.fillWidth: true }
                                IconButton { text: "+"; ToolTip.visible: hovered; ToolTip.text: "Add files"; onClicked: root.callController(function(c) { c.openFileDialog() }) }
                                IconButton { text: "D"; ToolTip.visible: hovered; ToolTip.text: "Add folder"; onClicked: root.callController(function(c) { c.openFolderDialog() }) }
                            }
                            ChromeButton { Layout.fillWidth: true; text: "Save all"; enabled: appState.hasDirtyFiles; onClicked: root.callController(function(c) { c.saveAll() }) }
                            Rectangle { visible: appState.hasActiveFilter; Layout.fillWidth: true; Layout.preferredHeight: 34; color: root.editorBackground; border.color: appState.activeFilterColor.length > 0 ? appState.activeFilterColor : root.borderColor; radius: 3
                                RowLayout { anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8; spacing: 8
                                    Rectangle { Layout.preferredWidth: 8; Layout.preferredHeight: 8; radius: 4; color: appState.activeFilterColor.length > 0 ? appState.activeFilterColor : root.mutedText }
                                    Text { Layout.fillWidth: true; text: appState.activeFilterName + " - " + appState.activeFileCount + " active"; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; elide: Text.ElideRight }
                                    IconButton { text: "x"; ToolTip.visible: hovered; ToolTip.text: "Deactivate"; onClicked: root.callController(function(c) { c.deactivateFilter() }) }
                                }
                            }
                            ListView { id: explorerList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 1; model: appState.fileModel
                                delegate: Rectangle { width: explorerList.width; height: 50; color: index === appState.currentIndex ? root.listActive : explorerMouseArea.containsMouse && activeFile ? root.listHover : "transparent"; opacity: activeFile ? 1.0 : 0.25
                                    MouseArea { id: explorerMouseArea; anchors.fill: parent; hoverEnabled: true; enabled: activeFile; onClicked: root.callController(function(c) { c.currentIndex = index }) }
                                    RowLayout { anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 4; spacing: 6
                                        Rectangle { visible: activeFilterColor.length > 0; Layout.preferredWidth: 8; Layout.preferredHeight: 8; radius: 4; color: activeFilterColor.length > 0 ? activeFilterColor : "transparent" }
                                        ColumnLayout { Layout.fillWidth: true; spacing: 1
                                            Text { Layout.fillWidth: true; text: (dirty ? "* " : "") + name; color: validJson ? root.textColor : root.warningColor; font.family: "Segoe UI"; font.pixelSize: 13; elide: Text.ElideMiddle }
                                            Text { Layout.fillWidth: true; text: matchCount > 0 ? matchCount + " match(es) - " + fileName : fileName; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                        }
                                        Text { visible: !validJson; text: "JSON"; color: root.warningColor; font.family: "Segoe UI"; font.pixelSize: 10; Layout.maximumWidth: 42; elide: Text.ElideRight; ToolTip.visible: invalidMouse.containsMouse; ToolTip.text: jsonError; MouseArea { id: invalidMouse; anchors.fill: parent; hoverEnabled: true } }
                                        IconButton { text: "S"; enabled: dirty; opacity: 1.0; ToolTip.visible: hovered; ToolTip.text: "Save"; onClicked: root.callController(function(c) { c.saveFile(index) }) }
                                        IconButton { text: "x"; contentColor: root.accentRed; opacity: 1.0; ToolTip.visible: hovered; ToolTip.text: "Remove"; onClicked: root.callController(function(c) { c.removeFile(index) }) }
                                    }
                                }
                            }
                        }
                        ColumnLayout { Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: 10; spacing: 8
                            PanelTitle { text: "SEARCH" }
                            Field { Layout.fillWidth: true; placeholderText: "Search"; text: appState.searchText; onTextEdited: root.callController(function(c) { c.searchText = text }) }
                            Field { Layout.fillWidth: true; placeholderText: "Replace"; text: appState.replaceText; onTextEdited: root.callController(function(c) { c.replaceText = text }) }
                            CheckBox { id: caseBox; text: "Match case"; checked: appState.caseSensitive; onToggled: root.callController(function(c) { c.caseSensitive = checked })
                                contentItem: Text { text: caseBox.text; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; leftPadding: caseBox.indicator.width + caseBox.spacing; verticalAlignment: Text.AlignVCenter }
                            }
                            RowLayout { Layout.fillWidth: true; spacing: 8
                                ChromeButton { Layout.fillWidth: true; text: "Replace file"; enabled: appState.currentIndex >= 0 && appState.searchText.length > 0; onClicked: root.callController(function(c) { c.replaceCurrentFile() }) }
                                ChromeButton { Layout.fillWidth: true; text: "Replace all"; enabled: appState.activeFileCount > 0 && appState.searchText.length > 0; onClicked: root.callController(function(c) { c.replaceAll() }) }
                            }
                            Text { Layout.fillWidth: true; text: appState.totalMatches + " match(es)" + (appState.hasActiveFilter ? " in " + appState.activeFileCount + " active file(s)" : ""); color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12 }
                            ListView { id: searchList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 4; model: appState.fileModel
                                delegate: Rectangle {
                                    id: searchFileResult
                                    property int fileRow: index
                                    width: searchList.width
                                    height: activeFile && appState.searchText.length > 0 && matchCount > 0 ? Math.min(210, 48 + previewsColumn.implicitHeight) : 0
                                    visible: height > 0
                                    color: index === appState.currentIndex ? root.listActive : searchMouseArea.containsMouse ? root.listHover : "transparent"
                                    border.color: root.borderColor
                                    MouseArea { id: searchMouseArea; anchors.fill: parent; hoverEnabled: true; onClicked: root.callController(function(c) { c.currentIndex = index }) }
                                    ColumnLayout { anchors.fill: parent; anchors.margins: 8; spacing: 6
                                        RowLayout { Layout.fillWidth: true
                                            Text { Layout.fillWidth: true; text: name; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 13; elide: Text.ElideMiddle }
                                            Text { text: matchCount + " match(es)"; color: root.okColor; font.family: "Segoe UI"; font.pixelSize: 11 }
                                        }
                                        ColumnLayout { id: previewsColumn; Layout.fillWidth: true; spacing: 4
                                            Repeater { model: matchPreviews
                                                delegate: Rectangle {
                                                    id: searchPreviewRow
                                                    property bool activeMatch: searchFileResult.fileRow === appState.activeMatchFileIndex && modelData.index === appState.activeMatchIndex
                                                    width: searchList.width - 20
                                                    height: 28
                                                    radius: 2
                                                    color: activeMatch ? "#36414a" : previewMouse.containsMouse ? "#303030" : "transparent"
                                                    MouseArea {
                                                        id: previewMouse
                                                        anchors.fill: parent
                                                        hoverEnabled: true
                                                        cursorShape: Qt.PointingHandCursor
                                                        onClicked: {
                                                            root.callController(function(c) { c.navigateToMatch(searchFileResult.fileRow, modelData.index) })
                                                            root.revealMatch(searchFileResult.fileRow, modelData.line)
                                                        }
                                                    }
                                                    RowLayout { anchors.fill: parent; anchors.leftMargin: 4; anchors.rightMargin: 4; spacing: 4
                                                        Text { Layout.fillWidth: true; text: "L" + modelData.line + " " + modelData.before; color: root.mutedText; font.family: "Consolas"; font.pixelSize: 11; elide: Text.ElideLeft }
                                                        DiffChip { value: modelData.match; active: searchPreviewRow.activeMatch; chipColor: appState.replaceText.length > 0 ? "#6f2424" : "#b59b00"; chipTextColor: appState.replaceText.length > 0 ? "#ffd7d7" : "#111111" }
                                                        DiffChip { visible: appState.replaceText.length > 0; value: modelData.replacement; active: searchPreviewRow.activeMatch; chipColor: "#183f2a"; chipTextColor: "#c6f6d5" }
                                                        Text { Layout.fillWidth: true; text: modelData.after; color: root.mutedText; font.family: "Consolas"; font.pixelSize: 11; elide: Text.ElideRight }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }

                        ColumnLayout { Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: 10; spacing: 8
                            RowLayout { Layout.fillWidth: true
                                PanelTitle { text: "FILTERS"; Layout.fillWidth: true }
                                IconButton { text: "+"; ToolTip.visible: hovered; ToolTip.text: "New filter"; onClicked: root.callController(function(c) { c.openNewFilterEditor() }) }
                            }
                            Rectangle { visible: appState.hasActiveFilter; Layout.fillWidth: true; Layout.preferredHeight: 40; color: root.editorBackground; border.color: appState.activeFilterColor.length > 0 ? appState.activeFilterColor : root.borderColor; radius: 3
                                RowLayout { anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8; spacing: 8
                                    Rectangle { Layout.preferredWidth: 10; Layout.preferredHeight: 10; radius: 5; color: appState.activeFilterColor.length > 0 ? appState.activeFilterColor : root.mutedText }
                                    Text { Layout.fillWidth: true; text: appState.activeFilterName + " active"; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; elide: Text.ElideRight }
                                    Text { text: appState.activeFileCount + "/" + appState.fileCount; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                                    IconButton { text: "x"; ToolTip.visible: hovered; ToolTip.text: "Deactivate"; onClicked: root.callController(function(c) { c.deactivateFilter() }) }
                                }
                            }
                            ListView { id: filterList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 6; model: appState.filterModel
                                delegate: Rectangle {
                                    width: filterList.width
                                    height: 88
                                    color: active ? root.listActive : filterMouse.containsMouse ? root.listHover : root.editorBackground
                                    border.color: active ? color : root.borderColor
                                    radius: 4
                                    MouseArea { id: filterMouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }
                                    ColumnLayout { anchors.fill: parent; anchors.margins: 8; spacing: 5
                                        RowLayout { Layout.fillWidth: true; spacing: 8
                                            Rectangle { Layout.preferredWidth: 10; Layout.preferredHeight: 10; radius: 5; color: model.color }
                                            ColumnLayout { Layout.fillWidth: true; spacing: 1
                                                Text { Layout.fillWidth: true; text: displayName; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 13; font.bold: true; elide: Text.ElideRight }
                                                Text { visible: readOnly; Layout.fillWidth: true; text: "Imported"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideRight }
                                            }
                                            ChromeButton { text: active ? "On" : "Apply"; implicitWidth: 58; normalColor: active ? root.accentGreen : root.accentBlue; hoverColor: active ? root.accentGreenHover : root.accentBlueHover; onClicked: root.callController(function(c) { active ? c.deactivateFilter() : c.applyFilter(index) }) }
                                            IconButton { text: "E"; enabled: !readOnly; ToolTip.visible: hovered; ToolTip.text: readOnly ? "Read-only" : "Edit"; onClicked: root.callController(function(c) { c.openEditFilterEditor(index) }) }
                                            IconButton { text: "x"; enabled: !readOnly; contentColor: root.accentRed; ToolTip.visible: hovered; ToolTip.text: readOnly ? "Read-only" : "Delete"; onClicked: root.callController(function(c) { c.deleteFilter(index) }) }
                                        }
                                        Text { Layout.fillWidth: true; text: ruleSummary; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 11; elide: Text.ElideRight }
                                    }
                                }
                            }
                            MutedLabel { visible: appState.filterCount === 0; Layout.fillWidth: true; text: "No filters." }
                        }

                        ColumnLayout { Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: 10; spacing: 8
                            RowLayout { Layout.fillWidth: true
                                PanelTitle { text: "SUGGESTIONS"; Layout.fillWidth: true }
                                Text { text: (appState.suggestionKeyCount + appState.suggestionValueCount) + " duplicate(s)"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                            }
                            SuggestionSection { title: "KEYS"; suggestionType: "key"; suggestionModel: appState.suggestionKeyModel; itemCount: appState.suggestionKeyCount }
                            SuggestionSection { title: "VALUES"; suggestionType: "value"; suggestionModel: appState.suggestionValueModel; itemCount: appState.suggestionValueCount }
                        }

                        ColumnLayout { Layout.fillWidth: true; Layout.fillHeight: true; Layout.margins: 10; spacing: 8
                            RowLayout { Layout.fillWidth: true
                                PanelTitle { text: "MACROS"; Layout.fillWidth: true }
                                Text { text: appState.macroCount + " macro(s)"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                                IconButton { text: "R"; ToolTip.visible: hovered; ToolTip.text: "Reload"; onClicked: root.callController(function(c) { c.reloadContent() }) }
                            }
                            ListView { id: macroList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 6; model: appState.macroModel
                                delegate: Rectangle {
                                    id: macroRow
                                    property bool expanded: false
                                    property int failedIndex: failedStepIndex
                                    width: macroList.width
                                    height: 58 + (validationText.length > 0 ? Math.min(58, validationLabel.implicitHeight + 6) : 0) + (expanded ? Math.min(190, stepsColumn.implicitHeight + 10) : 0)
                                    color: running ? "#30363d" : macroMouse.containsMouse ? root.listHover : root.editorBackground
                                    border.color: running ? root.okColor : validationText.length > 0 ? root.warningColor : root.borderColor
                                    radius: 4
                                    clip: true
                                    MouseArea { id: macroMouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }
                                    ColumnLayout { anchors.fill: parent; anchors.margins: 8; spacing: 5
                                        RowLayout { Layout.fillWidth: true; spacing: 8
                                            IconButton { text: macroRow.expanded ? "v" : ">"; onClicked: macroRow.expanded = !macroRow.expanded }
                                            ColumnLayout { Layout.fillWidth: true; spacing: 1
                                                Text { Layout.fillWidth: true; text: name; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 13; font.bold: true; elide: Text.ElideRight }
                                                Text { Layout.fillWidth: true; text: stepCount + " step(s) - " + statusText; color: validationText.length > 0 ? root.warningColor : running ? root.okColor : root.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideRight }
                                            }
                                            ChromeButton { text: running ? "Running" : "Run"; implicitWidth: 72; enabled: canRun && !appState.anyMacroRunning; normalColor: root.accentGreen; hoverColor: root.accentGreenHover; pressedColor: "#126a4d"; onClicked: root.callController(function(c) { c.runMacro(index) }) }
                                        }
                                        Text { id: validationLabel; visible: validationText.length > 0; Layout.fillWidth: true; text: validationText; color: root.warningColor; font.family: "Segoe UI"; font.pixelSize: 10; wrapMode: Text.WordWrap; maximumLineCount: 3; elide: Text.ElideRight }
                                        ScrollView { visible: macroRow.expanded; Layout.fillWidth: true; Layout.preferredHeight: Math.min(180, stepsColumn.implicitHeight + 4); clip: true
                                            ColumnLayout { id: stepsColumn; width: macroList.width - 20; spacing: 4
                                                Repeater { model: steps
                                                    delegate: Rectangle { Layout.fillWidth: true; height: 42; color: index === macroRow.failedIndex ? "#3d2727" : root.panelBackground; border.color: index === macroRow.failedIndex ? root.accentRed : root.borderColor; radius: 2
                                                        ColumnLayout { anchors.fill: parent; anchors.margins: 5; spacing: 1
                                                            Text { Layout.fillWidth: true; text: (index + 1) + ". " + modelData.type; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 11; font.bold: true; elide: Text.ElideRight }
                                                            Text { Layout.fillWidth: true; text: modelData.summary; color: root.mutedText; font.family: "Consolas"; font.pixelSize: 10; elide: Text.ElideRight }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                            MutedLabel { visible: appState.macroCount === 0; Layout.fillWidth: true; text: "No macros." }
                        }
                    }
                }
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: root.editorBackground
                    ColumnLayout { anchors.fill: parent; spacing: 0
                        Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 40; color: root.editorBackground; border.color: root.borderColor
                            RowLayout { anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 10
                                Text { text: "FILES"; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 13; font.bold: true; Layout.fillWidth: true }
                                Text { text: appState.hasActiveFilter ? appState.activeFileCount + " active / " + appState.fileCount : ""; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12 }
                                Text { text: appState.searchText.length > 0 ? appState.totalMatches + " match(es)" : ""; color: root.okColor; font.family: "Segoe UI"; font.pixelSize: 12 }
                            }
                        }
                        Rectangle { visible: appState.hasActiveFilter && appState.activeFileCount === 0; Layout.fillWidth: true; Layout.fillHeight: true; color: root.editorBackground
                            ColumnLayout { anchors.centerIn: parent; width: Math.min(parent.width - 48, 420); spacing: 8
                                Text { Layout.fillWidth: true; text: "No active files"; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 20; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                                MutedLabel { Layout.fillWidth: true; text: "No loaded file matches " + appState.activeFilterName + "."; horizontalAlignment: Text.AlignHCenter }
                            }
                        }
                        ListView { id: editorList; visible: !(appState.hasActiveFilter && appState.activeFileCount === 0); Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 8; model: appState.fileModel; boundsBehavior: Flickable.StopAtBounds; leftMargin: 10; rightMargin: 10; topMargin: 10; bottomMargin: 10
                            delegate: Rectangle {
                                id: accordion
                                width: editorList.width - 20
                                property bool expanded: activeFile && (index === appState.currentIndex || index === appState.activeMatchFileIndex)
                                property bool activeMatchFile: index === appState.activeMatchFileIndex
                                visible: activeFile
                                height: activeFile ? headerRow.height + (expanded ? contentColumn.implicitHeight + 16 : 0) : 0
                                color: root.panelBackground
                                border.color: index === appState.currentIndex ? root.statusBackground : root.borderColor
                                radius: 4

                                function revealPendingLine() {
                                    if (!activeFile)
                                        return
                                    accordion.expanded = true
                                    Qt.callLater(function() {
                                        editorList.positionViewAtIndex(index, ListView.Beginning)
                                        if (contentScroll.contentItem && contentScroll.contentItem.contentY !== undefined) {
                                            contentScroll.contentItem.contentY = Math.max(0, (root.pendingRevealLine - 1) * 19 - 48)
                                        }
                                    })
                                }

                                Connections {
                                    target: root
                                    function onPendingRevealFileIndexChanged() { if (root.pendingRevealFileIndex === index) accordion.revealPendingLine() }
                                    function onPendingRevealLineChanged() { if (root.pendingRevealFileIndex === index) accordion.revealPendingLine() }
                                }
                                Component.onCompleted: if (accordion.activeMatchFile) accordion.revealPendingLine()

                                ColumnLayout { anchors.fill: parent; spacing: 0
                                    Rectangle { id: headerRow; Layout.fillWidth: true; Layout.preferredHeight: 42; color: index === appState.currentIndex ? root.listActive : "#2d2d2d"; radius: 4
                                        MouseArea { anchors.fill: parent; onClicked: { accordion.expanded = !accordion.expanded; root.callController(function(c) { c.currentIndex = index }) } }
                                        RowLayout { anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 6; spacing: 8
                                            Text { text: accordion.expanded ? "v" : ">"; color: root.mutedText; font.family: "Consolas"; font.pixelSize: 13 }
                                            Rectangle { visible: activeFilterColor.length > 0; Layout.preferredWidth: 8; Layout.preferredHeight: 8; radius: 4; color: activeFilterColor.length > 0 ? activeFilterColor : "transparent" }
                                            ColumnLayout { Layout.fillWidth: true; spacing: 1
                                                Text { Layout.fillWidth: true; text: (dirty ? "* " : "") + name; color: validJson ? root.textColor : root.warningColor; font.family: "Segoe UI"; font.pixelSize: 13; font.bold: true; elide: Text.ElideMiddle }
                                                Text { Layout.fillWidth: true; text: fileName + (matchCount > 0 ? " - " + matchCount + " match(es)" : ""); color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                            }
                                            Text { text: validJson ? "Valid JSON" : jsonError; color: validJson ? root.okColor : root.warningColor; font.family: "Segoe UI"; font.pixelSize: 11; Layout.maximumWidth: 300; elide: Text.ElideRight }
                                            IconButton { text: "F"; ToolTip.visible: hovered; ToolTip.text: "Format"; onClicked: root.callController(function(c) { c.currentIndex = index; c.formatCurrentJson() }) }
                                            IconButton { text: "S"; enabled: dirty; ToolTip.visible: hovered; ToolTip.text: "Save"; onClicked: root.callController(function(c) { c.saveFile(index) }) }
                                        }
                                    }
                                    ColumnLayout { id: contentColumn; visible: accordion.expanded; Layout.fillWidth: true; Layout.leftMargin: 8; Layout.rightMargin: 8; Layout.topMargin: 8; Layout.bottomMargin: 8; spacing: 8
                                        Rectangle {
                                            visible: appState.searchText.length > 0
                                            Layout.fillWidth: true
                                            Layout.preferredHeight: 46
                                            color: "#2d2d2d"
                                            border.color: root.borderColor
                                            radius: 3
                                            RowLayout { anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 8; spacing: 8
                                                Text { text: "Find"; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12 }
                                                Text { Layout.fillWidth: true; text: appState.searchText; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; elide: Text.ElideRight }
                                                Text { text: accordion.activeMatchFile && appState.activeMatchDisplayIndex > 0 ? appState.activeMatchDisplayIndex + " of " + matchCount : matchCount + " match(es)"; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12 }
                                                IconButton { text: "^"; enabled: appState.totalMatches > 0; ToolTip.visible: hovered; ToolTip.text: "Previous match"; onClicked: root.callController(function(c) { c.navigatePreviousMatch(); Qt.callLater(function() { root.revealMatch(appState.activeMatchFileIndex, appState.activeMatchLine) }) }) }
                                                IconButton { text: "v"; enabled: appState.totalMatches > 0; ToolTip.visible: hovered; ToolTip.text: "Next match"; onClicked: root.callController(function(c) { c.navigateNextMatch(); Qt.callLater(function() { root.revealMatch(appState.activeMatchFileIndex, appState.activeMatchLine) }) }) }
                                                IconButton { text: "x"; ToolTip.visible: hovered; ToolTip.text: "Clear search"; onClicked: root.callController(function(c) { c.searchText = "" }) }
                                            }
                                        }

                                        Flow { visible: appState.searchText.length > 0 && matchCount > 0; Layout.fillWidth: true; spacing: 6
                                            Repeater { model: matchPreviews
                                                delegate: RowLayout { spacing: 4
                                                    Text { text: "L" + modelData.line; color: root.mutedText; font.family: "Consolas"; font.pixelSize: 11 }
                                                    DiffChip { value: modelData.match; active: accordion.activeMatchFile && modelData.index === appState.activeMatchIndex; chipColor: appState.replaceText.length > 0 ? "#6f2424" : "#b59b00"; chipTextColor: appState.replaceText.length > 0 ? "#ffd7d7" : "#111111" }
                                                    DiffChip { visible: appState.replaceText.length > 0; value: modelData.replacement; active: accordion.activeMatchFile && modelData.index === appState.activeMatchIndex; chipColor: "#183f2a"; chipTextColor: "#c6f6d5" }
                                                }
                                            }
                                        }
                                        ScrollView { id: contentScroll; Layout.fillWidth: true; Layout.preferredHeight: accordion.expanded ? Math.min(520, Math.max(220, editorContent.implicitHeight + 24)) : 0; clip: true
                                            TextArea { id: editorArea; visible: appState.searchText.length === 0; text: model.text; textFormat: TextEdit.PlainText; wrapMode: TextEdit.NoWrap; selectByMouse: true; persistentSelection: true; color: root.textColor; selectedTextColor: "#ffffff"; selectionColor: "#264f78"; font.family: "Consolas"; font.pixelSize: 14; leftPadding: 14; topPadding: 12; rightPadding: 14; bottomPadding: 12; background: Rectangle { color: root.editorBackground }
                                                onActiveFocusChanged: if (activeFocus) root.callController(function(c) { c.currentIndex = index })
                                                onTextChanged: { if (visible && text !== model.text) root.callController(function(c) { c.updateFileText(index, text) }) }
                                                Component.onCompleted: syntaxBridge.attach(textDocument)
                                            }
                                            TextEdit { id: editorContent; visible: appState.searchText.length > 0; readOnly: true; selectByMouse: true; textFormat: TextEdit.RichText; text: highlightedHtml; wrapMode: TextEdit.NoWrap; color: root.textColor; selectedTextColor: "#ffffff"; selectionColor: "#264f78"; font.family: "Consolas"; font.pixelSize: 14; leftPadding: 14; topPadding: 12; rightPadding: 14; bottomPadding: 12 }
                                        }
                                    }
                                }
                            }
                        }
                        Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 24; color: root.statusBackground
                            RowLayout { anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 10; spacing: 12
                                Text { text: appState.statusMessage; color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideRight }
                                Text { text: appState.hasActiveFilter ? appState.activeFileCount + "/" + appState.fileCount + " active" : appState.fileCount + " file(s)"; color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 11 }
                                Text { text: appState.hasDirtyFiles ? "dirty" : "clean"; color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 11 }
                            }
                        }
                    }
                }
            }
        }
    }
    Rectangle { anchors.fill: parent; visible: appState.folderImportVisible; color: "#aa000000"; z: 20
        MouseArea { anchors.fill: parent }
        Rectangle { width: Math.min(parent.width - 80, 760); height: Math.min(parent.height - 80, 560); anchors.centerIn: parent; color: root.panelBackground; border.color: root.borderColor; radius: 4
            ColumnLayout { anchors.fill: parent; anchors.margins: 16; spacing: 12
                RowLayout {
                    Layout.fillWidth: true
                    PanelTitle { text: "FOLDER IMPORT"; Layout.fillWidth: true }
                    IconButton { text: "x"; contentColor: root.accentRed; onClicked: root.callController(function(c) { c.cancelFolderImport() }) }
                }
                MutedLabel { Layout.fillWidth: true; text: appState.folderScanRoot; elide: Text.ElideMiddle }
                Text { Layout.fillWidth: true; text: appState.folderScanCount + " visual.json file(s) found"; color: appState.folderScanCount > 0 ? root.okColor : root.warningColor; font.family: "Segoe UI"; font.pixelSize: 13 }
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: root.editorBackground; border.color: root.borderColor
                    ListView { id: folderTree; anchors.fill: parent; anchors.margins: 8; clip: true; spacing: 1; model: appState.folderScanModel
                        delegate: Rectangle { width: folderTree.width; height: 42; color: folderMouse.containsMouse ? root.listHover : "transparent"
                            MouseArea { id: folderMouse; anchors.fill: parent; hoverEnabled: true }
                            RowLayout { anchors.fill: parent; anchors.leftMargin: 8 + depth * 16; anchors.rightMargin: 8; spacing: 8
                                Text { text: displayName; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 13; Layout.fillWidth: true; elide: Text.ElideMiddle }
                                Text { text: relativePath; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 11; Layout.maximumWidth: 360; elide: Text.ElideMiddle }
                            }
                        }
                    }
                }
                RowLayout { Layout.fillWidth: true; spacing: 10
                    MutedLabel { Layout.fillWidth: true; text: appState.statusMessage; elide: Text.ElideRight }
                    ChromeButton { text: "Cancel"; normalColor: "#3c3c3c"; hoverColor: "#4a4a4a"; onClicked: root.callController(function(c) { c.cancelFolderImport() }) }
                    ChromeButton { text: "Continue"; normalColor: root.accentGreen; hoverColor: root.accentGreenHover; pressedColor: "#126a4d"; enabled: appState.folderScanCount > 0; onClicked: { root.callController(function(c) { c.confirmFolderImport() }); root.pageName = "management" } }
                }
            }
        }
    }

    Rectangle { anchors.fill: parent; visible: appState.filterEditorVisible; color: "#aa000000"; z: 30
        MouseArea { anchors.fill: parent }
        Rectangle { width: Math.min(parent.width - 80, 820); height: Math.min(parent.height - 80, 620); anchors.centerIn: parent; color: root.panelBackground; border.color: root.borderColor; radius: 4
            ColumnLayout { anchors.fill: parent; anchors.margins: 16; spacing: 12
                RowLayout { Layout.fillWidth: true
                    PanelTitle { text: "FILTER EDITOR"; Layout.fillWidth: true }
                    IconButton { text: "x"; contentColor: root.accentRed; onClicked: root.callController(function(c) { c.cancelFilterEditor() }) }
                }
                RowLayout { Layout.fillWidth: true; spacing: 10
                    Field { Layout.fillWidth: true; placeholderText: "Filter name"; text: appState.editingFilterName; onTextEdited: root.callController(function(c) { c.editingFilterName = text }) }
                    Rectangle { Layout.preferredWidth: 32; Layout.preferredHeight: 32; radius: 3; color: appState.editingFilterColor.length > 0 ? appState.editingFilterColor : root.accentBlue; border.color: root.borderColor }
                    Text { text: appState.editingFilterColor; color: root.mutedText; font.family: "Consolas"; font.pixelSize: 12; Layout.preferredWidth: 76; elide: Text.ElideRight }
                    IconButton { text: "R"; ToolTip.visible: hovered; ToolTip.text: "Random color"; onClicked: root.callController(function(c) { c.randomizeEditingFilterColor() }) }
                }
                RowLayout { Layout.fillWidth: true
                    PanelTitle { text: "RULES"; Layout.fillWidth: true }
                    Text { text: appState.editingRuleCount + " rule(s)"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                }
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: root.editorBackground; border.color: root.borderColor; radius: 3
                    ListView { id: ruleList; anchors.fill: parent; anchors.margins: 8; clip: true; spacing: 6; model: appState.editingRuleModel
                        delegate: Rectangle { width: ruleList.width; height: 42; color: ruleMouse.containsMouse ? root.listHover : "transparent"; radius: 2
                            MouseArea { id: ruleMouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }
                            RowLayout { anchors.fill: parent; anchors.leftMargin: 4; anchors.rightMargin: 4; spacing: 8
                                Field { Layout.preferredWidth: 160; placeholderText: "Key"; text: key; onTextEdited: root.callController(function(c) { c.updateEditingRuleKey(index, text) }) }
                                DarkCombo { Layout.preferredWidth: 145; model: root.filterOperationOptions; currentIndex: Math.max(0, root.filterOperationOptions.indexOf(operation)); onActivated: root.callController(function(c) { c.updateEditingRuleOperation(index, currentText) }) }
                                Field { Layout.fillWidth: true; placeholderText: "Value"; text: value; onTextEdited: root.callController(function(c) { c.updateEditingRuleValue(index, text) }) }
                                IconButton { text: "x"; contentColor: root.accentRed; ToolTip.visible: hovered; ToolTip.text: "Remove rule"; onClicked: root.callController(function(c) { c.removeEditingRule(index) }) }
                            }
                        }
                    }
                }
                RowLayout { Layout.fillWidth: true; spacing: 10
                    ChromeButton { text: "Add rule"; onClicked: root.callController(function(c) { c.addEditingRule() }) }
                    MutedLabel { Layout.fillWidth: true; text: appState.statusMessage; elide: Text.ElideRight }
                    ChromeButton { text: "Cancel"; normalColor: "#3c3c3c"; hoverColor: "#4a4a4a"; onClicked: root.callController(function(c) { c.cancelFilterEditor() }) }
                    ChromeButton { text: "Save"; normalColor: root.accentGreen; hoverColor: root.accentGreenHover; pressedColor: "#126a4d"; enabled: appState.editingFilterCanSave; onClicked: root.callController(function(c) { c.saveFilterEditor() }) }
                }
            }
        }
    }
}
