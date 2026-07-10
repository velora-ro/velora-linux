#!/bin/bash
# ============================================================
#  Velora Linux - Flatpak + Apps
# ============================================================

echo "[flatpak] Setting up Flathub..."
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo

echo "[flatpak] Installing multimedia apps..."
flatpak install -y flathub org.videolan.VLC
flatpak install -y flathub com.obsproject.Studio
flatpak install -y flathub org.kde.kdenlive
flatpak install -y flathub org.gimp.GIMP

echo "[flatpak] Installing office..."
flatpak install -y flathub org.libreoffice.LibreOffice

echo "[flatpak] Installing browser..."
flatpak install -y flathub org.mozilla.firefox

echo "[flatpak] Done."
