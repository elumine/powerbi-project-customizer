.pragma library

function recordingAction(running, recording) { return running ? "Stop macro" : recording ? "Stop recording" : "Start recording" }

function isReady(value) {
    return value !== null && value !== undefined
}
