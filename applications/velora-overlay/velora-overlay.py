#!/usr/bin/env python3
# ============================================================
#  Velora Overlay
#  Performance overlay - apesi Alt+F12 si apare/dispare
#  CPU temp, RAM, FPS, GPU temp + Screenshot + Record
#  PyQt6, VeloraForest dark theme
# ============================================================

import sys
import os
import subprocess
import threading
import time
import signal
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QObject, QThread,
    QPropertyAnimation, QEasingCurve, QRect
)
from PyQt6.QtGui import (
    QFont, QColor, QPainter, QBrush, QPen,
    QKeySequence, QShortcut, QPixmap, QScreen
)

# ── Culori VeloraForest ───────────────────────────────────────
C_BG        = "#0a1510"
C_SURFACE   = "#0f1e17"
C_CARD      = "#111e16"
C_PRIMARY   = "#2F6B52"
C_ACCENT    = "#5F9E6E"
C_HIGHLIGHT = "#89C17D"
C_TEXT      = "#D2EBD8"
C_MUTED     = "#7A9E87"
C_DANGER    = "#DC5050"
C_WARNING   = "#C8A830"
C_GREEN_BAR = "#2F6B52"
C_YELLOW_BAR= "#C8A830"
C_RED_BAR   = "#DC5050"

SCREENSHOTS_DIR = os.path.expanduser("~/Pictures/Velora")
RECORDINGS_DIR  = os.path.expanduser("~/Videos/Velora")

# ── Stats reader (thread separat) ─────────────────────────────
class StatsWorker(QObject):
    updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self._running = False
        self._fps_counter = 0
        self._fps_last_time = time.time()

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            stats = self._read_stats()
            self.updated.emit(stats)
            time.sleep(1.0)

    def _read_stats(self):
        stats = {
            "cpu_temp": self._cpu_temp(),
            "gpu_temp": self._gpu_temp(),
            "ram_used": self._ram_used(),
            "ram_total": self._ram_total(),
            "ram_pct": self._ram_pct(),
            "cpu_pct": self._cpu_pct(),
            "fps": self._fps(),
            "gpu_name": self._gpu_name(),
        }
        return stats

    def _cpu_temp(self):
        # sensors sau /sys/class/thermal
        paths = [
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/class/thermal/thermal_zone1/temp",
        ]
        for p in paths:
            try:
                with open(p) as f:
                    return int(f.read().strip()) // 1000
            except Exception:
                pass
        try:
            r = subprocess.run(["sensors"], capture_output=True, text=True, timeout=2)
            for line in r.stdout.splitlines():
                if "Core 0" in line or "Package" in line or "Tdie" in line:
                    parts = line.split()
                    for p in parts:
                        if p.startswith("+") and "°C" in p:
                            return int(float(p.replace("+","").replace("°C","")))
        except Exception:
            pass
        return None

    def _gpu_temp(self):
        # NVIDIA
        try:
            r = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=2
            )
            return int(r.stdout.strip())
        except Exception:
            pass
        # AMD /sys
        try:
            import glob
            for path in glob.glob("/sys/class/drm/card*/device/hwmon/hwmon*/temp1_input"):
                with open(path) as f:
                    return int(f.read().strip()) // 1000
        except Exception:
            pass
        return None

    def _ram_used(self):
        try:
            with open("/proc/meminfo") as f:
                lines = f.readlines()
            total = int(next(l.split()[1] for l in lines if l.startswith("MemTotal")))
            avail = int(next(l.split()[1] for l in lines if l.startswith("MemAvailable")))
            return (total - avail) // 1024
        except Exception:
            return 0

    def _ram_total(self):
        try:
            with open("/proc/meminfo") as f:
                lines = f.readlines()
            return int(next(l.split()[1] for l in lines if l.startswith("MemTotal"))) // 1024
        except Exception:
            return 0

    def _ram_pct(self):
        total = self._ram_total()
        used  = self._ram_used()
        return int(used / total * 100) if total > 0 else 0

    def _cpu_pct(self):
        try:
            r = subprocess.run(
                ["sh", "-c", "top -bn1 | grep 'Cpu(s)' | awk '{print $2}'"],
                capture_output=True, text=True, timeout=3
            )
            return int(float(r.stdout.strip()))
        except Exception:
            return 0

    def _fps(self):
        # Incearca sa citeasca FPS din MangoHud sau returneaza N/A
        try:
            r = subprocess.run(
                ["sh", "-c", "mangohud --version 2>/dev/null && echo ok"],
                capture_output=True, text=True, timeout=1
            )
            if "ok" in r.stdout:
                return "MangoHud"
        except Exception:
            pass
        return "N/A"

    def _gpu_name(self):
        try:
            r = subprocess.run(["lspci"], capture_output=True, text=True, timeout=2)
            for line in r.stdout.splitlines():
                if any(x in line for x in ["VGA", "3D", "Display"]):
                    return line.split(":")[-1].strip()[:30]
        except Exception:
            pass
        return "Unknown GPU"

