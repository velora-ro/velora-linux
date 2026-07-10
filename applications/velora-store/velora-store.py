#!/usr/bin/env python3
# ============================================================
#  Velora Store
#  Application store for Velora Linux
#  Flatpak (Flathub) + apt, categories + search
#  PyQt6, Forest Green theme, iOS 26 style
# ============================================================

import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QLineEdit, QGridLayout,
    QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

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
    border-radius: 14px;
    padding: 11px 18px;
    color: {C_TEXT};
    font-size: 13px;
}}
QLineEdit:focus {{
    border: 1px solid {C_ACCENT};
    background: rgba(255,255,255,0.10);
}}
QScrollBar:vertical {{
    background: transparent; width: 5px;
}}
QScrollBar::handle:vertical {{
    background: {C_PRIMARY}; border-radius: 3px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""

STYLE_BTN = f"""
QPushButton {{
    background: {C_PRIMARY};
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 9px 20px;
    font-size: 12px;
    font-weight: bold;
}}
QPushButton:hover {{ background: {C_ACCENT}; }}
QPushButton:pressed {{ background: #1e4d3a; }}
QPushButton:disabled {{
    background: rgba(47,107,82,0.2);
    color: rgba(255,255,255,0.25);
}}
"""

STYLE_BTN_REMOVE = f"""
QPushButton {{
    background: rgba(220,80,80,0.12);
    color: {C_DANGER};
    border: 1px solid rgba(220,80,80,0.25);
    border-radius: 10px;
    padding: 9px 20px;
    font-size: 12px;
    font-weight: bold;
}}
QPushButton:hover {{ background: rgba(220,80,80,0.22); }}
QPushButton:disabled {{ opacity: 0.4; }}
"""

STYLE_CAT_BTN = f"""
QPushButton {{
    background: rgba(20,42,30,0.7);
    color: {C_MUTED};
    border: 1px solid rgba(95,158,110,0.15);
    border-radius: 12px;
    padding: 10px 18px;
    font-size: 13px;
}}
QPushButton:hover {{
    background: rgba(47,107,82,0.25);
    color: {C_TEXT};
}}
QPushButton[active="true"] {{
    background: rgba(47,107,82,0.45);
    color: {C_HIGHLIGHT};
    border-color: {C_ACCENT};
    font-weight: bold;
}}
"""

# ============================================================
#  APP CATALOGUE
#  method: "flatpak" or "apt"
#  id:     flatpak app-id or apt package name
# ============================================================

CATEGORIES = ["All", "Gaming", "Multimedia", "Office", "Internet", "Development", "System"]

APPS = [
    # ── Gaming ──────────────────────────────────────────────
    {
        "name":     "Steam",
        "icon":     "🎮",
        "desc":     "The ultimate gaming platform.",
        "category": "Gaming",
        "method":   "flatpak",
        "id":       "com.valvesoftware.Steam",
    },
    {
        "name":     "Heroic Games Launcher",
        "icon":     "🦸",
        "desc":     "Epic Games & GOG on Linux.",
        "category": "Gaming",
        "method":   "flatpak",
        "id":       "com.heroicgameslauncher.hgl",
    },
    {
        "name":     "Lutris",
        "icon":     "🍷",
        "desc":     "Open gaming platform for Linux.",
        "category": "Gaming",
        "method":   "flatpak",
        "id":       "net.lutris.Lutris",
    },
    {
        "name":     "Bottles",
        "icon":     "🍾",
        "desc":     "Run Windows apps with Wine.",
        "category": "Gaming",
        "method":   "flatpak",
        "id":       "com.usebottles.bottles",
    },
    {
        "name":     "ProtonUp-Qt",
        "icon":     "⬆️",
        "desc":     "Manage Proton and Wine versions.",
        "category": "Gaming",
        "method":   "flatpak",
        "id":       "net.davidotek.pupgui2",
    },
    {
        "name":     "MangoHud",
        "icon":     "📊",
        "desc":     "In-game performance overlay.",
        "category": "Gaming",
        "method":   "apt",
        "id":       "mangohud",
    },
    # ── Multimedia ──────────────────────────────────────────
    {
        "name":     "VLC",
        "icon":     "🎬",
        "desc":     "Universal media player.",
        "category": "Multimedia",
        "method":   "flatpak",
        "id":       "org.videolan.VLC",
    },
    {
        "name":     "OBS Studio",
        "icon":     "🔴",
        "desc":     "Streaming and recording.",
        "category": "Multimedia",
        "method":   "flatpak",
        "id":       "com.obsproject.Studio",
    },
    {
        "name":     "Kdenlive",
        "icon":     "🎞️",
        "desc":     "Professional video editor.",
        "category": "Multimedia",
        "method":   "flatpak",
        "id":       "org.kde.kdenlive",
    },
    {
        "name":     "GIMP",
        "icon":     "🖼️",
        "desc":     "Advanced image editor.",
        "category": "Multimedia",
        "method":   "flatpak",
        "id":       "org.gimp.GIMP",
    },
    {
        "name":     "Spotify",
        "icon":     "🎵",
        "desc":     "Music streaming.",
        "category": "Multimedia",
        "method":   "flatpak",
        "id":       "com.spotify.Client",
    },
    {
        "name":     "Inkscape",
        "icon":     "✏️",
        "desc":     "Vector graphics editor.",
        "category": "Multimedia",
        "method":   "flatpak",
        "id":       "org.inkscape.Inkscape",
    },
    # ── Office ──────────────────────────────────────────────
    {
        "name":     "LibreOffice",
        "icon":     "📄",
        "desc":     "Full office suite.",
        "category": "Office",
        "method":   "flatpak",
        "id":       "org.libreoffice.LibreOffice",
    },
    {
        "name":     "Obsidian",
        "icon":     "📝",
        "desc":     "Markdown notes and knowledge base.",
        "category": "Office",
        "method":   "flatpak",
        "id":       "md.obsidian.Obsidian",
    },
    {
        "name":     "Foliate",
        "icon":     "📚",
        "desc":     "Beautiful ebook reader.",
        "category": "Office",
        "method":   "flatpak",
        "id":       "com.github.johnfactotum.Foliate",
    },
    # ── Internet ────────────────────────────────────────────
    {
        "name":     "Firefox",
        "icon":     "🌐",
        "desc":     "Fast, private web browser.",
        "category": "Internet",
        "method":   "flatpak",
        "id":       "org.mozilla.firefox",
    },
    {
        "name":     "Brave",
        "icon":     "🦁",
        "desc":     "Privacy-first browser.",
        "category": "Internet",
        "method":   "flatpak",
        "id":       "com.brave.Browser",
    },
    {
        "name":     "Discord",
        "icon":     "💬",
        "desc":     "Voice, video and text chat.",
        "category": "Internet",
        "method":   "flatpak",
        "id":       "com.discordapp.Discord",
    },
    {
        "name":     "Telegram",
        "icon":     "✈️",
        "desc":     "Fast messaging app.",
        "category": "Internet",
        "method":   "flatpak",
        "id":       "org.telegram.desktop",
    },
    {
        "name":     "qBittorrent",
        "icon":     "⚡",
        "desc":     "Open-source torrent client.",
        "category": "Internet",
        "method":   "flatpak",
        "id":       "org.qbittorrent.qBittorrent",
    },
    # ── Development ─────────────────────────────────────────
    {
        "name":     "VS Code",
        "icon":     "💻",
        "desc":     "Code editor by Microsoft.",
        "category": "Development",
        "method":   "flatpak",
        "id":       "com.visualstudio.code",
    },
    {
        "name":     "Android Studio",
        "icon":     "🤖",
        "desc":     "Android app development IDE.",
        "category": "Development",
        "method":   "flatpak",
        "id":       "com.google.AndroidStudio",
    },
    {
        "name":     "Git",
        "icon":     "🔀",
        "desc":     "Version control system.",
        "category": "Development",
        "method":   "apt",
        "id":       "git",
    },
    {
        "name":     "Docker",
        "icon":     "🐳",
        "desc":     "Container platform.",
        "category": "Development",
        "method":   "apt",
        "id":       "docker.io",
    },
    # ── System ──────────────────────────────────────────────
    {
        "name":     "Timeshift",
        "icon":     "🔒",
        "desc":     "System backup and restore.",
        "category": "System",
        "method":   "apt",
        "id":       "timeshift",
    },
    {
        "name":     "GParted",
        "icon":     "💾",
        "desc":     "Partition manager.",
        "category": "System",
        "method":   "apt",
        "id":       "gparted",
    },
    {
        "name":     "Flatseal",
        "icon":     "🔐",
        "desc":     "Manage Flatpak permissions.",
        "category": "System",
        "method":   "flatpak",
        "id":       "com.github.tchx84.Flatseal",
    },
    {
        "name":     "Htop",
        "icon":     "📈",
        "desc":     "Interactive process viewer.",
        "category": "System",
        "method":   "apt",
        "id":       "htop",
    },
]

# ============================================================
#  INSTALLED CHECK
# ============================================================

def is_installed(app):
    try:
        if app["method"] == "flatpak":
            r = subprocess.run(
                ["flatpak", "list", "--app", "--columns=application"],
                capture_output=True, text=True
            )
            return app["id"] in r.stdout
        else:
            r = subprocess.run(
                ["dpkg", "-s", app["id"]],
                capture_output=True, text=True
            )
            return "Status: install ok installed" in r.stdout
    except Exception:
        return False


# ============================================================
#  WORKER THREAD
# ============================================================

class InstallWorker(QThread):
    line_out = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, app, remove=False):
        super().__init__()
        self.app    = app
        self.remove = remove

    def run(self):
        try:
            if self.app["method"] == "flatpak":
                if self.remove:
                    cmd = f"flatpak uninstall -y {self.app['id']}"
                else:
                    cmd = f"flatpak install -y flathub {self.app['id']}"
            else:
                if self.remove:
                    cmd = f"apt-get remove -y {self.app['id']}"
                else:
                    cmd = f"apt-get install -y {self.app['id']}"

            proc = subprocess.Popen(
                cmd, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for line in proc.stdout:
                self.line_out.emit(line.rstrip())
            proc.wait()
            self.finished.emit(proc.returncode == 0)
        except Exception as e:
            self.line_out.emit(f"Error: {e}")
            self.finished.emit(False)


# ============================================================
#  PROGRESS BAR
# ============================================================

class ProgressBar(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(6)
        self.setStyleSheet(
            "QFrame { background: rgba(255,255,255,0.08); border-radius: 3px; }"
        )
        self._fill = QFrame(self)
        self._fill.setFixedHeight(6)
        self._fill.setFixedWidth(0)
        self._fill.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C_PRIMARY}, stop:1 {C_HIGHLIGHT});
                border-radius: 3px;
            }}
        """)

    def set_value(self, pct):
        self._fill.setFixedWidth(int(self.width() * pct / 100))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._fill.setFixedHeight(6)


# ============================================================
#  APP CARD WIDGET
# ============================================================

class AppCard(QFrame):
    action_clicked = pyqtSignal(dict, bool)   # app, is_remove

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.installed = is_installed(app)

        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background: {C_CARD};
                border-radius: 16px;
                border: 1px solid rgba(95,158,110,0.13);
            }}
            QFrame:hover {{
                border-color: rgba(95,158,110,0.30);
            }}
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(14)

        # Icon
        icon = QLabel(app["icon"])
        icon.setFont(QFont("Segoe UI Emoji", 28))
        icon.setFixedWidth(48)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Info
        info = QVBoxLayout()
        info.setSpacing(3)
        name = QLabel(app["name"])
        name.setFont(QFont("Inter", 13, QFont.Weight.Bold))
        name.setStyleSheet(f"color: {C_TEXT};")
        desc = QLabel(app["desc"])
        desc.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")

        # Method badge
        method_badge = QLabel(
            "Flatpak" if app["method"] == "flatpak" else "APT"
        )
        method_badge.setStyleSheet(f"""
            color: {C_MUTED};
            background: rgba(0,0,0,0.2);
            border: 1px solid rgba(95,158,110,0.2);
            border-radius: 6px;
            padding: 1px 7px;
            font-size: 10px;
        """)
        method_badge.setFixedHeight(18)

        name_row = QHBoxLayout()
        name_row.addWidget(name)
        name_row.addWidget(method_badge)
        name_row.addStretch()

        info.addLayout(name_row)
        info.addWidget(desc)

        # Action button
        self.btn = QPushButton()
        self.btn.setFixedWidth(110)
        self._update_btn()
        self.btn.clicked.connect(self._on_click)

        layout.addWidget(icon)
        layout.addLayout(info)
        layout.addStretch()
        layout.addWidget(self.btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(layout)

    def _update_btn(self):
        if self.installed:
            self.btn.setText("Remove")
            self.btn.setStyleSheet(STYLE_BTN_REMOVE)
        else:
            self.btn.setText("⬇  Install")
            self.btn.setStyleSheet(STYLE_BTN)

    def _on_click(self):
        self.action_clicked.emit(self.app, self.installed)

    def set_loading(self, loading, remove=False):
        self.btn.setEnabled(not loading)
        if loading:
            self.btn.setText("Working...")
        else:
            self.installed = not remove
            self._update_btn()

# ============================================================
#  MAIN WINDOW
# ============================================================

class VeloraStore(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Velora Store")
        self.setMinimumSize(900, 620)
        self.setStyleSheet(STYLE_GLOBAL)
        self._current_cat = "All"
        self._search_term = ""
        self._cards = {}          # id -> AppCard
        self._build_ui()

    def _build_ui(self):
        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Sidebar ─────────────────────────────────────────
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: rgba(10,25,18,0.97);
                border-right: 1px solid rgba(47,107,82,0.2);
            }}
        """)
        sb_layout = QVBoxLayout()
        sb_layout.setContentsMargins(14, 28, 14, 20)
        sb_layout.setSpacing(4)

        logo = QLabel("🛍  Velora Store")
        logo.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        logo.setStyleSheet(f"color: {C_HIGHLIGHT}; padding-bottom: 16px;")
        sb_layout.addWidget(logo)

        self.cat_btns = {}
        for cat in CATEGORIES:
            emoji = {
                "All": "🔍", "Gaming": "🎮", "Multimedia": "🎬",
                "Office": "📄", "Internet": "🌐",
                "Development": "💻", "System": "⚙️"
            }.get(cat, "●")
            btn = QPushButton(f"  {emoji}  {cat}")
            btn.setStyleSheet(STYLE_CAT_BTN)
            btn.setProperty("active", "false")
            btn.clicked.connect(lambda _, c=cat: self._select_cat(c))
            sb_layout.addWidget(btn)
            self.cat_btns[cat] = btn

        sb_layout.addStretch()
        sidebar.setLayout(sb_layout)

        # ── Main area ────────────────────────────────────────
        main = QWidget()
        main.setStyleSheet(f"background: {C_BG};")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 28, 32, 20)
        main_layout.setSpacing(0)

        # Stack: browse / detail (log)
        self.stack = QStackedWidget()

        # ── Page 0: Browse ───────────────────────────────────
        browse = QWidget()
        browse_layout = QVBoxLayout()
        browse_layout.setContentsMargins(0, 0, 0, 0)
        browse_layout.setSpacing(14)

        # Search bar
        search_row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍   Search applications...")
        self.search.textChanged.connect(self._on_search)
        search_row.addWidget(self.search)
        browse_layout.addLayout(search_row)

        # Result count
        self.result_lbl = QLabel("")
        self.result_lbl.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        browse_layout.addWidget(self.result_lbl)

        # Scroll area with cards
        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_widget.setLayout(self.grid_layout)
        scroll.setWidget(self.grid_widget)
        browse_layout.addWidget(scroll)

        browse.setLayout(browse_layout)

        # ── Page 1: Install/Remove log ───────────────────────
        log_page = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(12)

        self.log_title = QLabel("")
        self.log_title.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        self.log_title.setStyleSheet(f"color: {C_TEXT};")

        self.log_progress = ProgressBar()

        self.log_status = QLabel("")
        self.log_status.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")

        log_scroll = QScrollArea()
        log_scroll.setFrameShape(QFrame.Shape.NoFrame)
        log_scroll.setWidgetResizable(True)
        self.log_scroll_area = log_scroll

        self.log_inner = QWidget()
        self.log_inner_layout = QVBoxLayout()
        self.log_inner_layout.setContentsMargins(0, 0, 0, 0)
        self.log_inner_layout.setSpacing(1)
        self.log_inner_layout.addStretch()
        self.log_inner.setLayout(self.log_inner_layout)
        log_scroll.setWidget(self.log_inner)

        self.back_btn = QPushButton("← Back to Store")
        self.back_btn.setStyleSheet(STYLE_CAT_BTN)
        self.back_btn.setEnabled(False)
        self.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        log_layout.addWidget(self.log_title)
        log_layout.addWidget(self.log_progress)
        log_layout.addWidget(self.log_status)
        log_layout.addWidget(log_scroll)
        log_layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        log_page.setLayout(log_layout)

        self.stack.addWidget(browse)
        self.stack.addWidget(log_page)

        main_layout.addWidget(self.stack)
        main.setLayout(main_layout)

        root.addWidget(sidebar)
        root.addWidget(main)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        # Initial load
        self._select_cat("All")

    # ── Category & search ─────────────────────────────────

    def _select_cat(self, cat):
        self._current_cat = cat
        self.search.clear()
        self._search_term = ""
        for c, btn in self.cat_btns.items():
            btn.setProperty("active", "true" if c == cat else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._refresh_grid()

    def _on_search(self, text):
        self._search_term = text.lower()
        self._current_cat = "All"
        for c, btn in self.cat_btns.items():
            btn.setProperty("active", "true" if c == "All" else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._refresh_grid()

    def _filtered_apps(self):
        result = []
        for app in APPS:
            cat_ok = (self._current_cat == "All" or
                      app["category"] == self._current_cat)
            search_ok = (not self._search_term or
                         self._search_term in app["name"].lower() or
                         self._search_term in app["desc"].lower() or
                         self._search_term in app["category"].lower())
            if cat_ok and search_ok:
                result.append(app)
        return result

    def _refresh_grid(self):
        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards.clear()

        apps = self._filtered_apps()
        count = len(apps)
        self.result_lbl.setText(
            f"{count} app{'s' if count != 1 else ''}"
            + (f" in {self._current_cat}" if self._current_cat != "All" else "")
            + (f' for "{self._search_term}"' if self._search_term else "")
        )

        cols = 2
        for i, app in enumerate(apps):
            card = AppCard(app)
            card.action_clicked.connect(self._on_action)
            self._cards[app["id"]] = card
            self.grid_layout.addWidget(card, i // cols, i % cols)

        # Fill last row
        if count % cols != 0:
            spacer = QWidget()
            spacer.setFixedHeight(100)
            self.grid_layout.addWidget(spacer, count // cols, count % cols)

    # ── Install / Remove ──────────────────────────────────

    def _on_action(self, app, is_remove):
        verb = "Removing" if is_remove else "Installing"
        self.log_title.setText(f"{verb} {app['name']}...")
        self.log_status.setText("Please wait...")
        self.log_progress.set_value(0)
        self.back_btn.setEnabled(False)

        # Clear log
        while self.log_inner_layout.count() > 1:
            item = self.log_inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.stack.setCurrentIndex(1)

        self._anim_val = 0
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._tick)
        self._anim_timer.start(40)

        self._current_app = app
        self._current_remove = is_remove

        self.worker = InstallWorker(app, remove=is_remove)
        self.worker.line_out.connect(self._on_log)
        self.worker.finished.connect(self._on_done)
        self.worker.start()

    def _on_log(self, line):
        if not line.strip():
            return
        lbl = QLabel(line)
        lbl.setStyleSheet(
            f"color: {C_MUTED}; font-size: 11px; font-family: monospace;"
        )
        lbl.setWordWrap(True)
        self.log_inner_layout.insertWidget(
            self.log_inner_layout.count() - 1, lbl
        )
        QTimer.singleShot(30, lambda: self.log_scroll_area.verticalScrollBar().setValue(
            self.log_scroll_area.verticalScrollBar().maximum()
        ))

    def _on_done(self, ok):
        self._anim_timer.stop()
        self.log_progress.set_value(100)
        app = self._current_app
        verb = "removed" if self._current_remove else "installed"
        if ok:
            self.log_status.setText(f"✅  {app['name']} {verb} successfully.")
        else:
            self.log_status.setText(f"❌  Operation failed. Check the log above.")
        self.back_btn.setEnabled(True)
        # Update card state
        if ok and app["id"] in self._cards:
            self._cards[app["id"]].set_loading(False, remove=self._current_remove)

    def _tick(self):
        self._anim_val = (self._anim_val + 3) % 95
        self.log_progress.set_value(self._anim_val)


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Velora Store")
    window = VeloraStore()
    window.show()
    sys.exit(app.exec())
