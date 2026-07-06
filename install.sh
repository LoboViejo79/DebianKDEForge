#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -e
cd "$(dirname "$0")"

is_debian=0
if [ -r /etc/os-release ] && grep -qiE '^ID=debian$' /etc/os-release; then
  is_debian=1
fi

if [ "$is_debian" != "1" ]; then
  echo "Este instalador está pensado para Debian Stable o Debian Testing."
  exit 1
fi

deps="python3 python3-pyqt6 policykit-1 pkexec apt-utils"
cmd="apt update && apt install -y $deps"

echo "Instalando dependencias de Debian KDE Forge..."
if command -v pkexec >/dev/null 2>&1; then
  pkexec bash -lc "$cmd"
else
  su -c "$cmd"
fi

./install-desktop-entry.sh

echo
echo "Instalación terminada."
echo "Podés ejecutar el programa con: ./autorun.sh"
echo "También debería aparecer como 'Debian KDE Forge' en el menú de aplicaciones."
