#!/bin/bash
# ============================================================
#  Velora Linux - Build Script
#  Manual debootstrap + xorriso method
#  Guaranteed bootable ISO (BIOS + UEFI)
# ============================================================

set -e

VELORA_VERSION="1.0"
ISO_NAME="VeloraLinux-${VELORA_VERSION}.iso"
WORK_DIR="$(pwd)/work"
CHROOT_DIR="${WORK_DIR}/chroot"
ISO_DIR="${WORK_DIR}/isoroot"

echo ""
echo "🌲 Velora Linux Build System"
echo "   Version: ${VELORA_VERSION}"
echo "============================================"
echo ""

# ── Install dependencies ─────────────────────────────────────
echo "[*] Installing build dependencies..."
apt-get update -q
apt-get install -y \
    debootstrap \
    squashfs-tools \
    xorriso \
    grub-pc-bin \
    grub-efi-amd64-bin \
    mtools \
    dosfstools

# ── Clean previous build ─────────────────────────────────────
echo "[*] Cleaning previous build..."
rm -rf "${WORK_DIR}"
mkdir -p "${CHROOT_DIR}" "${ISO_DIR}"

# ── Bootstrap base Ubuntu system ─────────────────────────────
echo "[*] Bootstrapping Ubuntu Jammy base system..."
debootstrap \
    --arch=amd64 \
    --include=linux-image-generic,systemd-sysv,sudo,grub-pc \
    jammy \
    "${CHROOT_DIR}" \
    http://archive.ubuntu.com/ubuntu/

# ── Configure chroot ─────────────────────────────────────────
echo "[*] Configuring system..."

# Copy resolv.conf for internet in chroot
cp /etc/resolv.conf "${CHROOT_DIR}/etc/resolv.conf"

# Mount virtual filesystems
mount --bind /dev "${CHROOT_DIR}/dev"
mount --bind /proc "${CHROOT_DIR}/proc"
mount --bind /sys "${CHROOT_DIR}/sys"

# Run configuration inside chroot
chroot "${CHROOT_DIR}" /bin/bash <<'CHROOT_END'
set -e

export DEBIAN_FRONTEND=noninteractive
export LANG=C

# Add Ubuntu repos
cat > /etc/apt/sources.list << 'EOF'
deb http://archive.ubuntu.com/ubuntu jammy main restricted universe multiverse
deb http://archive.ubuntu.com/ubuntu jammy-updates main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu jammy-security main restricted universe multiverse
EOF

apt-get update -q

# Install casper for live boot
echo "[chroot] Installing casper..."
apt-get install -y casper

# Make sure initramfs is generated
echo "[chroot] Generating initramfs..."
KERNEL_VERSION=$(ls /lib/modules/ | sort -V | tail -1)
echo "[chroot] Kernel version: $KERNEL_VERSION"
if [ -n "$KERNEL_VERSION" ]; then
    update-initramfs -c -k "$KERNEL_VERSION" || update-initramfs -u -k all
fi
ls -la /boot/

# Install desktop - XFCE (lightweight, works in QEMU)
echo "[chroot] Installing XFCE Desktop..."
apt-get install -y --no-install-recommends \
    xfce4 \
    xfce4-terminal \
    xfce4-taskmanager \
    lightdm \
    lightdm-gtk-greeter \
    xorg \
    network-manager \
    network-manager-gnome \
    nautilus \
    nautilus-admin \
    mousepad

# Set Nautilus as default file manager
xdg-mime default org.gnome.Nautilus.desktop inode/directory

# Install system tools
echo "[chroot] Installing system tools..."
apt-get install -y \
    wget curl git \
    python3 python3-pip \
    flatpak \
    htop

# Set locale
locale-gen en_US.UTF-8
update-locale LANG=en_US.UTF-8

# Enable LightDM
systemctl enable lightdm

# Fix casper CD-ROM detection for QEMU/VMs
mkdir -p /etc/casper.conf.d/
cat > /etc/casper.conf << 'CASPEREOF'
export FLAVOUR="Velora Linux"
export WRITABLE_IMAGES="false"
export LIVE_USERNAME="velora"
export LIVE_USER_FULLNAME="Velora User"
export LIVE_USER_DEFAULT_GROUPS="audio cdrom dip floppy video plugdev netdev powerdev scanner bluetooth"
CASPEREOF

# Set os-release
cat > /etc/os-release << 'EOF'
NAME="Velora Linux"
VERSION="1.0"
ID=velora
ID_LIKE=ubuntu
PRETTY_NAME="Velora Linux 1.0"
VERSION_ID="1.0"
HOME_URL="https://github.com/velora-ro/velora-linux"
EOF

# Set hostname
echo "velora" > /etc/hostname

