.pragma library

function clamp(value, minimum, maximum) {
    return Math.max(minimum, Math.min(maximum, value))
}

function normalizeHex(value, fallback) {
    const text = String(value || "").trim()
    if (/^#[0-9a-fA-F]{6}$/.test(text)) return text.toUpperCase()
    if (/^[0-9a-fA-F]{6}$/.test(text)) return ("#" + text).toUpperCase()
    return fallback || "#FFFFFF"
}

function hexToRgb(hex) {
    const value = normalizeHex(hex, "#FFFFFF").slice(1)
    return [parseInt(value.slice(0, 2), 16), parseInt(value.slice(2, 4), 16), parseInt(value.slice(4, 6), 16)]
}

function rgbToHex(red, green, blue) {
    const channels = [red, green, blue].map(function(value) {
        return Math.round(clamp(Number(value) || 0, 0, 255)).toString(16).padStart(2, "0")
    })
    return ("#" + channels.join("")).toUpperCase()
}

function rgbToHsv(red, green, blue) {
    const r = clamp(Number(red) || 0, 0, 255) / 255
    const g = clamp(Number(green) || 0, 0, 255) / 255
    const b = clamp(Number(blue) || 0, 0, 255) / 255
    const maximum = Math.max(r, g, b)
    const minimum = Math.min(r, g, b)
    const delta = maximum - minimum
    let hue = 0
    if (delta !== 0) {
        if (maximum === r) hue = 60 * (((g - b) / delta) % 6)
        else if (maximum === g) hue = 60 * ((b - r) / delta + 2)
        else hue = 60 * ((r - g) / delta + 4)
    }
    if (hue < 0) hue += 360
    return { hue: hue, saturation: maximum === 0 ? 0 : delta / maximum, value: maximum }
}

function hsvToRgb(hue, saturation, value) {
    const h = ((Number(hue) || 0) % 360 + 360) % 360
    const s = clamp(Number(saturation) || 0, 0, 1)
    const v = clamp(Number(value) || 0, 0, 1)
    const chroma = v * s
    const segment = h / 60
    const x = chroma * (1 - Math.abs(segment % 2 - 1))
    let red = 0
    let green = 0
    let blue = 0
    if (segment < 1) { red = chroma; green = x }
    else if (segment < 2) { red = x; green = chroma }
    else if (segment < 3) { green = chroma; blue = x }
    else if (segment < 4) { green = x; blue = chroma }
    else if (segment < 5) { red = x; blue = chroma }
    else { red = chroma; blue = x }
    const match = v - chroma
    return [Math.round((red + match) * 255), Math.round((green + match) * 255), Math.round((blue + match) * 255)]
}

function hsvToHex(hue, saturation, value) {
    const rgb = hsvToRgb(hue, saturation, value)
    return rgbToHex(rgb[0], rgb[1], rgb[2])
}
