.pragma library

function coalesce(value, fallback) {
    return value === undefined || value === null ? fallback : value
}
