# Debian KDE Forge

Asistente gráfico para preparar Debian Stable o Debian Testing para uso diario, gaming, streaming, productividad, escritorios alternativos y migración de configuración KDE.

## Uso rápido en Debian

```bash
chmod +x autorun.sh
./autorun.sh
```

Si ya tenés PyQt6 instalado, el programa abre directamente.

## Instalación recomendada en Debian

```bash
chmod +x install.sh
./install.sh
```

El instalador hace esto:

- Instala dependencias mínimas: `python3`, `python3-pyqt6`, `policykit-1`, `pkexec` y `apt-utils`.
- Crea una entrada en el menú de aplicaciones.
- Deja listo el lanzador `./autorun.sh`.

Después de instalar, podés abrirlo desde el menú como **Debian KDE Forge** o desde terminal:

```bash
./autorun.sh
```

## Instalación manual de dependencias en Debian

Si preferís no usar `install.sh`, podés instalar solo las dependencias necesarias con:

```bash
./autorun.sh --install-deps
```

Después ejecutá:

```bash
./autorun.sh
```

## Funciones

- Instalación por categorías: multimedia, gaming, productividad, KDE, compresión, fuentes, discos, utilidades.
- Instalación de entornos de escritorio oficiales de Debian: GNOME, KDE Plasma, Xfce, LXQt, LXDE, MATE, Cinnamon y GNOME Flashback.
- Flatpak + Flathub.
- Steam, Heroic, Lutris, ProtonPlus, Discord, Spotify, OBS, VLC, Firefox, Thunderbird, Remmina, KDiskMark, Ghostty y más.
- Drivers propietarios NVIDIA desde repositorios Debian.
- Repositorios Debian Stable y Debian Testing en formato deb822.
- Backports para Debian Stable.
- Opción controlada para pasar de Debian Stable a Testing.
- Backup completo de configuración KDE Plasma.
- Restauración de configuración KDE desde ZIP/TAR.GZ.
- Optimización gaming/productividad: GameMode, MangoHud, Vulkan, PipeWire, OBS, codecs, herramientas de monitoreo.
- Salida de progreso estilo terminal dentro del programa.
- Filtro de paquetes disponibles: si un paquete no existe en Stable o Testing, se omite con aviso en la terminal interna.

## 🧭 Guía rápida dentro del programa

La aplicación incluye una pestaña **Ayuda** con el resumen de uso, el orden recomendado de ejecución y advertencias. Es lo primero que conviene leer al abrir Debian KDE Forge.

## ✅ Orden recomendado de uso

1. 🔎 **Estado**

   Pulsá **Comprobar estado y versiones** para revisar qué paquetes APT y aplicaciones Flatpak ya están instalados.

2. 📦 **Repositorios**

   En Debian Stable, ejecutá **Configurar Debian Stable + backports + non-free firmware**. En Debian Testing, usá **Configurar Debian Testing + non-free firmware**. Stable agrega seguridad, updates y backports; Testing usa su propia rama sin backports.

3. 🔄 **Instalador**

   Ejecutá **Actualizar repositorios**. Después seleccioná primero paquetes de **Base esencial** y finalmente las categorías que necesites: gaming, streaming, productividad, fuentes, discos o terminal.

4. 🧑‍💻 **Entornos de escritorio**

   Si querés sumar otro escritorio, abrí **Entornos** y seleccioná GNOME, KDE Plasma, Xfce, LXQt, LXDE, MATE, Cinnamon o GNOME Flashback. Después elegís la sesión desde el gestor de inicio de sesión.

5. 🖥️ **Drivers propietarios**

   Primero usá **Detectar GPU**. Si tenés NVIDIA y querés el driver propietario, recién ahí ejecutá **Instalar NVIDIA propietario**. Para AMD o Intel normalmente conviene usar Mesa/Vulkan y firmware general.

6. 🧩 **Flatpak / Flathub**

   Instalá aplicaciones externas desde Flatpak cuando sea posible: Discord, Spotify, Chrome, Visual Studio Code, Heroic, ProtonPlus, Steam u OBS. Es una forma limpia de evitar repositorios externos innecesarios.

7. 🚀 **Gaming/Productividad**

   Cuando el sistema base, escritorios y drivers ya estén listos, ejecutá **Aplicar optimización recomendada**. Instala herramientas de gaming, streaming, codecs, monitoreo y servicios útiles sin aplicar overclock ni cambios agresivos.

8. 💾 **Backup KDE**

   Cuando Plasma quede configurado a tu gusto, usá **Crear backup KDE completo**. Guarda temas, iconos, wallpapers, paneles, atajos, Dolphin, Konsole y configuraciones principales.

9. 🔁 **Reinicio final**

   Cerrá sesión o reiniciá el sistema para aplicar grupos de usuario, drivers, servicios y sesiones de escritorio.

## 🧰 Qué hace cada pestaña

- 🆘 **Ayuda:** explica el objetivo del programa, cómo usarlo y el orden recomendado.
- 📦 **Instalador:** instala paquetes APT por categorías y apps Flatpak seleccionadas.
- 🧑‍💻 **Entornos:** instala escritorios Debian oficiales mediante metapaquetes `task-*`.
- 🖥️ **Drivers propietarios:** detecta GPU, habilita firmware non-free e instala NVIDIA, firmware general o Vulkan/Mesa.
- 💾 **Backup KDE:** crea y restaura backups de configuración KDE Plasma.
- 🚀 **Gaming/Productividad:** instala herramientas para gaming, streaming, audio/video, rendimiento y monitoreo.
- 🧪 **Repositorios:** configura Debian Stable o Testing, backports para Stable y actualizaciones completas.
- 🔎 **Estado:** comprueba instalación y versiones disponibles.

## 💡 Sugerencias de uso

- ✅ Ejecutá una acción por vez y esperá a que termine.
- ✅ Revisá siempre la terminal inferior del programa: muestra el comando ejecutado y sus errores.
- ✅ Hacé backup antes de restaurar KDE, cambiar repositorios o aplicar optimizaciones grandes.
- ✅ Preferí Flatpak para apps externas como Chrome, VS Code, Discord o Spotify.
- ✅ Si un paquete no existe en tu rama Debian, la app lo omite y lo informa en la terminal inferior.
- ⚠️ No uses **Cambiar a Debian Testing/Forky** salvo que aceptes posibles roturas y sepas recuperarte.
- ⚠️ No uses backports en Debian Testing; Testing ya trae paquetes más nuevos desde su propia rama.
- ⚠️ No instales el driver NVIDIA propietario si tu GPU es AMD o Intel.

## Advertencia

La sección “Pasar a Testing” cambia repositorios del sistema. Es para usuarios que aceptan el riesgo de usar Debian Testing. Usá backup antes.

## Licencia

Debian KDE Forge se publica bajo **GNU General Public License v3.0 only** (`GPL-3.0-only`). Consultá [LICENSE](LICENSE).

Las modificaciones y redistribuciones deben conservar los avisos de licencia y atribución del creador original, y deben marcar claramente los cambios realizados. Ver [NOTICE](NOTICE).

Nota importante: GPLv3 permite redistribuir copias gratis o cobradas siempre que se respeten sus condiciones, incluyendo mantener la licencia GPLv3 y ofrecer el código fuente correspondiente. Una cláusula de "prohibido vender" no es compatible con GPLv3.
