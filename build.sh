#!/bin/bash
# ============================================================
#  Velora Linux - Build Script v0.8
#  Base: Debian 12 Bookworm
#  Desktop: KDE Plasma + VeloraForest theme
# ============================================================

set -e

VELORA_VERSION="0.8"
ISO_NAME="VeloraLinux-${VELORA_VERSION}.iso"
WORK_DIR="$(pwd)/work"
CHROOT_DIR="${WORK_DIR}/chroot"
ISO_DIR="${WORK_DIR}/isoroot"

echo "Velora Linux Build System v${VELORA_VERSION} - Debian + KDE"

# ── Build dependencies ────────────────────────────────────────
apt-get update -q
apt-get install -y \
    debootstrap squashfs-tools xorriso \
    grub-pc-bin grub-efi-amd64-bin grub-common \
    mtools dosfstools

# ── Clean ─────────────────────────────────────────────────────
rm -rf "${WORK_DIR}"
mkdir -p "${CHROOT_DIR}" "${ISO_DIR}"

# ── Bootstrap Debian 12 ───────────────────────────────────────
echo "[*] Bootstrapping Debian 12 Bookworm..."
debootstrap --arch=amd64 \
    --include=linux-image-amd64,systemd-sysv,sudo,grub-pc \
    bookworm "${CHROOT_DIR}" \
    http://deb.debian.org/debian/

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
deb http://deb.debian.org/debian bookworm main contrib non-free non-free-firmware
deb http://deb.debian.org/debian bookworm-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security bookworm-security main contrib non-free
SOURCES

apt-get update -q

# Live boot support
apt-get install -y live-boot live-boot-initramfs-tools

# Generate initramfs
KERNEL_VERSION=$(ls /lib/modules/ | sort -V | tail -1)
[ -n "$KERNEL_VERSION" ] && update-initramfs -c -k "$KERNEL_VERSION" || true

# ── KDE Plasma Desktop ────────────────────────────────────────
echo "[chroot] Installing KDE Plasma..."
apt-get install -y --no-install-recommends \
    kde-plasma-desktop \
    sddm \
    xorg \
    xserver-xorg-video-all \
    xserver-xorg-input-all \
    plasma-nm \
    dolphin \
    konsole \
    ark \
    kate \
    kde-spectacle \
    network-manager \
    wget curl git \
    python3 python3-pip \
    flatpak \
    plasma-discover \
    htop unzip \
    apt-transport-https gnupg \
    papirus-icon-theme \
    fonts-cantarell

# ── Brave Browser ─────────────────────────────────────────────
curl -fsSL https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg \
    -o /usr/share/keyrings/brave-browser-archive-keyring.gpg 2>/dev/null || true
echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" \
    > /etc/apt/sources.list.d/brave.list
apt-get update -q
apt-get install -y brave-browser || true

# ── VeloraForest KDE Theme ────────────────────────────────────
echo "[chroot] Installing VeloraForest KDE theme..."

# Color scheme
mkdir -p /usr/share/color-schemes
cat > /usr/share/color-schemes/VeloraForest.colors <<COLEOF
[ColorEffects:Disabled]
Color=56,56,56
ColorAmount=0
ColorEffect=0
ContrastAmount=0.65
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
ChangeSelectionColor=true
Color=112,111,110
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=false
IntensityAmount=0
IntensityEffect=0

[Colors:Button]
BackgroundAlternate=44,55,48
BackgroundNormal=30,42,34
DecorationFocus=47,107,82
DecorationHover=95,158,110
ForegroundActive=232,245,233
ForegroundInactive=120,160,130
ForegroundLink=41,182,246
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=232,245,233
ForegroundPositive=39,174,96
ForegroundVisited=127,140,141

[Colors:Complementary]
BackgroundAlternate=22,30,24
BackgroundNormal=14,20,16
DecorationFocus=47,107,82
DecorationHover=95,158,110
ForegroundActive=232,245,233
ForegroundInactive=120,160,130
ForegroundLink=41,182,246
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=232,245,233
ForegroundPositive=39,174,96
ForegroundVisited=127,140,141