# Clean up
apt-get clean
rm -rf /tmp/* /var/tmp/*

CHROOT_END

# ── Unmount virtual filesystems ──────────────────────────────
echo "[*] Unmounting filesystems..."
umount "${CHROOT_DIR}/dev"  || true
umount "${CHROOT_DIR}/proc" || true
umount "${CHROOT_DIR}/sys"  || true

# ── Create squashfs ──────────────────────────────────────────
echo "[*] Creating squashfs filesystem..."
mkdir -p "${ISO_DIR}/live"
mksquashfs \
    "${CHROOT_DIR}" \
    "${ISO_DIR}/live/filesystem.squashfs" \
    -comp gzip \
    -noappend \
    -no-progress

# ── Create live boot structure ────────────────────────────────
echo "[*] Creating live boot structure..."
mkdir -p "${ISO_DIR}/.disk"
echo "Velora Linux 1.0 - Live" > "${ISO_DIR}/.disk/info"
echo "full_cd" > "${ISO_DIR}/.disk/cd_type"
touch "${ISO_DIR}/.disk/base_installable"

# Casper needs a specific label file
mkdir -p "${ISO_DIR}/casper"
# Copy squashfs to casper dir (casper looks here)
mv "${ISO_DIR}/live/filesystem.squashfs" "${ISO_DIR}/casper/filesystem.squashfs" 2>/dev/null || true
# Copy manifest
chroot "${CHROOT_DIR}" dpkg-query -W --showformat='${Package} ${Version}\n' > "${ISO_DIR}/casper/filesystem.manifest" 2>/dev/null || true

# ── Copy kernel and initrd to casper ────────────────────────
echo "[*] Copying kernel and initrd..."
mkdir -p "${ISO_DIR}/boot"

echo "[*] Contents of chroot/boot:"
ls -la "${CHROOT_DIR}/boot/" || echo "empty"

# Find kernel and initrd dynamically
VMLINUZ=$(find "${CHROOT_DIR}/boot" -name "vmlinuz*" -not -name "*.old" | sort -V | tail -1)
INITRD=$(find "${CHROOT_DIR}/boot" -name "initrd*" -not -name "*.old" | sort -V | tail -1)

echo "[*] Found kernel: $VMLINUZ"
echo "[*] Found initrd: $INITRD"

if [ -z "$VMLINUZ" ] || [ -z "$INITRD" ]; then
    echo "[ERROR] Could not find kernel or initrd in chroot/boot"
    ls -la "${CHROOT_DIR}/boot/"
    exit 1
fi

cp "$VMLINUZ" "${ISO_DIR}/casper/vmlinuz"
cp "$INITRD"  "${ISO_DIR}/casper/initrd"

# ── Setup GRUB ───────────────────────────────────────────────
echo "[*] Setting up GRUB bootloader..."

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
insmod search_fs_uuid

# Find the ISO device automatically by label
search --no-floppy --label --set=root "VELORA_LINUX"

menuentry "Velora Linux 1.0 (Live)" {
    search --no-floppy --label --set=root "VELORA_LINUX"
    linux  /casper/vmlinuz boot=casper cdrom-detect/try-usb=true quiet splash ---
    initrd /casper/initrd
}

menuentry "Velora Linux 1.0 (Safe Mode - nomodeset)" {
    search --no-floppy --label --set=root "VELORA_LINUX"
    linux  /casper/vmlinuz boot=casper cdrom-detect/try-usb=true nomodeset ---
    initrd /casper/initrd
}
EOF

# ── Build the ISO ────────────────────────────────────────────
echo "[*] Building ISO with grub-mkrescue..."
mkdir -p "$(pwd)/iso"

grub-mkrescue \
    --output="$(pwd)/iso/${ISO_NAME}" \
    --modules="iso9660 squash4 loopback linux normal search search_fs_uuid search_label all_video gfxterm" \
    -volid "VELORA_LINUX" \
    "${ISO_DIR}" \
    2>&1 | tee "$(pwd)/build.log"

# Show ISO structure for debugging
echo "[*] ISO structure:"
isoinfo -l -i "$(pwd)/iso/${ISO_NAME}" 2>/dev/null | head -50 || true

# ── Done ─────────────────────────────────────────────────────
if [ -f "$(pwd)/iso/${ISO_NAME}" ]; then
    SIZE=$(du -h "$(pwd)/iso/${ISO_NAME}" | cut -f1)
    echo ""
    echo "============================================"
    echo "✅ Build complete!"
    echo "   ISO: iso/${ISO_NAME}"
    echo "   Size: ${SIZE}"
    echo "============================================"
else
    echo "[ERROR] ISO not found. Check build.log."
    exit 1
fi
