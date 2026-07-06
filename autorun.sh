#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -e
cd "$(dirname "$0")"

is_debian=0
if [ -r /etc/os-release ] && grep -qiE '(^ID=debian$|ID_LIKE=.*debian)' /etc/os-release; then
  is_debian=1
fi

if ! python3 -c 'import PyQt6' >/dev/null 2>&1; then
  if [ "$is_debian" = "1" ] && [ "${1:-}" = "--install-deps" ]; then
    echo "Instalando dependencias necesarias para ejecutar Debian KDE Forge..."
    if command -v pkexec >/dev/null 2>&1; then
      pkexec bash -lc 'apt update && apt install -y python3 python3-pyqt6 policykit-1 pkexec apt-utils'
    else
      su -c 'apt update && apt install -y python3 python3-pyqt6 policykit-1 pkexec apt-utils'
    fi
  else
    echo "Falta PyQt6 para abrir la interfaz."
    if [ "$is_debian" = "1" ]; then
      echo "En Debian podés instalar dependencias ejecutando: ./autorun.sh --install-deps"
    else
      echo "En CachyOS/Arch instalá PyQt6 con tu gestor de paquetes, por ejemplo: sudo pacman -S python-pyqt6"
    fi
    exit 1
  fi
fi

python3 app/debian_kde_forge.py
