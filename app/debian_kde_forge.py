#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Debian KDE Forge project author
import sys, tarfile, subprocess, datetime, json
from pathlib import Path
from PyQt6.QtCore import Qt, QProcess, QTimer
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QCheckBox, QScrollArea, QGroupBox, QFileDialog,
    QMessageBox, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QSplitter
)

APP_NAME = "Debian KDE Forge"
APP_VERSION = "1.0"
BASE = Path(__file__).resolve().parent.parent
ICON = BASE / "assets" / "debian-kde-forge.svg"
HOME = Path.home()
CURRENT_STABLE = "trixie"
CURRENT_TESTING = "forky"

CATEGORIES = {
    "Base esencial": [
        "sudo", "curl", "wget", "git", "ca-certificates", "gnupg", "lsb-release",
        "software-properties-common", "apt-transport-https", "build-essential", "dkms",
        "linux-headers-amd64", "apt-listchanges", "synaptic", "gdebi", "gdebi-core"
    ],
    "KDE / escritorio": [
        "kde-plasma-desktop", "plasma-workspace-wayland", "kde-config-gtk-style",
        "qt6ct", "qt6-wayland", "breeze", "breeze-gtk-theme", "papirus-icon-theme",
        "kate", "kcalc", "gwenview", "dolphin-plugins", "ark", "kio-extras", "plasma-discover",
        "gnome-software-plugin-flatpak", "kdiskmark", "konsole"
    ],
    "Gaming": [
        "steam", "lutris", "gamemode", "mangohud", "goverlay", "vkbasalt",
        "vulkan-tools", "mesa-vulkan-drivers", "libvulkan1", "winetricks", "wine",
        "wine64", "protontricks"
    ],
    "Streaming / video / audio": [
        "obs-studio", "vlc", "ffmpeg", "kdenlive", "handbrake", "audacity",
        "libavcodec-extra", "gstreamer1.0-libav", "gstreamer1.0-plugins-ugly",
        "gstreamer1.0-plugins-bad", "gstreamer1.0-pulseaudio", "vorbis-tools",
        "pipewire", "pipewire-audio", "wireplumber", "pavucontrol"
    ],
    "Productividad / Internet": [
        "libreoffice", "firefox-esr", "thunderbird", "remmina", "filezilla", "keepassxc"
    ],
    "Fuentes": [
        "fonts-freefont-ttf", "fonts-freefont-otf", "ttf-mscorefonts-installer",
        "fonts-ubuntu", "fonts-noto", "fonts-noto-color-emoji", "fonts-crosextra-carlito",
        "fonts-crosextra-caladea"
    ],
    "Compresión y discos": [
        "p7zip-full", "p7zip-rar", "rar", "unrar", "exfat-fuse", "exfatprogs",
        "hfsplus", "hfsutils", "ntfs-3g", "gparted", "smartmontools", "nvme-cli"
    ],
    "Monitoreo / terminal": [
        "htop", "btop", "neofetch", "fastfetch", "micro", "tmux", "ncdu", "lm-sensors",
        "pciutils", "usbutils", "inxi", "ghostty"
    ]
}

FLATPAKS = {
    "Spotify": "com.spotify.Client",
    "Discord": "com.discordapp.Discord",
    "Heroic Games Launcher": "com.heroicgameslauncher.hgl",
    "ProtonPlus": "com.vysp3r.ProtonPlus",
    "Faugus Launcher": "io.github.Faugus.faugus-launcher",
    "Google Chrome": "com.google.Chrome",
    "Visual Studio Code": "com.visualstudio.code",
    "OBS Studio Flatpak": "com.obsproject.Studio",
    "Steam Flatpak": "com.valvesoftware.Steam"
}

