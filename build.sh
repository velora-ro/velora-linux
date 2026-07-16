#!/bin/bash
# ============================================================
#  Velora Linux - Build Script v0.8
#  GNOME desktop + VeloraForest theme (hardware real)
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

# ── Build dependencies ────────────────────────────────────────
apt-get update -q
apt-get install -y \
    debootstrap squashfs-tools xorriso \
    grub-pc-bin grub-efi-amd64-bin \
    mtools dosfstools imagemagick

# ── Clean ─────────────────────────────────────────────────────
rm -rf "${WORK_DIR}"
mkdir -p "${CHROOT_DIR}" "${ISO_DIR}"

# ── Bootstrap ─────────────────────────────────────────────────
echo "[*] Bootstrapping Ubuntu 22.04..."
debootstrap \
    --arch=amd64 \
    --include=linux-image-generic,systemd-sysv,sudo,grub-pc \
    jammy \
    "${CHROOT_DIR}" \
    http://archive.ubuntu.com/ubuntu/

# ── Chroot setup ─────────────────────────────────────────────
cp /etc/resolv.conf "${CHROOT_DIR}/etc/resolv.conf"
mount --bind /dev  "${CHROOT_DIR}/dev"
mount --bind /proc "${CHROOT_DIR}/proc"
mount --bind /sys  "${CHROOT_DIR}/sys"

chroot "${CHROOT_DIR}" /bin/bash <<'CHROOT_END'
set -e
export DEBIAN_FRONTEND=noninteractive
export LANG=C

cat > /etc/apt/sources.list << 'EOF'
deb http://archive.ubuntu.com/ubuntu jammy main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu jammy-updates main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu jammy-security main restricted universe multiverse
EOF

apt-get update -q

# Casper
apt-get install -y casper

# Initramfs
KERNEL_VERSION=$(ls /lib/modules/ | sort -V | tail -1)
if [ -n "$KERNEL_VERSION" ]; then
    update-initramfs -c -k "$KERNEL_VERSION" || update-initramfs -u -k all
fi

# ── GNOME Desktop ─────────────────────────────────────────────
echo "[chroot] Installing GNOME..."
apt-get install -y --no-install-recommends \
    gnome-shell \
    gnome-session \
    gnome-control-center \
    gnome-tweaks \
    gnome-shell-extensions \
    gdm3 \
    xorg \
    xserver-xorg-video-all \
    xserver-xorg-input-all \
    network-manager \
    network-manager-gnome \
    nautilus \
    nautilus-admin \
    xdg-utils \
    gnome-terminal \
    gnome-text-editor \
    papirus-icon-theme \
    wget curl git \
    python3 python3-pip \
    flatpak \
    gnome-software \
    gnome-software-plugin-flatpak \
    htop \
    unzip \
    imagemagick \
    apt-transport-https gnupg

# ── Brave Browser ─────────────────────────────────────────────
echo "[chroot] Installing Brave..."
curl -fsSL https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg \
    -o /usr/share/keyrings/brave-browser-archive-keyring.gpg 2>/dev/null || true
echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" \
    > /etc/apt/sources.list.d/brave-browser-release.list
apt-get update -q
apt-get install -y brave-browser || true

# ── Papirus Green icons ───────────────────────────────────────
# Change Papirus folder color to green
wget -qO /tmp/papirus-folders.sh \
    "https://raw.githubusercontent.com/PapirusDevelopmentTeam/papirus-folders/master/papirus-folders" || true
if [ -f /tmp/papirus-folders.sh ]; then
    chmod +x /tmp/papirus-folders.sh
    bash /tmp/papirus-folders.sh -C green --theme Papirus-Dark 2>/dev/null || true
fi

# ── VeloraForest GTK Theme ────────────────────────────────────
echo "[chroot] Building VeloraForest theme..."
mkdir -p /usr/share/themes/VeloraForest/gtk-3.0
mkdir -p /usr/share/themes/VeloraForest/gtk-4.0

