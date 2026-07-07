# Debian KDE Forge 2.1

Asistente gráfico para preparar Debian 13/Trixie con KDE, gaming, productividad, drivers, repositorios, sudo, Flatpak y backup/restauración KDE.

## Cambio importante de la versión 2.1

La instalación está separada por módulos:

- **APT** se ejecuta con permisos de administrador mediante `pkexec`.
- **Flatpak** se instala para el usuario actual con `flatpak --user`, para que las apps aparezcan en el menú de Plasma.
- **Estado** comprueba si una app está instalada como APT, Flatpak user o Flatpak system.
- Los logs se guardan en `~/.local/share/debian-kde-forge/logs/`.

## Instalación

```bash
unzip debian-kde-forge-v2.1.zip
cd debian-kde-forge-v2.1
chmod +x *.sh
sudo ./install.sh
./autorun.sh
```

## Orden recomendado

1. Abrir **Repositorios/Sudo** y configurar sources.list si hace falta.
2. Activar sudo para el usuario actual si todavía no puede usar `sudo`.
3. Abrir **APT** e instalar paquetes Debian seleccionados.
4. Abrir **Flatpak**:
   - primero instalar base Flatpak APT;
   - luego instalar apps Flatpak para el usuario.
5. Abrir **Estado** y comprobar instalación.
6. Si las apps Flatpak no aparecen en el menú, pulsar **Actualizar menú KDE** o cerrar sesión y volver a entrar.

## Seguridad

La configuración de sudo se realiza creando `/etc/sudoers.d/90-debian-kde-forge-sudo` y validando con `visudo -cf`. No se edita directamente `/etc/sudoers`.

Antes de modificar `/etc/apt/sources.list`, el programa crea un backup con fecha.


## Cambios v2.1

- El filtro APT ahora usa `apt-cache policy` y solo instala paquetes con `Candidate` real.
- `plasma-workspace-wayland` fue reemplazado por `plasma-workspace`.
- `steam` APT fue reemplazado por `steam-devices`; Steam se recomienda por Flatpak.
- Los paquetes obsoletos o sin candidato se omiten sin romper toda la instalación.
- Se agregó reparación/verificación Flatpak user y actualización del menú KDE.