DESKTOP_ENVIRONMENTS = {
    "GNOME": {
        "package": "task-gnome-desktop",
        "note": "Escritorio completo e integrado; buena opción general para Debian."
    },
    "KDE Plasma": {
        "package": "task-kde-desktop",
        "note": "Plasma completo usando los paquetes task oficiales de Debian."
    },
    "Xfce": {
        "package": "task-xfce-desktop",
        "note": "Ligero, estable y recomendable para equipos modestos."
    },
    "LXQt": {
        "package": "task-lxqt-desktop",
        "note": "Muy liviano, basado en Qt."
    },
    "LXDE": {
        "package": "task-lxde-desktop",
        "note": "Clásico y muy liviano."
    },
    "MATE": {
        "package": "task-mate-desktop",
        "note": "Tradicional, completo y equilibrado."
    },
    "Cinnamon": {
        "package": "task-cinnamon-desktop",
        "note": "Escritorio clásico moderno, cómodo para usuarios nuevos."
    },
    "GNOME Flashback": {
        "package": "task-gnome-flashback-desktop",
        "note": "Experiencia GNOME más tradicional."
    }
}

KDE_CONFIG_PATHS = [
    ".config/plasma-org.kde.plasma.desktop-appletsrc", ".config/plasmarc", ".config/plasmashellrc",
    ".config/plasma-localerc", ".config/kdeglobals", ".config/kwinrc", ".config/kwinrulesrc",
    ".config/kglobalshortcutsrc", ".config/khotkeysrc", ".config/kcminputrc", ".config/kscreenlockerrc",
    ".config/dolphinrc", ".config/konsolerc", ".config/gtk-3.0", ".config/gtk-4.0",
    ".local/share/plasma", ".local/share/aurorae", ".local/share/color-schemes",
    ".local/share/icons", ".local/share/wallpapers", ".local/share/konsole", ".local/share/dolphin",
    ".themes", ".icons", "Imágenes", "Pictures"
]

STYLE_DARK = """
QMainWindow, QWidget { background:#0f172a; color:#e5e7eb; font-size: 13px; }
QTabWidget::pane { border:1px solid #334155; border-radius:10px; }
QTabBar::tab { background:#1e293b; padding:10px 14px; border-top-left-radius:8px; border-top-right-radius:8px; }
QTabBar::tab:selected { background:#2563eb; color:white; }
QPushButton { background:#2563eb; color:white; border:0; padding:9px 12px; border-radius:8px; }
QPushButton:hover { background:#1d4ed8; }
QPushButton:disabled { background:#475569; color:#94a3b8; }
QGroupBox { border:1px solid #334155; border-radius:12px; margin-top:12px; padding:12px; font-weight:bold; }
QGroupBox::title { subcontrol-origin: margin; left:12px; padding:0 6px; }
QTextEdit, QLineEdit, QTableWidget, QComboBox { background:#020617; color:#e5e7eb; border:1px solid #334155; border-radius:8px; padding:6px; }
QCheckBox { padding:4px; }
QHeaderView::section { background:#1e293b; color:#e5e7eb; padding:6px; border:0; }
"""
STYLE_LIGHT = """
QMainWindow, QWidget { background:#f8fafc; color:#0f172a; font-size: 13px; }
QTabWidget::pane { border:1px solid #cbd5e1; border-radius:10px; }
QTabBar::tab { background:#e2e8f0; padding:10px 14px; border-top-left-radius:8px; border-top-right-radius:8px; }
QTabBar::tab:selected { background:#2563eb; color:white; }
QPushButton { background:#2563eb; color:white; border:0; padding:9px 12px; border-radius:8px; }
QPushButton:hover { background:#1d4ed8; }
QGroupBox { border:1px solid #cbd5e1; border-radius:12px; margin-top:12px; padding:12px; font-weight:bold; }
QGroupBox::title { subcontrol-origin: margin; left:12px; padding:0 6px; }
QTextEdit, QLineEdit, QTableWidget, QComboBox { background:white; color:#0f172a; border:1px solid #cbd5e1; border-radius:8px; padding:6px; }
QHeaderView::section { background:#e2e8f0; color:#0f172a; padding:6px; border:0; }
"""

def os_release():
    try:
        data = {}
        for line in Path("/etc/os-release").read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                data[k] = v.strip().strip('"')
        return data
    except Exception:
        return {}

def is_debian():
    return os_release().get("ID") == "debian"

def debian_codename():
    data = os_release()
    return data.get("VERSION_CODENAME") or data.get("DEBIAN_CODENAME") or ""

