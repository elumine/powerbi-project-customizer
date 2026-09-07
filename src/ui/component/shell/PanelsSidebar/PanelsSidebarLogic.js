.pragma library

function panels() { return ["explorer", "search", "filters", "suggestions", "visuals", "history", "macros"] }

function isReady(value) {
    return value !== null && value !== undefined
}
