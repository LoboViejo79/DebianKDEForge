#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -e
cd "$(dirname "$0")"
mkdir -p "$HOME/.local/share/applications" "$HOME/.local/share/icons"
cp assets/debian-kde-forge.svg "$HOME/.local/share/icons/debian-kde-forge.svg"
cat > "$HOME/.local/share/applications/debian-kde-forge.desktop" <<DESK
[Desktop Entry]
Name=Debian KDE Forge
Comment=Configurar Debian 13 KDE Plasma para gaming, productividad y restauración KDE
Exec=$(pwd)/autorun.sh
Icon=$HOME/.local/share/icons/debian-kde-forge.svg
Terminal=false
Type=Application
Categories=System;Settings;
DESK
chmod +x "$HOME/.local/share/applications/debian-kde-forge.desktop"
echo "Entrada creada en el menú de aplicaciones."