def debian_track():
    code = debian_codename()
    if code == CURRENT_STABLE:
        return "stable"
    if code == CURRENT_TESTING:
        return "testing"
    try:
        sources = "\n".join(
            p.read_text(errors="ignore")
            for p in [Path("/etc/apt/sources.list"), *Path("/etc/apt/sources.list.d").glob("*")]
            if p.is_file()
        ).lower()
        if " testing" in sources or f" {CURRENT_TESTING}" in sources:
            return "testing"
        if " stable" in sources or f" {CURRENT_STABLE}" in sources:
            return "stable"
    except Exception:
        pass
    return "unknown"

def debian_label():
    if not is_debian():
        return "Sistema no Debian"
    code = debian_codename() or "sin codename"
    track = debian_track()
    if track == "stable":
        return f"Debian Stable ({code})"
    if track == "testing":
        return f"Debian Testing ({code})"
    return f"Debian ({code})"

def shell_quote(value):
    return "'" + value.replace("'", "'\"'\"'") + "'"

def packages_cmd(packages):
    return " ".join(shell_quote(p) for p in packages)

def apt_install_available_cmd(packages):
    quoted = packages_cmd(packages)
    return f"""
apt update
install_pkgs=""
for pkg in {quoted}; do
  if apt-cache show "$pkg" >/dev/null 2>&1; then
    install_pkgs="$install_pkgs $pkg"
  else
    echo "[omitido] $pkg no está disponible en esta rama/repositorio Debian"
  fi
done
if [ -n "$install_pkgs" ]; then
  DEBIAN_FRONTEND=noninteractive apt install -y $install_pkgs
else
  echo "No hay paquetes disponibles para instalar."
fi
"""

class Forge(QMainWindow):
    def __init__(self):
        super().__init__()
        self.proc = None
        self.checks = {}
        self.flat_checks = {}
        self.de_checks = {}
        self.debian = is_debian()
        self.codename = debian_codename()
        self.track = debian_track()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        if ICON.exists(): self.setWindowIcon(QIcon(str(ICON)))
        self.resize(1180, 760)
        self.build_ui()
        self.apply_theme("Oscuro")
        QTimer.singleShot(500, self.refresh_status)

    def build_ui(self):
        root = QWidget(); self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        header = QHBoxLayout()
        title = QLabel(f"<h1>{APP_NAME}</h1><p>{debian_label()}: instalación, drivers, escritorios, gaming, backup y restauración KDE.</p>")
        header.addWidget(title, 1)
        self.theme = QComboBox(); self.theme.addItems(["Oscuro", "Claro", "Sistema"]); self.theme.currentTextChanged.connect(self.apply_theme)
        header.addWidget(QLabel("Tema:")); header.addWidget(self.theme)
        outer.addLayout(header)

        split = QSplitter(Qt.Orientation.Vertical)
        self.tabs = QTabWidget(); split.addWidget(self.tabs)
        self.terminal = QTextEdit(); self.terminal.setReadOnly(True); self.terminal.setFont(QFont("monospace", 10)); split.addWidget(self.terminal)
        split.setSizes([520, 220]); outer.addWidget(split)
        self.statusBar().showMessage("Listo")

        self.make_help_tab(); self.make_install_tab(); self.make_desktop_tab(); self.make_drivers_tab(); self.make_kde_tab(); self.make_opt_tab(); self.make_repos_tab(); self.make_status_tab()

    def apply_theme(self, name):
        if name == "Claro": self.setStyleSheet(STYLE_LIGHT)
        elif name == "Sistema": self.setStyleSheet("")
        else: self.setStyleSheet(STYLE_DARK)

    def log(self, text):
        self.terminal.append(text.rstrip())
        self.terminal.verticalScrollBar().setValue(self.terminal.verticalScrollBar().maximum())

    def run(self, cmd, root=False):
        if self.proc and self.proc.state() != QProcess.ProcessState.NotRunning:
            QMessageBox.warning(self, "Proceso en ejecución", "Esperá a que termine el proceso actual.")
            return
        if root and not self.debian:
            QMessageBox.warning(
                self,
                "Sistema no Debian",
                "Esta acción ejecutaría comandos de administrador pensados para Debian/APT.\n\n"
                "En este sistema se bloqueó para que puedas revisar la interfaz sin modificar CachyOS."
            )
            self.log("\n[Acción bloqueada: comandos root/APT deshabilitados fuera de Debian]\n")
            return
        full = cmd
        if root:
            full = f"pkexec bash -lc {json.dumps(cmd)}"
        self.log(f"\n$ {full}\n")
        self.proc = QProcess(self)
        self.proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.proc.readyReadStandardOutput.connect(lambda: self.log(bytes(self.proc.readAllStandardOutput()).decode(errors='replace')))
        self.proc.finished.connect(lambda code, status: self.finish_proc(code))
        self.proc.start("bash", ["-lc", full])

    def finish_proc(self, code):
        self.log(f"\n[Proceso finalizado con código {code}]\n")
        self.statusBar().showMessage("Proceso finalizado")
        self.refresh_status()

    def make_help_tab(self):
        tab = QWidget(); lay = QVBoxLayout(tab)
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
<h2>Ayuda de Debian KDE Forge</h2>
<p><b>Objetivo:</b> preparar Debian Stable o Debian Testing para uso diario, gaming,
streaming, productividad, drivers propietarios, entornos de escritorio y migración de configuración KDE.</p>

