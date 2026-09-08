import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property bool enabled: true
    readonly property int panelSpacing: Spacing.sm
    readonly property color cardBackground: Theme.cardBackground
    readonly property color cardHover: Theme.cardHover
    // These are stable palette tokens so the panel also works with older
    // cached theme modules during a hot reload.
    readonly property color added: Theme.okColor
    readonly property color removed: Theme.accentRed
}
