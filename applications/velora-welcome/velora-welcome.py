#!/usr/bin/env python3
# ============================================================
#  Velora Welcome
#  First-boot setup wizard for Velora Linux
#  Uses PyQt6 (PySide6 compatible)
# ============================================================

import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QLineEdit, QCheckBox, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QIcon

# ============================================================
#  PAGES
# ============================================================

class WelcomePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # Logo placeholder
        logo = QLabel("🌲")
        logo.setFont(QFont("Inter", 80))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Welcome to Velora Linux")
        title.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff;")

        subtitle = QLabel("Modern. Natural. Elegant.")
        subtitle.setFont(QFont("Inter", 16))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #aaaaaa;")

        layout.addStretch()
        layout.addWidget(logo)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        self.setLayout(layout)


class DriverPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("Hardware Drivers")
        title.setFont(QFont("Inter", 28, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff;")

        self.status_label = QLabel("Detecting your hardware...")
        self.status_label.setFont(QFont("Inter", 14))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #aaaaaa;")

        self.driver_card = QFrame()
        self.driver_card.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.08);
                border-radius: 16px;
                padding: 20px;
            }
        """)
        self.driver_card.setFixedWidth(500)
        self.driver_card.hide()

        card_layout = QVBoxLayout()
        self.driver_name = QLabel("")
        self.driver_name.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        self.driver_name.setStyleSheet("color: #4ade80;")

        self.driver_desc = QLabel("")
        self.driver_desc.setFont(QFont("Inter", 12))
        self.driver_desc.setStyleSheet("color: #aaaaaa;")

        self.install_btn = QPushButton("Install Driver")
        self.install_btn.setStyleSheet("""
            QPushButton {
                background: #4ade80;
                color: #000000;
                border: none;
                border-radius: 10px;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: #22c55e; }
        """)

        self.skip_btn = QPushButton("Skip")
        self.skip_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #aaaaaa;
                border: 1px solid #444;
                border-radius: 10px;
                padding: 12px 30px;
                font-size: 14px;
            }
            QPushButton:hover { color: #ffffff; border-color: #888; }
        """)

        card_layout.addWidget(self.driver_name)
        card_layout.addWidget(self.driver_desc)
        card_layout.addSpacing(10)

        btn_row = QHBoxLayout()
        btn_row.addWidget(self.install_btn)
        btn_row.addWidget(self.skip_btn)
        card_layout.addLayout(btn_row)

        self.driver_card.setLayout(card_layout)

        layout.addStretch()
        layout.addWidget(title)
        layout.addWidget(self.status_label)
        layout.addWidget(self.driver_card, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)
        QTimer.singleShot(1000, self.detect_drivers)

    def detect_drivers(self):
        # Check for NVIDIA GPU
        try:
            result = subprocess.run(
                ["lspci"],
                capture_output=True, text=True
            )
            if "NVIDIA" in result.stdout:
                self.status_label.setText("NVIDIA GPU detected!")
                self.driver_name.setText("NVIDIA Proprietary Driver")
                self.driver_desc.setText(
                    "Recommended for best gaming and graphics performance.\n"
                    "Version: nvidia-driver-535"
                )
                self.driver_card.show()
            else:
                self.status_label.setText("No additional drivers needed.")
        except Exception:
            self.status_label.setText("Could not detect hardware.")


class FinishPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        icon = QLabel("✅")
        icon.setFont(QFont("Inter", 60))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("You're all set!")
        title.setFont(QFont("Inter", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff;")

        subtitle = QLabel("Enjoy Velora Linux 🌲")
        subtitle.setFont(QFont("Inter", 16))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #aaaaaa;")

        layout.addStretch()
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()

        self.setLayout(layout)


# ============================================================
#  MAIN WINDOW
# ============================================================

class VeloraWelcome(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Velora Welcome")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0f0f14;
                color: #ffffff;
                font-family: 'Inter', sans-serif;
            }
        """)

        # Pages
        self.pages = QStackedWidget()
        self.welcome_page = WelcomePage()
        self.driver_page = DriverPage()
        self.finish_page = FinishPage()

        self.pages.addWidget(self.welcome_page)   # 0
        self.pages.addWidget(self.driver_page)    # 1
        self.pages.addWidget(self.finish_page)    # 2

        # Navigation
        nav = QHBoxLayout()
        nav.setContentsMargins(40, 0, 40, 30)

        self.back_btn = QPushButton("← Back")
        self.back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #aaaaaa;
                border: 1px solid #444;
                border-radius: 10px;
                padding: 12px 30px;
                font-size: 14px;
            }
            QPushButton:hover { color: #ffffff; border-color: #888; }
        """)
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.hide()

        self.next_btn = QPushButton("Get Started →")
        self.next_btn.setStyleSheet("""
            QPushButton {
                background: #4ade80;
                color: #000000;
                border: none;
                border-radius: 10px;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background: #22c55e; }
        """)
        self.next_btn.clicked.connect(self.go_next)

        nav.addWidget(self.back_btn)
        nav.addStretch()
        nav.addWidget(self.next_btn)

        # Page indicator dots
        self.dots_layout = QHBoxLayout()
        self.dots_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dots = []
        for i in range(3):
            dot = QLabel("●")
            dot.setFont(QFont("Inter", 10))
            self.dots.append(dot)
            self.dots_layout.addWidget(dot)

        # Root layout
        root = QVBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self.pages)
        root.addLayout(self.dots_layout)
        root.addLayout(nav)

        container = QWidget()
        container.setLayout(root)
        self.setCentralWidget(container)

        self.current_page = 0
        self.update_dots()

    def update_dots(self):
        for i, dot in enumerate(self.dots):
            if i == self.current_page:
                dot.setStyleSheet("color: #4ade80;")
            else:
                dot.setStyleSheet("color: #444444;")

        self.back_btn.setVisible(self.current_page > 0)

        if self.current_page == len(self.dots) - 1:
            self.next_btn.setText("Finish")
        else:
            self.next_btn.setText("Continue →")

    def go_next(self):
        if self.current_page < self.pages.count() - 1:
            self.current_page += 1
            self.pages.setCurrentIndex(self.current_page)
            self.update_dots()
        else:
            # Last page - close welcome
            self.close()

    def go_back(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.pages.setCurrentIndex(self.current_page)
            self.update_dots()


# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Velora Welcome")
    window = VeloraWelcome()
    window.show()
    sys.exit(app.exec())
