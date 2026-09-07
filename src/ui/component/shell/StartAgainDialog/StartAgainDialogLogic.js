.pragma library

function shouldConfirm(hasDirtyFiles) { return Boolean(hasDirtyFiles) }

function isReady(value) {
    return value !== null && value !== undefined
}
