// ============================================================
//  Velora SDDM Login Screen
//  Forest Green theme, iOS 26 glass card style
// ============================================================

import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtGraphicalEffects 1.15
import SddmComponents 2.0

Rectangle {
    id: root
    width: Screen.width
    height: Screen.height
    color: "#0a1510"

    // ── Background ──────────────────────────────────────────
    Image {
        id: bg
        anchors.fill: parent
        source: "background.jpg"
        fillMode: Image.PreserveAspectCrop
        visible: status === Image.Ready
    }

    // Dark overlay
    Rectangle {
        anchors.fill: parent
        color: "#0a1510"
        opacity: bg.visible ? 0.65 : 1.0
    }

    // ── Subtle grid overlay ──────────────────────────────────
    Canvas {
        anchors.fill: parent
        opacity: 0.04
        onPaint: {
            var ctx = getContext("2d")
            ctx.strokeStyle = "#89C17D"
            ctx.lineWidth = 1
            for (var x = 0; x < width; x += 80) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, height); ctx.stroke()
            }
            for (var y = 0; y < height; y += 80) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(width, y); ctx.stroke()
            }
        }
    }

    // ── Center login card ────────────────────────────────────
    Rectangle {
        id: card
        anchors.centerIn: parent
        width: 400
        height: 480
        radius: 24
        color: Qt.rgba(0.059, 0.122, 0.090, 0.85)
        border.color: Qt.rgba(0.373, 0.620, 0.431, 0.20)
        border.width: 1

        layer.enabled: true
        layer.effect: DropShadow {
            transparentBorder: true
            horizontalOffset: 0
            verticalOffset: 8
            radius: 32
            samples: 33
            color: Qt.rgba(0, 0, 0, 0.5)
        }

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 40
            spacing: 0

            // Logo
            Image {
                Layout.alignment: Qt.AlignHCenter
                source: "logo.png"
                width: 64
                height: 64
                fillMode: Image.PreserveAspectFit
                Layout.bottomMargin: 8
            }

            // Title
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Velora Linux"
                font.pixelSize: 24
                font.bold: true
                color: "#D2EBD8"
                Layout.bottomMargin: 4
            }

            // Subtitle
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Welcome back"
                font.pixelSize: 13
                color: "#7A9E87"
                Layout.bottomMargin: 32
            }

            // Avatar circle
            Rectangle {
                Layout.alignment: Qt.AlignHCenter
                width: 72
                height: 72
                radius: 36
                color: Qt.rgba(0.184, 0.420, 0.322, 0.6)
                border.color: Qt.rgba(0.373, 0.620, 0.431, 0.4)
                border.width: 2
                Layout.bottomMargin: 16

                Text {
                    anchors.centerIn: parent
                    text: userModel.data(userModel.index(userList.currentIndex, 0),
                                         Qt.UserRole + 3).toString().substring(0, 1).toUpperCase()
                    font.pixelSize: 28
                    font.bold: true
                    color: "#89C17D"
                }
            }

            // Username
            Text {
                id: username_lbl
                Layout.alignment: Qt.AlignHCenter
                text: userModel.data(userModel.index(userList.currentIndex, 0), Qt.UserRole + 3)
                font.pixelSize: 15
                font.bold: true
                color: "#D2EBD8"
                Layout.bottomMargin: 20
            }

            // Password field
            Rectangle {
                Layout.fillWidth: true
                height: 48
                radius: 14
                color: Qt.rgba(1, 1, 1, 0.07)
                border.color: passwordField.activeFocus
                              ? Qt.rgba(0.373, 0.620, 0.431, 0.8)
                              : Qt.rgba(0.373, 0.620, 0.431, 0.25)
                border.width: 1
                Layout.bottomMargin: 16

                TextInput {
                    id: passwordField
                    anchors.fill: parent
                    anchors.margins: 16
                    echoMode: TextInput.Password
                    color: "#D2EBD8"
                    font.pixelSize: 14
                    verticalAlignment: TextInput.AlignVCenter
                    focus: true

                    Text {
                        anchors.fill: parent
                        text: "Password"
                        color: "#4a7a60"
                        font.pixelSize: 14
                        verticalAlignment: Text.AlignVCenter
                        visible: !passwordField.text && !passwordField.activeFocus
                    }

                    Keys.onReturnPressed: loginButton.clicked()
                    Keys.onEnterPressed:  loginButton.clicked()
                }
            }

            // Error message
            Text {
                id: errorMsg
                Layout.alignment: Qt.AlignHCenter
                text: ""
                color: "#DC5050"
                font.pixelSize: 12
                Layout.bottomMargin: 8
                visible: text !== ""
            }

            // Login button
            Rectangle {
                id: loginButton
                Layout.fillWidth: true
                height: 48
                radius: 14
                color: loginMouseArea.pressed
                       ? "#1e4d3a"
                       : loginMouseArea.containsMouse ? "#5F9E6E" : "#2F6B52"

                Behavior on color { ColorAnimation { duration: 150 } }

                Text {
                    anchors.centerIn: parent
                    text: "Sign In"
                    color: "#ffffff"
                    font.pixelSize: 14
                    font.bold: true
                }

                MouseArea {
                    id: loginMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        if (passwordField.text === "") {
                            errorMsg.text = "Please enter your password."
                            return
                        }
                        errorMsg.text = ""
                        sddm.login(
                            userModel.data(userModel.index(userList.currentIndex, 0), Qt.UserRole + 3),
                            passwordField.text,
                            sessionIndex
                        )
                    }
                }
            }
        }
    }

    // ── Hidden user list (needed by SDDM) ────────────────────
    ListView {
        id: userList
        model: userModel
        visible: false
        currentIndex: userModel.lastIndex
    }

    // ── Session index ────────────────────────────────────────
    property int sessionIndex: sessionModel.lastIndex

    // ── Login failed handler ─────────────────────────────────
    Connections {
        target: sddm
        function onLoginFailed() {
            errorMsg.text = "Wrong password. Try again."
            passwordField.text = ""
            passwordField.forceActiveFocus()
        }
    }

    // ── Clock bottom-right ───────────────────────────────────
    Column {
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.margins: 32
        spacing: 4

        Text {
            id: clockTime
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatTime(new Date(), "HH:mm")
            font.pixelSize: 28
            font.bold: true
            color: "#D2EBD8"
        }

        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            text: Qt.formatDate(new Date(), "dddd, MMMM d")
            font.pixelSize: 13
            color: "#7A9E87"
        }

        Timer {
            interval: 1000
            running: true
            repeat: true
            onTriggered: clockTime.text = Qt.formatTime(new Date(), "HH:mm")
        }
    }

    // ── Power buttons bottom-left ────────────────────────────
    Row {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.margins: 32
        spacing: 12

        Repeater {
            model: [
                { "icon": "⏻", "action": "shutdown" },
                { "icon": "↺", "action": "reboot"   },
            ]
            delegate: Rectangle {
                width: 44
                height: 44
                radius: 12
                color: pma.containsMouse
                       ? Qt.rgba(0.184, 0.420, 0.322, 0.5)
                       : Qt.rgba(0.059, 0.122, 0.090, 0.6)
                border.color: Qt.rgba(0.373, 0.620, 0.431, 0.2)
                border.width: 1

                Text {
                    anchors.centerIn: parent
                    text: modelData.icon
                    font.pixelSize: 18
                    color: "#7A9E87"
                }

                MouseArea {
                    id: pma
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        if (modelData.action === "shutdown") sddm.powerOff()
                        else sddm.reboot()
                    }
                }
            }
        }
    }
}
