#!/bin/bash
# ============================================================
#  Velora Linux - Gaming Stack
# ============================================================

echo "[gaming] Adding Steam repository..."
apt-get install -y software-properties-common
add-apt-repository -y multiverse 2>/dev/null || true

# Steam
echo "[gaming] Installing Steam..."
apt-get install -y steam

# Lutris
echo "[gaming] Installing Lutris..."
apt-get install -y lutris

# Gamemode + MangoHud
echo "[gaming] Installing GameMode + MangoHud..."
apt-get install -y gamemode mangohud

# Heroic Games Launcher (Flatpak)
echo "[gaming] Installing Heroic Games Launcher..."
flatpak install -y flathub com.heroicgameslauncher.hgl

# ProtonUp-Qt (Flatpak)
echo "[gaming] Installing ProtonUp-Qt..."
flatpak install -y flathub net.davidotek.pupgui2

# DXVK + VKD3D-Proton (installed via winetricks per-bottle)
echo "[gaming] Note: DXVK and VKD3D-Proton are managed per-bottle via Bottles."

echo "[gaming] Done."
