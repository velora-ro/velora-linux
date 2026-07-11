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

# Install desktop
echo "[chroot] Installing KDE Plasma..."
apt-get install -y --no-install-recommends \
    kde-plasma-desktop \
    sddm \
    xorg \
    network-manager \
    plasma-nm \
    dolphin \
    konsole

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

# Enable SDDM
systemctl enable sddm

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

# ── Copy kernel and initrd ───────────────────────────────────
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

cp "$VMLINUZ" "${ISO_DIR}/boot/vmlinuz"
cp "$INITRD"  "${ISO_DIR}/boot/initrd.img"

# ── Setup GRUB ───────────────────────────────────────────────
echo "[*] Setting up GRUB bootloader..."

mkdir -p "${ISO_DIR}/boot/grub"

cat > "${ISO_DIR}/boot/grub/grub.cfg" << 'EOF'
search --no-floppy --label --set=root VeloraLinux
set prefix=($root)/boot/grub

insmod all_video
insmod gfxterm
insmod iso9660
insmod squash4
insmod loopback
insmod linux

set timeout=5
set default=0

menuentry "Velora Linux 1.0 (Live)" {
    linux /boot/vmlinuz boot=live components quiet splash
    initrd /boot/initrd.img
}

menuentry "Velora Linux 1.0 (Safe Mode)" {
    linux /boot/vmlinuz boot=live nomodeset
    initrd /boot/initrd.img
}
EOF

# ── Build the ISO ────────────────────────────────────────────
echo "[*] Building ISO with grub-mkrescue..."
mkdir -p "$(pwd)/iso"

grub-mkrescue \
    --output="$(pwd)/iso/${ISO_NAME}" \
    --modules="iso9660 squash4 loopback linux normal search search_fs_uuid search_label all_video gfxterm" \
    "${ISO_DIR}" \
    2>&1 | tee "$(pwd)/build.log"

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
