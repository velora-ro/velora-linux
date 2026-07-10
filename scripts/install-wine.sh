#!/bin/bash
# ============================================================
#  Velora Linux - Wine + Bottles
# ============================================================

echo "[wine] Adding WineHQ repository..."
dpkg --add-architecture i386
wget -qO /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
wget -qNP /etc/apt/sources.list.d/ \
    https://dl.winehq.org/wine-builds/debian/dists/bookworm/winehq-bookworm.sources

apt-get update -y

echo "[wine] Installing Wine..."
apt-get install -y --install-recommends winehq-stable
apt-get install -y winetricks

echo "[wine] Installing Bottles via Flatpak..."
flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install -y flathub com.usebottles.bottles

echo "[wine] Registering .exe handler..."
cat > /usr/share/applications/velora-wine.desktop << 'EOF'
[Desktop Entry]
Name=Windows Application
Comment=Run Windows application with Wine
Exec=wine %f
Icon=wine
Terminal=false
Type=Application
MimeType=application/x-ms-dos-executable;application/x-msi;
EOF

update-desktop-database

echo "[wine] Done."
