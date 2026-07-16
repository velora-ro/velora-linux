#!/bin/bash
# ============================================================
#  Velora Linux - Build Script v0.8
#  XFCE desktop (QEMU compatible) + Velora green theme
# ============================================================

set -e

VELORA_VERSION="0.8"
ISO_NAME="VeloraLinux-${VELORA_VERSION}.iso"
WORK_DIR="$(pwd)/work"
CHROOT_DIR="${WORK_DIR}/chroot"
ISO_DIR="${WORK_DIR}/isoroot"

echo ""
echo "Velora Linux Build System v${VELORA_VERSION}"
echo "============================================"
echo ""

# ── Install build dependencies ────────────────────────────────
apt-get update -q
apt-get install -y \
    debootstrap squashfs-tools xorriso \
    grub-pc-bin grub-efi-amd64-bin \
    mtools dosfstools

# ── Clean previous build ──────────────────────────────────────
rm -rf "${WORK_DIR}"
mkdir -p "${CHROOT_DIR}" "${ISO_DIR}"

# ── Bootstrap Ubuntu Jammy ────────────────────────────────────
echo "[*] Bootstrapping Ubuntu 22.04..."
debootstrap \
    --arch=amd64 \
    --include=linux-image-generic,systemd-sysv,sudo,grub-pc \
    jammy \
    "${CHROOT_DIR}" \
    http://archive.ubuntu.com/ubuntu/

# ── Chroot config ─────────────────────────────────────────────
cp /etc/resolv.conf "${CHROOT_DIR}/etc/resolv.conf"
mount --bind /dev  "${CHROOT_DIR}/dev"
mount --bind /proc "${CHROOT_DIR}/proc"
mount --bind /sys  "${CHROOT_DIR}/sys"

chroot "${CHROOT_DIR}" /bin/bash <<'CHROOT_END'
set -e
export DEBIAN_FRONTEND=noninteractive
export LANG=C

# Ubuntu repos
cat > /etc/apt/sources.list << 'EOF'
deb http://archive.ubuntu.com/ubuntu jammy main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu jammy-updates main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu jammy-security main restricted universe multiverse
EOF

apt-get update -q

# Casper for live boot
apt-get install -y casper

# Generate initramfs
KERNEL_VERSION=$(ls /lib/modules/ | sort -V | tail -1)
if [ -n "$KERNEL_VERSION" ]; then
    update-initramfs -c -k "$KERNEL_VERSION" || update-initramfs -u -k all
fi

# ── XFCE Desktop (works in QEMU) ──────────────────────────────
echo "[chroot] Installing XFCE..."
apt-get install -y --no-install-recommends \
    xfce4 \
    xfce4-terminal \
    xfce4-taskmanager \
    xfce4-settings \
    xfce4-power-manager \
    lightdm \
    lightdm-gtk-greeter \
    xorg \
    xserver-xorg-video-all \
    xserver-xorg-input-all \
    network-manager \
    network-manager-gnome \
    nautilus \
    nautilus-admin \
    xdg-utils \
    papirus-icon-theme \
    wget curl git \
    python3 python3-pip \
    flatpak \
    htop \
    unzip \
    apt-transport-https \
    gnupg

# ── Brave Browser ─────────────────────────────────────────────
echo "[chroot] Installing Brave..."
curl -fsSL https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg \
    -o /usr/share/keyrings/brave-browser-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" \
    > /etc/apt/sources.list.d/brave-browser-release.list
apt-get update -q
apt-get install -y brave-browser

# ── XFCE appearance settings ─────────────────────────────────
echo "[chroot] Configuring XFCE appearance..."
mkdir -p /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml

# GTK theme + icons
cat > /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xsettings.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xsettings" version="1.0">
  <property name="Net" type="empty">
    <property name="ThemeName" type="string" value="VeloraForest"/>
    <property name="IconThemeName" type="string" value="Papirus-Dark"/>
  </property>
  <property name="Gtk" type="empty">
    <property name="FontName" type="string" value="Sans 10"/>
    <property name="CursorThemeName" type="string" value="Adwaita"/>
  </property>
