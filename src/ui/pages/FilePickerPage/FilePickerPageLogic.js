.pragma library

function panelIndex(panel) {
    const values = ["explorer", "search", "filters", "suggestions", "visuals", "history", "macros"]
    return Math.max(0, values.indexOf(panel))
}

function isReady(value) {
    return value !== null && value !== undefined
}
