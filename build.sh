#!/bin/bash
# ============================================================
#  Velora Linux - Build Script
#  Builds the Velora Linux ISO using live-build
# ============================================================

set -e

VELORA_VERSION="1.0"
ISO_NAME="VeloraLinux-${VELORA_VERSION}.iso"
BUILD_DIR="$(pwd)/build"

echo ""
echo "🌲 Velora Linux Build System"
echo "   Version: ${VELORA_VERSION}"
echo "============================================"
echo ""

# Check if live-build is installed
if ! command -v lb &> /dev/null; then
    echo "[ERROR] live-build is not installed."
    echo "   Run: sudo apt install live-build"
    exit 1
fi

# Clean previous build
if [ -d "$BUILD_DIR" ]; then
    echo "[*] Cleaning previous build..."
    rm -rf "$BUILD_DIR"
fi

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

echo "[*] Configuring live-build..."
lb config \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --debian-installer none \
    --binary-images iso-hybrid \
    --bootappend-live "boot=live components quiet splash" \
    --iso-volume "Velora Linux ${VELORA_VERSION}" \
    --iso-publisher "Velora <velora.official.ro@gmail.com>" \
    --iso-application "Velora Linux" \
    --memtest none \
    --win32-loader false

echo "[*] Copying package lists..."
cp -r ../configs/packages.chroot config/package-lists/
cp -r ../configs/includes.chroot config/includes.chroot/ 2>/dev/null || true

echo "[*] Starting build (this will take a while)..."
echo ""
sudo lb build 2>&1 | tee ../build.log

# Find and rename ISO
ISO_FILE=$(find . -name "*.iso" | head -1)
if [ -n "$ISO_FILE" ]; then
    cp "$ISO_FILE" "../iso/${ISO_NAME}"
    echo ""
    echo "============================================"
    echo "✅ Build complete!"
    echo "   ISO: iso/${ISO_NAME}"
    echo "============================================"
else
    echo "[ERROR] ISO not found. Check build.log for errors."
    exit 1
fi
