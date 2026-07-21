#!/bin/bash
# Fix logo Kickoff Velora
echo "Verific logo..."
ls -lh /usr/share/pixmaps/velora-logo.png && echo "Logo exista!" || echo "Logo LIPSESTE!"

echo "Aplic setarile..."
kwriteconfig5 \
    --file plasma-org.kde.plasma.desktop-appletsrc \
    --group "Containments" --group "1" \
    --group "Applets" --group "2" \
    --group "Configuration" --group "General" \
    --key "icon" "/usr/share/pixmaps/velora-logo.png"

kwriteconfig5 \
    --file plasma-org.kde.plasma.desktop-appletsrc \
    --group "Containments" --group "1" \
    --group "Applets" --group "2" \
    --group "Configuration" --group "General" \
    --key "useCustomButtonImage" "true"

echo "Repornesc plasmashell..."
kquitapp5 plasmashell
sleep 2
kstart5 plasmashell &

echo "Gata! Verifica taskbar-ul."
