#!/bin/bash
# ============================================================
#  Velora Overlay - Install Script
# ============================================================
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "[overlay] Installing Velora Overlay..."

# Dependente
apt-get install -y python3-pyqt6 ffmpeg lm-sensors python3-pip || true
pip3 install evdev 2>/dev/null || true

# Activeaza sensors
sensors-detect --auto 2>/dev/null || true

# Copiaza fisierele
mkdir -p /usr/share/velora/overlay
cp "$REPO_DIR/applications/velora-overlay/velora-overlay.py" \
   /usr/share/velora/overlay/

# .desktop
cp "$REPO_DIR/applications/velora-overlay/velora-overlay.desktop" \
   /usr/share/applications/

# Autostart pentru toti utilizatorii
mkdir -p /etc/skel/.config/autostart
cp "$REPO_DIR/applications/velora-overlay/velora-overlay.desktop" \
   /etc/skel/.config/autostart/

echo "[overlay] Done. Porneste cu: python3 /usr/share/velora/overlay/velora-overlay.py"
echo "[overlay] Hotkey: Alt+F12"
