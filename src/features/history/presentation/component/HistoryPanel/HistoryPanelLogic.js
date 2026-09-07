.pragma library

function enabled(value) { return Boolean(value) }

function isReady(value) {
    return value !== null && value !== undefined
}