[Colors:Header]
BackgroundAlternate=22,30,24
BackgroundNormal=18,24,20
DecorationFocus=47,107,82
DecorationHover=95,158,110
ForegroundActive=232,245,233
ForegroundInactive=120,160,130
ForegroundLink=41,182,246
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=232,245,233
ForegroundPositive=39,174,96
ForegroundVisited=127,140,141

[Colors:Selection]
BackgroundAlternate=47,107,82
BackgroundNormal=47,107,82
DecorationFocus=47,107,82
DecorationHover=95,158,110
ForegroundActive=232,245,233
ForegroundInactive=232,245,233
ForegroundLink=41,182,246
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=232,245,233
ForegroundPositive=39,174,96
ForegroundVisited=127,140,141

[Colors:Tooltip]
BackgroundAlternate=22,30,24
BackgroundNormal=26,31,28
DecorationFocus=47,107,82
DecorationHover=95,158,110
ForegroundActive=232,245,233
ForegroundInactive=120,160,130
ForegroundLink=41,182,246
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=232,245,233
ForegroundPositive=39,174,96
ForegroundVisited=127,140,141

[Colors:View]
BackgroundAlternate=22,30,24
BackgroundNormal=18,26,20
DecorationFocus=47,107,82
DecorationHover=95,158,110
ForegroundActive=232,245,233
ForegroundInactive=120,160,130
ForegroundLink=41,182,246
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=232,245,233
ForegroundPositive=39,174,96
ForegroundVisited=127,140,141

[Colors:Window]
BackgroundAlternate=22,30,24
BackgroundNormal=16,22,18
DecorationFocus=47,107,82
DecorationHover=95,158,110
ForegroundActive=232,245,233
ForegroundInactive=120,160,130
ForegroundLink=41,182,246
ForegroundNegative=218,68,83
ForegroundNeutral=246,116,0
ForegroundNormal=232,245,233
ForegroundPositive=39,174,96
ForegroundVisited=127,140,141

[General]
ColorScheme=VeloraForest
Name=VeloraForest
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground=18,26,20
activeForeground=232,245,233
inactiveBackground=14,20,16
inactiveForeground=120,160,130
COLEOF

# ── KDE Plasma settings for live user ─────────────────────────
mkdir -p /etc/skel/.config

# Plasma appearance
cat > /etc/skel/.config/kdeglobals <<KDEEOF
[ColorEffects:Disabled]
Color=56,56,56

[General]
ColorScheme=VeloraForest
Name=VeloraForest
shadeSortColumn=true
widgetStyle=Breeze

[Icons]
Theme=Papirus-Dark

[KDE]
LookAndFeelPackage=org.kde.breezedark.desktop
contrast=4
SingleClick=false

[WM]
activeBackground=18,26,20
activeForeground=232,245,233
inactiveBackground=14,20,16
inactiveForeground=120,160,130
KDEEOF

# Plasma taskbar - Windows style (bottom panel)
mkdir -p /etc/skel/.config
cat > /etc/skel/.config/plasma-org.kde.plasma.desktop-appletsrc <<PANELEOF
[ActionPlugins][0]
RightButton;NoModifier=org.kde.contextmenu

[ActionPlugins][1]
RightButton;NoModifier=org.kde.contextmenu

[Containments][1]
activityId=
formfactor=2
immutability=1
lastScreen=0
location=4
plugin=org.kde.panel
wallpaperplugin=org.kde.image

[Containments][1][Applets][2]
immutability=1
plugin=org.kde.plasma.kickoff

[Containments][1][Applets][2][Configuration]
PreloadWeight=100

[Containments][1][Applets][2][Configuration][General]
icon=/usr/share/pixmaps/velora-logo.svg
useCustomButtonImage=true

[Containments][1][Applets][3]
immutability=1
plugin=org.kde.plasma.pager

[Containments][1][Applets][4]
immutability=1
plugin=org.kde.plasma.taskmanager

