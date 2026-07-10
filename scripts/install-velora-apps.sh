#!/bin/bash
# ============================================================
#  Velora Linux - Velora Applications
# ============================================================

APPS_DIR="/opt/velora"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[velora-apps] Setting up Python virtual environment..."
mkdir -p "$APPS_DIR"
python3 -m venv "$APPS_DIR/venv"
"$APPS_DIR/venv/bin/pip" install --upgrade pip
"$APPS_DIR/venv/bin/pip" install PyQt6

echo "[velora-apps] Installing Velora Welcome..."
cp -r "$REPO_DIR/applications/velora-welcome" "$APPS_DIR/"

# Create launcher script
cat > /usr/local/bin/velora-welcome << EOF
#!/bin/bash
/opt/velora/venv/bin/python3 /opt/velora/velora-welcome/velora-welcome.py
EOF
chmod +x /usr/local/bin/velora-welcome

# Autostart on first boot
cp "$REPO_DIR/applications/velora-welcome/velora-welcome.desktop" \
   /etc/xdg/autostart/velora-welcome.desktop

echo "[velora-apps] Done."
