#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -r /etc/os-release ] || ! grep -qiE '^ID=debian$' /etc/os-release; then
  echo "Debian KDE Forge está diseñado para Debian Stable/Testing."
  exit 1
fi
if ! python3 -c 'import PyQt6' >/dev/null 2>&1; then
  echo "Falta PyQt6. Instalando dependencias mínimas..."
  if command -v pkexec >/dev/null 2>&1; then
    pkexec bash -lc 'apt-get update && apt-get install -y python3 python3-pyqt6 polkitd pkexec apt-utils sudo locales'
  else
    su -c 'apt-get update && apt-get install -y python3 python3-pyqt6 polkitd pkexec apt-utils sudo locales'
  fi
fi
exec python3 app/debian_kde_forge.py
