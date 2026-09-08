.pragma library

function panelIndex(panel) {
    const values = ["explorer", "changes", "search", "filters", "suggestions", "visuals", "history", "macros"]
    return Math.max(0, values.indexOf(panel))
}

function panelWidthRatio(panel) {
    if (panel === "search" || panel === "history") return 0.40
    if (panel === "explorer") return 0.30
    if (panel === "changes") return 0.40
    if (panel === "macros") return 0.50
    return 0.50
}

function isReady(value) {
    return value !== null && value !== undefined
}
