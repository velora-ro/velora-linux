#!/bin/bash
# ============================================================
#  Velora Linux - Master Install Script
#  Runs all install scripts in order
# ============================================================

set -e

echo ""
echo "🌲 Velora Linux - Installation"
echo "================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

run_script() {
    echo "[*] Running: $1"
    bash "$SCRIPT_DIR/$1"
    echo "[✓] Done: $1"
    echo ""
}

run_script "install-base.sh"
run_script "install-kde.sh"
run_script "install-wine.sh"
run_script "install-gaming.sh"
run_script "install-flatpak.sh"
run_script "install-velora-apps.sh"
run_script "install-branding.sh"
run_script "install-theme.sh"
run_script "install-bootscreen.sh"

echo "================================"
echo "✅ Velora Linux installed!"
echo "   Please reboot."
echo "================================"