[Containments][1][Applets][4][Configuration][General]
groupingStrategy=0
maxStripes=1

[Containments][1][Applets][5]
immutability=1
plugin=org.kde.plasma.systemtray

[Containments][1][Applets][6]
immutability=1
plugin=org.kde.plasma.digitalclock

[Containments][1][Applets][6][Configuration][Appearance]
showDate=true
showSeconds=false

[Containments][1][General]
showToolbox=false

[Containments][2]
activityId=
formfactor=0
immutability=1
lastScreen=0
location=0
plugin=org.kde.plasma.folder
wallpaperplugin=org.kde.image

[Containments][2][Wallpaper][org.kde.image][General]
Image=file:///usr/share/backgrounds/velora-wallpaper.jpg

[ScreenMapping]
itemsOnDisabledScreens=
PANELEOF

# Breeze Dark window decorations
cat > /etc/skel/.config/kwinrc <<KWINEOF
[org.kde.kdecoration2]
ButtonsOnLeft=XIA
ButtonsOnRight=
library=org.kde.breeze
theme=Breeze

[Windows]
BorderlessMaximizedWindows=false
RoundedCorners=true

[Plugins]
blurEnabled=true
kwin4_effect_dialogparentEnabled=true
KWINEOF

# Breeze appearance
cat > /etc/skel/.config/breezerc <<BREEZEEOF
[Common]
OutlineIntensity=OutlineOff
ShadowSize=ShadowVeryLarge
ShadowStrength=128

[Windeco Exception 0]
Enabled=true
ExceptionType=0
HideTitleBar=false

[Style]
MenuOpacity=90
BREEZEEOF

# ── Velora Logo SVG ───────────────────────────────────────────
mkdir -p /usr/share/pixmaps
cat > /usr/share/pixmaps/velora-logo.svg <<SVGEOF
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
  <rect width="48" height="48" rx="10" fill="#161b18"/>
  <polygon points="8,12 24,36 40,12 34,12 24,28 14,12" fill="#2F6B52"/>
  <polygon points="14,12 24,28 34,12 28,12 24,22 20,12" fill="#5F9E6E"/>
</svg>
SVGEOF

# ── Wallpaper ─────────────────────────────────────────────────
mkdir -p /usr/share/backgrounds
wget -q -O /usr/share/backgrounds/velora-wallpaper.jpg \
    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1920&q=80" 2>/dev/null || true
if [ ! -s /usr/share/backgrounds/velora-wallpaper.jpg ]; then
    # Fallback gradient
    python3 -c "
from PIL import Image, ImageDraw
img = Image.new('RGB', (1920, 1080))
draw = ImageDraw.Draw(img)
for y in range(1080):
    r = int(10 + (20-10)*y/1080)
    g = int(26 + (55-26)*y/1080)
    b = int(16 + (35-16)*y/1080)
    draw.line([(0,y),(1920,y)], fill=(r,g,b))
img.save('/usr/share/backgrounds/velora-wallpaper.jpg')
" 2>/dev/null || true
fi

# ── SDDM autologin ────────────────────────────────────────────
mkdir -p /etc/sddm.conf.d
cat > /etc/sddm.conf.d/autologin.conf <<SDDMEOF
[Autologin]
User=velora
Session=plasma
Relogin=false
SDDMEOF

cat > /etc/sddm.conf.d/theme.conf <<SDDMTHEME
[Theme]
Current=breeze
SDDMTHEME

# ── Live boot config ──────────────────────────────────────────
cat > /etc/live/boot.conf <<LIVEEOF
LIVE_USERNAME="velora"
LIVE_USER_FULLNAME="Velora User"
LIVE_USER_DEFAULT_GROUPS="audio cdrom dip floppy video plugdev netdev powerdev scanner bluetooth sudo"
LIVEEOF

