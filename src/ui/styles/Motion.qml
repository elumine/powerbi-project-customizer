pragma Singleton
import QtQml

QtObject {
    // Enable from a deployment/test command with --reduce-motion, or assign it
    // from an embedding QML profile before components are created.
    property bool reduceMotion: Qt.application.arguments.indexOf("--reduce-motion") >= 0
    readonly property int instant: 0
    readonly property int quick: reduceMotion ? instant : 100
    readonly property int standard: reduceMotion ? instant : 180
    readonly property int relaxed: reduceMotion ? instant : 280
    readonly property int enterDelay: reduceMotion ? instant : 32
    readonly property real hoverScale: reduceMotion ? 1.0 : 1.015
    readonly property real pressScale: reduceMotion ? 1.0 : 0.985
}
