#!/bin/bash
# ============================================================
#  Velora Linux - Build Script v0.8
#  GNOME desktop + VeloraForest theme
# ============================================================

set -e

VELORA_VERSION="0.8"
ISO_NAME="VeloraLinux-${VELORA_VERSION}.iso"
WORK_DIR="$(pwd)/work"
CHROOT_DIR="${WORK_DIR}/chroot"
ISO_DIR="${WORK_DIR}/isoroot"

echo "Velora Linux Build System v${VELORA_VERSION}"

# ── Build dependencies ────────────────────────────────────────
apt-get update -q
apt-get install -y \
    debootstrap squashfs-tools xorriso \
    grub-pc-bin grub-efi-amd64-bin grub-common \
    mtools dosfstools

# ── Clean ─────────────────────────────────────────────────────
rm -rf "${WORK_DIR}"
mkdir -p "${CHROOT_DIR}" "${ISO_DIR}"

# ── Bootstrap ─────────────────────────────────────────────────
echo "[*] Bootstrapping..."
debootstrap --arch=amd64 \
    --include=linux-image-generic,systemd-sysv,sudo,grub-pc \
    jammy "${CHROOT_DIR}" \
    http://archive.ubuntu.com/ubuntu/

# ── Chroot ───────────────────────────────────────────────────
cp /etc/resolv.conf "${CHROOT_DIR}/etc/resolv.conf"
mount --bind /dev  "${CHROOT_DIR}/dev"
mount --bind /proc "${CHROOT_DIR}/proc"
mount --bind /sys  "${CHROOT_DIR}/sys"

chroot "${CHROOT_DIR}" /bin/bash <<'CHROOT_END'
set -e
export DEBIAN_FRONTEND=noninteractive
export LANG=C

cat > /etc/apt/sources.list <<SOURCES
deb http://archive.ubuntu.com/ubuntu jammy main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu jammy-updates main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu jammy-security main restricted universe multiverse
SOURCES

apt-get update -q
apt-get install -y casper

KERNEL_VERSION=$(ls /lib/modules/ | sort -V | tail -1)
[ -n "$KERNEL_VERSION" ] && (update-initramfs -c -k "$KERNEL_VERSION" || update-initramfs -u -k all)

# ── GNOME ─────────────────────────────────────────────────────
apt-get install -y --no-install-recommends \
    gnome-shell gnome-session gnome-control-center gnome-tweaks \
    gnome-shell-extensions gdm3 xorg \
    xserver-xorg-video-all xserver-xorg-input-all \
    network-manager network-manager-gnome \
    nautilus nautilus-admin xdg-utils \
    gnome-terminal papirus-icon-theme \
    wget curl git python3 python3-pip \
    flatpak gnome-software gnome-software-plugin-flatpak \
    htop unzip apt-transport-https gnupg imagemagick

# ── Brave ─────────────────────────────────────────────────────
curl -fsSL https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg \
    -o /usr/share/keyrings/brave-browser-archive-keyring.gpg 2>/dev/null || true
echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" \
    > /etc/apt/sources.list.d/brave.list
apt-get update -q
apt-get install -y brave-browser || true

# ── VeloraForest Theme ────────────────────────────────────────
mkdir -p /usr/share/themes/VeloraForest/gtk-3.0
mkdir -p /usr/share/themes/VeloraForest/gtk-4.0

cat > /usr/share/themes/VeloraForest/gtk-3.0/gtk.css <<GTKEOF
@define-color accent_color #2F6B52;
@define-color window_bg_color #1a1f1c;
@define-color window_fg_color #e8f5e9;
@define-color headerbar_bg_color #161b18;
@define-color sidebar_bg_color #161b18;
@define-color view_bg_color #1e2520;
@define-color popover_bg_color #1e2520;

window, .background { background-color: @window_bg_color; color: @window_fg_color; }
headerbar, .titlebar { background-color: @headerbar_bg_color; color: @window_fg_color; border-bottom: 1px solid rgba(47,107,82,0.3); border-radius: 12px 12px 0 0; min-height: 46px; padding: 0 8px; }
.view, scrolledwindow { background-color: @view_bg_color; color: @window_fg_color; }
.sidebar, placessidebar { background-color: @sidebar_bg_color; border-right: 1px solid rgba(47,107,82,0.2); }
.sidebar row:selected { background-color: rgba(47,107,82,0.3); color: white; }
button { background-color: rgba(47,107,82,0.15); color: @window_fg_color; border: 1px solid rgba(47,107,82,0.25); border-radius: 8px; padding: 6px 14px; }
button:hover { background-color: rgba(47,107,82,0.3); border-color: @accent_color; }
button.suggested-action { background-color: @accent_color; color: white; border: none; }
entry, searchentry { background-color: @view_bg_color; color: @window_fg_color; border: 1px solid rgba(47,107,82,0.3); border-radius: 8px; padding: 8px 12px; }
entry:focus { border-color: @accent_color; }
selection, *:selected { background-color: rgba(47,107,82,0.4); color: white; }
rubberband, .rubberband { background-color: rgba(47,107,82,0.2); border: 1px solid @accent_color; }
popover, .popover { background-color: @popover_bg_color; border: 1px solid rgba(47,107,82,0.3); border-radius: 12px; }
switch:checked { background-color: @accent_color; }
GTKEOF

cp /usr/share/themes/VeloraForest/gtk-3.0/gtk.css /usr/share/themes/VeloraForest/gtk-4.0/gtk.css

cat > /usr/share/themes/VeloraForest/index.theme <<THEOF
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
THEOF

# ── GNOME dconf ───────────────────────────────────────────────
mkdir -p /etc/dconf/db/local.d /etc/dconf/profile

