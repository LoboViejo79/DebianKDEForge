#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -r /etc/os-release ] || ! grep -qiE '^ID=debian$' /etc/os-release; then
  echo "Este instalador está pensado para Debian Stable/Testing."
  exit 1
fi
if [ "${EUID:-$(id -u)}" -ne 0 ]; then
  echo "Ejecutá: sudo ./install.sh"
  exit 1
fi
apt-get update
apt-get install -y python3 python3-pyqt6 polkitd pkexec apt-utils sudo locales desktop-file-utils
chmod +x autorun.sh install-desktop-entry.sh
USER_HOME="${SUDO_USER:+$(getent passwd "$SUDO_USER" | cut -d: -f6)}"
if [ -n "${SUDO_USER:-}" ] && [ -n "$USER_HOME" ]; then
  runuser -u "$SUDO_USER" -- ./install-desktop-entry.sh || true
else
  ./install-desktop-entry.sh || true
fi
echo
echo "Instalación terminada. Ejecutá: ./autorun.sh"