# ── OS identity ───────────────────────────────────────────────
cat > /etc/os-release <<OSEOF
NAME="Velora Linux"
VERSION="0.8"
ID=velora
ID_LIKE=debian
PRETTY_NAME="Velora Linux 0.8"
VERSION_ID="0.8"
HOME_URL="https://velora-ro.github.io"
OSEOF

echo "velora" > /etc/hostname

cat > /etc/hosts <<HOSTSEOF
127.0.0.1 localhost
127.0.1.1 velora
HOSTSEOF

# Set passwords
echo "root:velora" | chpasswd
useradd -m -s /bin/bash velora 2>/dev/null || true
echo "velora:velora" | chpasswd
usermod -aG sudo,audio,video,cdrom,plugdev velora

# Create velora user with no password for live session
useradd -m -s /bin/bash -G sudo,audio,video,cdrom,plugdev,netdev velora
passwd -d velora
echo "velora ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set root password to empty too
passwd -d root

# Enable SDDM
systemctl enable sddm
systemctl enable NetworkManager

# Set root password and velora user password
echo "root:velora" | chpasswd
# Live user will be created by live-boot automatically
# But we set a default password just in case
useradd -m -s /bin/bash velora 2>/dev/null || true
echo "velora:velora" | chpasswd
usermod -aG sudo velora 2>/dev/null || true

# Fix SDDM session detection
mkdir -p /usr/share/xsessions
cat > /usr/share/xsessions/plasma.desktop <<SESSEOF
[Desktop Entry]
Type=XSession
Exec=/usr/bin/startplasma-x11
TryExec=/usr/bin/startplasma-x11
DesktopNames=KDE
Name=Plasma
Comment=Plasma by KDE
SESSEOF

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
mkdir -p "${ISO_DIR}/live"
mksquashfs "${CHROOT_DIR}" "${ISO_DIR}/live/filesystem.squashfs" \
    -comp gzip -noappend -no-progress

# ── Kernel + initrd ───────────────────────────────────────────
VMLINUZ=$(find "${CHROOT_DIR}/boot" -name "vmlinuz*" -not -name "*.old" | sort -V | tail -1)
INITRD=$(find  "${CHROOT_DIR}/boot" -name "initrd*"  -not -name "*.old" | sort -V | tail -1)
[ -z "$VMLINUZ" ] && { echo "ERROR: kernel not found"; exit 1; }
[ -z "$INITRD"  ] && { echo "ERROR: initrd not found"; exit 1; }

mkdir -p "${ISO_DIR}/live"
cp "$VMLINUZ" "${ISO_DIR}/live/vmlinuz"
cp "$INITRD"  "${ISO_DIR}/live/initrd"

# ── Disk info ─────────────────────────────────────────────────
mkdir -p "${ISO_DIR}/.disk"
echo "Velora Linux 0.8" > "${ISO_DIR}/.disk/info"
touch "${ISO_DIR}/.disk/base_installable"

# ── GRUB ──────────────────────────────────────────────────────
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
    linux  /live/vmlinuz boot=live quiet splash
    initrd /live/initrd
}

menuentry "Velora Linux 0.8 (Safe Mode)" {
    search --no-floppy --label --set=root "VELORA_LINUX"
    linux  /live/vmlinuz boot=live nomodeset
    initrd /live/initrd
}
GRUBEOF

# ── Build ISO ─────────────────────────────────────────────────
echo "[*] Building ISO..."
mkdir -p "$(pwd)/iso"

grub-mkrescue \
    --output="$(pwd)/iso/${ISO_NAME}" \
    --modules="part_msdos part_gpt iso9660 linux normal configfile search search_label all_video gfxterm font" \
    -volid "VELORA_LINUX" \
    "${ISO_DIR}" \
    2>&1 | tee "$(pwd)/build.log"

if [ -f "$(pwd)/iso/${ISO_NAME}" ]; then
    SIZE=$(du -h "$(pwd)/iso/${ISO_NAME}" | cut -f1)
    echo "============================================"
    echo "Build complete: iso/${ISO_NAME} (${SIZE})"
    echo "============================================"
else
    echo "ERROR: ISO not found."
    exit 1
fi
