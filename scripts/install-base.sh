#!/bin/bash
# ============================================================
#  Velora Linux - Base System
# ============================================================

echo "[base] Updating system..."
apt-get update -y
apt-get upgrade -y

echo "[base] Installing base packages..."
apt-get install -y \
    wget curl git zip unzip p7zip-full \
    htop fastfetch \
    network-manager \
    bluetooth blueman \
    cups system-config-printer \
    gparted timeshift \
    python3 python3-pip python3-venv \
    flatpak \
    fonts-inter fonts-noto fonts-noto-color-emoji

echo "[base] Done."