cat > /usr/share/themes/VeloraForest/gtk-3.0/gtk.css << 'CSSEOF'
@define-color accent_color #2F6B52;
@define-color accent_bg_color #2F6B52;
@define-color accent_fg_color #ffffff;
@define-color window_bg_color #1a1f1c;
@define-color window_fg_color #e8f5e9;
@define-color view_bg_color #1e2520;
@define-color view_fg_color #e8f5e9;
@define-color headerbar_bg_color #161b18;
@define-color headerbar_fg_color #e8f5e9;
@define-color sidebar_bg_color #161b18;
@define-color card_bg_color rgba(30,37,32,0.95);
@define-color popover_bg_color #1e2520;

* { outline: none; }

window, .background, dialog {
    background-color: @window_bg_color;
    color: @window_fg_color;
}
headerbar, .titlebar {
    background-color: @headerbar_bg_color;
    color: @headerbar_fg_color;
    border-bottom: 1px solid rgba(47,107,82,0.3);
    border-radius: 12px 12px 0 0;
    min-height: 46px;
    padding: 0 8px;
}
headerbar button, .titlebar button {
    border-radius: 50%;
    min-width: 14px; min-height: 14px;
    padding: 0;
    border: none;
}
.view, scrolledwindow, textview {
    background-color: @view_bg_color;
    color: @view_fg_color;
}
.sidebar, placessidebar {
    background-color: @sidebar_bg_color;
    color: @window_fg_color;
    border-right: 1px solid rgba(47,107,82,0.2);
}
.sidebar row:selected, placessidebar row:selected {
    background-color: rgba(47,107,82,0.3);
    color: white;
}
button {
    background-color: rgba(47,107,82,0.15);
    color: @window_fg_color;
    border: 1px solid rgba(47,107,82,0.25);
    border-radius: 8px;
    padding: 6px 14px;
}
button:hover {
    background-color: rgba(47,107,82,0.3);
    border-color: @accent_color;
}
button.suggested-action {
    background-color: @accent_color;
    color: white;
    border: none;
}
button.suggested-action:hover {
    background-color: #3a8566;
}
entry, searchentry {
    background-color: @view_bg_color;
    color: @window_fg_color;
    border: 1px solid rgba(47,107,82,0.3);
    border-radius: 8px;
    padding: 8px 12px;
}
entry:focus, searchentry:focus {
    border-color: @accent_color;
    box-shadow: 0 0 0 2px rgba(47,107,82,0.2);
}
selection, *:selected {
    background-color: rgba(47,107,82,0.4);
    color: white;
}
rubberband, .rubberband {
    background-color: rgba(47,107,82,0.2);
    border: 1px solid @accent_color;
}
popover, .popover {
    background-color: @popover_bg_color;
    border: 1px solid rgba(47,107,82,0.3);
    border-radius: 12px;
}
tooltip {
    background-color: #1e2520;
    color: @window_fg_color;
    border-radius: 6px;
}
progressbar progress {
    background-color: @accent_color;
    border-radius: 4px;
}
switch:checked {
    background-color: @accent_color;
}
CSSEOF

# GTK4 uses same CSS
cp /usr/share/themes/VeloraForest/gtk-3.0/gtk.css \
   /usr/share/themes/VeloraForest/gtk-4.0/gtk.css

cat > /usr/share/themes/VeloraForest/index.theme << 'THEMEEOF'
[Desktop Entry]
Type=X-GNOME-Metatheme
Name=VeloraForest
Comment=Velora Linux dark green theme
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=VeloraForest
MetacityTheme=VeloraForest
IconTheme=Papirus-Dark
CursorTheme=Adwaita
ButtonLayout=close,minimize,maximize:
THEMEEOF

