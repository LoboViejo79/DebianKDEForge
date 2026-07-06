# Notas de seguridad

- El programa usa `pkexec` para pedir permisos de administrador cuando instala paquetes o modifica repositorios.
- Antes de tocar repositorios crea backup de `/etc/apt/sources.list` cuando existe.
- La migración KDE copia configuraciones del usuario, no toca `/etc` salvo que uses secciones de repositorios, drivers u optimización.
- Para aplicar restauración KDE completa, cerrar sesión o reiniciar Plasma.
- Debian Testing/Forky no es estable; usar solo si aceptás el riesgo.
