#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-only
set -e
cd "$(dirname "$0")"

is_debian=0
if [ -r /etc/os-release ] && grep -qiE '^ID=debian$' /etc/os-release; then
  is_debian=1
fi

if [ "$is_debian" != "1" ]; then
  echo "Debian KDE Forge está diseñado para ejecutarse en Debian Stable o Debian Testing."
  exit 1
fi

if ! python3 -c 'import PyQt6' >/dev/null 2>&1; then
  if [ "${1:-}" = "--install-deps" ]; then
    echo "Instalando dependencias necesarias para ejecutar Debian KDE Forge..."
    if command -v pkexec >/dev/null 2>&1; then
      pkexec bash -lc 'apt update && apt install -y python3 python3-pyqt6 policykit-1 pkexec apt-utils'
    else
      su -c 'apt update && apt install -y python3 python3-pyqt6 policykit-1 pkexec apt-utils'
    fi
  else
    echo "Falta PyQt6 para abrir la interfaz."
    echo "Instalá las dependencias ejecutando: ./install.sh"
    echo "Alternativa directa: ./autorun.sh --install-deps"
    exit 1
  fi
fi

python3 app/debian_kde_forge.py
