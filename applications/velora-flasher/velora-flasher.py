#!/usr/bin/env python3
# ============================================================
#  Velora Flasher
#  Flasheaza Velora Linux pe USB sau instaleaza pe PC
#  Ruleaza pe Windows si Linux
#  PyQt6, VeloraForest dark theme
# ============================================================

import sys
import os
import platform
import subprocess
import threading
import urllib.request
import time
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QComboBox,
    QProgressBar, QFileDialog, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QBrush, QPen, QPixmap

IS_WINDOWS = platform.system() == "Windows"
IS_LINUX   = platform.system() == "Linux"

# ── Culori ───────────────────────────────────────────────────
C_BG        = "#0a1510"
C_CARD      = "#111e16"
C_PRIMARY   = "#2F6B52"
C_ACCENT    = "#5F9E6E"
C_HIGHLIGHT = "#89C17D"
C_TEXT      = "#D2EBD8"
C_MUTED     = "#7A9E87"
C_DANGER    = "#DC5050"

STYLE = f"""
QMainWindow, QWidget {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
}}
QLabel {{ background: transparent; }}
QComboBox {{
    background: {C_CARD};
    color: {C_TEXT};
    border: 1px solid rgba(47,107,82,0.4);
    border-radius: 10px;
    padding: 8px 14px;
    font-size: 13px;
    min-height: 20px;
}}
QComboBox::drop-down {{ border: none; width: 30px; }}
QComboBox QAbstractItemView {{
    background: {C_CARD};
    color: {C_TEXT};
    selection-background-color: {C_PRIMARY};
    border: 1px solid rgba(47,107,82,0.4);
}}
QProgressBar {{
    background: rgba(255,255,255,0.08);
    border-radius: 8px;
    height: 18px;
    text-align: center;
    color: {C_TEXT};
    font-size: 11px;
    border: none;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {C_PRIMARY}, stop:1 {C_ACCENT});
    border-radius: 8px;
}}
"""

BTN_PRIMARY = f"""
QPushButton {{
    background: {C_PRIMARY};
    color: white;
    border: none;
    border-radius: 12px;
    padding: 14px 28px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton:hover {{ background: {C_ACCENT}; }}
QPushButton:pressed {{ background: #1e4d3a; }}
QPushButton:disabled {{ background: rgba(47,107,82,0.3); color: {C_MUTED}; }}
"""

BTN_GHOST = f"""
QPushButton {{
    background: transparent;
    color: {C_MUTED};
    border: 1px solid rgba(95,158,110,0.3);
    border-radius: 12px;
    padding: 14px 28px;
    font-size: 14px;
}}
QPushButton:hover {{
    color: {C_TEXT};
    border-color: {C_ACCENT};
    background: rgba(47,107,82,0.1);
}}
"""

BTN_OPTION = f"""
QPushButton {{
    background: {C_CARD};
    color: {C_TEXT};
    border: 2px solid rgba(47,107,82,0.3);
    border-radius: 16px;
    padding: 24px;
    font-size: 13px;
    text-align: left;
}}
QPushButton:hover {{
    border-color: {C_ACCENT};
    background: rgba(47,107,82,0.15);
}}
QPushButton:pressed {{
    background: rgba(47,107,82,0.3);
}}
"""


