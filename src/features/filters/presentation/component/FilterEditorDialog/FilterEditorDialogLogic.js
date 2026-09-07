.pragma library

function isVisible(value) { return Boolean(value) }

function isReady(value) {
    return value !== null && value !== undefined
}
