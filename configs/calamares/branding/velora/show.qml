/* ============================================================
   Velora Linux - Calamares Slideshow
   Shown during installation
   ============================================================ */

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import calamares.slideshow 1.0

Presentation {
    id: presentation

    function nextSlide() {
        if (presentation.currentSlide < slides.count - 1)
            presentation.currentSlide++
        else
            presentation.currentSlide = 0
    }

    Timer {
        id: timer
        interval: 4000
        running: true
        repeat: true
        onTriggered: nextSlide()
    }

    Slide {
        ColumnLayout {
            anchors.centerIn: parent
            spacing: 20

            Image {
                Layout.alignment: Qt.AlignHCenter
                source: "logo.png"
                width: 80; height: 80
                fillMode: Image.PreserveAspectFit
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Welcome to Velora Linux"
                font.pixelSize: 28; font.bold: true
                color: "#D2EBD8"
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Modern. Natural. Elegant."
                font.pixelSize: 15
                color: "#7A9E87"
            }
        }
    }

    Slide {
        ColumnLayout {
            anchors.centerIn: parent
            spacing: 16
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "🎮"
                font.pixelSize: 56
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Gaming Ready"
                font.pixelSize: 26; font.bold: true
                color: "#D2EBD8"
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Steam, Heroic, Lutris, Wine and Bottles\nare pre-installed and ready to use."
                font.pixelSize: 14
                color: "#7A9E87"
                horizontalAlignment: Text.AlignHCenter
            }
        }
    }

    Slide {
        ColumnLayout {
            anchors.centerIn: parent
            spacing: 16
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "🪟"
                font.pixelSize: 56
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Windows Compatible"
                font.pixelSize: 26; font.bold: true
                color: "#D2EBD8"
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Run your Windows apps with Wine + Bottles.\nNo configuration needed."
                font.pixelSize: 14
                color: "#7A9E87"
                horizontalAlignment: Text.AlignHCenter
            }
        }
    }

    Slide {
        ColumnLayout {
            anchors.centerIn: parent
            spacing: 16
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "🛍️"
                font.pixelSize: 56
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Velora Store"
                font.pixelSize: 26; font.bold: true
                color: "#D2EBD8"
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Install apps in one click.\nFlatpak and APT packages all in one place."
                font.pixelSize: 14
                color: "#7A9E87"
                horizontalAlignment: Text.AlignHCenter
            }
        }
    }

    Slide {
        ColumnLayout {
            anchors.centerIn: parent
            spacing: 16
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "🌲"
                font.pixelSize: 56
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Almost done!"
                font.pixelSize: 26; font.bold: true
                color: "#D2EBD8"
            }
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Your system is being installed.\nThis will only take a few minutes."
                font.pixelSize: 14
                color: "#7A9E87"
                horizontalAlignment: Text.AlignHCenter
            }
        }
    }
}
