#!/bin/bash
# ============================================================
#  Velora Linux - Branding
# ============================================================

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[branding] Setting os-release..."
cp "$REPO_DIR/configs/includes.chroot/etc/os-release" /etc/os-release

echo "[branding] Setting hostname..."
echo "velora" > /etc/hostname

echo "[branding] Installing logo..."
mkdir -p /usr/share/velora
cp "$REPO_DIR/branding/velora-logo.png" /usr/share/velora/logo.png
cp "$REPO_DIR/branding/velora-logo.png" /usr/share/pixmaps/velora-logo.png

echo "[branding] Setting wallpaper..."
if [ -f "$REPO_DIR/wallpapers/velora-wallpaper.png" ]; then
    mkdir -p /usr/share/backgrounds
    cp "$REPO_DIR/wallpapers/velora-wallpaper.png" /usr/share/backgrounds/
fi

echo "[branding] Done."
