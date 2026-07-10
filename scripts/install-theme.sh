#!/bin/bash
# ============================================================
#  Velora Linux - Apply Velora Theme
#  Forest Green + iOS 26 Glass Style
# ============================================================

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
THEME_DIR="$REPO_DIR/themes/velora-kde"

echo "[theme] Installing Velora color scheme..."
mkdir -p /usr/share/color-schemes
cp "$THEME_DIR/colors/VeloraForest" /usr/share/color-schemes/VeloraForest.colors

echo "[theme] Installing Velora Plasma theme..."
mkdir -p /usr/share/plasma/desktoptheme/velora
cp -r "$THEME_DIR/plasma/desktoptheme/velora/." /usr/share/plasma/desktoptheme/velora/

echo "[theme] Applying theme via dconf (for live session)..."
mkdir -p /etc/dconf/db/local.d

cat > /etc/dconf/db/local.d/00-velora-theme << 'EOF'
[org/kde/plasma/desktop/appletsettings]
color-scheme='VeloraForest'

[org/gnome/desktop/background]
picture-uri='file:///usr/share/backgrounds/velora-wallpaper.png'
EOF

dconf update 2>/dev/null || true

echo "[theme] Setting KDE defaults via kwriteconfig5..."
# Color scheme
kwriteconfig5 --file kdeglobals --group General --key ColorScheme VeloraForest 2>/dev/null || true

# Window decorations - rounded corners, minimal
kwriteconfig5 --file kwinrc --group org.kde.kdecoration2 --key library "org.kde.breeze" 2>/dev/null || true
kwriteconfig5 --file kwinrc --group org.kde.kdecoration2 --key theme "Breeze" 2>/dev/null || true

# Blur effect enabled
kwriteconfig5 --file kwinrc --group Plugins --key blurEnabled true 2>/dev/null || true

# Round corners
kwriteconfig5 --file kwinrc --group Effect-RoundCorners --key Enabled true 2>/dev/null || true
kwriteconfig5 --file kwinrc --group Effect-RoundCorners --key Radius 12 2>/dev/null || true

# Font - Inter
kwriteconfig5 --file kdeglobals --group General --key font "Inter,10,-1,5,50,0,0,0,0,0" 2>/dev/null || true
kwriteconfig5 --file kdeglobals --group General --key fixed "JetBrains Mono,10,-1,5,50,0,0,0,0,0" 2>/dev/null || true

echo "[theme] Installing wallpaper..."
if [ -f "$REPO_DIR/wallpapers/velora-wallpaper.png" ]; then
    mkdir -p /usr/share/backgrounds
    cp "$REPO_DIR/wallpapers/velora-wallpaper.png" /usr/share/backgrounds/
    echo "[theme] Wallpaper installed."
else
    echo "[theme] WARNING: velora-wallpaper.png not found in wallpapers/"
fi

echo "[theme] Done."
