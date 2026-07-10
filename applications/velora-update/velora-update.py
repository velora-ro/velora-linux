#!/usr/bin/env python3
# ============================================================
#  Velora Update
#  System update manager for Velora Linux
#  PyQt6, Forest Green theme, iOS 26 style
# ============================================================

import sys
import subprocess
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QListWidget, QListWidgetItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

# ============================================================
#  COLORS
# ============================================================
C_BG        = "#0a1510"
C_CARD      = "rgba(20, 42, 30, 0.82)"
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
}}
QScrollBar:vertical {{
    background: transparent; width: 5px;
}}
QScrollBar::handle:vertical {{
    background: {C_PRIMARY}; border-radius: 3px; min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QListWidget {{
    background: transparent;
    border: none;
    outline: none;
}}
QListWidget::item {{
    background: rgba(20,42,30,0.7);
    border-radius: 10px;
    margin: 3px 0;
    padding: 10px 14px;
    color: {C_TEXT};
    font-size: 13px;
    border: 1px solid rgba(95,158,110,0.1);
}}
QListWidget::item:selected {{
    background: rgba(47,107,82,0.35);
    border-color: {C_ACCENT};
}}
"""

STYLE_BTN = f"""
QPushButton {{
    background: {C_PRIMARY};
    color: #ffffff;
    border: none;
    border-radius: 14px;
    padding: 13px 30px;
    font-size: 13px;
    font-weight: bold;
}}
QPushButton:hover {{ background: {C_ACCENT}; }}
QPushButton:pressed {{ background: #1e4d3a; }}
QPushButton:disabled {{
    background: rgba(47,107,82,0.25);
    color: rgba(255,255,255,0.3);
}}
"""

STYLE_BTN_GHOST = f"""
QPushButton {{
    background: transparent;
    color: {C_MUTED};
    border: 1px solid rgba(95,158,110,0.25);
    border-radius: 14px;
    padding: 13px 30px;
    font-size: 13px;
}}
QPushButton:hover {{ color: {C_TEXT}; border-color: {C_ACCENT}; }}
QPushButton:disabled {{ opacity: 0.4; }}
"""

# ============================================================
#  WORKER THREADS
# ============================================================

class CheckWorker(QThread):
    """Runs apt-get update + apt list --upgradable"""
    found      = pyqtSignal(list)   # list of (name, version, size)
    error      = pyqtSignal(str)
    status_msg = pyqtSignal(str)

    def run(self):
        try:
            self.status_msg.emit("Refreshing package lists...")
            subprocess.run(
                ["apt-get", "update", "-q"],
                capture_output=True, check=True
            )
            self.status_msg.emit("Checking for upgradable packages...")
            result = subprocess.run(
                ["apt", "list", "--upgradable"],
                capture_output=True, text=True
            )
            packages = []
            for line in result.stdout.splitlines():
                if "/" not in line or "Listing" in line:
                    continue
                # Format: name/repo version arch [upgradable from: old]
                parts = line.split()
                name    = parts[0].split("/")[0]
                version = parts[1] if len(parts) > 1 else "?"
                packages.append((name, version))
            self.found.emit(packages)
        except subprocess.CalledProcessError as e:
            self.error.emit(str(e))
        except Exception as e:
            self.error.emit(str(e))


class InstallWorker(QThread):
    """Runs apt-get upgrade"""
    line_out  = pyqtSignal(str)
    finished  = pyqtSignal(bool)
    progress  = pyqtSignal(int)   # 0-100

    def run(self):
        try:
            proc = subprocess.Popen(
                ["apt-get", "upgrade", "-y"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            done = 0
            for line in proc.stdout:
                line = line.rstrip()
                self.line_out.emit(line)
                if line.startswith("Get:") or line.startswith("Unpacking") or \
                   line.startswith("Setting up"):
                    done = min(done + 3, 95)
                    self.progress.emit(done)
            proc.wait()
            self.progress.emit(100)
            self.finished.emit(proc.returncode == 0)
        except Exception as e:
            self.line_out.emit(f"Error: {e}")
            self.finished.emit(False)


# ============================================================
#  PROGRESS BAR WIDGET
# ============================================================

class ProgressBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(8)
        self.setStyleSheet(f"""
            QFrame {{
                background: rgba(255,255,255,0.08);
                border-radius: 4px;
            }}
        """)
        self._fill = QFrame(self)
        self._fill.setFixedHeight(8)
        self._fill.setFixedWidth(0)
        self._fill.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {C_PRIMARY}, stop:1 {C_HIGHLIGHT});
                border-radius: 4px;
            }}
        """)

    def set_value(self, pct):
        total = self.width()
        w = int(total * pct / 100)
        self._fill.setFixedWidth(w)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fill.setFixedHeight(8)


# ============================================================
#  MAIN WINDOW
# ============================================================

class VeloraUpdate(QMainWindow):

    # States
    STATE_IDLE      = "idle"
    STATE_CHECKING  = "checking"
    STATE_READY     = "ready"
    STATE_UPDATING  = "updating"
    STATE_DONE      = "done"
    STATE_UP_TO_DATE = "up_to_date"
    STATE_ERROR     = "error"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Velora Update")
        self.setMinimumSize(720, 560)
        self.setStyleSheet(STYLE_GLOBAL)
        self._state = self.STATE_IDLE
        self._packages = []
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(40, 36, 40, 32)
        root.setSpacing(0)

        # --- Header ---
        header = QHBoxLayout()
        icon = QLabel("🔄")
        icon.setFont(QFont("Segoe UI Emoji", 28))
        icon.setFixedWidth(44)

        title_col = QVBoxLayout()
        title = QLabel("Velora Update")
        title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_TEXT};")
        self.subtitle = QLabel("Keep your system secure and up to date.")
        self.subtitle.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        title_col.addWidget(title)
        title_col.addWidget(self.subtitle)

        header.addWidget(icon)
        header.addLayout(title_col)
        header.addStretch()
        root.addLayout(header)
        root.addSpacing(28)

        # --- Status card ---
        self.status_card = QFrame()
        self.status_card.setStyleSheet(f"""
            QFrame {{
                background: {C_CARD};
                border-radius: 18px;
                border: 1px solid rgba(95,158,110,0.15);
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(12)

        self.status_icon = QLabel("🔍")
        self.status_icon.setFont(QFont("Segoe UI Emoji", 36))
        self.status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.status_text = QLabel("Press 'Check for Updates' to start.")
        self.status_text.setFont(QFont("Inter", 15, QFont.Weight.Bold))
        self.status_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_text.setStyleSheet(f"color: {C_TEXT};")

        self.status_sub = QLabel("")
        self.status_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_sub.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        self.status_sub.setWordWrap(True)

        self.progress = ProgressBar()
        self.progress.setVisible(False)

        card_layout.addWidget(self.status_icon)
        card_layout.addWidget(self.status_text)
        card_layout.addWidget(self.status_sub)
        card_layout.addWidget(self.progress)
        self.status_card.setLayout(card_layout)
        root.addWidget(self.status_card)
        root.addSpacing(16)

        # --- Package list ---
        self.list_label = QLabel("Available updates:")
        self.list_label.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        self.list_label.setVisible(False)
        root.addWidget(self.list_label)

        self.pkg_list = QListWidget()
        self.pkg_list.setVisible(False)
        self.pkg_list.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        root.addWidget(self.pkg_list)

        # --- Log area (shown during update) ---
        self.log_label = QLabel("Update log:")
        self.log_label.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        self.log_label.setVisible(False)
        root.addWidget(self.log_label)

        log_scroll = QScrollArea()
        log_scroll.setFrameShape(QFrame.Shape.NoFrame)
        log_scroll.setWidgetResizable(True)
        log_scroll.setVisible(False)
        self.log_scroll = log_scroll

        self.log_inner = QWidget()
        self.log_layout = QVBoxLayout()
        self.log_layout.setContentsMargins(0, 0, 0, 0)
        self.log_layout.setSpacing(2)
        self.log_layout.addStretch()
        self.log_inner.setLayout(self.log_layout)
        log_scroll.setWidget(self.log_inner)
        root.addWidget(log_scroll)

        root.addSpacing(16)

        # --- Buttons ---
        btn_row = QHBoxLayout()
        self.check_btn = QPushButton("🔍  Check for Updates")
        self.check_btn.setStyleSheet(STYLE_BTN)
        self.check_btn.clicked.connect(self.check_updates)

        self.install_btn = QPushButton("⬇️  Install Updates")
        self.install_btn.setStyleSheet(STYLE_BTN)
        self.install_btn.setVisible(False)
        self.install_btn.clicked.connect(self.install_updates)

        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet(STYLE_BTN_GHOST)
        self.close_btn.clicked.connect(self.close)

        btn_row.addWidget(self.check_btn)
        btn_row.addWidget(self.install_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.close_btn)
        root.addLayout(btn_row)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

    # --------------------------------------------------------

    def check_updates(self):
        self._set_state(self.STATE_CHECKING)
        self.worker = CheckWorker()
        self.worker.status_msg.connect(self._on_check_status)
        self.worker.found.connect(self._on_packages_found)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_check_status(self, msg):
        self.status_sub.setText(msg)

    def _on_packages_found(self, packages):
        self._packages = packages
        if packages:
            self._set_state(self.STATE_READY)
        else:
            self._set_state(self.STATE_UP_TO_DATE)

    def install_updates(self):
        self._set_state(self.STATE_UPDATING)
        self.install_worker = InstallWorker()
        self.install_worker.line_out.connect(self._on_log_line)
        self.install_worker.progress.connect(self._on_progress)
        self.install_worker.finished.connect(self._on_install_done)
        self.install_worker.start()

    def _on_log_line(self, line):
        if not line.strip():
            return
        lbl = QLabel(line)
        lbl.setStyleSheet(f"color: {C_MUTED}; font-size: 11px; font-family: monospace;")
        lbl.setWordWrap(True)
        # Insert before the stretch
        self.log_layout.insertWidget(self.log_layout.count() - 1, lbl)
        # Auto-scroll
        QTimer.singleShot(50, lambda: self.log_scroll.verticalScrollBar().setValue(
            self.log_scroll.verticalScrollBar().maximum()
        ))

    def _on_progress(self, pct):
        self.progress.set_value(pct)

    def _on_install_done(self, ok):
        if ok:
            self._set_state(self.STATE_DONE)
        else:
            self._set_state(self.STATE_ERROR)

    def _on_error(self, msg):
        self.status_sub.setText(msg)
        self._set_state(self.STATE_ERROR)

    # --------------------------------------------------------

    def _set_state(self, state):
        self._state = state
        s = state

        # Defaults
        self.pkg_list.setVisible(False)
        self.list_label.setVisible(False)
        self.log_scroll.setVisible(False)
        self.log_label.setVisible(False)
        self.progress.setVisible(False)
        self.install_btn.setVisible(False)
        self.check_btn.setEnabled(True)

        if s == self.STATE_CHECKING:
            self.status_icon.setText("🔄")
            self.status_text.setText("Checking for updates...")
            self.status_sub.setText("Refreshing package lists...")
            self.progress.setVisible(True)
            self.progress.set_value(0)
            self.check_btn.setEnabled(False)
            # Animate indeterminate feel
            self._anim_val = 0
            self._anim_timer = QTimer()
            self._anim_timer.timeout.connect(self._tick_anim)
            self._anim_timer.start(40)

        elif s == self.STATE_UP_TO_DATE:
            self._stop_anim()
            self.status_icon.setText("✅")
            self.status_text.setText("Your system is up to date.")
            self.status_sub.setText("No updates available.")
            self.progress.setVisible(False)

        elif s == self.STATE_READY:
            self._stop_anim()
            count = len(self._packages)
            self.status_icon.setText("📦")
            self.status_text.setText(f"{count} update{'s' if count != 1 else ''} available")
            self.status_sub.setText("Review the list below and press Install.")
            self.progress.setVisible(False)

            # Populate list
            self.pkg_list.clear()
            for name, version in self._packages:
                item = QListWidgetItem(f"  📦  {name}   →   {version}")
                self.pkg_list.addItem(item)
            self.list_label.setVisible(True)
            self.pkg_list.setVisible(True)
            self.install_btn.setVisible(True)

        elif s == self.STATE_UPDATING:
            self.status_icon.setText("⚙️")
            self.status_text.setText("Installing updates...")
            self.status_sub.setText("Please do not turn off your computer.")
            self.progress.setVisible(True)
            self.progress.set_value(0)
            self.log_label.setVisible(True)
            self.log_scroll.setVisible(True)
            self.install_btn.setVisible(False)
            self.check_btn.setEnabled(False)

        elif s == self.STATE_DONE:
            self.status_icon.setText("✅")
            self.status_text.setText("Updates installed successfully!")
            self.status_sub.setText("Your system is up to date. A restart may be required.")
            self.progress.set_value(100)
            self.progress.setVisible(True)

        elif s == self.STATE_ERROR:
            self.status_icon.setText("❌")
            self.status_text.setText("Something went wrong.")
            self.status_sub.setText("Make sure you have internet and run as administrator.")

    def _tick_anim(self):
        self._anim_val = (self._anim_val + 4) % 100
        self.progress.set_value(self._anim_val)

    def _stop_anim(self):
        if hasattr(self, "_anim_timer") and self._anim_timer:
            self._anim_timer.stop()


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Velora Update")
    window = VeloraUpdate()
    window.show()
    sys.exit(app.exec())