# ── Worker pentru DD ─────────────────────────────────────────
class FlashWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, iso_path, target, mode="usb"):
        super().__init__()
        self.iso_path = iso_path
        self.target   = target  # ex: /dev/sdb sau \\.\PhysicalDrive1
        self.mode     = mode    # "usb" sau "pc"

    def run(self):
        try:
            iso_size = os.path.getsize(self.iso_path)
            self.progress.emit(0, "Se pregateste scrierea...")

            if IS_WINDOWS:
                self._flash_windows(iso_size)
            else:
                self._flash_linux(iso_size)

        except Exception as e:
            self.finished.emit(False, str(e))

    def _flash_linux(self, iso_size):
        """dd if=iso of=target bs=4M status=progress"""
        cmd = ["dd", f"if={self.iso_path}", f"of={self.target}",
               "bs=4M", "conv=fsync", "status=progress"]

        proc = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            text=True
        )

        written = 0
        for line in proc.stderr:
            # dd scrie progress pe stderr: "104857600 bytes (105 MB, 100 MiB) copied"
            if "bytes" in line and "copied" in line:
                try:
                    written = int(line.split()[0])
                    pct = min(int(written / iso_size * 100), 99)
                    mb = written // (1024 * 1024)
                    total_mb = iso_size // (1024 * 1024)
                    self.progress.emit(pct, f"{mb} MB / {total_mb} MB scrise...")
                except Exception:
                    pass

        proc.wait()
        if proc.returncode == 0:
            self.progress.emit(100, "Se sincronizeaza...")
            subprocess.run(["sync"], check=False)
            self.finished.emit(True, "Gata! Velora Linux a fost scris cu succes.")
        else:
            self.finished.emit(False, f"Eroare la scriere (cod {proc.returncode})")

    def _flash_windows(self, iso_size):
        """Pe Windows folosim dd.exe din pachetul inclus sau PowerShell"""
        # Calea catre dd.exe (inclus langa script)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dd_exe = os.path.join(script_dir, "dd.exe")

        if os.path.exists(dd_exe):
            cmd = [dd_exe, f"if={self.iso_path}", f"of={self.target}",
                   "bs=4M", "--progress"]
            proc = subprocess.Popen(cmd, stderr=subprocess.PIPE,
                                    stdout=subprocess.DEVNULL, text=True)
            for line in proc.stderr:
                if "%" in line:
                    try:
                        pct = int(line.strip().replace("%",""))
                        self.progress.emit(pct, f"Se scrie... {pct}%")
                    except Exception:
                        pass
            proc.wait()
            ok = proc.returncode == 0
        else:
            # Fallback: PowerShell cu StreamReader
            self.progress.emit(5, "Se foloseste PowerShell pentru scriere...")
            ps_script = f"""
$isoPath = '{self.iso_path}'
$target  = '{self.target}'
$bs = 4MB
$inStream  = [System.IO.File]::OpenRead($isoPath)
$outStream = [System.IO.File]::Open($target, 'Open', 'Write')
$buf = New-Object byte[] $bs
$total = $inStream.Length
$written = 0
while (($read = $inStream.Read($buf, 0, $buf.Length)) -gt 0) {{
    $outStream.Write($buf, 0, $read)
    $written += $read
    $pct = [int]($written * 100 / $total)
    Write-Output $pct
}}
$outStream.Flush()
$outStream.Close()
$inStream.Close()
"""
            proc = subprocess.Popen(
                ["powershell", "-Command", ps_script],
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
            )
            iso_mb = iso_size // (1024*1024)
            for line in proc.stdout:
                try:
                    pct = int(line.strip())
                    mb = pct * iso_mb // 100
                    self.progress.emit(pct, f"{mb} MB / {iso_mb} MB scrise...")
                except Exception:
                    pass
            proc.wait()
            ok = proc.returncode == 0

        if ok:
            self.progress.emit(100, "Finalizat!")
            self.finished.emit(True, "Gata! Velora Linux a fost scris cu succes.")
        else:
            self.finished.emit(False, "Eroare la scriere. Incearca cu drepturi de administrator.")