<h3>Antes de empezar</h3>
<ul>
  <li>Usar en Debian Stable o Debian Testing. En otros sistemas se abre en modo vista y se bloquean acciones APT/root.</li>
  <li>Leer la salida de la terminal inferior antes de cerrar la app o reiniciar.</li>
  <li>Ejecutar una sola acción por vez y esperar a que termine.</li>
  <li>Hacer backup antes de cambiar repositorios, restaurar KDE o aplicar ajustes grandes.</li>
</ul>

<h3>Orden recomendado para una instalación correcta</h3>
<ol>
  <li><b>Estado:</b> pulsar "Comprobar estado y versiones" para revisar qué paquetes y Flatpaks ya existen.</li>
  <li><b>Repositorios:</b> elegir Stable o Testing. Stable agrega seguridad, updates y backports; Testing usa la rama testing sin backports.</li>
  <li><b>Instalador:</b> pulsar "Actualizar repositorios". Después seleccionar Base esencial y utilidades necesarias.</li>
  <li><b>Entornos:</b> instalar GNOME, KDE Plasma, Xfce, LXQt, LXDE, MATE, Cinnamon o GNOME Flashback si querés sumar escritorios.</li>
  <li><b>Drivers propietarios:</b> primero usar "Detectar GPU". Instalar NVIDIA solo si tu GPU es NVIDIA y necesitás el driver propietario.</li>
  <li><b>Instalador / Flatpak:</b> elegir apps de Flathub como Discord, Spotify, Chrome, VS Code, Heroic, ProtonPlus u OBS.</li>
  <li><b>Gaming/Productividad:</b> aplicar la optimización recomendada cuando el sistema base, escritorios y drivers ya estén listos.</li>
  <li><b>Backup KDE:</b> crear un backup final cuando el escritorio quede como querés.</li>
  <li><b>Reiniciar:</b> cerrar sesión o reiniciar el sistema para aplicar grupos, drivers, servicios y sesiones.</li>
</ol>

<h3>Qué hace cada pestaña</h3>
<p><b>Instalador:</b> instala paquetes APT por categorías y aplicaciones Flatpak desde Flathub.</p>
<p><b>Entornos:</b> instala metapaquetes task oficiales para GNOME, KDE Plasma, Xfce, LXQt, LXDE, MATE, Cinnamon y GNOME Flashback.</p>
<p><b>Drivers propietarios:</b> detecta GPU, habilita repositorios non-free/firmware e instala firmware, NVIDIA o Vulkan/Mesa.</p>
<p><b>Backup KDE:</b> guarda o restaura configuraciones de Plasma, Dolphin, Konsole, temas, iconos, wallpapers y atajos.</p>
<p><b>Gaming/Productividad:</b> instala herramientas como GameMode, MangoHud, Vulkan, Steam, Lutris, OBS, codecs y servicios útiles.</p>
<p><b>Repositorios:</b> configura Debian Stable o Testing, backports solo en Stable, actualizaciones completas y migración controlada a Testing/Forky.</p>
<p><b>Estado:</b> muestra si los paquetes y apps recomendadas están instalados y, en Debian, sus versiones disponibles.</p>