cat > /etc/dconf/profile/user <<PROFEOF
user-db:user
system-db:local
PROFEOF

cat > /etc/dconf/db/local.d/00-velora <<DCONF
[org/gnome/desktop/interface]
gtk-theme='VeloraForest'
icon-theme='Papirus-Dark'
cursor-theme='Adwaita'
font-name='Cantarell 11'
color-scheme='prefer-dark'

[org/gnome/desktop/background]
picture-uri='file:///usr/share/backgrounds/velora-wallpaper.jpg'
picture-uri-dark='file:///usr/share/backgrounds/velora-wallpaper.jpg'
picture-options='zoom'
primary-color='#0d1a12'

[org/gnome/desktop/wm/preferences]
button-layout='close,minimize,maximize:'
num-workspaces=2

[org/gnome/mutter]
dynamic-workspaces=false
edge-tiling=true

[org/gnome/shell]
enabled-extensions=['dash-to-dock@micxgx.gmail.com']
favorite-apps=['brave-browser.desktop', 'org.gnome.Nautilus.desktop', 'org.gnome.Terminal.desktop', 'org.gnome.Settings.desktop']

[org/gnome/shell/extensions/dash-to-dock]
dock-position='BOTTOM'
dock-fixed=true
extend-height=false
dash-max-icon-size=42
transparency-mode='FIXED'
background-opacity=0.75
custom-background-color=true
background-color='#161b18'
show-apps-button=true
autohide=false
intellihide=false
running-indicator-style='DOTS'
DCONF

dconf update 2>/dev/null || true

# ── Dash-to-dock ──────────────────────────────────────────────
DOCK_DIR="/usr/share/gnome-shell/extensions/dash-to-dock@micxgx.gmail.com"
mkdir -p "${DOCK_DIR}"
wget -q -O /tmp/dtd.zip \
    "https://extensions.gnome.org/extension-data/dash-to-dockmicxgx.gmail.com.v84.shell-extension.zip" || true
[ -f /tmp/dtd.zip ] && unzip -q /tmp/dtd.zip -d "${DOCK_DIR}" 2>/dev/null || true
rm -f /tmp/dtd.zip

# ── Wallpaper ─────────────────────────────────────────────────
mkdir -p /usr/share/backgrounds
wget -q -O /usr/share/backgrounds/velora-wallpaper.jpg \
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&q=80" 2>/dev/null || true
if [ ! -s /usr/share/backgrounds/velora-wallpaper.jpg ]; then
    convert -size 1920x1080 gradient:"#0a1a0f"-"#1a3520" \
        /usr/share/backgrounds/velora-wallpaper.jpg 2>/dev/null || true
fi

# ── GDM autologin ─────────────────────────────────────────────
mkdir -p /etc/gdm3
cat > /etc/gdm3/custom.conf <<GDMEOF
[daemon]
AutomaticLoginEnable=true
AutomaticLogin=velora
TimedLoginEnable=false
WaylandEnable=false
GDMEOF

# ── Casper ────────────────────────────────────────────────────
cat > /etc/casper.conf <<CASPEREOF
export FLAVOUR="Velora Linux"
export WRITABLE_IMAGES="false"
export LIVE_USERNAME="velora"
export LIVE_USER_FULLNAME="Velora User"
export LIVE_USER_DEFAULT_GROUPS="audio cdrom dip floppy video plugdev netdev powerdev scanner bluetooth sudo"
CASPEREOF

# ── OS identity ───────────────────────────────────────────────
cat > /etc/os-release <<OSEOF
NAME="Velora Linux"
VERSION="0.8"
ID=velora
ID_LIKE=ubuntu
PRETTY_NAME="Velora Linux 0.8"
VERSION_ID="0.8"
HOME_URL="https://velora-ro.github.io"
OSEOF

echo "velora" > /etc/hostname
systemctl enable gdm3
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null || true
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
mksquashfs "${CHROOT_DIR}" "${ISO_DIR}/casper/filesystem.squashfs" \
    -comp gzip -noappend -no-progress

chroot "${CHROOT_DIR}" dpkg-query -W --showformat='${Package} ${Version}\n' \
    > "${ISO_DIR}/casper/filesystem.manifest" 2>/dev/null || true

# ── Kernel ────────────────────────────────────────────────────
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

# ── GRUB config ───────────────────────────────────────────────
mkdir -p "${ISO_DIR}/boot/grub"

cat > "${ISO_DIR}/boot/grub/grub.cfg" <<GRUBEOF
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
GRUBEOF

# ── Early GRUB config (embedded) ─────────────────────────────
# This runs BEFORE grub.cfg - ensures modules are loaded
cat > /tmp/grub-early.cfg <<EARLYEOF
insmod part_msdos
insmod part_gpt
insmod iso9660
insmod normal
insmod search
insmod search_label
search --no-floppy --label --set=root "VELORA_LINUX"
set prefix=(\$root)/boot/grub
normal
EARLYEOF

# ── Build ISO ─────────────────────────────────────────────────
echo "[*] Building ISO..."
mkdir -p "$(pwd)/iso"

grub-mkrescue \
    --output="$(pwd)/iso/${ISO_NAME}" \
    --modules="part_msdos part_gpt iso9660 linux normal configfile search search_fs_label search_fs_uuid all_video gfxterm gfxterm_background font" \
    --core-compress=xz \
    -volid "VELORA_LINUX" \
    "${ISO_DIR}" \
    2>&1 | tee "$(pwd)/build.log"

if [ -f "$(pwd)/iso/${ISO_NAME}" ]; then
    SIZE=$(du -h "$(pwd)/iso/${ISO_NAME}" | cut -f1)
    echo "Build complete: iso/${ISO_NAME} (${SIZE})"
else
    echo "ERROR: ISO not found."
    exit 1
fi
