.pragma library

function isReady(value) {
    return value !== null && value !== undefined
}

function displayName(name, relativePath) {
    const shortName = String(name || "Changed file")
    const path = String(relativePath || "")
    return path.length > 0 ? shortName + " · " + path : shortName
}
