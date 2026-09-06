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
    title: "Power BI PBIR Editor"

    property var controller: appController
    property string pageName: "picker"
    property string activePanel: "explorer"
    readonly property var filterOperationOptions: ["equals", "includes", "notEquals", "notIncludes"]
    readonly property var filterTargetOptions: ["All", "Page", "Visual"]
    readonly property var visualEditorCategories: ["General", "Specific"]

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
        property string activeFilterTarget: root.controller ? root.controller.activeFilterTarget : ""
        property string editingFilterName: root.controller ? root.controller.editingFilterName : ""
        property string editingFilterColor: root.controller ? root.controller.editingFilterColor : ""
        property string editingFilterTarget: root.controller ? root.controller.editingFilterTarget : "All"
        property string currentName: root.controller ? root.controller.currentName : "No file selected"
        property string currentPath: root.controller ? root.controller.currentPath : ""
        property string currentFileType: root.controller ? root.controller.currentFileType : ""
        property string currentRelativePath: root.controller ? root.controller.currentRelativePath : ""
        property string currentHighlightedHtml: root.controller ? root.controller.currentHighlightedHtml : ""
        property string currentText: root.controller ? root.controller.currentText : ""
        property string currentJsonError: root.controller ? root.controller.currentJsonError : ""
        property string visualEditorCategory: root.controller ? root.controller.visualEditorCategory : "General"
        property string visualEditorStatus: root.controller ? root.controller.visualEditorStatus : ""
        property var visualEditorCategoryOptions: root.controller ? root.controller.visualEditorCategoryOptions : ["General", "Specific"]
        property int fileCount: root.controller ? root.controller.fileCount : 0
        property int activeFileCount: root.controller ? root.controller.activeFileCount : 0
        property int visibleFileCount: root.controller ? root.controller.visibleFileCount : 0
        property int projectTreeCount: root.controller ? root.controller.projectTreeCount : 0
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
        property int activeVisualCount: root.controller ? root.controller.activeVisualCount : 0
        property int visualEditorControlCount: root.controller ? root.controller.visualEditorControlCount : 0
        property int historyCount: root.controller ? root.controller.historyCount : 0
        property int historyCurrentIndex: root.controller ? root.controller.historyCurrentIndex : -1
        property bool hasDirtyFiles: root.controller ? root.controller.hasDirtyFiles : false
        property bool currentDirty: root.controller ? root.controller.currentDirty : false
        property bool currentValidJson: root.controller ? root.controller.currentValidJson : true
        property bool caseSensitive: root.controller ? root.controller.caseSensitive : false
        property bool folderImportVisible: root.controller ? root.controller.folderImportVisible : false
        property bool hasActiveFilter: root.controller ? root.controller.hasActiveFilter : false
        property bool filterEditorVisible: root.controller ? root.controller.filterEditorVisible : false
        property bool editingFilterCanSave: root.controller ? root.controller.editingFilterCanSave : false
        property bool anyMacroRunning: root.controller ? root.controller.anyMacroRunning : false
        property var fileModel: root.controller ? root.controller.fileModel : null
        property var projectTreeModel: root.controller ? root.controller.projectTreeModel : null
        property var folderScanModel: root.controller ? root.controller.folderScanModel : null
        property var filterModel: root.controller ? root.controller.filterModel : null
        property var suggestionKeyModel: root.controller ? root.controller.suggestionKeyModel : null
        property var suggestionValueModel: root.controller ? root.controller.suggestionValueModel : null
        property var macroModel: root.controller ? root.controller.macroModel : null
        property var editingRuleModel: root.controller ? root.controller.editingRuleModel : null
        property var visualEditorControlModel: root.controller ? root.controller.visualEditorControlModel : null
        property var historyModel: root.controller ? root.controller.historyModel : null
    }

    function callController(action) { if (root.controller) action(root.controller) }
    function visualEditorOptionIndex(options, value) {
        for (var i = 0; i < options.length; i++) {
            var option = options[i]
            var optionValue = typeof option === "object" && option !== null && option.value !== undefined ? option.value : option
            if (optionValue === value) return i
        }
        return 0
    }

    function panelIndex() {
        if (root.activePanel === "explorer") return 0
        if (root.activePanel === "search") return 1
        if (root.activePanel === "filters") return 2
        if (root.activePanel === "suggestions") return 3
        if (root.activePanel === "visuals") return 4
        if (root.activePanel === "history") return 5
        return 6
    }

    Connections {
        target: root.controller
        function onPanelRequested(panelName) { root.activePanel = panelName }
        function onSessionResetRequested() { root.pageName = "picker"; root.activePanel = "explorer" }
    }

    Shortcut { sequences: [StandardKey.Save]; onActivated: root.callController(function(c) { c.saveFile(appState.currentIndex) }) }
    Shortcut { sequence: "Ctrl+Shift+S"; onActivated: root.callController(function(c) { c.saveAll() }) }

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
        property string textRoleName: "label"
        property string valueRoleName: "value"
        function optionText(option) { return typeof option === "object" && option !== null && option[textRoleName] !== undefined ? option[textRoleName] : option }
        function optionValue(option) { return typeof option === "object" && option !== null && option[valueRoleName] !== undefined ? option[valueRoleName] : optionText(option) }
        function optionEnabled(option) { return !(typeof option === "object" && option !== null && option.enabled === false) }
        implicitHeight: 32
        contentItem: Text { text: control.optionText(control.currentIndex >= 0 ? control.model[control.currentIndex] : control.displayText); color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; verticalAlignment: Text.AlignVCenter; leftPadding: 8; rightPadding: 24; elide: Text.ElideRight }
        background: Rectangle { color: root.inputBackground; border.color: control.activeFocus ? root.statusBackground : root.borderColor; radius: 2 }
        delegate: ItemDelegate {
            width: control.width
            height: 30
            enabled: control.optionEnabled(modelData)
            opacity: enabled ? 1.0 : 0.5
            contentItem: Text { text: control.optionText(modelData); color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; verticalAlignment: Text.AlignVCenter; elide: Text.ElideRight }
            background: Rectangle { color: highlighted && enabled ? root.listActive : root.panelBackground }
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

    header: Rectangle {
        height: 38
        color: root.headerBackground
        border.color: root.borderColor
        RowLayout { anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 10
            Text { text: "Power BI PBIR Editor"; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 13; font.bold: true; Layout.fillWidth: true; elide: Text.ElideRight }
            Text { text: appState.hasActiveFilter ? appState.activeFilterName + " (" + appState.activeFilterTarget + ")" : ""; color: appState.activeFilterColor.length > 0 ? appState.activeFilterColor : root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12; visible: appState.hasActiveFilter }
            Text { text: appState.hasDirtyFiles ? "Unsaved changes" : "All saved"; color: appState.hasDirtyFiles ? root.warningColor : root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12 }
            ChromeButton { text: "Start Again"; normalColor: "#3c3c3c"; hoverColor: "#4a4a4a"; onClicked: appState.hasDirtyFiles ? startAgainDialog.open() : root.callController(function(c) { c.startAgain() }) }
        }
    }

    StackLayout {
        anchors.fill: parent
        currentIndex: root.pageName === "picker" ? 0 : 1

        Item {
            DropArea { id: pickerDropArea; anchors.fill: parent; keys: ["text/uri-list"]; onDropped: function(drop) { if (drop.hasUrls) { root.callController(function(c) { if (c.addFiles(drop.urls) > 0) root.pageName = "management" }); drop.acceptProposedAction() } } }
            Rectangle { anchors.fill: parent; color: pickerDropArea.containsDrag ? "#242b32" : root.editorBackground }
            ColumnLayout { anchors.fill: parent; anchors.margins: 36; spacing: 22
                ColumnLayout { Layout.fillWidth: true; spacing: 8
                    Text { text: "Open Power BI report JSON"; color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 28; font.bold: true }
                    MutedLabel { Layout.maximumWidth: 760; text: "Drop a PBIR report folder, page.json, or visual.json. Folder import scans pages and visuals while preserving their hierarchy." }
                }
                Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 180; color: root.panelBackground; border.color: pickerDropArea.containsDrag ? root.statusBackground : root.borderColor; radius: 4
                    ColumnLayout { anchors.centerIn: parent; width: Math.min(parent.width - 48, 560); spacing: 14
                        Text { Layout.fillWidth: true; text: pickerDropArea.containsDrag ? "Release to scan or add" : "Drag Power BI JSON files or folders here"; color: pickerDropArea.containsDrag ? "#ffffff" : root.textColor; font.family: "Segoe UI"; font.pixelSize: 18; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                        RowLayout { Layout.alignment: Qt.AlignHCenter; spacing: 10
                            ChromeButton { text: "Add JSON files"; onClicked: root.callController(function(c) { if (c.openFileDialog() > 0) root.pageName = "management" }) }
                            ChromeButton { text: "Add folder"; onClicked: root.callController(function(c) { c.openFolderDialog() }) }
                        }
                    }
                }
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: root.panelBackground; border.color: root.borderColor; radius: 4
                    ColumnLayout { anchors.fill: parent; anchors.margins: 12; spacing: 8
                        RowLayout {
                            Layout.fillWidth: true
                            PanelTitle { text: "OPEN DOCUMENTS"; Layout.fillWidth: true }
                            Text { text: appState.fileCount + " file(s)"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12 }
                        }
                        ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 1; model: appState.fileModel
                            delegate: Rectangle { width: parent ? parent.width : 0; height: 44; color: "transparent"; opacity: visibleInTree ? 1.0 : 0.4
                                RowLayout { anchors.fill: parent; anchors.leftMargin: 8; anchors.rightMargin: 4; spacing: 8
                                    Rectangle { Layout.preferredWidth: 8; Layout.preferredHeight: 8; radius: 4; color: activeFilterColor.length > 0 ? activeFilterColor : "transparent" }
                                    ColumnLayout { Layout.fillWidth: true; spacing: 1
                                        Text { Layout.fillWidth: true; text: (dirty ? "* " : "") + name; color: validJson ? root.textColor : root.warningColor; font.family: "Segoe UI"; font.pixelSize: 13; font.bold: true; elide: Text.ElideMiddle }
                                        Text { Layout.fillWidth: true; text: fileType + " - " + relativePath; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        Item {
            RowLayout { anchors.fill: parent; spacing: 0
                Rectangle { Layout.preferredWidth: 52; Layout.fillHeight: true; color: root.activityBackground
                    ColumnLayout { anchors.fill: parent; spacing: 0
                        PanelButton { text: "E"; tooltipText: "Explorer"; active: root.activePanel === "explorer"; onClicked: root.activePanel = "explorer" }
                        PanelButton { text: "S"; tooltipText: "Search"; active: root.activePanel === "search"; onClicked: root.activePanel = "search" }
                        PanelButton { text: "F"; tooltipText: "Filters"; active: root.activePanel === "filters"; onClicked: root.activePanel = "filters" }
                        PanelButton { text: "!"; tooltipText: "Suggestions"; active: root.activePanel === "suggestions"; onClicked: root.activePanel = "suggestions" }
                        PanelButton { text: "V"; tooltipText: "Visuals Editor"; active: root.activePanel === "visuals"; onClicked: root.activePanel = "visuals" }
                        PanelButton { text: "H"; tooltipText: "History"; active: root.activePanel === "history"; onClicked: root.activePanel = "history" }
                        PanelButton { text: "M"; tooltipText: "Macros"; active: root.activePanel === "macros"; onClicked: root.activePanel = "macros" }
                        Item { Layout.fillHeight: true }
                    }
                }

                Rectangle { Layout.preferredWidth: 340; Layout.fillHeight: true; color: root.panelBackground; border.color: root.borderColor
                    StackLayout { anchors.fill: parent; anchors.margins: 10; currentIndex: root.panelIndex()
                        ColumnLayout { spacing: 8
                            RowLayout {
                                Layout.fillWidth: true
                                PanelTitle { text: "PROJECT"; Layout.fillWidth: true }
                                Text { text: appState.projectTreeCount + " row(s)"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                            }
                            RowLayout { Layout.fillWidth: true; spacing: 6
                                ChromeButton { Layout.fillWidth: true; text: "Add folder"; onClicked: root.callController(function(c) { c.openFolderDialog() }) }
                                ChromeButton { Layout.fillWidth: true; text: "Add files"; onClicked: root.callController(function(c) { c.openFileDialog() }) }
                            }
                            ChromeButton { Layout.fillWidth: true; text: "Save all"; enabled: appState.hasDirtyFiles; onClicked: root.callController(function(c) { c.saveAll() }) }
                            ListView { id: projectTree; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 2; model: appState.projectTreeModel
                                delegate: Rectangle { width: projectTree.width; height: 48; color: fileIndex === appState.currentIndex ? root.listActive : rowMouse.containsMouse ? root.listHover : "transparent"; opacity: activeFile || containerOnly ? 1.0 : 0.55
                                    MouseArea { id: rowMouse; anchors.fill: parent; hoverEnabled: true; onClicked: root.callController(function(c) { c.selectTreeRow(index) }) }
                                    RowLayout { anchors.fill: parent; anchors.leftMargin: 6 + depth * 18; anchors.rightMargin: 4; spacing: 6
                                        IconButton { visible: fileType === "Page"; text: expanded ? "v" : ">"; onClicked: root.callController(function(c) { c.setPageExpanded(model.id, !expanded) }) }
                                        Text { visible: fileType !== "Page"; text: fileType === "Visual" && depth > 0 ? "-" : ""; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12; Layout.preferredWidth: fileType === "Page" ? 0 : 30 }
                                        Rectangle { Layout.preferredWidth: 8; Layout.preferredHeight: 8; radius: 4; color: activeFilterColor.length > 0 ? activeFilterColor : "transparent" }
                                        ColumnLayout { Layout.fillWidth: true; spacing: 1
                                            Text { Layout.fillWidth: true; text: (dirty ? "* " : "") + name; color: validJson ? root.textColor : root.warningColor; font.family: "Segoe UI"; font.pixelSize: 13; font.bold: fileType === "Page"; elide: Text.ElideMiddle }
                                            Text { Layout.fillWidth: true; text: fileType + (visualType.length > 0 ? " - " + visualType : "") + (matchCount > 0 ? " - " + matchCount + " match(es)" : ""); color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                        }
                                        IconButton { text: "x"; contentColor: root.accentRed; ToolTip.visible: hovered; ToolTip.text: "Remove"; onClicked: root.callController(function(c) { c.removeFile(fileIndex) }) }
                                    }
                                }
                            }
                            MutedLabel { visible: appState.projectTreeCount === 0; Layout.fillWidth: true; text: "No Power BI JSON files loaded." }
                        }

                        ColumnLayout { spacing: 8
                            PanelTitle { text: "SEARCH" }
                            Field { Layout.fillWidth: true; placeholderText: "Find"; text: appState.searchText; onTextEdited: root.callController(function(c) { c.searchText = text }) }
                            Field { Layout.fillWidth: true; placeholderText: "Replace with"; text: appState.replaceText; onTextEdited: root.callController(function(c) { c.replaceText = text }) }
                            CheckBox { text: "Case sensitive"; checked: appState.caseSensitive; onToggled: root.callController(function(c) { c.caseSensitive = checked }); contentItem: Text { text: parent.text; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; leftPadding: parent.indicator.width + 6 } }
                            RowLayout { Layout.fillWidth: true; spacing: 6
                                ChromeButton { Layout.fillWidth: true; text: "Replace"; enabled: appState.activeFileCount > 0 && appState.searchText.length > 0; onClicked: root.callController(function(c) { c.replaceCurrentMatch() }) }
                                ChromeButton { Layout.fillWidth: true; text: "Replace all"; enabled: appState.activeFileCount > 0 && appState.searchText.length > 0; onClicked: root.callController(function(c) { c.replaceAll() }) }
                            }
                            RowLayout { Layout.fillWidth: true; spacing: 6
                                IconButton { text: "^"; enabled: appState.totalMatches > 0; ToolTip.visible: hovered; ToolTip.text: "Previous match"; onClicked: root.callController(function(c) { c.navigatePreviousMatch() }) }
                                IconButton { text: "v"; enabled: appState.totalMatches > 0; ToolTip.visible: hovered; ToolTip.text: "Next match"; onClicked: root.callController(function(c) { c.navigateNextMatch() }) }
                                Text { Layout.fillWidth: true; text: appState.totalMatches + " match(es) in active files"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12; elide: Text.ElideRight }
                            }
                            ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; model: appState.fileModel; spacing: 5
                                delegate: Rectangle { width: parent ? parent.width : 0; height: activeFile && matchCount > 0 ? 58 : 0; visible: activeFile && matchCount > 0; color: root.editorBackground; border.color: root.borderColor; radius: 3
                                    MouseArea { anchors.fill: parent; onClicked: root.callController(function(c) { c.currentIndex = index; c.navigateToMatch(index, 0) }) }
                                    ColumnLayout { anchors.fill: parent; anchors.margins: 6; spacing: 2
                                        Text { Layout.fillWidth: true; text: name + " - " + matchCount + " match(es)"; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; elide: Text.ElideMiddle }
                                        Text { Layout.fillWidth: true; text: relativePath; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                    }
                                }
                            }
                        }

                        ColumnLayout { spacing: 8
                            RowLayout {
                                Layout.fillWidth: true
                                PanelTitle { text: "FILTERS"; Layout.fillWidth: true }
                                IconButton { text: "+"; ToolTip.visible: hovered; ToolTip.text: "New filter"; onClicked: root.callController(function(c) { c.openNewFilterEditor() }) }
                            }
                            RowLayout { Layout.fillWidth: true; spacing: 6
                                ChromeButton { Layout.fillWidth: true; text: "Import"; onClicked: root.callController(function(c) { c.importFilter() }) }
                                ChromeButton { Layout.fillWidth: true; text: "Reload"; onClicked: root.callController(function(c) { c.reloadContent() }) }
                                ChromeButton { Layout.fillWidth: true; text: "Clear"; enabled: appState.hasActiveFilter; onClicked: root.callController(function(c) { c.deactivateFilter() }) }
                            }
                            Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 96; color: root.editorBackground; border.color: root.borderColor; radius: 3
                                ColumnLayout { anchors.fill: parent; anchors.margins: 8; spacing: 6
                                    PanelTitle { text: "DYNAMIC" }
                                    RowLayout {
                                        Layout.fillWidth: true
                                        property string pageFilterText: ""
                                        Field { Layout.fillWidth: true; placeholderText: "Page name"; onTextEdited: parent.pageFilterText = text }
                                        ChromeButton { text: "Apply"; enabled: parent.pageFilterText.length > 0; onClicked: root.callController(function(c) { c.applyDynamicPageNameFilter(parent.pageFilterText) }) }
                                    }
                                    RowLayout {
                                        Layout.fillWidth: true
                                        property string visualFilterText: ""
                                        Field { Layout.fillWidth: true; placeholderText: "Visual type"; onTextEdited: parent.visualFilterText = text }
                                        ChromeButton { text: "Apply"; enabled: parent.visualFilterText.length > 0; onClicked: root.callController(function(c) { c.applyDynamicVisualTypeFilter(parent.visualFilterText) }) }
                                    }
                                }
                            }
                            ListView { id: filterList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 6; model: appState.filterModel
                                delegate: Rectangle { width: filterList.width; height: 88; color: active ? root.listActive : filterMouse.containsMouse ? root.listHover : root.editorBackground; border.color: active ? color : root.borderColor; radius: 4
                                    MouseArea { id: filterMouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }
                                    ColumnLayout { anchors.fill: parent; anchors.margins: 7; spacing: 4
                                        RowLayout { Layout.fillWidth: true; spacing: 6
                                            Rectangle { Layout.preferredWidth: 10; Layout.preferredHeight: 10; radius: 5; color: color }
                                            Text { Layout.fillWidth: true; text: displayName; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; font.bold: true; elide: Text.ElideRight }
                                            Text { text: targetJsonFileType; color: root.okColor; font.family: "Segoe UI"; font.pixelSize: 10 }
                                        }
                                        Text { Layout.fillWidth: true; text: ruleSummary; color: root.mutedText; font.family: "Consolas"; font.pixelSize: 10; elide: Text.ElideRight }
                                        RowLayout { Layout.fillWidth: true; spacing: 6
                                            ChromeButton { text: active ? "Active" : "Apply"; enabled: !active; onClicked: root.callController(function(c) { c.applyFilter(index) }) }
                                            ChromeButton { text: "Export"; onClicked: root.callController(function(c) { c.exportFilter(index) }) }
                                            ChromeButton { text: "Edit"; enabled: !readOnly; onClicked: root.callController(function(c) { c.openEditFilterEditor(index) }) }
                                            IconButton { text: "x"; enabled: !readOnly; contentColor: root.accentRed; onClicked: root.callController(function(c) { c.deleteFilter(index) }) }
                                            Item { Layout.fillWidth: true }
                                        }
                                    }
                                }
                            }
                            MutedLabel { visible: appState.filterCount === 0; Layout.fillWidth: true; text: "No filters." }
                        }

                        ColumnLayout { spacing: 8
                            PanelTitle { text: "SUGGESTIONS" }
                            Text { Layout.fillWidth: true; text: appState.suggestionKeyCount + " key duplicate(s), " + appState.suggestionValueCount + " value duplicate(s)"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12 }
                            ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; model: appState.suggestionKeyModel; spacing: 4
                                delegate: Rectangle { width: parent ? parent.width : 0; height: 36; color: suggestionColor; radius: 3
                                    MouseArea { anchors.fill: parent; onClicked: root.callController(function(c) { c.openSuggestionSearch("key", index) }) }
                                    Text { anchors.fill: parent; anchors.margins: 7; text: duplicationValue + " : " + duplicationCount; color: "#ffffff"; font.family: "Consolas"; font.pixelSize: 12; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter }
                                }
                            }
                            ListView { Layout.fillWidth: true; Layout.fillHeight: true; clip: true; model: appState.suggestionValueModel; spacing: 4
                                delegate: Rectangle { width: parent ? parent.width : 0; height: 36; color: suggestionColor; radius: 3
                                    MouseArea { anchors.fill: parent; onClicked: root.callController(function(c) { c.openSuggestionSearch("value", index) }) }
                                    Text { anchors.fill: parent; anchors.margins: 7; text: duplicationValue + " : " + duplicationCount; color: "#ffffff"; font.family: "Consolas"; font.pixelSize: 12; elide: Text.ElideRight; verticalAlignment: Text.AlignVCenter }
                                }
                            }
                        }

                        ColumnLayout { spacing: 8
                            RowLayout {
                                Layout.fillWidth: true
                                PanelTitle { text: "VISUALS EDITOR"; Layout.fillWidth: true }
                                Text { text: appState.activeVisualCount + " active"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                            }
                            DarkCombo { Layout.fillWidth: true; model: appState.visualEditorCategoryOptions; currentIndex: root.visualEditorOptionIndex(appState.visualEditorCategoryOptions, appState.visualEditorCategory); onActivated: { var option = appState.visualEditorCategoryOptions[index]; if (optionEnabled(option)) root.callController(function(c) { c.setVisualEditorCategory(optionValue(option)) }) } }
                            MutedLabel { Layout.fillWidth: true; text: appState.visualEditorStatus }
                            ListView { id: visualControlList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 6; model: appState.visualEditorControlModel
                                delegate: Rectangle { width: visualControlList.width; height: 78; color: root.editorBackground; border.color: root.borderColor; radius: 3
                                    RowLayout { anchors.fill: parent; anchors.margins: 7; spacing: 8
                                        ColumnLayout { Layout.fillWidth: true; spacing: 4
                                            Text { Layout.fillWidth: true; text: label; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; font.bold: true; elide: Text.ElideRight }
                                            Text { Layout.fillWidth: true; text: (visualTypeGroup.length > 0 ? visualTypeGroup + " - " : "") + valueType + (matchingCount > 0 ? " - " + matchingCount + " matching" : ""); color: root.mutedText; font.family: "Consolas"; font.pixelSize: 10; elide: Text.ElideRight }
                                            Field { id: visualValue; Layout.fillWidth: true; placeholderText: control === "color" ? "#3B82F6" : control === "boolean" ? "true" : "Value" }
                                        }
                                        ChromeButton { text: "Apply"; enabled: appState.activeVisualCount > 0; onClicked: root.callController(function(c) { c.applyVisualEditorChange(model.id, visualValue.text) }) }
                                    }
                                }
                            }
                            MutedLabel { visible: appState.visualEditorControlCount === 0; Layout.fillWidth: true; text: "No controls for the active visual scope." }
                        }


                        ColumnLayout { spacing: 8
                            RowLayout {
                                Layout.fillWidth: true
                                PanelTitle { text: "HISTORY"; Layout.fillWidth: true }
                                Text { text: appState.historyCount + " row(s)"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                            }
                            MutedLabel { Layout.fillWidth: true; text: appState.historyCurrentIndex >= 0 ? "Current row " + appState.historyCurrentIndex : "No history yet." }
                            ListView { id: historyList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 5; model: appState.historyModel
                                delegate: Rectangle {
                                    width: historyList.width
                                    height: 64
                                    radius: 3
                                    color: rowState === "current" ? "#0e7490" : rowState === "previous" ? "#1f5f46" : "#6b2d35"
                                    border.color: historyMouse.containsMouse && rowState !== "current" ? "#ffffff" : root.borderColor
                                    opacity: reversible ? 1.0 : 0.65
                                    MouseArea { id: historyMouse; anchors.fill: parent; hoverEnabled: true; enabled: rowState !== "current"; onClicked: root.callController(function(c) { c.goToHistoryIndex(historyIndex) }) }
                                    ColumnLayout { anchors.fill: parent; anchors.margins: 7; spacing: 3
                                        Text { Layout.fillWidth: true; text: "[ " + historyIndex + " ] [ " + timeText + " ] [ " + operationType + " ]"; color: "#ffffff"; font.family: "Consolas"; font.pixelSize: 10; elide: Text.ElideRight }
                                        Text { Layout.fillWidth: true; text: displayName + (metadataText.length > 0 ? " ( " + metadataText + " )" : ""); color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 12; font.bold: rowState === "current"; elide: Text.ElideRight }
                                    }
                                }
                            }
                            MutedLabel { visible: appState.historyCount === 0; Layout.fillWidth: true; text: "No operations recorded." }
                        }
                        ColumnLayout { spacing: 8
                            RowLayout {
                                Layout.fillWidth: true
                                PanelTitle { text: "MACROS"; Layout.fillWidth: true }
                                Text { text: appState.macroCount + " macro(s)"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 11 }
                            }
                            RowLayout { Layout.fillWidth: true; spacing: 6
                                ChromeButton { Layout.fillWidth: true; text: "Import"; onClicked: root.callController(function(c) { c.importMacro() }) }
                                ChromeButton { Layout.fillWidth: true; text: "Reload"; onClicked: root.callController(function(c) { c.reloadContent() }) }
                            }
                            ListView { id: macroList; Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 6; model: appState.macroModel
                                delegate: Rectangle { width: macroList.width; height: 86; color: macroMouse.containsMouse ? root.listHover : root.editorBackground; border.color: validationText.length > 0 ? root.warningColor : root.borderColor; radius: 4
                                    MouseArea { id: macroMouse; anchors.fill: parent; hoverEnabled: true; acceptedButtons: Qt.NoButton }
                                    ColumnLayout { anchors.fill: parent; anchors.margins: 7; spacing: 4
                                        RowLayout {
                                            Layout.fillWidth: true
                                            Text { Layout.fillWidth: true; text: name; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 12; font.bold: true; elide: Text.ElideRight }
                                            Text { text: stepCount + " step(s)"; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 10 }
                                        }
                                        Text { Layout.fillWidth: true; text: statusText; color: validationText.length > 0 ? root.warningColor : root.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideRight }
                                        RowLayout { Layout.fillWidth: true; spacing: 6
                                            ChromeButton { text: running ? "Running" : "Run"; enabled: canRun; onClicked: root.callController(function(c) { c.runMacro(index) }) }
                                            ChromeButton { text: "Export"; onClicked: root.callController(function(c) { c.exportMacro(index) }) }
                                            Item { Layout.fillWidth: true }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: root.editorBackground
                    ColumnLayout { anchors.fill: parent; spacing: 0
                        Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 52; color: root.headerBackground; border.color: root.borderColor
                            RowLayout { anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12; spacing: 10
                                ColumnLayout { Layout.fillWidth: true; spacing: 1
                                    Text { Layout.fillWidth: true; text: appState.currentName; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 14; font.bold: true; elide: Text.ElideMiddle }
                                    Text { Layout.fillWidth: true; text: appState.currentFileType + " - " + appState.currentRelativePath; color: root.mutedText; font.family: "Segoe UI"; font.pixelSize: 10; elide: Text.ElideMiddle }
                                }
                                Text { text: appState.currentDirty ? "dirty" : "clean"; color: appState.currentDirty ? root.warningColor : root.mutedText; font.family: "Segoe UI"; font.pixelSize: 12 }
                                Text { text: appState.currentValidJson ? "Valid JSON" : appState.currentJsonError; color: appState.currentValidJson ? root.okColor : root.warningColor; font.family: "Segoe UI"; font.pixelSize: 11; Layout.maximumWidth: 280; elide: Text.ElideRight }
                                IconButton { text: "F"; enabled: appState.currentIndex >= 0; ToolTip.visible: hovered; ToolTip.text: "Format"; onClicked: root.callController(function(c) { c.formatCurrentJson() }) }
                                IconButton { text: "S"; enabled: appState.currentIndex >= 0 && appState.currentDirty; ToolTip.visible: hovered; ToolTip.text: "Save"; onClicked: root.callController(function(c) { c.saveFile(appState.currentIndex) }) }
                            }
                        }
                        Rectangle { visible: appState.currentIndex < 0; Layout.fillWidth: true; Layout.fillHeight: true; color: root.editorBackground
                            ColumnLayout { anchors.centerIn: parent; width: Math.min(parent.width - 64, 420); spacing: 8
                                Text { Layout.fillWidth: true; text: appState.hasActiveFilter ? "No visible file selected" : "No file selected"; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 20; font.bold: true; horizontalAlignment: Text.AlignHCenter }
                                MutedLabel { Layout.fillWidth: true; text: appState.hasActiveFilter ? "No loaded document matches the active filter." : "Select a page or visual from the project tree."; horizontalAlignment: Text.AlignHCenter }
                            }
                        }
                        ScrollView { visible: appState.currentIndex >= 0; Layout.fillWidth: true; Layout.fillHeight: true; clip: true
                            TextArea { id: editorArea; visible: appState.searchText.length === 0; text: appState.currentText; textFormat: TextEdit.PlainText; wrapMode: TextEdit.NoWrap; selectByMouse: true; persistentSelection: true; color: root.textColor; selectedTextColor: "#ffffff"; selectionColor: "#264f78"; font.family: "Consolas"; font.pixelSize: 14; leftPadding: 14; topPadding: 12; rightPadding: 14; bottomPadding: 12; background: Rectangle { color: root.editorBackground }
                                onTextChanged: if (visible && activeFocus && text !== appState.currentText) root.callController(function(c) { c.updateFileText(appState.currentIndex, text) })
                                Component.onCompleted: syntaxBridge.attach(textDocument)
                            }
                            TextEdit { visible: appState.searchText.length > 0; readOnly: true; selectByMouse: true; textFormat: TextEdit.RichText; text: appState.currentHighlightedHtml; wrapMode: TextEdit.NoWrap; color: root.textColor; selectedTextColor: "#ffffff"; selectionColor: "#264f78"; font.family: "Consolas"; font.pixelSize: 14; leftPadding: 14; topPadding: 12; rightPadding: 14; bottomPadding: 12 }
                        }
                        Rectangle { Layout.fillWidth: true; Layout.preferredHeight: 24; color: root.statusBackground
                            RowLayout { anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 10; spacing: 12
                                Text { text: appState.statusMessage; color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 11; Layout.fillWidth: true; elide: Text.ElideRight }
                                Text { text: appState.activeFileCount + "/" + appState.fileCount + " active"; color: "#ffffff"; font.family: "Segoe UI"; font.pixelSize: 11 }
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
                Text { Layout.fillWidth: true; text: appState.folderScanCount + " Power BI JSON file(s) found"; color: appState.folderScanCount > 0 ? root.okColor : root.warningColor; font.family: "Segoe UI"; font.pixelSize: 13 }
                Rectangle { Layout.fillWidth: true; Layout.fillHeight: true; color: root.editorBackground; border.color: root.borderColor
                    ListView { id: folderTree; anchors.fill: parent; anchors.margins: 8; clip: true; spacing: 1; model: appState.folderScanModel
                        delegate: Rectangle { width: folderTree.width; height: 42; color: folderMouse.containsMouse ? root.listHover : "transparent"
                            MouseArea { id: folderMouse; anchors.fill: parent; hoverEnabled: true }
                            RowLayout { anchors.fill: parent; anchors.leftMargin: 8 + depth * 16; anchors.rightMargin: 8; spacing: 8
                                Text { text: displayName; color: root.textColor; font.family: "Segoe UI"; font.pixelSize: 13; Layout.fillWidth: true; elide: Text.ElideMiddle }
                                Text { text: fileType; color: root.okColor; font.family: "Segoe UI"; font.pixelSize: 11 }
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
        Rectangle { width: Math.min(parent.width - 80, 860); height: Math.min(parent.height - 80, 660); anchors.centerIn: parent; color: root.panelBackground; border.color: root.borderColor; radius: 4
            ColumnLayout { anchors.fill: parent; anchors.margins: 16; spacing: 12
                RowLayout {
                    Layout.fillWidth: true
                    PanelTitle { text: "FILTER EDITOR"; Layout.fillWidth: true }
                    IconButton { text: "x"; contentColor: root.accentRed; onClicked: root.callController(function(c) { c.cancelFilterEditor() }) }
                }
                RowLayout { Layout.fillWidth: true; spacing: 10
                    Field { Layout.fillWidth: true; placeholderText: "Filter name"; text: appState.editingFilterName; onTextEdited: root.callController(function(c) { c.editingFilterName = text }) }
                    DarkCombo { Layout.preferredWidth: 130; model: root.filterTargetOptions; currentIndex: Math.max(0, root.filterTargetOptions.indexOf(appState.editingFilterTarget)); onActivated: root.callController(function(c) { c.editingFilterTarget = currentText }) }
                    Rectangle { Layout.preferredWidth: 32; Layout.preferredHeight: 32; radius: 3; color: appState.editingFilterColor.length > 0 ? appState.editingFilterColor : root.accentBlue; border.color: root.borderColor }
                    Text { text: appState.editingFilterColor; color: root.mutedText; font.family: "Consolas"; font.pixelSize: 12; Layout.preferredWidth: 76; elide: Text.ElideRight }
                    IconButton { text: "R"; ToolTip.visible: hovered; ToolTip.text: "Random color"; onClicked: root.callController(function(c) { c.randomizeEditingFilterColor() }) }
                }
                RowLayout {
                    Layout.fillWidth: true
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

    Popup {
        id: startAgainDialog
        modal: true
        focus: true
        width: Math.min(root.width - 80, 420)
        height: 170
        anchors.centerIn: parent
        background: Rectangle { color: root.panelBackground; border.color: root.borderColor; radius: 4 }
        ColumnLayout { anchors.fill: parent; anchors.margins: 16; spacing: 12
            PanelTitle { text: "START AGAIN" }
            MutedLabel { Layout.fillWidth: true; text: "Unsaved changes will remain only in memory until this session is cleared." }
            Item { Layout.fillHeight: true }
            RowLayout { Layout.fillWidth: true; spacing: 10
                Item { Layout.fillWidth: true }
                ChromeButton { text: "Cancel"; normalColor: "#3c3c3c"; hoverColor: "#4a4a4a"; onClicked: startAgainDialog.close() }
                ChromeButton { text: "Clear"; normalColor: root.accentRed; hoverColor: "#d65252"; onClicked: { startAgainDialog.close(); root.callController(function(c) { c.startAgain() }) } }
            }
        }
    }
}