<h3>Recomendaciones importantes</h3>
<ul>
  <li>No uses Testing/Forky salvo que aceptes un sistema más cambiante y posibles roturas.</li>
  <li>No uses backports en Testing; Testing ya recibe paquetes más nuevos desde su propia rama.</li>
  <li>No instales driver NVIDIA si usás AMD o Intel.</li>
  <li>Preferí Flatpak para apps externas como Chrome, VS Code, Discord o Spotify si querés evitar repositorios de terceros.</li>
  <li>Si algo falla, copiá la salida de la terminal inferior: ahí queda el comando ejecutado y el error.</li>
</ul>
""")
        lay.addWidget(help_text)
        self.tabs.addTab(tab, "Ayuda")

    def make_install_tab(self):
        tab = QWidget(); lay = QVBoxLayout(tab)
        info_text = "Seleccioná paquetes APT y apps Flatpak. El programa verifica qué está instalado y muestra versión disponible."
        if not self.debian:
            info_text += " Modo vista: las acciones APT/root están bloqueadas fuera de Debian."
        info = QLabel(info_text)
        info.setWordWrap(True)
        lay.addWidget(info)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); body = QWidget(); bl = QVBoxLayout(body)
        for cat, pkgs in CATEGORIES.items():
            box = QGroupBox(cat); vl = QVBoxLayout(box)
            row = QHBoxLayout(); sel = QPushButton("Seleccionar todo"); unsel = QPushButton("Limpiar")
            row.addWidget(sel); row.addWidget(unsel); row.addStretch(); vl.addLayout(row)
            local=[]
            for p in pkgs:
                cb=QCheckBox(p); self.checks[p]=cb; local.append(cb); vl.addWidget(cb)
            sel.clicked.connect(lambda _, items=local: [c.setChecked(True) for c in items])
            unsel.clicked.connect(lambda _, items=local: [c.setChecked(False) for c in items])
            bl.addWidget(box)
        fbox = QGroupBox("Apps recomendadas vía Flatpak / Flathub")
        fv = QVBoxLayout(fbox)
        for name, appid in FLATPAKS.items():
            cb=QCheckBox(f"{name}  ({appid})"); self.flat_checks[appid]=cb; fv.addWidget(cb)
        bl.addWidget(fbox); bl.addStretch(); scroll.setWidget(body); lay.addWidget(scroll)
        buttons = QHBoxLayout()
        b1=QPushButton("Actualizar repositorios"); b1.clicked.connect(lambda: self.run("apt update", True))
        b2=QPushButton("Instalar seleccionados"); b2.clicked.connect(self.install_selected)
        b3=QPushButton("Instalar Flathub + seleccionados"); b3.clicked.connect(self.install_flatpaks)
        buttons.addWidget(b1); buttons.addWidget(b2); buttons.addWidget(b3); buttons.addStretch(); lay.addLayout(buttons)
        self.tabs.addTab(tab, "Instalador")

    def install_selected(self):
        pkgs=[p for p,c in self.checks.items() if c.isChecked()]
        if not pkgs: return QMessageBox.information(self,"Sin selección","No seleccionaste paquetes APT.")
        cmd=apt_install_available_cmd(pkgs)
        self.run(cmd, True)

    def install_flatpaks(self):
        apps=[a for a,c in self.flat_checks.items() if c.isChecked()]
        if not apps: return QMessageBox.information(self,"Sin selección","No seleccionaste aplicaciones Flatpak.")
        cmd=apt_install_available_cmd(["flatpak", "plasma-discover-backend-flatpak", "gnome-software-plugin-flatpak"]) + "\nflatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo && flatpak install -y flathub " + packages_cmd(apps)
        self.run(cmd, True)

    def make_desktop_tab(self):
        tab=QWidget(); lay=QVBoxLayout(tab)
        info=QLabel("Instalación de entornos de escritorio ofrecidos por Debian mediante paquetes task oficiales. Podés tener varios instalados y elegir sesión desde el gestor de inicio.")
        info.setWordWrap(True); lay.addWidget(info)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); body=QWidget(); bl=QVBoxLayout(body)
        for name, meta in DESKTOP_ENVIRONMENTS.items():
            cb=QCheckBox(f"{name}  ({meta['package']}) - {meta['note']}")
            self.de_checks[meta["package"]]=cb
            bl.addWidget(cb)
        bl.addStretch(); scroll.setWidget(body); lay.addWidget(scroll)
        buttons=QHBoxLayout()
        b1=QPushButton("Actualizar repositorios")
        b1.clicked.connect(lambda: self.run("apt update", True))
        b2=QPushButton("Instalar entornos seleccionados")
        b2.clicked.connect(self.install_desktops)
        b3=QPushButton("Instalar tasksel")
        b3.clicked.connect(lambda: self.run(apt_install_available_cmd(["tasksel"]), True))
        buttons.addWidget(b1); buttons.addWidget(b2); buttons.addWidget(b3); buttons.addStretch(); lay.addLayout(buttons)
        self.tabs.addTab(tab,"Entornos")

    def install_desktops(self):
        pkgs=[p for p,c in self.de_checks.items() if c.isChecked()]
        if not pkgs: return QMessageBox.information(self,"Sin selección","No seleccionaste entornos de escritorio.")
        if QMessageBox.question(self,"Confirmar instalación", "Instalar varios escritorios puede descargar muchos paquetes y agregar nuevos gestores de sesión. ¿Continuar?") != QMessageBox.StandardButton.Yes:
            return
        self.run(apt_install_available_cmd(["tasksel", *pkgs]), True)

    def make_drivers_tab(self):
        tab=QWidget(); lay=QVBoxLayout(tab)
        lay.addWidget(QLabel("Drivers propietarios y firmware. Para NVIDIA se habilita non-free/non-free-firmware y se instala el driver Debian empaquetado."))
        cmds=[
            ("Detectar GPU", "lspci -nn | grep -Ei 'vga|3d|display|nvidia|amd|intel' || true", False),
            ("Habilitar repos non-free/firmware", self.cmd_sources_for_track(self.track if self.track in ("stable", "testing") else "stable"), True),
            ("Instalar NVIDIA propietario", apt_install_available_cmd(["nvidia-driver", "firmware-misc-nonfree", "nvidia-settings", "nvidia-smi", "linux-headers-amd64", "dkms"]) + "\nupdate-initramfs -u || true", True),
            ("Instalar firmware general", apt_install_available_cmd(["firmware-linux", "firmware-linux-nonfree", "firmware-misc-nonfree", "firmware-realtek", "firmware-iwlwifi", "firmware-amd-graphics", "intel-microcode", "amd64-microcode"]), True),
            ("Instalar Vulkan/mesa", apt_install_available_cmd(["mesa-vulkan-drivers", "vulkan-tools", "libvulkan1", "mesa-utils"]), True)
        ]
        for text, cmd, root in cmds:
            b=QPushButton(text); b.clicked.connect(lambda _, c=cmd, r=root: self.run(c,r)); lay.addWidget(b)
        lay.addStretch(); self.tabs.addTab(tab,"Drivers propietarios")

    def make_kde_tab(self):
        tab=QWidget(); lay=QVBoxLayout(tab)
        lay.addWidget(QLabel("Backup y restauración de Plasma 6: temas, iconos, cursores, wallpapers, widgets, paneles, atajos, Dolphin, Konsole y estilos."))
        b1=QPushButton("Crear backup KDE completo") ; b1.clicked.connect(self.kde_backup)
        b2=QPushButton("Restaurar backup KDE desde .tar.gz") ; b2.clicked.connect(self.kde_restore)
        b3=QPushButton("Reiniciar Plasma Shell") ; b3.clicked.connect(lambda: self.run("kquitapp6 plasmashell || true; kstart plasmashell || kstart6 plasmashell || plasmashell &", False))
        lay.addWidget(b1); lay.addWidget(b2); lay.addWidget(b3); lay.addStretch(); self.tabs.addTab(tab,"Backup KDE")

    def kde_backup(self):
        target, _ = QFileDialog.getSaveFileName(self, "Guardar backup", str(HOME/ f"backup-kde-plasma6-{datetime.date.today()}.tar.gz"), "Tar GZ (*.tar.gz)")
        if not target: return
        with tarfile.open(target, "w:gz") as tar:
            for rel in KDE_CONFIG_PATHS:
                p=HOME/rel
                if p.exists(): tar.add(p, arcname=rel)
        self.log(f"Backup KDE creado: {target}")
        QMessageBox.information(self,"Backup creado",f"Backup guardado en:\n{target}")

    def kde_restore(self):
        source, _ = QFileDialog.getOpenFileName(self, "Seleccionar backup KDE", str(HOME), "Tar GZ (*.tar.gz)")
        if not source: return
        if QMessageBox.question(self,"Confirmar", "Esto va a sobrescribir configuraciones KDE actuales. ¿Continuar?") != QMessageBox.StandardButton.Yes: return
        with tarfile.open(source,"r:gz") as tar:
            tar.extractall(HOME)
        self.log(f"Backup KDE restaurado desde: {source}")
        QMessageBox.information(self,"Restaurado","Cerrá sesión o reiniciá Plasma para aplicar todos los cambios.")

    def make_opt_tab(self):
        tab=QWidget(); lay=QVBoxLayout(tab)
        lay.addWidget(QLabel("Optimización equilibrada para gaming + productividad + streaming. No aplica overclock ni cambios agresivos."))
        b=QPushButton("Aplicar optimización recomendada")
        cmd=apt_install_available_cmd(["gamemode", "mangohud", "goverlay", "vkbasalt", "vulkan-tools", "mesa-vulkan-drivers", "libvulkan1", "steam", "lutris", "obs-studio", "ffmpeg", "kdenlive", "handbrake", "pipewire", "pipewire-audio", "wireplumber", "pavucontrol", "linux-headers-amd64", "dkms", "cpufrequtils", "irqbalance", "earlyoom", "preload"]) + """