# ── Mini bar de progres custom ────────────────────────────────
class MiniBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0
        self.setFixedHeight(6)

    def set_value(self, v):
        self.value = max(0, min(100, v))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Background
        painter.setBrush(QBrush(QColor("#1a2e22")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 3, 3)
        # Fill
        fill_w = int(self.width() * self.value / 100)
        if fill_w > 0:
            if self.value < 60:
                color = QColor(C_GREEN_BAR)
            elif self.value < 80:
                color = QColor(C_YELLOW_BAR)
            else:
                color = QColor(C_RED_BAR)
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(0, 0, fill_w, self.height(), 3, 3)
        painter.end()


# ── Rand de stat (label + valoare + bar opțional) ─────────────
def stat_row(label_text, value_text, bar_value=None):
    container = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(0, 4, 0, 4)
    layout.setSpacing(3)

    top = QHBoxLayout()
    lbl = QLabel(label_text)
    lbl.setFont(QFont("Inter", 10))
    lbl.setStyleSheet(f"color: {C_MUTED};")

    val = QLabel(value_text)
    val.setFont(QFont("Inter", 11, QFont.Weight.Bold))
    val.setStyleSheet(f"color: {C_TEXT};")
    val.setAlignment(Qt.AlignmentFlag.AlignRight)

    top.addWidget(lbl)
    top.addStretch()
    top.addWidget(val)
    layout.addLayout(top)

    bar = None
    if bar_value is not None:
        bar = MiniBar()
        bar.set_value(bar_value)
        layout.addWidget(bar)

    container.setLayout(layout)
    return container, val, bar

# ── Fereastra principala overlay ──────────────────────────────
class VeloraOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self._recording = False
        self._record_proc = None
        self._visible = False

        os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
        os.makedirs(RECORDINGS_DIR, exist_ok=True)

        # Fereastră fără borduri, deasupra tuturor, pe dreapta ecranului
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(260)

        self._build_ui()
        self._position_window()

        # Stats worker
        self._worker = StatsWorker()
        self._worker.updated.connect(self._update_stats)
        self._worker.start()

        # Animatie slide
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(300)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Hotkey global Alt+F12 — funcționează doar când fereastra e focusata
        # Pentru global hotkey folosim un timer care ascultă pe /dev/input
        self._setup_hotkey()

        # Ascunde la start
        self.hide()

    def _build_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(0)
        self.setLayout(root)

        # Card principal
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(10, 21, 16, 0.95);
                border-radius: 16px;
                border: 1px solid rgba(47, 107, 82, 0.4);
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 160))
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(8)
        card.setLayout(card_layout)

        # Header
        header = QHBoxLayout()
        logo = QLabel("🌲")
        logo.setFont(QFont("Inter", 14))
        title = QLabel("Velora Overlay")
        title.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_HIGHLIGHT};")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(22, 22)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {C_MUTED};
                border: none;
                font-size: 12px;
                border-radius: 11px;
            }}
            QPushButton:hover {{ background: rgba(220,80,80,0.3); color: {C_DANGER}; }}
        """)
        close_btn.clicked.connect(self.toggle_overlay)
        header.addWidget(logo)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        card_layout.addLayout(header)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: rgba(47,107,82,0.3);")
        card_layout.addWidget(sep)
        card_layout.addSpacing(4)

        # ── Stats ──
        # CPU Temp
        row, self.lbl_cpu_temp, self.bar_cpu_temp = stat_row("CPU Temp", "-- °C", 0)
        card_layout.addWidget(row)

        # GPU Temp
        row, self.lbl_gpu_temp, self.bar_gpu_temp = stat_row("GPU Temp", "-- °C", 0)
        card_layout.addWidget(row)

        # CPU Usage
        row, self.lbl_cpu_pct, self.bar_cpu_pct = stat_row("CPU Usage", "--%", 0)
        card_layout.addWidget(row)

        # RAM
        row, self.lbl_ram, self.bar_ram = stat_row("RAM", "-- / -- MB", 0)
        card_layout.addWidget(row)

        # FPS
        row_fps, self.lbl_fps, _ = stat_row("FPS", "N/A")
        card_layout.addWidget(row_fps)

        card_layout.addSpacing(8)
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet(f"color: rgba(47,107,82,0.3);")
        card_layout.addWidget(sep2)
        card_layout.addSpacing(6)

        # ── Butoane ──
        btn_style = f"""
            QPushButton {{
                background: rgba(47,107,82,0.25);
                color: {C_TEXT};
                border: 1px solid rgba(47,107,82,0.4);
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 12px;
                text-align: left;
            }}
            QPushButton:hover {{
                background: rgba(47,107,82,0.5);
                border-color: {C_ACCENT};
            }}
            QPushButton:pressed {{
                background: rgba(47,107,82,0.7);
            }}
        """
        btn_record_style_active = f"""
            QPushButton {{
                background: rgba(220,80,80,0.3);
                color: {C_DANGER};
                border: 1px solid rgba(220,80,80,0.5);
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 12px;
                text-align: left;
            }}
            QPushButton:hover {{ background: rgba(220,80,80,0.5); }}
        """

        self.btn_screenshot = QPushButton("📷  Screenshot")
        self.btn_screenshot.setStyleSheet(btn_style)
        self.btn_screenshot.clicked.connect(self.take_screenshot)

        self.btn_record = QPushButton("⏺  Inregistreaza")
        self.btn_record.setStyleSheet(btn_style)
        self.btn_record.clicked.connect(self.toggle_recording)
        self._btn_record_normal = btn_style
        self._btn_record_active = btn_record_style_active

        self.btn_open_folder = QPushButton("📁  Deschide folderul")
        self.btn_open_folder.setStyleSheet(btn_style)
        self.btn_open_folder.clicked.connect(self.open_folder)

        card_layout.addWidget(self.btn_screenshot)
        card_layout.addWidget(self.btn_record)
        card_layout.addWidget(self.btn_open_folder)

        card_layout.addSpacing(4)
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet(f"color: {C_MUTED}; font-size: 10px;")
        self.lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_status.setWordWrap(True)
        card_layout.addWidget(self.lbl_status)

        # Hint hotkey
        hint = QLabel("Alt+F12 pentru a ascunde/arăta")
        hint.setStyleSheet(f"color: rgba(122,158,135,0.5); font-size: 9px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(hint)

        root.addWidget(card)

    def _position_window(self):
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            screen.width() - self.width() - 20,
            80,
            self.width(),
            500
        )

    def _setup_hotkey(self):
        # Shortcut in-app (funcționează când overlay-ul e focusat)
        sc = QShortcut(QKeySequence("Alt+F12"), self)
        sc.activated.connect(self.toggle_overlay)

        # Timer care verifică dacă există o comandă externă de toggle
        self._ipc_path = "/tmp/velora-overlay.toggle"
        self._ipc_timer = QTimer()
        self._ipc_timer.setInterval(200)
        self._ipc_timer.timeout.connect(self._check_ipc)
        self._ipc_timer.start()

    def _check_ipc(self):
        """Verifică dacă a fost creat fișierul IPC de toggle (de la daemon)."""
        if os.path.exists(self._ipc_path):
            try:
                os.remove(self._ipc_path)
            except Exception:
                pass
            self.toggle_overlay()

    def toggle_overlay(self):
        screen = QApplication.primaryScreen().geometry()
        w = self.width()
        h = max(self.sizeHint().height(), 460)

        shown_x  = screen.width() - w - 20
        hidden_x = screen.width() + 10
        y = 80

        if not self._visible:
            self.setGeometry(hidden_x, y, w, h)
            self.show()
            self._anim.setStartValue(QRect(hidden_x, y, w, h))
            self._anim.setEndValue(QRect(shown_x, y, w, h))
            self._anim.start()
            self._visible = True
        else:
            self._anim.setStartValue(QRect(shown_x, y, w, h))
            self._anim.setEndValue(QRect(hidden_x, y, w, h))
            self._anim.finished.connect(self._on_hide_done)
            self._anim.start()
            self._visible = False

    def _on_hide_done(self):
        self.hide()
        try:
            self._anim.finished.disconnect(self._on_hide_done)
        except Exception:
            pass

    def _update_stats(self, stats):
        # CPU Temp
        ct = stats.get("cpu_temp")
        if ct is not None:
            self.lbl_cpu_temp.setText(f"{ct} °C")
            self.bar_cpu_temp.set_value(min(ct, 100))
        else:
            self.lbl_cpu_temp.setText("N/A")

        # GPU Temp
        gt = stats.get("gpu_temp")
        if gt is not None:
            self.lbl_gpu_temp.setText(f"{gt} °C")
            self.bar_gpu_temp.set_value(min(gt, 100))
        else:
            self.lbl_gpu_temp.setText("N/A")

        # CPU %
        cp = stats.get("cpu_pct", 0)
        self.lbl_cpu_pct.setText(f"{cp}%")
        self.bar_cpu_pct.set_value(cp)

        # RAM
        ru = stats.get("ram_used", 0)
        rt = stats.get("ram_total", 1)
        rp = stats.get("ram_pct", 0)
        self.lbl_ram.setText(f"{ru} / {rt} MB")
        self.bar_ram.set_value(rp)

        # FPS
        fps = stats.get("fps", "N/A")
        self.lbl_fps.setText(str(fps))

    def take_screenshot(self):
        self.hide()
        QTimer.singleShot(300, self._do_screenshot)

    def _do_screenshot(self):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(SCREENSHOTS_DIR, f"screenshot_{ts}.png")
        screen = QApplication.primaryScreen()
        pixmap = screen.grabWindow(0)
        pixmap.save(path, "PNG")
        if self._visible:
            self.show()
        self.lbl_status.setText(f"✅ Salvat: screenshot_{ts}.png")
        QTimer.singleShot(3000, lambda: self.lbl_status.setText(""))

    def toggle_recording(self):
        if not self._recording:
            self._start_recording()
        else:
            self._stop_recording()

    def _start_recording(self):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(RECORDINGS_DIR, f"recording_{ts}.mp4")
        self._record_path = path

        # Incearca ffmpeg cu x11grab
        screen = QApplication.primaryScreen().geometry()
        cmd = [
            "ffmpeg", "-y",
            "-f", "x11grab",
            "-r", "30",
            "-s", f"{screen.width()}x{screen.height()}",
            "-i", os.environ.get("DISPLAY", ":0"),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "28",
            path
        ]
        try:
            self._record_proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self._recording = True
            self.btn_record.setText("⏹  Opreste inregistrarea")
            self.btn_record.setStyleSheet(self._btn_record_active)
            self.lbl_status.setText("🔴 Inregistrare activa...")
        except FileNotFoundError:
            self.lbl_status.setText("❌ ffmpeg negasit. Instaleaza-l cu: sudo apt install ffmpeg")

    def _stop_recording(self):
        if self._record_proc:
            self._record_proc.send_signal(signal.SIGINT)
            self._record_proc.wait()
            self._record_proc = None
        self._recording = False
        self.btn_record.setText("⏺  Inregistreaza")
        self.btn_record.setStyleSheet(self._btn_record_normal)
        self.lbl_status.setText(f"✅ Salvat in Videos/Velora")
        QTimer.singleShot(3000, lambda: self.lbl_status.setText(""))

    def open_folder(self):
        # Deschide folderul Screenshots sau Videos in Dolphin
        subprocess.Popen(["xdg-open", SCREENSHOTS_DIR])

    def closeEvent(self, event):
        if self._recording:
            self._stop_recording()
        self._worker.stop()
        event.accept()


# ── Daemon pentru hotkey global (Alt+F12) ─────────────────────
DAEMON_SCRIPT = """#!/usr/bin/env python3
# velora-overlay-daemon.py
# Ascultă Alt+F12 global și trimite semnal la overlay prin IPC

