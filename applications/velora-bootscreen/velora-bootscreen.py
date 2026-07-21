#!/usr/bin/env python3
# ============================================================
#  Velora Boot Screen
#  Ecran grafic de boot - Live Mode sau Install
#  PyQt6, fullscreen, fundal wallpaper
# ============================================================

import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import (
    QPixmap, QFont, QColor, QPainter, QBrush,
    QLinearGradient, QPalette
)

WALLPAPER_PATHS = [
    "/usr/share/backgrounds/velora-wallpaper.jpg",
    "/usr/share/backgrounds/velora-wallpaper.png",
]

STYLE = """
QWidget#root {
    background: transparent;
}
QLabel {
    background: transparent;
}
"""

class BootScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("root")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.showFullScreen()
        self.setStyleSheet(STYLE)

        # Incarca wallpaper
        self._wallpaper = None
        for p in WALLPAPER_PATHS:
            if os.path.exists(p):
                self._wallpaper = QPixmap(p)
                break

        self._build_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Fundal wallpaper scaled
        if self._wallpaper and not self._wallpaper.isNull():
            scaled = self._wallpaper.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            # Fallback gradient verde
            grad = QLinearGradient(0, 0, 0, self.height())
            grad.setColorAt(0, QColor("#0a1f12"))
            grad.setColorAt(1, QColor("#1a3d22"))
            painter.fillRect(self.rect(), QBrush(grad))

        # Overlay semi-transparent
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
        painter.end()

    def _build_ui(self):
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setLayout(root)

        # ── Top bar ───────────────────────────────────────────
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(32, 20, 32, 0)

        # Info OS stanga
        os_info = QWidget()
        os_info.setStyleSheet("""
            QWidget {
                background: rgba(255,255,255,0.15);
                border-radius: 10px;
            }
        """)
        os_layout = QHBoxLayout()
        os_layout.setContentsMargins(14, 8, 14, 8)
        os_layout.setSpacing(10)

        # Mini logo V
        mini_logo = QLabel("V")
        mini_logo.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        mini_logo.setStyleSheet("color: #5F9E6E; background: transparent;")

        os_text = QVBoxLayout()
        os_text.setSpacing(0)
        lbl_name = QLabel("Velora Linux 0.8")
        lbl_name.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_name.setStyleSheet("color: white; background: transparent;")
        lbl_mode = QLabel("Live Mode")
        lbl_mode.setFont(QFont("Segoe UI", 9))
        lbl_mode.setStyleSheet("color: rgba(255,255,255,0.7); background: transparent;")
        os_text.addWidget(lbl_name)
        os_text.addWidget(lbl_mode)

        os_layout.addWidget(mini_logo)
        os_layout.addLayout(os_text)
        os_info.setLayout(os_layout)

        top_bar.addWidget(os_info, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        top_bar.addStretch()

        # Ora dreapta
        self.lbl_time = QLabel("00:00")
        self.lbl_time.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.lbl_time.setStyleSheet("""
            color: white;
            background: rgba(255,255,255,0.15);
            border-radius: 10px;
            padding: 8px 16px;
        """)
        self._update_time()
        timer = QTimer(self)
        timer.timeout.connect(self._update_time)
        timer.start(1000)
        top_bar.addWidget(self.lbl_time, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        root.addLayout(top_bar)
        root.addStretch()

        # ── Center: Logo + carduri ────────────────────────────
        center = QVBoxLayout()
        center.setSpacing(0)
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo Velora
        logo_widget = QWidget()
        logo_widget.setStyleSheet("background: transparent;")
        logo_layout = QVBoxLayout()
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(4)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # V mare
        lbl_v = QLabel("▲")
        lbl_v.setFont(QFont("Segoe UI", 56, QFont.Weight.Bold))
        lbl_v.setStyleSheet("color: #5F9E6E; background: transparent;")
        lbl_v.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_velora = QLabel("VELORA")
        lbl_velora.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        lbl_velora.setStyleSheet("color: white; background: transparent; letter-spacing: 8px;")
        lbl_velora.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Separator decorativ
        sep_layout = QHBoxLayout()
        sep_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sep_line1 = QFrame()
        sep_line1.setFixedSize(60, 1)
        sep_line1.setStyleSheet("background: #5F9E6E;")
        sep_lbl = QLabel("Live Environment")
        sep_lbl.setFont(QFont("Segoe UI", 11))
        sep_lbl.setStyleSheet("color: #5F9E6E; background: transparent; padding: 0 12px;")
        sep_line2 = QFrame()
        sep_line2.setFixedSize(60, 1)
        sep_line2.setStyleSheet("background: #5F9E6E;")
        sep_layout.addWidget(sep_line1)
        sep_layout.addWidget(sep_lbl)
        sep_layout.addWidget(sep_line2)

        logo_layout.addWidget(lbl_v)
        logo_layout.addWidget(lbl_velora)
        logo_layout.addLayout(sep_layout)
        logo_widget.setLayout(logo_layout)
        center.addWidget(logo_widget)

        center.addSpacing(48)

        # Carduri Live + Install
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(24)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Card Live Mode
        card_live = self._make_card(
            "💾",
            "Live Mode",
            "Try Velora without installing.\nAll changes will be lost when\nyou restart your computer.",
            "Start Velora",
            primary=True,
            callback=self._start_live
        )

        # Card Install
        card_install = self._make_card(
            "⬇",
            "Install Velora",
            "Install Velora permanently\non your computer.",
            "Install Velora",
            primary=False,
            callback=self._start_install
        )

        cards_layout.addWidget(card_live)
        cards_layout.addWidget(card_install)
        center.addLayout(cards_layout)

        # Tagline
        tagline = QLabel("Simple. Beautiful. Yours.")
        tagline.setFont(QFont("Segoe UI", 11))
        tagline.setStyleSheet("color: rgba(255,255,255,0.6); background: transparent;")
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center.addSpacing(24)
        center.addWidget(tagline)

        root.addLayout(center)
        root.addStretch()

        # ── Bottom bar ────────────────────────────────────────
        bottom = QHBoxLayout()
        bottom.setContentsMargins(24, 0, 24, 20)
        bottom.setSpacing(8)

        for label, callback in [
            ("❓  Help", self._help),
            ("ℹ️  About Velora", self._about),
            ("🖥️  System Info", self._sysinfo),
        ]:
            btn = QPushButton(label)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.15);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 18px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.25);
                }
            """)
            btn.clicked.connect(callback)
            bottom.addWidget(btn)

        bottom.addStretch()

        btn_shutdown = QPushButton("⏻  Shutdown")
        btn_shutdown.setStyleSheet("""
            QPushButton {
                background: rgba(220,80,80,0.25);
                color: white;
                border: 1px solid rgba(220,80,80,0.4);
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(220,80,80,0.5);
            }
        """)
        btn_shutdown.clicked.connect(self._shutdown)
        bottom.addWidget(btn_shutdown)

        root.addLayout(bottom)

    def _make_card(self, icon, title, desc, btn_text, primary, callback):
        card = QFrame()
        card.setFixedSize(280, 280)
        card.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.15);
                border-radius: 16px;
                border: 1px solid rgba(255,255,255,0.25);
            }
            QFrame:hover {
                background: rgba(255,255,255,0.22);
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon
        icon_container = QWidget()
        icon_container.setFixedSize(64, 64)
        icon_container.setStyleSheet("""
            QWidget {
                background: rgba(95,158,110,0.25);
                border-radius: 32px;
            }
        """)
        icon_layout = QVBoxLayout()
        icon_layout.setContentsMargins(0, 0, 0, 0)
        lbl_icon = QLabel(icon)
        lbl_icon.setFont(QFont("Segoe UI", 24))
        lbl_icon.setStyleSheet("color: #5F9E6E; background: transparent;")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(lbl_icon)
        icon_container.setLayout(icon_layout)
        layout.addWidget(icon_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Title
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #5F9E6E; background: transparent;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        # Desc
        lbl_desc = QLabel(desc)
        lbl_desc.setFont(QFont("Segoe UI", 10))
        lbl_desc.setStyleSheet("color: rgba(255,255,255,0.75); background: transparent;")
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_desc.setWordWrap(True)
        layout.addWidget(lbl_desc)

        layout.addStretch()

        # Buton
        if primary:
            btn_style = """
                QPushButton {
                    background: #2F6B52;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover { background: #5F9E6E; }
                QPushButton:pressed { background: #1e4d3a; }
            """
        else:
            btn_style = """
                QPushButton {
                    background: transparent;
                    color: white;
                    border: 2px solid rgba(255,255,255,0.5);
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.15);
                    border-color: white;
                }
            """

        btn = QPushButton(btn_text)
        btn.setStyleSheet(btn_style)
        btn.clicked.connect(callback)
        layout.addWidget(btn)

        card.setLayout(layout)
        return card

    def _update_time(self):
        from datetime import datetime
        self.lbl_time.setText(datetime.now().strftime("%H:%M"))

    def _start_live(self):
        self.close()
        # Continua boot-ul normal
        subprocess.Popen(["systemctl", "start", "display-manager"])

    def _start_install(self):
        self.close()
        # Lanseaza Calamares installer
        subprocess.Popen(["calamares"])

    def _help(self):
        subprocess.Popen(["xdg-open", "https://velora-ro.github.io"])

    def _about(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "About Velora",
            "Velora Linux 0.8\nModern. Natural. Elegant.\n\nvelora-ro.github.io")

    def _sysinfo(self):
        try:
            result = subprocess.run(["inxi", "-F"], capture_output=True, text=True)
            info = result.stdout or "inxi nu este instalat."
        except Exception:
            info = "System info indisponibil."
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "System Info", info[:800])

    def _shutdown(self):
        subprocess.run(["systemctl", "poweroff"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = app.primaryScreen().geometry()
    window = BootScreen()
    sys.exit(app.exec())