systemctl enable --now irqbalance earlyoom || true
usermod -aG video,audio,render,input,plugdev,sudo "$SUDO_USER" || true
mkdir -p /etc/sysctl.d
cat >/etc/sysctl.d/99-debian-kde-forge-gaming.conf <<'EOF'
vm.swappiness=10
vm.vfs_cache_pressure=50
fs.inotify.max_user_watches=1048576
EOF
sysctl --system || true
"""
        b.clicked.connect(lambda: self.run(cmd, True)); lay.addWidget(b)
        b2=QPushButton("Permitir sudo al usuario actual")
        b2.clicked.connect(lambda: self.run('usermod -aG sudo "$SUDO_USER" && echo "Usuario agregado al grupo sudo. Cerrá sesión y volvé a entrar."', True))
        lay.addWidget(b2)
        lay.addStretch(); self.tabs.addTab(tab,"Gaming/Productividad")

    def cmd_sources_for_track(self, track):
        if track == "testing":
            suite = self.codename if self.codename == CURRENT_TESTING else CURRENT_TESTING
            return f"""
mkdir -p /etc/apt/sources.list.d
cp -a /etc/apt/sources.list /etc/apt/sources.list.bak.$(date +%F_%H%M) 2>/dev/null || true
cat >/etc/apt/sources.list.d/debian-kde-forge-testing.sources <<'EOF'
Types: deb
URIs: https://deb.debian.org/debian
Suites: {suite}
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
EOF
apt update
"""
        suite = self.codename if self.codename == CURRENT_STABLE else CURRENT_STABLE
        return f"""
