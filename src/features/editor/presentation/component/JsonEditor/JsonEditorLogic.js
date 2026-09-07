.pragma library

function lineNumbers(value) {
    const count = Math.max(1, String(value || "").split("\n").length)
    return Array.from({ length: count }, (_, index) => index + 1).join("\n")
}

function lineOffset(value, line) {
    const text = String(value || "")
    const target = Math.max(1, line)
    let current = 1
    for (let index = 0; index < text.length; index += 1) {
        if (current === target) return index
        if (text.charAt(index) === "\n") current += 1
    }
    return text.length
}

function isReady(value) {
    return value !== null && value !== undefined
}
