.pragma library

function optionIndex(options, value) {
    for (let index = 0; index < options.length; index += 1) {
        const option = options[index]
        const optionValue = typeof option === "object" && option !== null && option.value !== undefined ? option.value : option
        if (optionValue === value) return index
    }
    return 0
}

function isReady(value) {
    return value !== null && value !== undefined
}
