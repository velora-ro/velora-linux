#!/usr/bin/env python3
# ============================================================
#  Velora Driver Manager
#  Hardware driver management for Velora Linux
#  PyQt6, Forest Green theme, iOS 26 style
# ============================================================

import sys
import subprocess
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QFrame,
    QScrollArea, QSizePolicy, QStackedWidget
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
C_INFO      = "#5B9BD5"

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
"""

STYLE_BTN = f"""
QPushButton {{
    background: {C_PRIMARY};
    color: #ffffff;
    border: none;
    border-radius: 12px;
    padding: 11px 26px;
    font-size: 13px;
    font-weight: bold;
}}
QPushButton:hover {{ background: {C_ACCENT}; }}
QPushButton:pressed {{ background: #1e4d3a; }}
QPushButton:disabled {{
    background: rgba(47,107,82,0.2);
    color: rgba(255,255,255,0.25);
}}
"""

STYLE_BTN_DANGER = f"""
QPushButton {{
    background: rgba(220,80,80,0.15);
    color: {C_DANGER};
    border: 1px solid rgba(220,80,80,0.3);
    border-radius: 12px;
    padding: 11px 26px;
    font-size: 13px;
    font-weight: bold;
}}
QPushButton:hover {{
    background: rgba(220,80,80,0.25);
    border-color: {C_DANGER};
}}
QPushButton:disabled {{ opacity: 0.4; }}
"""

STYLE_BTN_GHOST = f"""
QPushButton {{
    background: transparent;
    color: {C_MUTED};
    border: 1px solid rgba(95,158,110,0.25);
    border-radius: 12px;
    padding: 11px 26px;
    font-size: 13px;
}}
QPushButton:hover {{ color: {C_TEXT}; border-color: {C_ACCENT}; }}
"""

# ============================================================
#  HARDWARE DETECTION
# ============================================================

def detect_hardware():
    """Returns dict with detected GPU, WiFi, Bluetooth, Audio info."""
    hw = {
        "gpu":       [],
        "wifi":      [],
        "bluetooth": [],
        "audio":     [],
        "cpu":       "",
    }

    try:
        lspci = subprocess.run(["lspci"], capture_output=True, text=True).stdout
        for line in lspci.splitlines():
            l = line.lower()
            if any(x in l for x in ["vga", "3d controller", "display controller"]):
                hw["gpu"].append(line.split(":")[-1].strip())
            if "network" in l or "wireless" in l or "wi-fi" in l or "wifi" in l:
                hw["wifi"].append(line.split(":")[-1].strip())
            if "bluetooth" in l:
                hw["bluetooth"].append(line.split(":")[-1].strip())
            if "audio" in l or "sound" in l or "multimedia" in l:
                hw["audio"].append(line.split(":")[-1].strip())
    except Exception:
        pass

    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    hw["cpu"] = line.split(":")[1].strip()
                    break
    except Exception:
        pass

    return hw


def check_installed(package):
    try:
        r = subprocess.run(
            ["dpkg", "-s", package],
            capture_output=True, text=True
        )
        return "Status: install ok installed" in r.stdout
    except Exception:
        return False


def get_driver_recommendations(hw):
    """
    Returns list of driver dicts:
    { name, description, package, status, type, remove_package }
    status: 'installed' | 'recommended' | 'optional' | 'not_needed'
    type:   'nvidia' | 'amd' | 'intel' | 'wifi' | 'audio' | 'other'
    """
    drivers = []
    gpu_str = " ".join(hw["gpu"]).lower()
    wifi_str = " ".join(hw["wifi"]).lower()

    # ---- NVIDIA ----
    if "nvidia" in gpu_str:
        pkg535 = "nvidia-driver-535"
        pkg_open = "nvidia-open"
        installed_535  = check_installed(pkg535)
        installed_open = check_installed(pkg_open)

        drivers.append({
            "name":           "NVIDIA Driver 535 (Proprietary)",
            "description":    "Best performance for NVIDIA GPUs. Recommended for gaming.",
            "package":        pkg535,
            "status":         "installed" if installed_535 else "recommended",
            "type":           "nvidia",
            "remove_package": pkg535,
            "icon":           "🟢",
        })
        drivers.append({
            "name":           "NVIDIA Open Kernel Module",
            "description":    "Open-source kernel module. For Turing (RTX 20xx) and newer.",
            "package":        pkg_open,
            "status":         "installed" if installed_open else "optional",
            "type":           "nvidia",
            "remove_package": pkg_open,
            "icon":           "🔓",
        })

    # ---- AMD ----
    if "amd" in gpu_str or "radeon" in gpu_str or "advanced micro" in gpu_str:
        mesa_installed = check_installed("mesa-vulkan-drivers")
        drivers.append({
            "name":           "AMD AMDGPU (built-in)",
            "description":    "AMD GPU driver is included in the Linux kernel. No install needed.",
            "package":        None,
            "status":         "installed",
            "type":           "amd",
            "remove_package": None,
            "icon":           "🔴",
        })
        drivers.append({
            "name":           "Mesa Vulkan Drivers",
            "description":    "Vulkan support for AMD GPUs. Required for gaming with DXVK.",
            "package":        "mesa-vulkan-drivers",
            "status":         "installed" if mesa_installed else "recommended",
            "type":           "amd",
            "remove_package": "mesa-vulkan-drivers",
            "icon":           "🎮",
        })

    # ---- Intel GPU ----
    if "intel" in gpu_str:
        i965 = check_installed("i965-va-driver")
        drivers.append({
            "name":           "Intel VA-API Driver",
            "description":    "Hardware video acceleration for Intel integrated graphics.",
            "package":        "i965-va-driver",
            "status":         "installed" if i965 else "recommended",
            "type":           "intel",
            "remove_package": "i965-va-driver",
            "icon":           "🔵",
        })

    # ---- WiFi ----
    if "broadcom" in wifi_str or "bcm" in wifi_str:
        b43 = check_installed("firmware-b43-installer")
        drivers.append({
            "name":           "Broadcom WiFi Firmware",
            "description":    "Required for Broadcom WiFi adapters.",
            "package":        "firmware-b43-installer",
            "status":         "installed" if b43 else "recommended",
            "type":           "wifi",
            "remove_package": "firmware-b43-installer",
            "icon":           "📶",
        })
    if "realtek" in wifi_str or "rtl" in wifi_str:
        rtl = check_installed("firmware-realtek")
        drivers.append({
            "name":           "Realtek WiFi Firmware",
            "description":    "Firmware for Realtek WiFi and Ethernet adapters.",
            "package":        "firmware-realtek",
            "status":         "installed" if rtl else "recommended",
            "type":           "wifi",
            "remove_package": "firmware-realtek",
            "icon":           "📶",
        })

    # ---- If nothing detected ----
    if not drivers:
        drivers.append({
            "name":           "No drivers needed",
            "description":    "Your hardware is fully supported by built-in drivers.",
            "package":        None,
            "status":         "not_needed",
            "type":           "other",
            "remove_package": None,
            "icon":           "✅",
        })

    return drivers


# ============================================================
#  WORKER THREAD
# ============================================================

class DriverWorker(QThread):
    line_out = pyqtSignal(str)
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
        self.setStyleSheet("QFrame { background: rgba(255,255,255,0.08); border-radius: 3px; }")
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
#  DRIVER CARD WIDGET
# ============================================================

STATUS_COLORS = {
    "installed":  C_HIGHLIGHT,
    "recommended": C_WARNING,
    "optional":   C_INFO,
    "not_needed": C_MUTED,
}
STATUS_LABELS = {
    "installed":   "Installed",
    "recommended": "Recommended",
    "optional":    "Optional",
    "not_needed":  "Not needed",
}

class DriverCard(QFrame):
    install_clicked = pyqtSignal(dict)
    remove_clicked  = pyqtSignal(dict)

    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.setStyleSheet(f"""
            QFrame {{
                background: {C_CARD};
                border-radius: 16px;
                border: 1px solid rgba(95,158,110,0.15);
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        # Top row: icon + name + status badge
        top = QHBoxLayout()

        icon = QLabel(driver["icon"])
        icon.setFont(QFont("Segoe UI Emoji", 22))
        icon.setFixedWidth(38)

        name_col = QVBoxLayout()
        name_lbl = QLabel(driver["name"])
        name_lbl.setFont(QFont("Inter", 13, QFont.Weight.Bold))
        name_lbl.setStyleSheet(f"color: {C_TEXT};")
        desc_lbl = QLabel(driver["description"])
        desc_lbl.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        desc_lbl.setWordWrap(True)
        name_col.addWidget(name_lbl)
        name_col.addWidget(desc_lbl)

        status = driver["status"]
        badge = QLabel(STATUS_LABELS[status])
        badge.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        badge.setStyleSheet(f"""
            color: {STATUS_COLORS[status]};
            background: rgba(0,0,0,0.25);
            border: 1px solid {STATUS_COLORS[status]};
            border-radius: 8px;
            padding: 3px 10px;
        """)
        badge.setFixedHeight(24)

        top.addWidget(icon)
        top.addLayout(name_col)
        top.addStretch()
        top.addWidget(badge, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(top)

        # Package info
        if driver["package"]:
            pkg_lbl = QLabel(f"Package:  {driver['package']}")
            pkg_lbl.setStyleSheet(f"color: {C_MUTED}; font-size: 11px; font-family: monospace;")
            layout.addWidget(pkg_lbl)

        # Buttons
        if driver["status"] != "not_needed" and driver["package"]:
            btn_row = QHBoxLayout()
            if driver["status"] != "installed":
                self.install_btn = QPushButton("⬇️  Install")
                self.install_btn.setStyleSheet(STYLE_BTN)
                self.install_btn.setFixedWidth(130)
                self.install_btn.clicked.connect(lambda: self.install_clicked.emit(self.driver))
                btn_row.addWidget(self.install_btn)

            if driver["status"] == "installed":
                self.remove_btn = QPushButton("🗑  Remove")
                self.remove_btn.setStyleSheet(STYLE_BTN_DANGER)
                self.remove_btn.setFixedWidth(130)
                self.remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self.driver))
                btn_row.addWidget(self.remove_btn)

            btn_row.addStretch()
            layout.addLayout(btn_row)

        self.setLayout(layout)

    def set_loading(self, loading):
        if hasattr(self, "install_btn"):
            self.install_btn.setEnabled(not loading)
            self.install_btn.setText("Installing..." if loading else "⬇️  Install")
        if hasattr(self, "remove_btn"):
            self.remove_btn.setEnabled(not loading)
            self.remove_btn.setText("Removing..." if loading else "🗑  Remove")


# ============================================================
#  MAIN WINDOW
# ============================================================

class VeloraDrivers(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Velora Driver Manager")
        self.setMinimumSize(760, 580)
        self.setStyleSheet(STYLE_GLOBAL)
        self._active_card = None
        self._build_ui()
        QTimer.singleShot(300, self.scan)

    def _build_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(40, 36, 40, 32)
        root.setSpacing(0)

        # Header
        hdr = QHBoxLayout()
        icon = QLabel("🖥️")
        icon.setFont(QFont("Segoe UI Emoji", 26))
        icon.setFixedWidth(42)

        title_col = QVBoxLayout()
        title = QLabel("Driver Manager")
        title.setFont(QFont("Inter", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_TEXT};")
        self.hw_label = QLabel("Scanning hardware...")
        self.hw_label.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        title_col.addWidget(title)
        title_col.addWidget(self.hw_label)

        self.rescan_btn = QPushButton("🔍  Rescan")
        self.rescan_btn.setStyleSheet(STYLE_BTN_GHOST)
        self.rescan_btn.clicked.connect(self.scan)

        hdr.addWidget(icon)
        hdr.addLayout(title_col)
        hdr.addStretch()
        hdr.addWidget(self.rescan_btn)
        root.addLayout(hdr)
        root.addSpacing(24)

        # Stacked: list view / log view
        self.stack = QStackedWidget()

        # -- Page 0: driver cards --
        cards_page = QWidget()
        cards_layout = QVBoxLayout()
        cards_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidgetResizable(True)

        self.cards_inner = QWidget()
        self.cards_inner_layout = QVBoxLayout()
        self.cards_inner_layout.setSpacing(12)
        self.cards_inner_layout.addStretch()
        self.cards_inner.setLayout(self.cards_inner_layout)
        scroll.setWidget(self.cards_inner)
        cards_layout.addWidget(scroll)
        cards_page.setLayout(cards_layout)

        # -- Page 1: log view --
        log_page = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(0, 0, 0, 0)
        log_layout.setSpacing(12)

        self.log_title = QLabel("Installing driver...")
        self.log_title.setFont(QFont("Inter", 15, QFont.Weight.Bold))
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

        self.back_btn = QPushButton("← Back to Drivers")
        self.back_btn.setStyleSheet(STYLE_BTN_GHOST)
        self.back_btn.setEnabled(False)
        self.back_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        log_layout.addWidget(self.log_title)
        log_layout.addWidget(self.log_progress)
        log_layout.addWidget(self.log_status)
        log_layout.addWidget(log_scroll)
        log_layout.addWidget(self.back_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        log_page.setLayout(log_layout)

        self.stack.addWidget(cards_page)
        self.stack.addWidget(log_page)
        root.addWidget(self.stack)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

    # --------------------------------------------------------

    def scan(self):
        self.hw_label.setText("Scanning hardware...")
        self.rescan_btn.setEnabled(False)
        # Clear old cards
        while self.cards_inner_layout.count() > 1:
            item = self.cards_inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.scan_worker = QThread()
        # Do it in a one-shot timer (fast enough, no real thread needed for lspci)
        QTimer.singleShot(200, self._do_scan)

    def _do_scan(self):
        hw = detect_hardware()
        drivers = get_driver_recommendations(hw)

        # Update hw label
        gpu_names = ", ".join(hw["gpu"]) if hw["gpu"] else "Unknown GPU"
        self.hw_label.setText(f"Detected: {gpu_names[:60]}")

        for drv in drivers:
            card = DriverCard(drv)
            card.install_clicked.connect(self.on_install)
            card.remove_clicked.connect(self.on_remove)
            self.cards_inner_layout.insertWidget(
                self.cards_inner_layout.count() - 1, card
            )

        self.rescan_btn.setEnabled(True)

    def on_install(self, driver):
        pkg = driver["package"]
        self._start_operation(
            title=f"Installing {driver['name']}",
            command=f"apt-get install -y {pkg}",
            success_msg=f"✅  {driver['name']} installed successfully.",
            fail_msg=f"❌  Installation failed. Check the log above."
        )

    def on_remove(self, driver):
        pkg = driver["remove_package"]
        self._start_operation(
            title=f"Removing {driver['name']}",
            command=f"apt-get remove -y {pkg} && apt-get autoremove -y",
            success_msg=f"✅  {driver['name']} removed.",
            fail_msg=f"❌  Removal failed. Check the log above."
        )

    def _start_operation(self, title, command, success_msg, fail_msg):
        # Clear log
        while self.log_inner_layout.count() > 1:
            item = self.log_inner_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.log_title.setText(title)
        self.log_status.setText("Running...")
        self.log_progress.set_value(0)
        self.back_btn.setEnabled(False)
        self.stack.setCurrentIndex(1)

        self._anim_val = 0
        self._anim_timer = QTimer()
        self._anim_timer.timeout.connect(self._tick)
        self._anim_timer.start(40)

        self.worker = DriverWorker(command)
        self.worker.line_out.connect(self._on_log)
        self.worker.finished.connect(
            lambda ok: self._on_done(ok, success_msg, fail_msg)
        )
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

    def _on_done(self, ok, success_msg, fail_msg):
        self._anim_timer.stop()
        self.log_progress.set_value(100)
        self.log_status.setText(success_msg if ok else fail_msg)
        self.back_btn.setEnabled(True)
        # Re-scan after change
        if ok:
            QTimer.singleShot(1500, self._go_back_and_rescan)

    def _go_back_and_rescan(self):
        self.stack.setCurrentIndex(0)
        self.scan()

    def _tick(self):
        self._anim_val = (self._anim_val + 3) % 95
        self.log_progress.set_value(self._anim_val)


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Velora Driver Manager")
    window = VeloraDrivers()
    window.show()
    sys.exit(app.exec())