# ── GNOME Shell theme (top bar + overview) ────────────────────
mkdir -p /usr/share/themes/VeloraForest/gnome-shell
cat > /usr/share/themes/VeloraForest/gnome-shell/gnome-shell.css << 'SHELLCSS'
#panel {
    background-color: rgba(22,27,24,0.85);
    border-bottom: 1px solid rgba(47,107,82,0.3);
    font-size: 13px;
}
#panel .panel-button {
    color: #e8f5e9;
    padding: 0 8px;
}
#panel .panel-button:hover {
    background-color: rgba(47,107,82,0.2);
    border-radius: 6px;
}
.overview-controls .search-entry {
    background-color: rgba(30,37,32,0.9);
    border: 1px solid rgba(47,107,82,0.4);
    border-radius: 12px;
    color: #e8f5e9;
}
.app-grid .overview-icon {
    border-radius: 16px;
}
SHELLCSS

# ── GNOME dconf settings ──────────────────────────────────────
mkdir -p /etc/dconf/db/local.d /etc/dconf/profile

cat > /etc/dconf/profile/user << 'PROFEOF'
user-db:user
system-db:local
PROFEOF

cat > /etc/dconf/db/local.d/00-velora << 'DCONFEOF'
[org/gnome/desktop/interface]
gtk-theme='VeloraForest'
icon-theme='Papirus-Dark'
cursor-theme='Adwaita'
font-name='Cantarell 11'
document-font-name='Cantarell 11'
monospace-font-name='Source Code Pro 11'
color-scheme='prefer-dark'
enable-animations=true
show-battery-percentage=true

[org/gnome/desktop/background]
picture-uri='file:///usr/share/backgrounds/velora-wallpaper.jpg'
picture-uri-dark='file:///usr/share/backgrounds/velora-wallpaper.jpg'
picture-options='zoom'
primary-color='#0d1a12'
secondary-color='#1a2e22'

[org/gnome/desktop/wm/preferences]
button-layout='close,minimize,maximize:'
titlebar-font='Cantarell Bold 11'
num-workspaces=2

[org/gnome/desktop/wm/keybindings]
switch-to-workspace-left=['<Super>Left']
switch-to-workspace-right=['<Super>Right']

[org/gnome/mutter]
dynamic-workspaces=false
edge-tiling=true

[org/gnome/shell]
enabled-extensions=['dash-to-dock@micxgx.gmail.com', 'user-theme@gnome-shell-extensions.gcampax.github.com']
favorite-apps=['brave-browser.desktop', 'org.gnome.Nautilus.desktop', 'org.gnome.Terminal.desktop', 'org.gnome.Settings.desktop']
had-bluetooth-devices-setup=false

[org/gnome/shell/extensions/dash-to-dock]
dock-position='BOTTOM'
dock-fixed=true
extend-height=false
dash-max-icon-size=42
icon-size-fixed=false
transparency-mode='FIXED'
background-opacity=0.75
custom-background-color=true
background-color='#161b18'
show-apps-button=true
show-show-apps-button=true
click-action='cycle-windows'
scroll-action='cycle-windows'
animate-show-dock=true
autohide=false
intellihide=false
height-fraction=0.9
running-indicator-style='DOTS'

[org/gnome/shell/extensions/user-theme]
name='VeloraForest'

[org/gnome/nautilus/preferences]
default-folder-viewer='icon-view'
search-filter-time-type='last_modified'

[org/gnome/nautilus/icon-view]
default-zoom-level='medium'

[org/gtk/settings/file-chooser]
sort-directories-first=true
DCONFEOF

dconf update 2>/dev/null || true

# ── Dash-to-dock extension ────────────────────────────────────
echo "[chroot] Installing dash-to-dock..."
DOCK_DIR="/usr/share/gnome-shell/extensions/dash-to-dock@micxgx.gmail.com"
mkdir -p "${DOCK_DIR}"
wget -q -O /tmp/dtd.zip \
    "https://extensions.gnome.org/extension-data/dash-to-dockmicxgx.gmail.com.v84.shell-extension.zip" \
    2>/dev/null || true
if [ -f /tmp/dtd.zip ]; then
    unzip -q /tmp/dtd.zip -d "${DOCK_DIR}" 2>/dev/null || true
    rm -f /tmp/dtd.zip
fi

# ── User theme extension ──────────────────────────────────────
UTHEME_DIR="/usr/share/gnome-shell/extensions/user-theme@gnome-shell-extensions.gcampax.github.com"
if [ ! -d "${UTHEME_DIR}" ]; then
    apt-get install -y gnome-shell-extension-prefs 2>/dev/null || true
