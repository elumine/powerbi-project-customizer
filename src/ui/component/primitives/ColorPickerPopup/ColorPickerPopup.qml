import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ui.component.primitives 1.0
import ui.styles 1.0
import "ColorPickerPopupLogic.js" as Logic

Popup {
    id: popup
    ColorPickerPopupStyle { id: style }

    property string selectedColor: String(Theme.white)
    property real hue: 0
    property real saturation: 0
    property real value: 1
    property string hexText: selectedColor
    signal colorSelected(string color)

    modal: true
    focus: true
    width: 360
    height: 465
    padding: Spacing.md
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
    parent: Overlay.overlay

    function openFor(color) {
        const normalized = Logic.normalizeHex(color, String(Theme.white))
        selectedColor = normalized
        setFromHex(normalized)
        centerInOverlay()
        open()
    }

    function centerInOverlay() {
        if (!Overlay.overlay) return
        x = Math.max(Spacing.sm, (Overlay.overlay.width - width) / 2)
        y = Math.max(Spacing.sm, (Overlay.overlay.height - height) / 2)
    }

    onOpened: centerInOverlay()

    function setFromHex(color) {
        const rgb = Logic.hexToRgb(color)
        const hsv = Logic.rgbToHsv(rgb[0], rgb[1], rgb[2])
        hue = hsv.hue
        saturation = hsv.saturation
        value = hsv.value
        selectedColor = Logic.hsvToHex(hue, saturation, value)
        hexText = selectedColor
        redField.text = String(rgb[0])
        greenField.text = String(rgb[1])
        blueField.text = String(rgb[2])
    }

    function updateFromHsv() {
        selectedColor = Logic.hsvToHex(hue, saturation, value)
        hexText = selectedColor
        const rgb = Logic.hsvToRgb(hue, saturation, value)
        redField.text = String(rgb[0])
        greenField.text = String(rgb[1])
        blueField.text = String(rgb[2])
    }

    function updateFromRgb() {
        const red = Logic.clamp(Number(redField.text) || 0, 0, 255)
        const green = Logic.clamp(Number(greenField.text) || 0, 0, 255)
        const blue = Logic.clamp(Number(blueField.text) || 0, 0, 255)
        const hsv = Logic.rgbToHsv(red, green, blue)
        hue = hsv.hue
        saturation = hsv.saturation
        value = hsv.value
        selectedColor = Logic.rgbToHex(red, green, blue)
        hexText = selectedColor
    }

    function updateFromHex() {
        const normalized = Logic.normalizeHex(hexText, selectedColor)
        setFromHex(normalized)
    }

    background: Rectangle {
        color: style.background
        border.width: Geometry.borderWidth
        border.color: style.border
        radius: Geometry.radiusMd
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: Spacing.sm

        RowLayout {
            Layout.fillWidth: true
            Text {
                Layout.fillWidth: true
                text: "Choose color"
                color: Theme.textColor
                font.family: Typography.uiFamily
                font.pixelSize: Typography.sectionSize
                font.weight: Font.DemiBold
            }
            Rectangle {
                Layout.preferredWidth: 28
                Layout.preferredHeight: 28
                radius: width / 2
                color: selectedColor
                border.width: Geometry.borderWidth
                border.color: Theme.white
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Spacing.sm

            Rectangle {
                id: saturationValueArea
                Layout.preferredWidth: style.pickerSize
                Layout.preferredHeight: style.pickerSize
                color: Logic.hsvToHex(popup.hue, 1, 1)
                border.width: Geometry.borderWidth
                border.color: style.border

                Rectangle {
                    anchors.fill: parent
                    gradient: Gradient {
                        GradientStop { position: 0; color: Theme.white }
                        GradientStop { position: 1; color: Qt.rgba(1, 1, 1, 0) }
                    }
                }
                Rectangle {
                    anchors.fill: parent
                    gradient: Gradient {
                        GradientStop { position: 0; color: Qt.rgba(0, 0, 0, 0) }
                        GradientStop { position: 1; color: Theme.black }
                    }
                }
                Rectangle {
                    x: Logic.clamp(popup.saturation * parent.width - width / 2, 0, parent.width - width)
                    y: Logic.clamp((1 - popup.value) * parent.height - height / 2, 0, parent.height - height)
                    width: 16
                    height: 16
                    radius: width / 2
                    color: Qt.rgba(0, 0, 0, 0)
                    border.width: 2
                    border.color: Theme.white
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: 3
                        radius: width / 2
                        color: Qt.rgba(0, 0, 0, 0)
                        border.width: 1
                        border.color: Theme.black
                    }
                }
                MouseArea {
                    anchors.fill: parent
                    onPressed: updatePosition(mouse)
                    onPositionChanged: if (pressed) updatePosition(mouse)
                    function updatePosition(mouse) {
                        popup.saturation = Logic.clamp(mouse.x / width, 0, 1)
                        popup.value = Logic.clamp(1 - mouse.y / height, 0, 1)
                        popup.updateFromHsv()
                    }
                }
            }

            Rectangle {
                id: hueArea
                Layout.preferredWidth: 22
                Layout.preferredHeight: style.pickerSize
                border.width: Geometry.borderWidth
                border.color: style.border
                gradient: Gradient {
                    GradientStop { position: 0.00; color: Qt.rgba(1, 0, 0, 1) }
                    GradientStop { position: 0.17; color: Qt.rgba(1, 0, 1, 1) }
                    GradientStop { position: 0.33; color: Qt.rgba(0, 0, 1, 1) }
                    GradientStop { position: 0.50; color: Qt.rgba(0, 1, 1, 1) }
                    GradientStop { position: 0.67; color: Qt.rgba(0, 1, 0, 1) }
                    GradientStop { position: 0.83; color: Qt.rgba(1, 1, 0, 1) }
                    GradientStop { position: 1.00; color: Qt.rgba(1, 0, 0, 1) }
                }
                Rectangle {
                    x: -2
                    y: Logic.clamp((1 - popup.hue / 360) * parent.height - height / 2, -2, parent.height - height + 2)
                    width: parent.width + 4
                    height: 5
                    color: Qt.rgba(0, 0, 0, 0)
                    border.width: 2
                    border.color: Theme.white
                }
                MouseArea {
                    anchors.fill: parent
                    onPressed: updateHue(mouse)
                    onPositionChanged: if (pressed) updateHue(mouse)
                    function updateHue(mouse) {
                        popup.hue = Logic.clamp((1 - mouse.y / height) * 360, 0, 360)
                        popup.updateFromHsv()
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Spacing.xs
            Text { text: "HEX"; color: style.muted; font.family: Typography.uiFamily; font.pixelSize: Typography.captionSize; font.weight: Font.DemiBold }
            Field {
                id: hexField
                Layout.fillWidth: true
                text: popup.hexText
                onTextChanged: popup.hexText = text
                onEditingFinished: popup.updateFromHex()
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Spacing.xs
            Text { text: "RGB"; color: style.muted; font.family: Typography.uiFamily; font.pixelSize: Typography.captionSize; font.weight: Font.DemiBold }
            Field { id: redField; Layout.fillWidth: true; placeholderText: "R"; onEditingFinished: popup.updateFromRgb() }
            Field { id: greenField; Layout.fillWidth: true; placeholderText: "G"; onEditingFinished: popup.updateFromRgb() }
            Field { id: blueField; Layout.fillWidth: true; placeholderText: "B"; onEditingFinished: popup.updateFromRgb() }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Spacing.sm
            Item { Layout.fillWidth: true }
            ChromeButton { text: "Cancel"; actionType: "cancel"; onClicked: popup.close() }
            ChromeButton {
                text: "Apply"
                actionType: "execute"
                onClicked: {
                    popup.colorSelected(Logic.normalizeHex(popup.selectedColor, String(Theme.white)))
                    popup.close()
                }
            }
        }
    }
}
