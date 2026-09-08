pragma Singleton
import QtQml

QtObject {
    readonly property string uiFamily: "Segoe UI Variable"
    readonly property string uiFallbackFamily: "Segoe UI"
    readonly property string dataFamily: "Cascadia Mono"
    readonly property string dataFallbackFamily: "Consolas"
    // The interface is intentionally readable at compact desktop widths.
    // Every shared size is two pixels larger than the original scale, with a
    // hard minimum of 12px for any user-facing text.
    readonly property int microSize: 12
    readonly property int captionSize: 13
    readonly property int bodySize: 14
    readonly property int labelSize: 15
    readonly property int sectionSize: 17
    readonly property int titleSize: 24
    readonly property int heroSize: 32
}
