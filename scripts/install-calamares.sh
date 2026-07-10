#!/bin/bash
# ============================================================
#  Velora Linux - Install & Configure Calamares
# ============================================================

set -e
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[calamares] Installing Calamares..."
apt-get install -y \
    calamares \
    calamares-settings-debian \
    qml-module-qtquick2 \
    qml-module-qtquick-controls2 \
    qml-module-qtquick-layouts \
    qml-module-qtgraphicaleffects

echo "[calamares] Copying Velora config..."
mkdir -p /etc/calamares/modules
mkdir -p /usr/share/calamares/branding/velora

# Main settings
cp "$REPO_DIR/configs/calamares/settings.conf" /etc/calamares/

# Module configs
cp "$REPO_DIR/configs/calamares/modules/"*.conf /etc/calamares/modules/

# Branding
cp -r "$REPO_DIR/configs/calamares/branding/velora/." \
    /usr/share/calamares/branding/velora/

# Copy logo to branding folder
cp "$REPO_DIR/branding/velora-logo.png" \
    /usr/share/calamares/branding/velora/logo.png

echo "[calamares] Done."