</channel>
EOF

# Taskbar - Windows style (bottom panel, start button + taskbar + clock)
cat > /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-panel.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-panel" version="1.0">
  <property name="configver" type="int" value="2"/>
  <property name="panels" type="array">
    <value type="int" value="1"/>
    <property name="panel-1" type="empty">
      <property name="position" type="string" value="p=8;x=0;y=0"/>
      <property name="length" type="uint" value="100"/>
      <property name="position-locked" type="bool" value="true"/>
      <property name="size" type="uint" value="36"/>
      <property name="background-style" type="uint" value="1"/>
      <property name="background-color" type="string" value="#1a1f1cff"/>
      <property name="plugin-ids" type="array">
        <value type="int" value="1"/>
        <value type="int" value="2"/>
        <value type="int" value="3"/>
        <value type="int" value="4"/>
        <value type="int" value="5"/>
      </property>
    </property>
  </property>
  <property name="plugins" type="empty">
    <property name="plugin-1" type="string" value="applicationsmenu">
      <property name="button-title" type="string" value="Velora"/>
      <property name="show-button-title" type="bool" value="true"/>
      <property name="button-icon" type="string" value="/usr/share/pixmaps/velora-logo.png"/>
    </property>
    <property name="plugin-2" type="string" value="tasklist">
      <property name="show-labels" type="bool" value="true"/>
      <property name="grouping" type="uint" value="1"/>
    </property>
    <property name="plugin-3" type="string" value="separator">
      <property name="expand" type="bool" value="true"/>
      <property name="style" type="uint" value="0"/>
    </property>
    <property name="plugin-4" type="string" value="systray"/>
    <property name="plugin-5" type="string" value="clock">
      <property name="digital-format" type="string" value="%H:%M  %d %b"/>
    </property>
  </property>
</channel>
EOF

# Desktop wallpaper dark green
cat > /etc/skel/.config/xfce4/xfconf/xfce-perchannel-xml/xfce4-desktop.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<channel name="xfce4-desktop" version="1.0">
  <property name="backdrop" type="empty">
    <property name="screen0" type="empty">
      <property name="monitorVGA-1" type="empty">
        <property name="workspace0" type="empty">
          <property name="color-style" type="int" value="0"/>
          <property name="image-style" type="int" value="5"/>
          <property name="last-image" type="string" value="/usr/share/backgrounds/velora-wallpaper.jpg"/>
        </property>
      </property>
      <property name="monitorscreen" type="empty">
        <property name="workspace0" type="empty">
          <property name="color-style" type="int" value="0"/>
          <property name="image-style" type="int" value="5"/>
          <property name="last-image" type="string" value="/usr/share/backgrounds/velora-wallpaper.jpg"/>
        </property>
      </property>
    </property>
  </property>
  <property name="desktop-icons" type="empty">
    <property name="file-icons" type="empty">
      <property name="show-removable" type="bool" value="false"/>
      <property name="show-trash" type="bool" value="true"/>
      <property name="show-filesystem" type="bool" value="false"/>
      <property name="show-home" type="bool" value="true"/>
    </property>
  </property>
</channel>
EOF

# ── Velora logo for start button ──────────────────────────────
mkdir -p /usr/share/pixmaps
# Create simple SVG logo (V green)
cat > /usr/share/pixmaps/velora-logo.svg << 'SVGEOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" width="32" height="32">
  <rect width="32" height="32" rx="6" fill="#1a2e22"/>
  <text x="16" y="23" font-family="Arial" font-size="20" font-weight="bold"
        fill="#2F6B52" text-anchor="middle">V</text>
</svg>
SVGEOF
cp /usr/share/pixmaps/velora-logo.svg /usr/share/pixmaps/velora-logo.png || true