mkdir -p /etc/apt/sources.list.d
cp -a /etc/apt/sources.list /etc/apt/sources.list.bak.$(date +%F_%H%M) 2>/dev/null || true
cat >/etc/apt/sources.list.d/debian-kde-forge-stable.sources <<'EOF'
Types: deb
URIs: https://deb.debian.org/debian
Suites: {suite} {suite}-updates {suite}-backports
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

Types: deb
URIs: https://security.debian.org/debian-security
Suites: {suite}-security
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
EOF
apt update
"""

    def run_backports_kernel(self):
        if self.track != "stable":
            QMessageBox.warning(self, "Backports no disponible", "Backports está pensado para Debian Stable. En Testing usá el kernel de la propia rama testing.")
            return
        suite = self.codename if self.codename == CURRENT_STABLE else CURRENT_STABLE
        self.run(f"apt update && apt install -y -t {suite}-backports linux-image-amd64 linux-headers-amd64", True)

    def make_repos_tab(self):
        tab=QWidget(); lay=QVBoxLayout(tab)
        lay.addWidget(QLabel(f"Repositorios oficiales para {debian_label()}. Stable usa {CURRENT_STABLE}; Testing usa {CURRENT_TESTING}."))
        b1=QPushButton("Configurar Debian Stable + backports + non-free firmware")
        b1.clicked.connect(lambda: self.run(self.cmd_sources_for_track("stable"), True)); lay.addWidget(b1)
        b1b=QPushButton("Configurar Debian Testing + non-free firmware")
        b1b.clicked.connect(lambda: self.confirm_testing(self.cmd_sources_for_track("testing"))); lay.addWidget(b1b)
        b2=QPushButton("Actualizar sistema completo")
        b2.clicked.connect(lambda: self.run("apt update && apt full-upgrade -y && apt autoremove -y", True)); lay.addWidget(b2)
        b3=QPushButton("Instalar kernel desde backports de Stable")
        b3.clicked.connect(self.run_backports_kernel); lay.addWidget(b3)
        b4=QPushButton("Cambiar a Debian Testing/Forky")
        testcmd=self.cmd_sources_for_track("testing") + "\napt full-upgrade -y\n"
        b4.clicked.connect(lambda: self.confirm_testing(testcmd)); lay.addWidget(b4)
        lay.addStretch(); self.tabs.addTab(tab,"Repositorios")

    def confirm_testing(self, cmd):
        if QMessageBox.warning(self,"Riesgo: Debian Testing", "Esto cambia Debian Stable a Testing/Forky. Puede romper paquetes o drivers. ¿Continuar?", QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.run(cmd, True)

    def make_status_tab(self):
        tab=QWidget(); lay=QVBoxLayout(tab)
        self.table=QTableWidget(0,4); self.table.setHorizontalHeaderLabels(["Paquete/App", "Tipo", "Instalado", "Versión"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self.table)
        b=QPushButton("Comprobar estado y versiones") ; b.clicked.connect(self.refresh_status); lay.addWidget(b)
        self.tabs.addTab(tab,"Estado")

    def refresh_status(self):
        if not hasattr(self,"table"): return
        items=[]
        for pkgs in CATEGORIES.values():
            for p in pkgs: items.append((p,"APT"))
        for meta in DESKTOP_ENVIRONMENTS.values():
            items.append((meta["package"],"APT"))
        for name, appid in FLATPAKS.items(): items.append((appid,"Flatpak"))
        self.table.setRowCount(0)
        for name, typ in items:
            row=self.table.rowCount(); self.table.insertRow(row)
            installed="No"; version="-"
            try:
                if typ=="APT" and self.debian:
                    r=subprocess.run(["dpkg-query","-W","-f=${Version}",name],capture_output=True,text=True,timeout=2)
                    if r.returncode==0: installed="Sí"; version=r.stdout.strip()
                    else:
                        a=subprocess.run(["apt-cache","policy",name],capture_output=True,text=True,timeout=2)
                        for line in a.stdout.splitlines():
                            if "Candidate:" in line: version="Disponible: "+line.split(":",1)[1].strip()
                elif typ=="APT":
                    version="Solo Debian/APT"
                else:
                    r=subprocess.run(["flatpak","info",name],capture_output=True,text=True,timeout=2)
                    if r.returncode==0: installed="Sí"; version="Instalado"
            except Exception:
                pass
            for col,val in enumerate([name,typ,installed,version]): self.table.setItem(row,col,QTableWidgetItem(val))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Forge(); w.show()
    if not is_debian():
        QMessageBox.warning(w,"Sistema no Debian", "La app está pensada para Debian Stable o Debian Testing. Las acciones APT/root quedan bloqueadas fuera de Debian.")
    sys.exit(app.exec())
