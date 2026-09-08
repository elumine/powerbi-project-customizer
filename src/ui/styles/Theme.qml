pragma Singleton
import QtQml
import QtQuick

// Dashboard palette. Keep all user-facing color decisions here.
QtObject {
    readonly property color appBackground: "#101214"
    readonly property color activityBackground: "#171a1d"
    readonly property color panelBackground: "#1c2023"
    readonly property color editorBackground: "#171a1d"
    readonly property color headerBackground: "#171a1d"
    readonly property color statusBackground: "#141619"
    readonly property color cardBackground: "#202427"
    readonly property color cardRaised: "#292d31"
    readonly property color cardHover: "#2b3034"
    readonly property color listHover: "#2b3034"
    readonly property color listActive: "#343a3f"
    readonly property color controlBackground: "#24282c"
    readonly property color controlHover: "#30353a"
    readonly property color inputBackground: "#15191c"
    readonly property color inputFocus: "#242a2f"
    readonly property color borderColor: "#363b40"
    readonly property color borderSubtle: "#2b2f33"
    readonly property color textColor: "#eeeeee"
    readonly property color mutedText: "#b4b7ba"
    readonly property color dimText: "#85898d"
    readonly property color diffContextText: "#888888"
    readonly property color accentBlue: "#ff5358"
    readonly property color accentBlueHover: "#ff6b70"
    readonly property color accentBluePressed: "#e64349"
    // Semantic action colors: blue executes, green commits/imports, red clears.
    readonly property color actionExecute: "#3B82F6"
    readonly property color actionExecuteHover: "#60A5FA"
    readonly property color actionExecutePressed: "#2563EB"
    readonly property color actionSave: "#35B779"
    readonly property color actionSaveHover: "#4CC98D"
    readonly property color actionSavePressed: "#25885A"
    readonly property color actionCancel: "#E05252"
    readonly property color actionCancelHover: "#F06A6A"
    readonly property color actionCancelPressed: "#B9363E"
    readonly property color neutralAction: "#30363D"
    readonly property color neutralActionHover: "#3A424B"
    readonly property color neutralActionPressed: "#252B31"
    readonly property color accentGreen: "#f7b733"
    readonly property color accentGreenHover: "#ffc64d"
    readonly property color accentGreenPressed: "#dc9d1f"
    readonly property color accentRed: "#ff5358"
    readonly property color accentRedHover: "#ff6b70"
    readonly property color accentRedPressed: "#d94147"
    readonly property color warningColor: "#ffb52b"
    readonly property color okColor: "#54d39a"
    readonly property color selectionColor: "#4a4f54"
    readonly property color scrimColor: "#090a0b"
    readonly property color white: "#ffffff"
    readonly property color black: "#0a0b0c"

    // Data-driven filter colors are deliberately separate from the shell palette.
    readonly property color filterTeal: "#42c6b4"
    readonly property color filterLavender: "#a78bfa"
    readonly property color filterAmber: "#f7b733"
    readonly property color filterCoral: "#ff7b72"
    readonly property color filterSky: "#52b6ff"
    readonly property color filterPeach: "#ff8f66"
    readonly property color filterMint: "#59d2b6"
    readonly property color filterViolet: "#b99aff"

    // Visual editor type accents.
    readonly property color visualTable: "#59d2b6"
    readonly property color visualChart: "#ffba3b"
    readonly property color visualLine: "#6ea8fe"
    readonly property color visualPie: "#ba8cff"
    readonly property color visualSlicer: "#ff8f66"
    readonly property color visualOther: "#b4b7ba"

    // Input-control accents inside the visual editor.
    readonly property color controlText: "#8fc5ff"
    readonly property color controlNumber: "#ffca6a"
    readonly property color controlOpacity: "#b99aff"
    readonly property color controlColor: "#59d2b6"
    readonly property color controlBoolean: "#ff8f99"

    // History states use stable, legible dashboard accents.
    readonly property color historyCurrent: "#1d8f9d"
    readonly property color historyPrevious: "#2b8b66"
    readonly property color historyFuture: "#a64f61"

    function visualTypeColor(visualType) {
        const value = String(visualType || "").toLowerCase()
        if (value.indexOf("table") >= 0 || value.indexOf("matrix") >= 0) return visualTable
        if (value.indexOf("line") >= 0) return visualLine
        if (value.indexOf("pie") >= 0 || value.indexOf("donut") >= 0) return visualPie
        if (value.indexOf("slicer") >= 0) return visualSlicer
        if (value.indexOf("bar") >= 0 || value.indexOf("column") >= 0 || value.indexOf("chart") >= 0) return visualChart
        return visualOther
    }

    function controlTypeColor(control, valueType) {
        const type = String(control || "").toLowerCase()
        const value = String(valueType || "").toLowerCase()
        if (type === "color" || value.indexOf("color") >= 0) return controlColor
        if (type === "boolean" || value === "boolean") return controlBoolean
        if (type === "slider" || value === "percentage" || value.indexOf("opacity") >= 0) return controlOpacity
        if (type === "number" || value.indexOf("number") >= 0 || value === "integer") return controlNumber
        return controlText
    }

    function safeColor(value, fallback) {
        const text = String(value || "").trim()
        return /^#[0-9a-fA-F]{6}$/.test(text) ? text : fallback
    }

    function contrastText(value) {
        const color = safeColor(value, filterSky).slice(1)
        const red = parseInt(color.slice(0, 2), 16)
        const green = parseInt(color.slice(2, 4), 16)
        const blue = parseInt(color.slice(4, 6), 16)
        const luminance = (red * 0.299 + green * 0.587 + blue * 0.114) / 255
        return luminance > 0.57 ? black : white
    }
}
