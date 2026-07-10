#!/usr/bin/env python3
# ============================================================
#  Velora Hub
#  System management center for Velora Linux
#  PyQt6, iOS 26 glass style, Forest Green theme
# ============================================================

import sys
import os
import subprocess
import platform
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QFrame, QScrollArea, QGridLayout, QProgressBar,
    QListWidget, QListWidgetItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette

# ============================================================
#  COLORS
# ============================================================
C_BG        = "#0a1510"
C_SURFACE   = "rgba(15, 30, 22, 0.85)"
C_CARD      = "rgba(20, 40, 30, 0.80)"
C_PRIMARY   = "#2F6B52"
C_ACCENT    = "#5F9E6E"
C_HIGHLIGHT = "#89C17D"
C_TEXT      = "#D2EBD8"
C_MUTED     = "#7A9E87"
C_DANGER    = "#DC5050"
C_WARNING   = "#C8A830"

STYLE_GLOBAL = f"""
QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: 'Inter', 'Segoe UI', sans-serif;
    font-size: 13px;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {C_PRIMARY};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""

STYLE_CARD = f"""
QFrame {{
    background: {C_CARD};
    border-radius: 18px;
    border: 1px solid rgba(95, 158, 110, 0.15);
}}
"""

STYLE_BTN_PRIMARY = f"""
QPushButton {{
    background: {C_PRIMARY};
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: bold;
}}
QPushButton:hover {{ background: {C_ACCENT}; }}
QPushButton:pressed {{ background: #1e4d3a; }}
"""

STYLE_BTN_GHOST = f"""
QPushButton {{
    background: transparent;
    color: {C_MUTED};
    border: 1px solid rgba(95,158,110,0.25);
    border-radius: 12px;
    padding: 10px 22px;
    font-size: 13px;
}}
QPushButton:hover {{ color: {C_TEXT}; border-color: {C_ACCENT}; }}
"""

STYLE_NAV_BTN = f"""
QPushButton {{
    background: transparent;
    color: {C_MUTED};
    border: none;
    border-radius: 14px;
    padding: 12px 16px;
    font-size: 13px;
    text-align: left;
}}
QPushButton:hover {{
    background: rgba(47, 107, 82, 0.25);
    color: {C_TEXT};
}}
QPushButton[active="true"] {{
    background: rgba(47, 107, 82, 0.45);
    color: {C_HIGHLIGHT};
    font-weight: bold;
}}
"""

# ============================================================
#  WORKER THREAD - runs shell commands without freezing UI
# ============================================================

class CommandWorker(QThread):
    output = pyqtSignal(str)
    finished = pyqtSignal(bool)

    def __init__(self, command):
        super().__init__()
        self.command = command

    def run(self):
        try:
            proc = subprocess.Popen(
                self.command, shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            for line in proc.stdout:
                self.output.emit(line.rstrip())
            proc.wait()
            self.finished.emit(proc.returncode == 0)
        except Exception as e:
            self.output.emit(f"Error: {e}")
            self.finished.emit(False)


# ============================================================
#  HELPER WIDGETS
# ============================================================

def make_card(parent_layout, margin=10):
    card = QFrame()
    card.setStyleSheet(STYLE_CARD)
    inner = QVBoxLayout()
    inner.setContentsMargins(20, 18, 20, 18)
    inner.setSpacing(10)
    card.setLayout(inner)
    parent_layout.addWidget(card)
    return card, inner


def section_title(text):
    lbl = QLabel(text)
    lbl.setFont(QFont("Inter", 11, QFont.Weight.Bold))
    lbl.setStyleSheet(f"color: {C_HIGHLIGHT}; letter-spacing: 1px;")
    return lbl


def info_row(label, value):
    row = QHBoxLayout()
    lbl = QLabel(label)
    lbl.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
    val = QLabel(value)
    val.setStyleSheet(f"color: {C_TEXT}; font-size: 12px;")
    val.setAlignment(Qt.AlignmentFlag.AlignRight)
    row.addWidget(lbl)
    row.addStretch()
    row.addWidget(val)
    return row


# ============================================================
#  PAGES
# ============================================================

# --- System Information ---
class SystemInfoPage(QWidget):
    def __init__(self):
        super().__init__()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        content.setLayout(layout)

        layout.addWidget(section_title("SYSTEM INFORMATION"))

        # OS card
        card, inner = make_card(layout)
        inner.addWidget(QLabel("🌲  Operating System"))
        inner.addLayout(info_row("Distribution", "Velora Linux 1.0"))
        inner.addLayout(info_row("Kernel", platform.release()))
        inner.addLayout(info_row("Architecture", platform.machine()))

        # Hardware card
        card2, inner2 = make_card(layout)
        inner2.addWidget(QLabel("💻  Hardware"))

        try:
            with open("/proc/cpuinfo") as f:
                cpu = next((l.split(":")[1].strip() for l in f
                            if l.startswith("model name")), "Unknown")
        except Exception:
            cpu = "Unknown"

        try:
            with open("/proc/meminfo") as f:
                lines = f.readlines()
            total = int(next(l.split()[1] for l in lines if l.startswith("MemTotal"))) // 1024
            avail = int(next(l.split()[1] for l in lines if l.startswith("MemAvailable"))) // 1024
            used = total - avail
            mem_text = f"{used} MB used / {total} MB total"
        except Exception:
            mem_text = "Unknown"

        inner2.addLayout(info_row("CPU", cpu))
        inner2.addLayout(info_row("RAM", mem_text))

        # GPU card
        card3, inner3 = make_card(layout)
        inner3.addWidget(QLabel("🎮  Graphics"))
        try:
            result = subprocess.run(["lspci"], capture_output=True, text=True)
            gpus = [l for l in result.stdout.splitlines()
                    if any(x in l for x in ["VGA", "3D", "Display"])]
            gpu_text = gpus[0].split(":")[-1].strip() if gpus else "Unknown"
        except Exception:
            gpu_text = "Unknown"
        inner3.addLayout(info_row("GPU", gpu_text))

        layout.addStretch()
        scroll.setWidget(content)

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)
        self.setLayout(root)


# --- Drivers ---
class DriversPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(section_title("DRIVERS"))

        self.status_lbl = QLabel("Scanning hardware...")
        self.status_lbl.setStyleSheet(f"color: {C_MUTED};")
        layout.addWidget(self.status_lbl)

        self.cards_layout = QVBoxLayout()
        layout.addLayout(self.cards_layout)
        layout.addStretch()

        self.setLayout(layout)
        QTimer.singleShot(500, self.scan)

    def scan(self):
        found = False
        try:
            r = subprocess.run(["lspci"], capture_output=True, text=True)
            if "NVIDIA" in r.stdout:
                found = True
                self.add_driver_card(
                    "🟢  NVIDIA Proprietary Driver",
                    "nvidia-driver-535",
                    "Recommended for best performance with NVIDIA GPU.",
                    "sudo apt install -y nvidia-driver-535"
                )
            if "AMD" in r.stdout or "Radeon" in r.stdout:
                found = True
                self.add_driver_card(
                    "🔴  AMD Driver",
                    "amdgpu (built-in)",
                    "AMDGPU driver is included in the kernel.",
                    None
                )
        except Exception:
            pass

        if not found:
            self.status_lbl.setText("✅  No additional drivers needed.")
        else:
            self.status_lbl.setText("Recommended drivers found:")

    def add_driver_card(self, title, package, desc, cmd):
        card, inner = make_card(self.cards_layout)
        t = QLabel(title)
        t.setFont(QFont("Inter", 13, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {C_TEXT};")
        d = QLabel(desc)
        d.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        p = QLabel(f"Package: {package}")
        p.setStyleSheet(f"color: {C_HIGHLIGHT}; font-size: 11px;")
        inner.addWidget(t)
        inner.addWidget(d)
        inner.addWidget(p)
        if cmd:
            btn = QPushButton("Install")
            btn.setStyleSheet(STYLE_BTN_PRIMARY)
            btn.setFixedWidth(120)
            btn.clicked.connect(lambda: self.install(cmd, btn))
            inner.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)

    def install(self, cmd, btn):
        btn.setText("Installing...")
        btn.setEnabled(False)
        self.worker = CommandWorker(cmd)
        self.worker.finished.connect(lambda ok: btn.setText("✅ Done" if ok else "❌ Failed"))
        self.worker.start()


# --- Gaming ---
class GamingPage(QWidget):
    def __init__(self):
        super().__init__()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(section_title("GAMING"))

        apps = [
            ("🎮  Steam", "Launch Steam", "flatpak run com.valvesoftware.Steam"),
            ("🦸  Heroic Games", "Epic & GOG Games", "flatpak run com.heroicgameslauncher.hgl"),
            ("🍷  Lutris", "Game manager", "lutris"),
            ("🍾  Bottles", "Windows app manager", "flatpak run com.usebottles.bottles"),
            ("⬆️  ProtonUp-Qt", "Manage Proton versions", "flatpak run net.davidotek.pupgui2"),
        ]

        for name, desc, cmd in apps:
            card, inner = make_card(layout)
            row = QHBoxLayout()
            info = QVBoxLayout()
            n = QLabel(name)
            n.setFont(QFont("Inter", 13, QFont.Weight.Bold))
            d = QLabel(desc)
            d.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
            info.addWidget(n)
            info.addWidget(d)
            btn = QPushButton("Launch")
            btn.setStyleSheet(STYLE_BTN_PRIMARY)
            btn.setFixedWidth(100)
            _cmd = cmd
            btn.clicked.connect(lambda _, c=_cmd: subprocess.Popen(c.split()))
            row.addLayout(info)
            row.addStretch()
            row.addWidget(btn)
            inner.addLayout(row)

        layout.addStretch()
        content.setLayout(layout)
        scroll.setWidget(content)

        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)
        self.setLayout(root)


# --- Wine ---
class WinePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(section_title("WINDOWS COMPATIBILITY"))

        card, inner = make_card(layout)
        title = QLabel("🍷  Wine + Bottles")
        title.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        desc = QLabel(
            "Run Windows applications (.exe) on Velora Linux.\n"
            "Use Bottles to create isolated environments for each app."
        )
        desc.setStyleSheet(f"color: {C_MUTED};")
        desc.setWordWrap(True)

        btn_bottles = QPushButton("Open Bottles")
        btn_bottles.setStyleSheet(STYLE_BTN_PRIMARY)
        btn_bottles.clicked.connect(
            lambda: subprocess.Popen(["flatpak", "run", "com.usebottles.bottles"])
        )

        btn_winetricks = QPushButton("Winetricks")
        btn_winetricks.setStyleSheet(STYLE_BTN_GHOST)
        btn_winetricks.clicked.connect(
            lambda: subprocess.Popen(["konsole", "-e", "winetricks"])
        )

        btn_row = QHBoxLayout()
        btn_row.addWidget(btn_bottles)
        btn_row.addWidget(btn_winetricks)
        btn_row.addStretch()

        inner.addWidget(title)
        inner.addWidget(desc)
        inner.addLayout(btn_row)

        layout.addStretch()
        self.setLayout(layout)


# --- Updates ---
class UpdatesPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(section_title("UPDATES"))

        card, inner = make_card(layout)
        self.status = QLabel("Press 'Check for Updates' to start.")
        self.status.setStyleSheet(f"color: {C_MUTED};")

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setVisible(False)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background: rgba(255,255,255,0.08);
                border-radius: 6px;
                height: 8px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background: {C_PRIMARY};
                border-radius: 6px;
            }}
        """)

        btn = QPushButton("🔄  Check for Updates")
        btn.setStyleSheet(STYLE_BTN_PRIMARY)
        btn.clicked.connect(self.check_updates)

        inner.addWidget(self.status)
        inner.addWidget(self.progress)
        inner.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addStretch()
        self.setLayout(layout)

    def check_updates(self):
        self.status.setText("Checking for updates...")
        self.progress.setVisible(True)
        self.worker = CommandWorker("apt-get update -q && apt list --upgradable 2>/dev/null")
        self.worker.output.connect(self.on_output)
        self.worker.finished.connect(self.on_done)
        self.worker.start()
        self.updates = []

    def on_output(self, line):
        if "/" in line and "upgradable" not in line:
            self.updates.append(line)

    def on_done(self, ok):
        self.progress.setVisible(False)
        count = len(self.updates) if hasattr(self, "updates") else 0
        if count > 0:
            self.status.setText(f"✅  {count} update(s) available.")
        else:
            self.status.setText("✅  Your system is up to date.")


# --- Backup ---
class BackupPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        layout.addWidget(section_title("BACKUP"))

        card, inner = make_card(layout)
        title = QLabel("🔒  Timeshift Backup")
        title.setFont(QFont("Inter", 14, QFont.Weight.Bold))
        desc = QLabel(
            "Create and restore system snapshots.\n"
            "Recommended: create a snapshot before installing new software."
        )
        desc.setStyleSheet(f"color: {C_MUTED};")
        desc.setWordWrap(True)

        btn = QPushButton("Open Timeshift")
        btn.setStyleSheet(STYLE_BTN_PRIMARY)
        btn.clicked.connect(
            lambda: subprocess.Popen(["pkexec", "timeshift-gtk"])
        )

        inner.addWidget(title)
        inner.addWidget(desc)
        inner.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addStretch()
        self.setLayout(layout)


# ============================================================
#  MAIN WINDOW
# ============================================================

class VeloraHub(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Velora Hub")
        self.setMinimumSize(960, 640)
        self.setStyleSheet(STYLE_GLOBAL)

        # Navigation items: (icon, label, page_widget)
        self.nav_items = [
            ("🖥️", "System Info",  SystemInfoPage()),
            ("⚙️", "Drivers",      DriversPage()),
            ("🎮", "Gaming",       GamingPage()),
            ("🍷", "Wine",         WinePage()),
            ("🔄", "Updates",      UpdatesPage()),
            ("🔒", "Backup",       BackupPage()),
        ]

        # Sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background: rgba(10, 25, 18, 0.95);
                border-right: 1px solid rgba(47,107,82,0.2);
            }}
        """)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(12, 24, 12, 24)
        sidebar_layout.setSpacing(4)

        # Logo
        logo = QLabel("🌲 Velora Hub")
        logo.setFont(QFont("Inter", 15, QFont.Weight.Bold))
        logo.setStyleSheet(f"color: {C_HIGHLIGHT}; padding: 0 8px 16px 8px;")
        sidebar_layout.addWidget(logo)

        # Nav buttons
        self.nav_buttons = []
        self.pages = QStackedWidget()

        for icon, label, page in self.nav_items:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setStyleSheet(STYLE_NAV_BTN)
            btn.setProperty("active", "false")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            idx = len(self.nav_buttons)
            btn.clicked.connect(lambda _, i=idx: self.switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            self.pages.addWidget(page)

        sidebar_layout.addStretch()

        # Version label
        ver = QLabel("Velora Linux 1.0")
        ver.setStyleSheet(f"color: {C_MUTED}; font-size: 11px; padding: 0 8px;")
        sidebar_layout.addWidget(ver)

        sidebar.setLayout(sidebar_layout)

        # Main area
        main_area = QWidget()
        main_area.setStyleSheet(f"background: {C_BG};")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.pages)
        main_area.setLayout(main_layout)

        # Root layout
        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(sidebar)
        root.addWidget(main_area)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        self.switch_page(0)

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Velora Hub")
    window = VeloraHub()
    window.show()
    sys.exit(app.exec())
