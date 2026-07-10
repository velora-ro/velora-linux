#!/bin/bash
# ============================================================
#  Velora Linux - Boot Screen Setup
#  GRUB theme + Plymouth animation + SDDM login screen
# ============================================================

set -e
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ── GRUB Theme ───────────────────────────────────────────────
echo "[grub] Installing Velora GRUB theme..."
mkdir -p /boot/grub/themes
cp -r "$REPO_DIR/branding/grub/velora-grub" /boot/grub/themes/

# Generate assets if Pillow is available
if python3 -c "import PIL" 2>/dev/null; then
    echo "[grub] Generating theme assets..."
    python3 /boot/grub/themes/velora-grub/generate_assets.py
else
    echo "[grub] Pillow not found - skipping asset generation."
    echo "[grub] Install with: pip3 install Pillow"
fi

# Set GRUB theme
sed -i 's|^#\?GRUB_THEME=.*|GRUB_THEME="/boot/grub/themes/velora-grub/theme.txt"|' \
    /etc/default/grub

# Clean boot look
sed -i 's|^#\?GRUB_TIMEOUT=.*|GRUB_TIMEOUT=5|'         /etc/default/grub
sed -i 's|^#\?GRUB_TIMEOUT_STYLE=.*|GRUB_TIMEOUT_STYLE=menu|' /etc/default/grub

# Copy wallpaper as GRUB background too
if [ -f "$REPO_DIR/wallpapers/velora-wallpaper.png" ]; then
    cp "$REPO_DIR/wallpapers/velora-wallpaper.png" \
       /boot/grub/themes/velora-grub/background.png
fi

update-grub
echo "[grub] Done."

# ── Plymouth ─────────────────────────────────────────────────
echo "[plymouth] Installing Velora Plymouth theme..."
apt-get install -y plymouth plymouth-themes

mkdir -p /usr/share/plymouth/themes/velora-plymouth
cp -r "$REPO_DIR/branding/plymouth/velora-plymouth/." \
    /usr/share/plymouth/themes/velora-plymouth/

# Set as default theme
update-alternatives --install \
    /usr/share/plymouth/themes/default.plymouth \
    default.plymouth \
    /usr/share/plymouth/themes/velora-plymouth/velora-plymouth.plymouth \
    100

update-alternatives --set \
    default.plymouth \
    /usr/share/plymouth/themes/velora-plymouth/velora-plymouth.plymouth

# Add splash to GRUB cmdline if not already there
if ! grep -q "splash" /etc/default/grub; then
    sed -i 's|GRUB_CMDLINE_LINUX_DEFAULT="\(.*\)"|GRUB_CMDLINE_LINUX_DEFAULT="\1 quiet splash"|' \
        /etc/default/grub
fi

update-initramfs -u
update-grub
echo "[plymouth] Done."

# ── SDDM Login Screen ────────────────────────────────────────
echo "[sddm] Installing Velora SDDM theme..."
apt-get install -y sddm

mkdir -p /usr/share/sddm/themes/velora-sddm
cp -r "$REPO_DIR/branding/sddm/velora-sddm/." \
    /usr/share/sddm/themes/velora-sddm/

# Copy wallpaper as SDDM background
if [ -f "$REPO_DIR/wallpapers/velora-wallpaper.png" ]; then
    cp "$REPO_DIR/wallpapers/velora-wallpaper.png" \
       /usr/share/sddm/themes/velora-sddm/background.jpg
fi

# Configure SDDM
mkdir -p /etc/sddm.conf.d
cat > /etc/sddm.conf.d/velora.conf << 'EOF'
[Theme]
Current=velora-sddm

[General]
HaltCommand=/usr/bin/systemctl poweroff
RebootCommand=/usr/bin/systemctl reboot
EOF

systemctl enable sddm
echo "[sddm] Done."

echo ""
echo "============================================"
echo "✅ Boot screens installed!"
echo "   GRUB:    velora-grub"
echo "   Plymouth: velora-plymouth"
echo "   SDDM:    velora-sddm"
echo "   Reboot to see the changes."
echo "============================================"