fi

# ── Velora Logo ───────────────────────────────────────────────
mkdir -p /usr/share/pixmaps
cat > /usr/share/pixmaps/velora-logo.svg << 'SVGEOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
  <rect width="48" height="48" rx="10" fill="#161b18"/>
  <polygon points="8,12 24,36 40,12 34,12 24,28 14,12" fill="#2F6B52"/>
  <polygon points="14,12 24,28 34,12 28,12 24,22 20,12" fill="#5F9E6E"/>
</svg>
SVGEOF

# ── Wallpaper ─────────────────────────────────────────────────
mkdir -p /usr/share/backgrounds
wget -q -O /usr/share/backgrounds/velora-wallpaper.jpg \
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&q=80" 2>/dev/null || \
wget -q -O /usr/share/backgrounds/velora-wallpaper.jpg \
    "https://picsum.photos/seed/velora/1920/1080" 2>/dev/null || true
# Fallback: generate gradient
if [ ! -s /usr/share/backgrounds/velora-wallpaper.jpg ]; then
    convert -size 1920x1080 \
        gradient:"#0a1a0f"-"#1a3520" \
        /usr/share/backgrounds/velora-wallpaper.jpg 2>/dev/null || true
fi

# ── GDM autologin ─────────────────────────────────────────────
mkdir -p /etc/gdm3
cat > /etc/gdm3/custom.conf << 'GDMEOF'
[daemon]
AutomaticLoginEnable=true
AutomaticLogin=velora
TimedLoginEnable=false
WaylandEnable=false

[security]
[xdmcp]
[chooser]
[debug]
GDMEOF

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
HOME_URL="https://velora-ro.github.io"
EOF

echo "velora" > /etc/hostname

# Enable GDM
systemctl enable gdm3

# Flatpak
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null || true

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

chroot "${CHROOT_DIR}" dpkg-query -W --showformat='${Package} ${Version}\n' \
    > "${ISO_DIR}/casper/filesystem.manifest" 2>/dev/null || true

# ── Kernel + initrd ───────────────────────────────────────────
VMLINUZ=$(find "${CHROOT_DIR}/boot" -name "vmlinuz*" -not -name "*.old" | sort -V | tail -1)
INITRD=$(find  "${CHROOT_DIR}/boot" -name "initrd*"  -not -name "*.old" | sort -V | tail -1)
[ -z "$VMLINUZ" ] && { echo "ERROR: kernel not found"; exit 1; }
[ -z "$INITRD"  ] && { echo "ERROR: initrd not found"; exit 1; }
cp "$VMLINUZ" "${ISO_DIR}/casper/vmlinuz"
cp "$INITRD"  "${ISO_DIR}/casper/initrd"

# ── Disk info ─────────────────────────────────────────────────
mkdir -p "${ISO_DIR}/.disk"
echo "Velora Linux 0.8" > "${ISO_DIR}/.disk/info"
echo "full_cd" > "${ISO_DIR}/.disk/cd_type"
touch "${ISO_DIR}/.disk/base_installable"

# ── GRUB ──────────────────────────────────────────────────────
mkdir -p "${ISO_DIR}/boot/grub"
cat > "${ISO_DIR}/boot/grub/grub.cfg" << 'EOF'
set default=0
set timeout=5

insmod part_msdos
insmod part_gpt
insmod iso9660
insmod all_video
insmod gfxterm
insmod linux
insmod normal
insmod search
insmod search_label
insmod configfile

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
mkdir -p "$(pwd)/iso"
grub-mkrescue \
    --output="$(pwd)/iso/${ISO_NAME}" \
    --modules="iso9660 squash4 loopback linux normal configfile search search_fs_uuid search_label search_fs_file all_video gfxterm gfxterm_background font png jpeg" \
    -volid "VELORA_LINUX" \
    "${ISO_DIR}" \
    2>&1 | tee "$(pwd)/build.log"

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
