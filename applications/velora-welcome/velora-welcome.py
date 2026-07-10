#!/usr/bin/env python3
# ============================================================
#  Velora Welcome
#  First-boot setup wizard - Velora Linux
#  Screens: Welcome -> Language -> User -> Apps -> Finish
# ============================================================

import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QFrame, QLineEdit, QCheckBox, QButtonGroup,
    QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QPixmap

# ============================================================
#  COLORS & STYLES
# ============================================================
C_BG        = "#0a1510"
C_CARD      = "rgba(20, 42, 30, 0.82)"
C_PRIMARY   = "#2F6B52"
C_ACCENT    = "#5F9E6E"
C_HIGHLIGHT = "#89C17D"
C_TEXT      = "#D2EBD8"
C_MUTED     = "#7A9E87"
C_DANGER    = "#DC5050"

STYLE_GLOBAL = f"""
QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: 'Inter', 'Segoe UI', sans-serif;
}}
QLineEdit {{
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(95,158,110,0.3);
    border-radius: 12px;
    padding: 12px 16px;
    color: {C_TEXT};
    font-size: 14px;
}}
QLineEdit:focus {{
    border: 1px solid {C_ACCENT};
    background: rgba(255,255,255,0.10);
}}
QCheckBox {{
    color: {C_TEXT};
    font-size: 13px;
    spacing: 10px;
}}
QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border-radius: 6px;
    border: 2px solid rgba(95,158,110,0.4);
    background: rgba(255,255,255,0.05);
}}
QCheckBox::indicator:checked {{
    background: {C_PRIMARY};
    border-color: {C_ACCENT};
}}
QScrollBar:vertical {{
    background: transparent;
    width: 5px;
}}
QScrollBar::handle:vertical {{
    background: {C_PRIMARY};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""

STYLE_BTN_PRIMARY = f"""
QPushButton {{
    background: {C_PRIMARY};
    color: #ffffff;
    border: none;
    border-radius: 14px;
    padding: 14px 36px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton:hover {{ background: {C_ACCENT}; }}
QPushButton:pressed {{ background: #1e4d3a; }}
QPushButton:disabled {{ background: rgba(47,107,82,0.3); color: rgba(255,255,255,0.3); }}
"""

STYLE_BTN_GHOST = f"""
QPushButton {{
    background: transparent;
    color: {C_MUTED};
    border: 1px solid rgba(95,158,110,0.25);
    border-radius: 14px;
    padding: 14px 36px;
    font-size: 14px;
}}
QPushButton:hover {{ color: {C_TEXT}; border-color: {C_ACCENT}; }}
"""

STYLE_LANG_BTN = f"""
QPushButton {{
    background: rgba(20,42,30,0.7);
    color: {C_TEXT};
    border: 1px solid rgba(95,158,110,0.2);
    border-radius: 14px;
    padding: 16px;
    font-size: 14px;
    text-align: left;
}}
QPushButton:hover {{
    background: rgba(47,107,82,0.3);
    border-color: {C_ACCENT};
}}
QPushButton[selected="true"] {{
    background: rgba(47,107,82,0.5);
    border: 2px solid {C_HIGHLIGHT};
    color: {C_HIGHLIGHT};
    font-weight: bold;
}}
"""

# ============================================================
#  WORKER THREAD
# ============================================================

class CommandWorker(QThread):
    output  = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            proc = subprocess.Popen(
                self.command, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            for line in proc.stdout:
                self.output.emit(line.rstrip())
            proc.wait()
            self.finished.emit(proc.returncode == 0)
        except Exception as e:
            self.output.emit(f"Error: {e}")
            self.finished.emit(False)


# ============================================================
#  PAGE 1 - WELCOME
# ============================================================

class PageWelcome(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        logo = QLabel("🌲")
        logo.setFont(QFont("Segoe UI Emoji", 72))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Welcome to Velora Linux")
        title.setFont(QFont("Inter", 34, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {C_TEXT};")

        subtitle = QLabel("Modern. Natural. Elegant.")
        subtitle.setFont(QFont("Inter", 16))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {C_MUTED};")

        desc = QLabel("Let's set up your system.\nThis will only take a few minutes.")
        desc.setFont(QFont("Inter", 13))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet(f"color: {C_MUTED};")

        layout.addStretch()
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addWidget(desc)
        layout.addStretch()
        self.setLayout(layout)


# ============================================================
#  PAGE 2 - LANGUAGE
# ============================================================

class PageLanguage(QWidget):
    def __init__(self):
        super().__init__()
        self.selected = "en_US"

        layout = QVBoxLayout()
        layout.setContentsMargins(80, 40, 80, 20)
        layout.setSpacing(20)

        title = QLabel("Choose your language")
        title.setFont(QFont("Inter", 26, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_TEXT};")

        layout.addWidget(title)

        self.languages = [
            ("🇷🇴", "Română",    "ro_RO"),
            ("🇬🇧", "English",   "en_US"),
            ("🇩🇪", "Deutsch",   "de_DE"),
            ("🇫🇷", "Français",  "fr_FR"),
            ("🇪🇸", "Español",   "es_ES"),
            ("🇮🇹", "Italiano",  "it_IT"),
        ]

        grid = QGridLayout()
        grid.setSpacing(12)
        self.lang_btns = {}

        for i, (flag, name, code) in enumerate(self.languages):
            btn = QPushButton(f"{flag}  {name}")
            btn.setStyleSheet(STYLE_LANG_BTN)
            btn.setFixedHeight(60)
            btn.setProperty("selected", "false")
            btn.clicked.connect(lambda _, c=code: self.select(c))
            self.lang_btns[code] = btn
            grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(grid)
        layout.addStretch()
        self.setLayout(layout)

        # Default select English
        self.select("en_US")

    def select(self, code):
        self.selected = code
        for c, btn in self.lang_btns.items():
            btn.setProperty("selected", "true" if c == code else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def get_language(self):
        return self.selected


# ============================================================
#  PAGE 3 - USER ACCOUNT
# ============================================================

class PageUser(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(80, 40, 80, 20)
        layout.setSpacing(16)

        title = QLabel("Create your account")
        title.setFont(QFont("Inter", 26, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_TEXT};")
        layout.addWidget(title)

        sub = QLabel("This will be your user on Velora Linux.")
        sub.setStyleSheet(f"color: {C_MUTED}; font-size: 13px;")
        layout.addWidget(sub)
        layout.addSpacing(8)

        # Full name
        lbl_name = QLabel("Full Name")
        lbl_name.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Alex Ionescu")
        self.name_input.textChanged.connect(self.auto_username)

        # Username
        lbl_user = QLabel("Username")
        lbl_user.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("e.g. alex")

        # Password
        lbl_pass = QLabel("Password")
        lbl_pass.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("Choose a password")

        # Confirm password
        lbl_pass2 = QLabel("Confirm Password")
        lbl_pass2.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        self.pass2_input = QLineEdit()
        self.pass2_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass2_input.setPlaceholderText("Repeat password")
        self.pass2_input.textChanged.connect(self.check_match)

        self.match_lbl = QLabel("")
        self.match_lbl.setStyleSheet(f"color: {C_DANGER}; font-size: 12px;")

        for w in [lbl_name, self.name_input,
                  lbl_user, self.user_input,
                  lbl_pass, self.pass_input,
                  lbl_pass2, self.pass2_input,
                  self.match_lbl]:
            layout.addWidget(w)

        layout.addStretch()
        self.setLayout(layout)

    def auto_username(self, text):
        username = text.lower().split()[0] if text.strip() else ""
        username = "".join(c for c in username if c.isalnum())
        self.user_input.setText(username)

    def check_match(self):
        p1 = self.pass_input.text()
        p2 = self.pass2_input.text()
        if p2 and p1 != p2:
            self.match_lbl.setText("⚠️ Passwords do not match")
        else:
            self.match_lbl.setText("")

    def is_valid(self):
        return (
            bool(self.name_input.text().strip()) and
            bool(self.user_input.text().strip()) and
            bool(self.pass_input.text()) and
            self.pass_input.text() == self.pass2_input.text()
        )

    def get_data(self):
        return {
            "name":     self.name_input.text().strip(),
            "username": self.user_input.text().strip(),
            "password": self.pass_input.text(),
        }


# ============================================================
#  PAGE 4 - APPLICATIONS
# ============================================================

class PageApps(QWidget):
    def __init__(self):
        super().__init__()

        self.apps = [
            ("💻", "VS Code",    "Visual Studio Code editor",    "code",      True,  False),
            ("🎮", "Steam",      "Gaming platform",              "steam",     True,  False),
            ("🎵", "Spotify",    "Music streaming",              "spotify",   False, False),
            ("💬", "Discord",    "Voice and chat",               "discord",   False, False),
            ("🌐", "Brave",      "Privacy browser",              "brave",     False, False),
            ("🌐", "Chromium",   "Web browser",                  "chromium",  False, False),
            ("🎬", "VLC",        "Media player",                 "vlc",       True,  False),
            ("🍷", "Wine",       "Windows compatibility",        "wine",      True,  True),
        ]

        layout = QVBoxLayout()
        layout.setContentsMargins(80, 30, 80, 20)
        layout.setSpacing(14)

        title = QLabel("Choose applications")
        title.setFont(QFont("Inter", 26, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_TEXT};")
        layout.addWidget(title)

        sub = QLabel("Select what to install. Wine is required and always included.")
        sub.setStyleSheet(f"color: {C_MUTED}; font-size: 13px;")
        layout.addWidget(sub)
        layout.addSpacing(4)

        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)

        inner = QWidget()
        inner_layout = QVBoxLayout()
        inner_layout.setSpacing(10)

        self.checkboxes = {}

        for icon, name, desc, key, default, required in self.apps:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background: rgba(20,42,30,0.7);
                    border-radius: 14px;
                    border: 1px solid rgba(95,158,110,0.15);
                }}
            """)
            card_layout = QHBoxLayout()
            card_layout.setContentsMargins(16, 12, 16, 12)

            cb = QCheckBox()
            cb.setChecked(default)
            if required:
                cb.setEnabled(False)
                cb.setChecked(True)

            icon_lbl = QLabel(icon)
            icon_lbl.setFont(QFont("Segoe UI Emoji", 20))
            icon_lbl.setFixedWidth(36)

            info = QVBoxLayout()
            n = QLabel(name + (" (required)" if required else ""))
            n.setFont(QFont("Inter", 13, QFont.Weight.Bold))
            n.setStyleSheet(f"color: {C_TEXT};")
            d = QLabel(desc)
            d.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
            info.addWidget(n)
            info.addWidget(d)

            card_layout.addWidget(cb)
            card_layout.addWidget(icon_lbl)
            card_layout.addLayout(info)
            card_layout.addStretch()
            card.setLayout(card_layout)
            inner_layout.addWidget(card)
            self.checkboxes[key] = cb

        inner_layout.addStretch()
        inner.setLayout(inner_layout)
        scroll.setWidget(inner)
        layout.addWidget(scroll)
        self.setLayout(layout)

    def get_selected(self):
        return [key for key, cb in self.checkboxes.items() if cb.isChecked()]


# ============================================================
#  PAGE 5 - INSTALLING
# ============================================================

class PageInstalling(QWidget):
    done = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout_ = QVBoxLayout()
        self.layout_.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_.setSpacing(20)

        self.icon = QLabel("⚙️")
        self.icon.setFont(QFont("Segoe UI Emoji", 48))
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel("Setting up your system...")
        self.title.setFont(QFont("Inter", 22, QFont.Weight.Bold))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(f"color: {C_TEXT};")

        self.status = QLabel("Please wait.")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet(f"color: {C_MUTED}; font-size: 13px;")

        self.progress_bar = QFrame()
        self.progress_bar.setFixedSize(400, 6)
        self.progress_bar.setStyleSheet(f"""
            QFrame {{
                background: rgba(255,255,255,0.08);
                border-radius: 3px;
            }}
        """)

        self.progress_fill = QFrame(self.progress_bar)
        self.progress_fill.setFixedHeight(6)
        self.progress_fill.setFixedWidth(0)
        self.progress_fill.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C_PRIMARY}, stop:1 {C_HIGHLIGHT});
                border-radius: 3px;
            }}
        """)

        self.layout_.addStretch()
        self.layout_.addWidget(self.icon)
        self.layout_.addWidget(self.title)
        self.layout_.addWidget(self.status)
        self.layout_.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout_.addStretch()
        self.setLayout(self.layout_)

        self._progress = 0

    def start(self, user_data, selected_apps):
        self.user_data = user_data
        self.selected_apps = selected_apps
        self._steps = self._build_steps()
        self._current = 0
        self._run_next()

    def _build_steps(self):
        ud = self.user_data
        steps = []

        # Create user
        steps.append((
            "Creating user account...",
            f"useradd -m -c '{ud['name']}' -s /bin/bash {ud['username']} && "
            f"echo '{ud['username']}:{ud['password']}' | chpasswd && "
            f"usermod -aG sudo {ud['username']}"
        ))

        # Install selected apps
        flatpak_map = {
            "code":     "com.visualstudio.code",
            "steam":    "com.valvesoftware.Steam",
            "spotify":  "com.spotify.Client",
            "discord":  "com.discordapp.Discord",
            "brave":    "com.brave.Browser",
            "chromium": "org.chromium.Chromium",
            "vlc":      "org.videolan.VLC",
        }
        apt_map = {
            "wine": "wine wine32 wine64 winetricks",
        }

        for app in self.selected_apps:
            if app in flatpak_map:
                steps.append((
                    f"Installing {app}...",
                    f"flatpak install -y flathub {flatpak_map[app]}"
                ))
            elif app in apt_map:
                steps.append((
                    f"Installing {app}...",
                    f"apt-get install -y {apt_map[app]}"
                ))

        # Set locale
        steps.append(("Finalizing...", "echo done"))
        return steps

    def _run_next(self):
        if self._current >= len(self._steps):
            self._finish()
            return

        label, cmd = self._steps[self._current]
        self.status.setText(label)
        pct = int((self._current / len(self._steps)) * 400)
        self.progress_fill.setFixedWidth(pct)

        self.worker = CommandWorker(cmd)
        self.worker.finished.connect(self._step_done)
        self.worker.start()

    def _step_done(self, ok):
        self._current += 1
        self._run_next()

    def _finish(self):
        self.progress_fill.setFixedWidth(400)
        self.icon.setText("✅")
        self.title.setText("All done!")
        self.status.setText("Your system is ready.")
        QTimer.singleShot(1200, self.done.emit)


# ============================================================
#  PAGE 6 - FINISH
# ============================================================

class PageFinish(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        icon = QLabel("🌲")
        icon.setFont(QFont("Segoe UI Emoji", 72))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Welcome to Velora Linux!")
        title.setFont(QFont("Inter", 30, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {C_TEXT};")

        sub = QLabel("Your system is set up and ready.\nEnjoy the experience.")
        sub.setFont(QFont("Inter", 14))
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {C_MUTED};")

        layout.addStretch()
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(sub)
        layout.addStretch()
        self.setLayout(layout)


# ============================================================
#  MAIN WINDOW
# ============================================================

class VeloraWelcome(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Velora Welcome")
        self.setMinimumSize(820, 580)
        self.setStyleSheet(STYLE_GLOBAL)

        self.page_welcome   = PageWelcome()
        self.page_language  = PageLanguage()
        self.page_user      = PageUser()
        self.page_apps      = PageApps()
        self.page_installing = PageInstalling()
        self.page_finish    = PageFinish()

        self.pages = QStackedWidget()
        for p in [self.page_welcome, self.page_language,
                  self.page_user, self.page_apps,
                  self.page_installing, self.page_finish]:
            self.pages.addWidget(p)

        # Dots
        self.dot_count = 4  # welcome, language, user, apps (no dot for installing/finish)
        dots_row = QHBoxLayout()
        dots_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dots = []
        for _ in range(self.dot_count):
            d = QLabel("●")
            d.setFont(QFont("Inter", 9))
            self.dots.append(d)
            dots_row.addWidget(d)

        # Nav buttons
        self.back_btn = QPushButton("← Back")
        self.back_btn.setStyleSheet(STYLE_BTN_GHOST)
        self.back_btn.setFixedWidth(140)
        self.back_btn.clicked.connect(self.go_back)

        self.next_btn = QPushButton("Get Started →")
        self.next_btn.setStyleSheet(STYLE_BTN_PRIMARY)
        self.next_btn.setFixedWidth(200)
        self.next_btn.clicked.connect(self.go_next)

        nav = QHBoxLayout()
        nav.setContentsMargins(40, 8, 40, 24)
        nav.addWidget(self.back_btn)
        nav.addStretch()
        nav.addWidget(self.next_btn)

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self.pages)
        root.addLayout(dots_row)
        root.addLayout(nav)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        self.current = 0
        self.page_installing.done.connect(self.on_install_done)
        self.update_nav()

    def update_nav(self):
        idx = self.current
        # Hide nav on installing/finish screens
        installing = (idx == 4)
        finish = (idx == 5)

        self.back_btn.setVisible(idx > 0 and not installing and not finish)
        self.next_btn.setVisible(not installing)

        if finish:
            self.next_btn.setText("Finish")
        elif idx == 3:
            self.next_btn.setText("Install →")
        elif idx == 0:
            self.next_btn.setText("Get Started →")
        else:
            self.next_btn.setText("Continue →")

        # Dots
        for i, d in enumerate(self.dots):
            if i == min(idx, self.dot_count - 1):
                d.setStyleSheet(f"color: {C_HIGHLIGHT};")
            else:
                d.setStyleSheet(f"color: #2a4a38;")

    def go_next(self):
        idx = self.current

        # Validate user page
        if idx == 2 and not self.page_user.is_valid():
            self.page_user.match_lbl.setText("⚠️ Please fill in all fields correctly.")
            return

        if idx == 5:
            # Finish - disable autostart so it doesn't run again
            autostart = os.path.expanduser(
                "~/.config/autostart/velora-welcome.desktop"
            )
            if os.path.exists(autostart):
                os.remove(autostart)
            self.close()
            return

        if idx == 3:
            # Start installation
            self.current = 4
            self.pages.setCurrentIndex(4)
            self.update_nav()
            user_data = self.page_user.get_data()
            selected  = self.page_apps.get_selected()
            self.page_installing.start(user_data, selected)
            return

        self.current += 1
        self.pages.setCurrentIndex(self.current)
        self.update_nav()

    def go_back(self):
        if self.current > 0:
            self.current -= 1
            self.pages.setCurrentIndex(self.current)
            self.update_nav()

    def on_install_done(self):
        self.current = 5
        self.pages.setCurrentIndex(5)
        self.update_nav()


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Velora Welcome")
    window = VeloraWelcome()
    window.showFullScreen()
    sys.exit(app.exec())