# ── Wallpaper ─────────────────────────────────────────────────
mkdir -p /usr/share/backgrounds
wget -q -O /usr/share/backgrounds/velora-wallpaper.jpg \
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&q=80" || \
wget -q -O /usr/share/backgrounds/velora-wallpaper.jpg \
    "https://picsum.photos/seed/velora/1920/1080" || true
# Fallback: solid dark green background
if [ ! -s /usr/share/backgrounds/velora-wallpaper.jpg ]; then
    convert -size 1920x1080 gradient:"#0d1a12"-"#1a2e22" \
        /usr/share/backgrounds/velora-wallpaper.jpg 2>/dev/null || \
    apt-get install -y imagemagick && \
    convert -size 1920x1080 gradient:"#0d1a12"-"#1a2e22" \
        /usr/share/backgrounds/velora-wallpaper.jpg || true
fi

# ── Velora Forest Theme (GTK dark green) ──────────────────────
mkdir -p /usr/share/themes/VeloraForest/gtk-3.0

cat > /usr/share/themes/VeloraForest/gtk-3.0/gtk.css << 'CSSEOF'
@define-color accent_color #2F6B52;
@define-color window_bg_color #1a1f1c;
@define-color window_fg_color #e8f5e9;
@define-color headerbar_bg_color #161b18;
@define-color sidebar_bg_color #161b18;

window, .background {
    background-color: @window_bg_color;
    color: @window_fg_color;
}
headerbar {
    background-color: @headerbar_bg_color;
    color: @window_fg_color;
    border-bottom: 1px solid rgba(47,107,82,0.4);
}
button.suggested-action {
    background-color: @accent_color;
    color: white;
    border-radius: 6px;
}
selection, *:selected {
    background-color: rgba(47, 107, 82, 0.4);
    color: @window_fg_color;
}
rubberband, .rubberband {
    background-color: rgba(47, 107, 82, 0.2);
    border: 1px solid #2F6B52;
}
CSSEOF

cat > /usr/share/themes/VeloraForest/index.theme << 'THEMEEOF'
[Desktop Entry]
Type=X-GNOME-Metatheme
Name=VeloraForest
Comment=Velora Linux dark green theme
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=VeloraForest
IconTheme=Papirus-Dark
CursorTheme=Adwaita
THEMEEOF

# ── LightDM autologin ─────────────────────────────────────────
mkdir -p /etc/lightdm
cat > /etc/lightdm/lightdm.conf << 'LDMEOF'
[Seat:*]
autologin-user=velora
autologin-user-timeout=0
user-session=xfce
LDMEOF

# ── Xorg config for QEMU/VMs ──────────────────────────────────
mkdir -p /etc/X11
cat > /etc/X11/xorg.conf << 'XORGEOF'
Section "Device"
    Identifier "Card0"
    Driver     "vesa"
EndSection

Section "Screen"
    Identifier "Screen0"
    Device     "Card0"
    DefaultDepth 24
    SubSection "Display"
        Depth  24
        Modes  "1024x768" "800x600"
    EndSubSection
EndSection
XORGEOF

# ── Casper config ─────────────────────────────────────────────
cat > /etc/casper.conf << 'CASPEREOF'
export FLAVOUR="Velora Linux"
export WRITABLE_IMAGES="false"
export LIVE_USERNAME="velora"
export LIVE_USER_FULLNAME="Velora User"
export LIVE_USER_DEFAULT_GROUPS="audio cdrom dip floppy video plugdev netdev powerdev scanner bluetooth sudo"
CASPEREOF

# ── OS identity ───────────────────────────────────────────────
cat > /etc/os-release << 'EOF'
NAME="Velora Linux"
VERSION="0.8"
ID=velora
ID_LIKE=ubuntu
PRETTY_NAME="Velora Linux 0.8"
VERSION_ID="0.8"
HOME_URL="https://github.com/velora-ro/velora-linux"
EOF

