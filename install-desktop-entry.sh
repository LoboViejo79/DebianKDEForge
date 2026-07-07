#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p "$HOME/.local/share/applications" "$HOME/.local/share/icons"
cp assets/debian-kde-forge.svg "$HOME/.local/share/icons/debian-kde-forge.svg" 2>/dev/null || true
cat > "$HOME/.local/share/applications/debian-kde-forge.desktop" <<DESK
[Desktop Entry]
Name=Debian KDE Forge 2.0
Comment=Configurar Debian para escritorio, gaming, productividad y Flatpak
Exec=$(pwd)/autorun.sh
Icon=$HOME/.local/share/icons/debian-kde-forge.svg
Terminal=false
Type=Application
Categories=System;Settings;
DESK
chmod +x "$HOME/.local/share/applications/debian-kde-forge.desktop"
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
kbuildsycoca6 --noincremental 2>/dev/null || kbuildsycoca5 --noincremental 2>/dev/null || true
echo "Entrada creada en el menú de aplicaciones."