# ── Obtine lista de discuri ───────────────────────────────────
def get_drives(include_all=False):
    """Returneaza lista [(display_name, device_path)]"""
    drives = []
    if IS_WINDOWS:
        try:
            result = subprocess.run(
                ["wmic", "diskdrive", "get", "Caption,DeviceID,Size", "/format:csv"],
                capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                parts = line.strip().split(",")
                if len(parts) >= 4 and "PhysicalDrive" in parts[2]:
                    caption = parts[1].strip()
                    device  = parts[2].strip()
                    size_b  = int(parts[3].strip()) if parts[3].strip().isdigit() else 0
                    size_gb = size_b // (1024**3)
                    if include_all or size_gb < 128:  # USB = sub 128GB
                        drives.append((f"{caption} ({size_gb} GB) — {device}", device))
        except Exception:
            pass
    else:
        try:
            result = subprocess.run(
                ["lsblk", "-d", "-o", "NAME,SIZE,MODEL,TYPE", "--json"],
                capture_output=True, text=True, timeout=5
            )
            import json
            data = json.loads(result.stdout)
            for dev in data.get("blockdevices", []):
                if dev.get("type") == "disk":
                    name  = dev.get("name", "")
                    size  = dev.get("size", "?")
                    model = dev.get("model", "").strip()
                    path  = f"/dev/{name}"
                    # Exclude disk-ul de sistem (sda de obicei) daca nu include_all
                    if not include_all and name == "sda":
                        continue
                    drives.append((f"{model or name}  {size}  ({path})", path))
        except Exception:
            pass

    return drives


# ── Fereastra principala ──────────────────────────────────────
class VeloraFlasher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Velora Flasher")
        self.setFixedSize(600, 500)
        self.setStyleSheet(STYLE)

        self._iso_path = None
        self._mode     = None  # "usb" sau "pc"

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self._build_page_welcome()
        self._build_page_usb()
        self._build_page_pc()
        self._build_page_progress()
        self._build_page_done()

        self.stack.setCurrentIndex(0)

    # ── Pagina 0: Welcome ─────────────────────────────────────
    def _build_page_welcome(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(0)

        # Logo + titlu
        logo = QLabel("▲")
        logo.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        logo.setStyleSheet(f"color: {C_ACCENT}; background: transparent;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        title = QLabel("Velora Flasher")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_TEXT};")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Instaleaza Velora Linux pe PC-ul tau sau pe un stick USB")
        sub.setStyleSheet(f"color: {C_MUTED}; font-size: 13px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setWordWrap(True)
        layout.addWidget(sub)

        layout.addSpacing(40)

        # Doua butoane optiuni
        btn_usb = QPushButton()
        btn_usb.setStyleSheet(BTN_OPTION)
        btn_usb.setMinimumHeight(90)
        btn_usb_layout = QVBoxLayout()
        btn_usb_layout.setContentsMargins(16, 12, 16, 12)
        lbl_usb_title = QLabel("💾  Flasheaza pe USB")
        lbl_usb_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_usb_title.setStyleSheet(f"color: {C_TEXT};")
        lbl_usb_desc = QLabel("Scrie ISO-ul pe un stick USB ca sa bootezi pe orice PC")
        lbl_usb_desc.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        btn_usb_layout.addWidget(lbl_usb_title)
        btn_usb_layout.addWidget(lbl_usb_desc)
        btn_usb.setLayout(btn_usb_layout)
        btn_usb.clicked.connect(lambda: self._go_usb())
        layout.addWidget(btn_usb)

        layout.addSpacing(12)

        btn_pc = QPushButton()
        btn_pc.setStyleSheet(BTN_OPTION)
        btn_pc.setMinimumHeight(90)
        btn_pc_layout = QVBoxLayout()
        btn_pc_layout.setContentsMargins(16, 12, 16, 12)
        lbl_pc_title = QLabel("🖥️  Instaleaza pe PC-ul meu")
        lbl_pc_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_pc_title.setStyleSheet(f"color: {C_TEXT};")
        lbl_pc_desc = QLabel("Instaleaza Velora Linux permanent pe acest calculator")
        lbl_pc_desc.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        btn_pc_layout.addWidget(lbl_pc_title)
        btn_pc_layout.addWidget(lbl_pc_desc)
        btn_pc.setLayout(btn_pc_layout)
        btn_pc.clicked.connect(lambda: self._go_pc())
        layout.addWidget(btn_pc)

        layout.addStretch()

        ver = QLabel("Velora Flasher 1.0  •  velora-ro.github.io")
        ver.setStyleSheet(f"color: rgba(122,158,135,0.4); font-size: 10px;")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver)

        page.setLayout(layout)
        self.stack.addWidget(page)  # index 0

    # ── Pagina 1: USB ─────────────────────────────────────────
    def _build_page_usb(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(12)

        title = QLabel("💾  Flasheaza pe USB")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_TEXT};")
        layout.addWidget(title)

        sub = QLabel("Selecteaza fisierul ISO si stick-ul USB pe care vrei sa scrii.")
        sub.setStyleSheet(f"color: {C_MUTED};")
        sub.setWordWrap(True)
        layout.addWidget(sub)

        layout.addSpacing(10)

        # ISO
        lbl_iso = QLabel("Fisier ISO:")
        lbl_iso.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_iso)

        iso_row = QHBoxLayout()
        self.lbl_iso_path_usb = QLabel("Niciun fisier selectat")
        self.lbl_iso_path_usb.setStyleSheet(f"""
            color: {C_TEXT}; background: {C_CARD};
            border-radius: 10px; padding: 10px 14px;
            border: 1px solid rgba(47,107,82,0.3);
        """)
        self.lbl_iso_path_usb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_browse_usb = QPushButton("Cauta...")
        btn_browse_usb.setStyleSheet(BTN_GHOST)
        btn_browse_usb.setFixedWidth(100)
        btn_browse_usb.clicked.connect(lambda: self._browse_iso("usb"))
        iso_row.addWidget(self.lbl_iso_path_usb)
        iso_row.addWidget(btn_browse_usb)
        layout.addLayout(iso_row)

        layout.addSpacing(6)

        # USB
        lbl_usb = QLabel("Stick USB:")
        lbl_usb.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_usb)

        usb_row = QHBoxLayout()
        self.combo_usb = QComboBox()
        self.combo_usb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        usb_row.addWidget(self.combo_usb)
        btn_refresh_usb = QPushButton("↻")
        btn_refresh_usb.setStyleSheet(BTN_GHOST)
        btn_refresh_usb.setFixedWidth(50)
        btn_refresh_usb.clicked.connect(lambda: self._refresh_drives("usb"))
        usb_row.addWidget(btn_refresh_usb)
        layout.addLayout(usb_row)

        self._refresh_drives("usb")

        # Warning
        warn = QLabel("⚠️  Atentie: Tot ce e pe stick-ul USB va fi sters!")
        warn.setStyleSheet(f"color: {C_WARNING}; font-size: 12px; padding: 8px 0;")
        warn.setWordWrap(True)
        layout.addWidget(warn)

        layout.addStretch()

        # Butoane
        btn_row = QHBoxLayout()
        btn_back = QPushButton("← Inapoi")
        btn_back.setStyleSheet(BTN_GHOST)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.btn_start_usb = QPushButton("⚡  Scrie pe USB")
        self.btn_start_usb.setStyleSheet(BTN_PRIMARY)
        self.btn_start_usb.clicked.connect(self._confirm_and_flash_usb)

        btn_row.addWidget(btn_back)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_start_usb)
        layout.addLayout(btn_row)

        page.setLayout(layout)
        self.stack.addWidget(page)  # index 1

    # ── Pagina 2: PC ──────────────────────────────────────────
    def _build_page_pc(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(12)

        title = QLabel("🖥️  Instaleaza pe PC")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_TEXT};")
        layout.addWidget(title)

        sub = QLabel("Selecteaza fisierul ISO si disk-ul pe care vrei sa instalezi Velora Linux.")
        sub.setStyleSheet(f"color: {C_MUTED};")
        sub.setWordWrap(True)
        layout.addWidget(sub)

        layout.addSpacing(10)

        # ISO
        lbl_iso = QLabel("Fisier ISO:")
        lbl_iso.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_iso)

        iso_row = QHBoxLayout()
        self.lbl_iso_path_pc = QLabel("Niciun fisier selectat")
        self.lbl_iso_path_pc.setStyleSheet(f"""
            color: {C_TEXT}; background: {C_CARD};
            border-radius: 10px; padding: 10px 14px;
            border: 1px solid rgba(47,107,82,0.3);
        """)
        self.lbl_iso_path_pc.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        btn_browse_pc = QPushButton("Cauta...")
        btn_browse_pc.setStyleSheet(BTN_GHOST)
        btn_browse_pc.setFixedWidth(100)
        btn_browse_pc.clicked.connect(lambda: self._browse_iso("pc"))
        iso_row.addWidget(self.lbl_iso_path_pc)
        iso_row.addWidget(btn_browse_pc)
        layout.addLayout(iso_row)

        layout.addSpacing(6)

        # Disk
        lbl_disk = QLabel("Disk tinta:")
        lbl_disk.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        layout.addWidget(lbl_disk)

        disk_row = QHBoxLayout()
        self.combo_pc = QComboBox()
        self.combo_pc.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        disk_row.addWidget(self.combo_pc)
        btn_refresh_pc = QPushButton("↻")
        btn_refresh_pc.setStyleSheet(BTN_GHOST)
        btn_refresh_pc.setFixedWidth(50)
        btn_refresh_pc.clicked.connect(lambda: self._refresh_drives("pc"))
        disk_row.addWidget(btn_refresh_pc)
        layout.addLayout(disk_row)

        self._refresh_drives("pc")

        # Warning mare
        warn = QFrame()
        warn.setStyleSheet(f"""
            QFrame {{
                background: rgba(220,80,80,0.1);
                border: 1px solid rgba(220,80,80,0.4);
                border-radius: 10px;
                padding: 8px;
            }}
        """)
        warn_layout = QVBoxLayout()
        warn_layout.setContentsMargins(12, 10, 12, 10)
        w1 = QLabel("⚠️  ATENTIE: Aceasta operatiune va sterge TOT de pe disk-ul selectat!")
        w1.setStyleSheet(f"color: {C_DANGER}; font-weight: bold; font-size: 13px;")
        w1.setWordWrap(True)
        w2 = QLabel("Asigura-te ca ai backup la toate datele importante inainte sa continui.")
        w2.setStyleSheet(f"color: {C_WARNING}; font-size: 12px;")
        w2.setWordWrap(True)
        warn_layout.addWidget(w1)
        warn_layout.addWidget(w2)
        warn.setLayout(warn_layout)
        layout.addWidget(warn)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_back = QPushButton("← Inapoi")
        btn_back.setStyleSheet(BTN_GHOST)
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.btn_start_pc = QPushButton("🖥️  Instaleaza Velora")
        self.btn_start_pc.setStyleSheet(BTN_PRIMARY.replace(C_PRIMARY, C_DANGER).replace(C_ACCENT, "#e06060"))
        self.btn_start_pc.clicked.connect(self._confirm_and_flash_pc)

        btn_row.addWidget(btn_back)
        btn_row.addStretch()
        btn_row.addWidget(self.btn_start_pc)
        layout.addLayout(btn_row)

        page.setLayout(layout)
        self.stack.addWidget(page)  # index 2

    # ── Pagina 3: Progress ────────────────────────────────────
    def _build_page_progress(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 60, 50, 60)
        layout.setSpacing(16)
        layout.addStretch()

        self.lbl_progress_title = QLabel("Se scrie ISO-ul...")
        self.lbl_progress_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self.lbl_progress_title.setStyleSheet(f"color: {C_TEXT};")
        self.lbl_progress_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_progress_title)

        self.lbl_progress_sub = QLabel("Nu opri computerul in timpul scrierii!")
        self.lbl_progress_sub.setStyleSheet(f"color: {C_MUTED};")
        self.lbl_progress_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_progress_sub)

        layout.addSpacing(20)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        layout.addWidget(self.progress_bar)

        self.lbl_progress_detail = QLabel("0 MB / 0 MB")
        self.lbl_progress_detail.setStyleSheet(f"color: {C_MUTED}; font-size: 12px;")
        self.lbl_progress_detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_progress_detail)

        layout.addStretch()
        page.setLayout(layout)
        self.stack.addWidget(page)  # index 3

    # ── Pagina 4: Done ────────────────────────────────────────
    def _build_page_done(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 60, 50, 60)
        layout.setSpacing(12)
        layout.addStretch()

        check = QLabel("✓")
        check.setFont(QFont("Segoe UI", 64))
        check.setStyleSheet(f"color: {C_ACCENT};")
        check.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(check)

        self.lbl_done_title = QLabel("Gata!")
        self.lbl_done_title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        self.lbl_done_title.setStyleSheet(f"color: {C_TEXT};")
        self.lbl_done_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_done_title)

        self.lbl_done_sub = QLabel("")
        self.lbl_done_sub.setStyleSheet(f"color: {C_MUTED}; font-size: 13px;")
        self.lbl_done_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_done_sub.setWordWrap(True)
        layout.addWidget(self.lbl_done_sub)

        layout.addSpacing(30)

        btn_restart = QPushButton("↩  Flasheaza din nou")
        btn_restart.setStyleSheet(BTN_GHOST)
        btn_restart.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        btn_close = QPushButton("Inchide")
        btn_close.setStyleSheet(BTN_PRIMARY)
        btn_close.clicked.connect(self.close)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(btn_restart)
        btn_row.addWidget(btn_close)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        layout.addStretch()
        page.setLayout(layout)
        self.stack.addWidget(page)  # index 4

    # ── Helpers ───────────────────────────────────────────────
    def _go_usb(self):
        self._mode = "usb"
        self.stack.setCurrentIndex(1)

    def _go_pc(self):
        self._mode = "pc"
        self.stack.setCurrentIndex(2)

    def _browse_iso(self, mode):
        path, _ = QFileDialog.getOpenFileName(
            self, "Selecteaza ISO Velora Linux", "",
            "ISO Files (*.iso);;All Files (*)"
        )
        if path:
            self._iso_path = path
            name = os.path.basename(path)
            if mode == "usb":
                self.lbl_iso_path_usb.setText(name)
            else:
                self.lbl_iso_path_pc.setText(name)

    def _refresh_drives(self, mode):
        include_all = (mode == "pc")
        drives = get_drives(include_all=include_all)
        combo = self.combo_usb if mode == "usb" else self.combo_pc
        combo.clear()
        if drives:
            for label, path in drives:
                combo.addItem(label, path)
        else:
            combo.addItem("Niciun disk detectat", None)

    def _get_selected_drive(self, mode):
        combo = self.combo_usb if mode == "usb" else self.combo_pc
        return combo.currentData()

    def _confirm_and_flash_usb(self):
        if not self._iso_path:
            QMessageBox.warning(self, "Eroare", "Selecteaza fisierul ISO mai intai!")
            return
        drive = self._get_selected_drive("usb")
        if not drive:
            QMessageBox.warning(self, "Eroare", "Selecteaza un stick USB!")
            return

        reply = QMessageBox.question(
            self, "Confirmare",
            f"Esti sigur ca vrei sa scrii ISO-ul pe:\n{drive}\n\nToate datele de pe stick vor fi sterse!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._start_flash(drive, "usb")

    def _confirm_and_flash_pc(self):
        if not self._iso_path:
            QMessageBox.warning(self, "Eroare", "Selecteaza fisierul ISO mai intai!")
            return
        drive = self._get_selected_drive("pc")
        if not drive:
            QMessageBox.warning(self, "Eroare", "Selecteaza un disk!")
            return

        reply = QMessageBox.critical(
            self, "ATENTIE - Operatiune ireversibila",
            f"Esti ABSOLUT SIGUR ca vrei sa instalezi Velora Linux pe:\n{drive}\n\nTOT CE ESTE PE ACEST DISK VA FI STERS DEFINITIV!\n\nAceasta operatiune NU poate fi anulata!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # A doua confirmare
            reply2 = QMessageBox.question(
                self, "Confirmare finala",
                "Ultima sansa! Continui cu instalarea?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply2 == QMessageBox.StandardButton.Yes:
                self._start_flash(drive, "pc")

    def _start_flash(self, drive, mode):
        self.lbl_progress_title.setText(
            "Se scrie ISO-ul pe USB..." if mode == "usb"
            else "Se instaleaza Velora Linux..."
        )
        self.progress_bar.setValue(0)
        self.lbl_progress_detail.setText("Se pregateste...")
        self.stack.setCurrentIndex(3)

        self._worker = FlashWorker(self._iso_path, drive, mode)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_progress(self, pct, msg):
        self.progress_bar.setValue(pct)
        self.lbl_progress_detail.setText(msg)

    def _on_finished(self, ok, msg):
        if ok:
            self.lbl_done_title.setText("Gata! ✓")
            if self._mode == "usb":
                self.lbl_done_sub.setText(
                    "Stick-ul USB e pregatit!\nScoate-l si boteaza de pe el pentru a rula Velora Linux."
                )
            else:
                self.lbl_done_sub.setText(
                    "Velora Linux a fost instalat!\nReporneste computerul pentru a-l folosi."
                )
        else:
            self.lbl_done_title.setText("Eroare ✗")
            self.lbl_done_sub.setText(f"A aparut o eroare:\n{msg}\n\nIncearca din nou cu drepturi de administrator.")
            check_lbl = self.stack.widget(4).findChild(QLabel, "")
            self.stack.widget(4).findChildren(QLabel)[0].setStyleSheet(f"color: {C_DANGER};")
        self.stack.setCurrentIndex(4)


# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    # Pe Linux verifica daca are root (necesar pentru dd)
    if IS_LINUX and os.geteuid() != 0:
        print("Velora Flasher trebuie rulat cu sudo pe Linux!")
        print("Incearca: sudo python3 velora-flasher.py")
        # Incearca sa se relanseze cu pkexec
        try:
            os.execvp("pkexec", ["pkexec", sys.executable] + sys.argv)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("Velora Flasher")
    window = VeloraFlasher()
    window.show()
    sys.exit(app.exec())