echo "velora" > /etc/hostname

# Enable LightDM
systemctl enable lightdm

# Cleanup
apt-get clean
rm -rf /tmp/* /var/tmp/*

CHROOT_END

# ── Unmount ───────────────────────────────────────────────────
umount "${CHROOT_DIR}/dev"  || true
umount "${CHROOT_DIR}/proc" || true
umount "${CHROOT_DIR}/sys"  || true

# ── Squashfs ──────────────────────────────────────────────────
echo "[*] Creating squashfs..."
mkdir -p "${ISO_DIR}/casper"
mksquashfs \
    "${CHROOT_DIR}" \
    "${ISO_DIR}/casper/filesystem.squashfs" \
    -comp gzip -noappend -no-progress

# Manifest
chroot "${CHROOT_DIR}" dpkg-query -W --showformat='${Package} ${Version}\n' \
    > "${ISO_DIR}/casper/filesystem.manifest" 2>/dev/null || true

# ── Kernel + initrd ───────────────────────────────────────────
echo "[*] Copying kernel..."
VMLINUZ=$(find "${CHROOT_DIR}/boot" -name "vmlinuz*" -not -name "*.old" | sort -V | tail -1)
INITRD=$(find  "${CHROOT_DIR}/boot" -name "initrd*"  -not -name "*.old" | sort -V | tail -1)

[ -z "$VMLINUZ" ] && { echo "ERROR: kernel not found"; exit 1; }
[ -z "$INITRD"  ] && { echo "ERROR: initrd not found"; exit 1; }

cp "$VMLINUZ" "${ISO_DIR}/casper/vmlinuz"
cp "$INITRD"  "${ISO_DIR}/casper/initrd"

# ── Disk info ─────────────────────────────────────────────────
mkdir -p "${ISO_DIR}/.disk"
echo "Velora Linux 0.8 - Live" > "${ISO_DIR}/.disk/info"
echo "full_cd" > "${ISO_DIR}/.disk/cd_type"
touch "${ISO_DIR}/.disk/base_installable"

# ── GRUB config ───────────────────────────────────────────────
mkdir -p "${ISO_DIR}/boot/grub"

cat > "${ISO_DIR}/boot/grub/grub.cfg" << 'EOF'
set default=0
set timeout=5

insmod all_video
insmod gfxterm
insmod iso9660
insmod linux
insmod search
insmod search_label

search --no-floppy --label --set=root "VELORA_LINUX"

menuentry "Velora Linux 0.8 (Live)" {
    search --no-floppy --label --set=root "VELORA_LINUX"
    linux  /casper/vmlinuz boot=casper cdrom-detect/try-usb=true quiet splash ---
    initrd /casper/initrd
}

menuentry "Velora Linux 0.8 (Safe Mode)" {
    search --no-floppy --label --set=root "VELORA_LINUX"
    linux  /casper/vmlinuz boot=casper cdrom-detect/try-usb=true nomodeset ---
    initrd /casper/initrd
}
EOF

# ── Build ISO ─────────────────────────────────────────────────
echo "[*] Building ISO..."
mkdir -p "$(pwd)/iso"

grub-mkrescue \
    --output="$(pwd)/iso/${ISO_NAME}" \
    --modules="iso9660 squash4 loopback linux normal search search_fs_uuid search_label all_video gfxterm" \
    -volid "VELORA_LINUX" \
    "${ISO_DIR}" \
    2>&1 | tee "$(pwd)/build.log"

# ── Done ──────────────────────────────────────────────────────
if [ -f "$(pwd)/iso/${ISO_NAME}" ]; then
    SIZE=$(du -h "$(pwd)/iso/${ISO_NAME}" | cut -f1)
    echo ""
    echo "============================================"
    echo "Build complete: iso/${ISO_NAME} (${SIZE})"
    echo "============================================"
else
    echo "ERROR: ISO not found."
    exit 1
fi