import subprocess
import os
import time

IPC_PATH = "/tmp/velora-overlay.toggle"

def listen():
    try:
        import evdev
        from evdev import InputDevice, categorize, ecodes

        devices = [InputDevice(path) for path in evdev.list_devices()]
        keyboards = [d for d in devices if ecodes.EV_KEY in d.capabilities()]
        if not keyboards:
            print("Nu s-a gasit nicio tastatura.")
            return

        # Monitorizare Alt+F12
        alt_held = False
        for event in keyboards[0].read_loop():
            if event.type == ecodes.EV_KEY:
                key = categorize(event)
                if key.scancode == ecodes.KEY_LEFTALT or key.scancode == ecodes.KEY_RIGHTALT:
                    alt_held = (key.keystate == key.key_down)
                if key.scancode == ecodes.KEY_F12 and key.keystate == key.key_down and alt_held:
                    open(IPC_PATH, 'w').close()
    except ImportError:
        print("evdev negasit, hotkey global dezactivat.")
        print("Instaleaza cu: pip3 install evdev")

if __name__ == "__main__":
    listen()
"""

# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Velora Overlay")
    app.setQuitOnLastWindowClosed(False)

    overlay = VeloraOverlay()
    overlay.toggle_overlay()  # Arata la start

    # System tray icon (optional - dacă PyQt6 are suport)
    try:
        from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
        from PyQt6.QtGui import QIcon

        tray = QSystemTrayIcon(app)
        tray_icon = QPixmap(24, 24)
        tray_icon.fill(QColor(C_PRIMARY))
        tray.setIcon(QIcon(tray_icon))
        tray.setToolTip("Velora Overlay — Alt+F12")

        tray_menu = QMenu()
        act_toggle = tray_menu.addAction("Arata/Ascunde (Alt+F12)")
        act_toggle.triggered.connect(overlay.toggle_overlay)
        tray_menu.addSeparator()
        act_quit = tray_menu.addAction("Inchide")
        act_quit.triggered.connect(app.quit)

        tray.setContextMenu(tray_menu)
        tray.activated.connect(lambda reason: overlay.toggle_overlay()
                               if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
        tray.show()
    except Exception as e:
        print(f"Tray icon indisponibil: {e}")

    sys.exit(app.exec())
