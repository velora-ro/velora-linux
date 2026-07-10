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

cat > /usr/local/bin/velora-welcome << EOF
#!/bin/bash
/opt/velora/venv/bin/python3 /opt/velora/velora-welcome/velora-welcome.py
EOF
chmod +x /usr/local/bin/velora-welcome

cp "$REPO_DIR/applications/velora-welcome/velora-welcome.desktop" \
   /etc/xdg/autostart/velora-welcome.desktop

echo "[velora-apps] Installing Velora Hub..."
cp -r "$REPO_DIR/applications/velora-hub" "$APPS_DIR/"

cat > /usr/local/bin/velora-hub << EOF
#!/bin/bash
/opt/velora/venv/bin/python3 /opt/velora/velora-hub/velora-hub.py
EOF
chmod +x /usr/local/bin/velora-hub
cp "$REPO_DIR/applications/velora-hub/velora-hub.desktop" \
   /usr/share/applications/velora-hub.desktop

echo "[velora-apps] Installing Velora Update..."
cp -r "$REPO_DIR/applications/velora-update" "$APPS_DIR/"

cat > /usr/local/bin/velora-update << EOF
#!/bin/bash
pkexec /opt/velora/venv/bin/python3 /opt/velora/velora-update/velora-update.py
EOF
chmod +x /usr/local/bin/velora-update
cp "$REPO_DIR/applications/velora-update/velora-update.desktop" \
   /usr/share/applications/velora-update.desktop

echo "[velora-apps] Installing Velora Driver Manager..."
cp -r "$REPO_DIR/applications/velora-drivers" "$APPS_DIR/"

cat > /usr/local/bin/velora-drivers << EOF
#!/bin/bash
pkexec /opt/velora/venv/bin/python3 /opt/velora/velora-drivers/velora-drivers.py
EOF
chmod +x /usr/local/bin/velora-drivers
cp "$REPO_DIR/applications/velora-drivers/velora-drivers.desktop" \
   /usr/share/applications/velora-drivers.desktop

echo "[velora-apps] Done."
