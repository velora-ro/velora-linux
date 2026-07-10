#!/bin/bash
# ============================================================
#  Velora Linux - KDE Plasma Desktop
# ============================================================

echo "[kde] Installing KDE Plasma..."
apt-get install -y \
    kde-plasma-desktop \
    plasma-workspace \
    plasma-nm \
    plasma-pa \
    plasma-systemmonitor \
    kscreen \
    kde-spectacle \
    dolphin \
    konsole \
    ark \
    kate \
    okular \
    gwenview \
    kcalc \
    kdeconnect \
    sddm \
    sddm-theme-breeze

echo "[kde] Setting SDDM as default display manager..."
systemctl enable sddm

echo "[kde] Done."
