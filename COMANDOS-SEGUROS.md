# Notas de seguridad

- APT, repositorios, drivers y sudo se ejecutan con `pkexec`.
- Flatpak se instala como usuario con `--user`, no como root.
- El programa no edita directamente `/etc/sudoers`; crea `/etc/sudoers.d/90-debian-kde-forge-sudo` y valida con `visudo -c`.
- Antes de modificar `/etc/apt/sources.list`, crea backup automático.
- v2.1 omite paquetes sin candidato real para evitar errores de APT código 100.
