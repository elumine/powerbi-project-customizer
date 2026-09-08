.pragma library

function isReady(value) {
    return value !== null && value !== undefined
}

function lineValue(line, key, fallback) {
    if (!line) return fallback
    const value = line[key]
    return value === undefined || value === null ? fallback : value
}
