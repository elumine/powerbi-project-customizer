import QtQml
import QtQuick
import ui.styles 1.0

QtObject {
    readonly property color activeBackground: Theme.cardRaised
    readonly property color activeBorder: Theme.accentBlue
    readonly property color hoverBackground: Theme.cardHover
    readonly property color idleContent: Theme.dimText
    readonly property color activeContent: Theme.white
    readonly property int indicatorWidth: 3
}
