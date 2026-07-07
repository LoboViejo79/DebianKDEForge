#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
import os, sys, json, shlex, tempfile, subprocess, datetime, tarfile, re
from pathlib import Path
from PyQt6.QtCore import Qt, QProcess, QTimer
from PyQt6.QtGui import QIcon, QFont, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,
    QTextEdit,QCheckBox,QScrollArea,QGroupBox,QFileDialog,QMessageBox,QTabWidget,
    QTableWidget,QTableWidgetItem,QHeaderView,QComboBox,QProgressBar,QSplitter
)

APP_NAME='Debian KDE Forge'
APP_VERSION='2.1'
BASE=Path(__file__).resolve().parent.parent
ICON=BASE/'assets'/'debian-kde-forge.svg'
LOGDIR=Path.home()/'.local/share/debian-kde-forge/logs'
CURRENT_STABLE='trixie'
CURRENT_TESTING='forky'

CATEGORIES={
 'Base esencial':['sudo','curl','wget','git','ca-certificates','gnupg','lsb-release','apt-transport-https','build-essential','dkms','linux-headers-amd64','apt-listchanges','synaptic','gdebi','gdebi-core'],
 'KDE / escritorio':['kde-plasma-desktop','plasma-workspace','kde-config-gtk-style','qt6ct','qt6-wayland','breeze','breeze-gtk-theme','papirus-icon-theme','kate','kcalc','gwenview','dolphin-plugins','ark','kio-extras','plasma-discover','plasma-discover-backend-flatpak','kdiskmark','konsole'],
 'Gaming':['steam-devices','lutris','gamemode','mangohud','goverlay','vkbasalt','vulkan-tools','mesa-vulkan-drivers','libvulkan1','winetricks','wine','wine64','protontricks'],
 'Streaming / video / audio':['obs-studio','vlc','ffmpeg','kdenlive','handbrake','audacity','libavcodec-extra','gstreamer1.0-libav','gstreamer1.0-plugins-ugly','gstreamer1.0-plugins-bad','gstreamer1.0-pulseaudio','vorbis-tools','pipewire','pipewire-audio','wireplumber','pavucontrol'],
 'Productividad / Internet':['libreoffice','firefox-esr','thunderbird','remmina','filezilla','keepassxc'],
 'Fuentes':['fonts-freefont-ttf','fonts-freefont-otf','fonts-ubuntu','fonts-noto','fonts-noto-color-emoji','fonts-crosextra-carlito','fonts-crosextra-caladea'],
 'Compresión y discos':['p7zip-full','p7zip-rar','rar','unrar','exfat-fuse','exfatprogs','hfsplus','hfsutils','ntfs-3g','gparted','smartmontools','nvme-cli'],
 'Monitoreo / terminal':['htop','btop','fastfetch','micro','tmux','ncdu','lm-sensors','pciutils','usbutils','inxi']
}
FLATPAKS={
 'Spotify':'com.spotify.Client','Discord':'com.discordapp.Discord','Heroic Games Launcher':'com.heroicgameslauncher.hgl','ProtonPlus':'com.vysp3r.ProtonPlus','Faugus Launcher':'io.github.Faugus.faugus-launcher','Google Chrome':'com.google.Chrome','Visual Studio Code':'com.visualstudio.code','OBS Studio Flatpak':'com.obsproject.Studio','Steam Flatpak':'com.valvesoftware.Steam'
}
DESKTOPS={'GNOME':'task-gnome-desktop','KDE Plasma':'task-kde-desktop','Xfce':'task-xfce-desktop','LXQt':'task-lxqt-desktop','LXDE':'task-lxde-desktop','MATE':'task-mate-desktop','Cinnamon':'task-cinnamon-desktop','GNOME Flashback':'task-gnome-flashback-desktop'}
KDE_CONFIG_PATHS=['.config/plasma-org.kde.plasma.desktop-appletsrc','.config/plasmarc','.config/plasmashellrc','.config/kdeglobals','.config/kwinrc','.config/kglobalshortcutsrc','.config/dolphinrc','.config/konsolerc','.local/share/plasma','.local/share/aurorae','.local/share/color-schemes','.local/share/icons','.local/share/wallpapers','.local/share/konsole','.themes','.icons','Imágenes','Pictures']

STYLE='''QMainWindow,QWidget{background:#0f172a;color:#e5e7eb;font-size:13px}QTabWidget::pane{border:1px solid #334155;border-radius:10px}QTabBar::tab{background:#1e293b;padding:10px 14px;border-top-left-radius:8px;border-top-right-radius:8px}QTabBar::tab:selected{background:#2563eb;color:white}QPushButton{background:#2563eb;color:white;border:0;padding:9px 12px;border-radius:8px}QPushButton:hover{background:#1d4ed8}QPushButton:disabled{background:#475569;color:#94a3b8}QGroupBox{border:1px solid #334155;border-radius:12px;margin-top:12px;padding:12px;font-weight:bold}QGroupBox::title{subcontrol-origin:margin;left:12px;padding:0 6px}QTextEdit,QLineEdit,QTableWidget,QComboBox{background:#020617;color:#e5e7eb;border:1px solid #334155;border-radius:8px;padding:6px}QProgressBar{border:1px solid #334155;border-radius:8px;text-align:center;height:22px}QProgressBar::chunk{background:#2563eb;border-radius:8px}QHeaderView::section{background:#1e293b;color:#e5e7eb;padding:6px;border:0}'''

def os_release():
    d={}
    try:
        for line in Path('/etc/os-release').read_text().splitlines():
            if '=' in line:
                k,v=line.split('=',1); d[k]=v.strip().strip('"')
    except Exception: pass
    return d

def is_debian(): return os_release().get('ID')=='debian'
def codename(): return os_release().get('VERSION_CODENAME') or os_release().get('DEBIAN_CODENAME') or ''
def current_user(): return os.environ.get('SUDO_USER') or os.environ.get('USER') or str(Path.home().name)

def shell_array(name, items):
    return name+'=('+ ' '.join(shlex.quote(x) for x in items) +')\n'

def mk_script(body, root=False):
    head='''#!/usr/bin/env bash
set -Eeuo pipefail
export DEBIAN_FRONTEND=noninteractive
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
'''
    if root:
        head += 'export PATH=/usr/sbin:/usr/bin:/sbin:/bin\n'
    fd,path=tempfile.mkstemp(prefix='debian-kde-forge-',suffix='.sh',text=True)
    os.close(fd)
    Path(path).write_text(head+'\n'+body+'\n')
    os.chmod(path,0o755)
    return path

class Forge(QMainWindow):
    def __init__(self):
        super().__init__(); self.proc=None; self.current_log=None; self.checks={}; self.flat_checks={}; self.de_checks={}
        self.setWindowTitle(f'{APP_NAME} {APP_VERSION}'); self.resize(1220,820)
        if ICON.exists(): self.setWindowIcon(QIcon(str(ICON)))
        self.setStyleSheet(STYLE); self.build_ui(); QTimer.singleShot(400,self.refresh_status)

    def build_ui(self):
        root=QWidget(); self.setCentralWidget(root); outer=QVBoxLayout(root)
        title=QLabel(f'<h1>{APP_NAME} {APP_VERSION}</h1><p>Instalador modular para Debian 13/Trixie: APT con root, Flatpak para tu usuario, progreso, verificación y log.</p>'); outer.addWidget(title)
        self.progress=QProgressBar(); self.progress.setValue(0); self.progress.setFormat('Listo'); outer.addWidget(self.progress)
        split=QSplitter(Qt.Orientation.Vertical); self.tabs=QTabWidget(); split.addWidget(self.tabs)
        self.terminal=QTextEdit(); self.terminal.setReadOnly(True); self.terminal.setFont(QFont('monospace',10)); split.addWidget(self.terminal); split.setSizes([560,240]); outer.addWidget(split)
        self.make_help(); self.make_install(); self.make_flatpak(); self.make_repos(); self.make_drivers(); self.make_kde(); self.make_opt(); self.make_status()

    def log(self,t):
        self.terminal.moveCursor(QTextCursor.MoveOperation.End); self.terminal.insertPlainText(t); self.terminal.moveCursor(QTextCursor.MoveOperation.End)
        if self.current_log:
            try: Path(self.current_log).parent.mkdir(parents=True,exist_ok=True); Path(self.current_log).open('a').write(t)
            except Exception: pass
        m=re.findall(r'(\d{1,3})%',t)
        if m:
            self.progress.setValue(min(100,int(m[-1]))); self.progress.setFormat(f'Progreso {self.progress.value()}%')

    def start(self, body, root=False, label='Proceso'):
        if self.proc and self.proc.state()!=QProcess.ProcessState.NotRunning:
            QMessageBox.warning(self,'Proceso en ejecución','Esperá a que termine el proceso actual.'); return
        LOGDIR.mkdir(parents=True,exist_ok=True); self.current_log=str(LOGDIR/(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.log'))
        path=mk_script(body,root=root); cmd=['bash',path]
        shown=' '.join(cmd)
        if root: cmd=['pkexec','bash',path]; shown=' '.join(cmd)
        self.progress.setValue(0); self.progress.setFormat(label)
        self.log(f'\n$ {shown}\n[Iniciando: {label}]\nLog: {self.current_log}\n\n')
        self.proc=QProcess(self); self.proc.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.proc.readyReadStandardOutput.connect(lambda: self.log(bytes(self.proc.readAllStandardOutput()).decode(errors='replace')))
        self.proc.finished.connect(lambda code,status: self.finish(code,path))
        self.proc.start(cmd[0],cmd[1:])

    def finish(self, code, path):
        try: Path(path).unlink(missing_ok=True)
        except Exception: pass
        self.progress.setValue(100 if code==0 else 0); self.progress.setFormat('Finalizado correctamente' if code==0 else f'Error código {code}')
        self.log(f'\n[Proceso finalizado con código {code}]\n')
        self.refresh_status()

    def make_help(self):
        tab=QWidget(); l=QVBoxLayout(tab); q=QTextEdit(); q.setReadOnly(True); q.setHtml('''<h2>Debian KDE Forge 2.0</h2><p><b>Cambio importante:</b> APT se ejecuta con pkexec/root, pero Flatpak se instala para tu usuario con <code>--user</code>, para que OBS, Steam, Discord y demás aparezcan en el menú de KDE.</p><ol><li>Repositorio: configurar Debian Stable/Trixie.</li><li>APT: instalar paquetes Debian seleccionados.</li><li>Flatpak: instalar Flathub y apps para tu usuario.</li><li>Estado: verificar si quedaron como APT, Flatpak user o Flatpak system.</li></ol><p>Los logs quedan en <code>~/.local/share/debian-kde-forge/logs/</code>.</p>'''); l.addWidget(q); self.tabs.addTab(tab,'Ayuda')

    def make_install(self):
        tab=QWidget(); l=QVBoxLayout(tab); scroll=QScrollArea(); scroll.setWidgetResizable(True); body=QWidget(); bl=QVBoxLayout(body)
        for cat,pkgs in CATEGORIES.items():
            box=QGroupBox(cat); vl=QVBoxLayout(box); row=QHBoxLayout(); sel=QPushButton('Seleccionar todo'); clr=QPushButton('Limpiar'); row.addWidget(sel); row.addWidget(clr); row.addStretch(); vl.addLayout(row); local=[]
            for p in pkgs:
                cb=QCheckBox(p); self.checks[p]=cb; local.append(cb); vl.addWidget(cb)
            sel.clicked.connect(lambda _,items=local:[c.setChecked(True) for c in items]); clr.clicked.connect(lambda _,items=local:[c.setChecked(False) for c in items]); bl.addWidget(box)
        bl.addStretch(); scroll.setWidget(body); l.addWidget(scroll); row=QHBoxLayout(); b=QPushButton('Instalar paquetes APT seleccionados'); b.clicked.connect(self.install_apt); row.addWidget(b); row.addStretch(); l.addLayout(row); self.tabs.addTab(tab,'APT')

    def install_apt(self):
        pkgs=[p for p,c in self.checks.items() if c.isChecked()]
        if not pkgs: QMessageBox.information(self,'Sin selección','No seleccionaste paquetes APT.'); return
        body=shell_array('PKGS',pkgs)+r'''
echo '[APT] Actualizando repositorios...'
apt-get update
INSTALL=()
SKIP=()
for pkg in "${PKGS[@]}"; do
  candidate="$(apt-cache policy "$pkg" 2>/dev/null | awk '/Candidate:/ {print $2; exit}')"
  if [ -n "$candidate" ] && [ "$candidate" != "(none)" ]; then
    INSTALL+=("$pkg")
  else
    SKIP+=("$pkg")
    echo "[omitido] $pkg sin candidato instalable en estos repositorios"
  fi
done
if [ ${#SKIP[@]} -gt 0 ]; then
  echo "[APT] Paquetes omitidos: ${SKIP[*]}"
fi
if [ ${#INSTALL[@]} -eq 0 ]; then echo 'No hay paquetes disponibles.'; exit 0; fi
echo "[APT] Instalando ${#INSTALL[@]} paquetes con candidato real..."
apt-get install -y --show-progress "${INSTALL[@]}"
echo '[APT] Verificando instalación...'
for pkg in "${INSTALL[@]}"; do dpkg-query -W -f='[OK] ${binary:Package} ${Version}\n' "$pkg" 2>/dev/null || echo "[AVISO] $pkg no quedó instalado con ese nombre (puede ser paquete virtual/metapaquete)"; done
'''
        self.start(body,root=True,label='Instalando paquetes APT')

    def make_flatpak(self):
        tab=QWidget(); l=QVBoxLayout(tab); info=QLabel('Flatpak se instala para el usuario actual, no como root. Así KDE Plasma muestra las apps en el menú.'); info.setWordWrap(True); l.addWidget(info)
        box=QGroupBox('Apps Flathub'); vl=QVBoxLayout(box)
        for name,appid in FLATPAKS.items():
            cb=QCheckBox(f'{name} ({appid})'); self.flat_checks[appid]=cb; vl.addWidget(cb)
        l.addWidget(box); row=QHBoxLayout(); b1=QPushButton('Instalar base Flatpak APT'); b1.clicked.connect(self.install_flatpak_base); b2=QPushButton('Instalar apps Flatpak para mi usuario'); b2.clicked.connect(self.install_flatpak_user); b3=QPushButton('Actualizar menú KDE'); b3.clicked.connect(self.refresh_kde_menu); row.addWidget(b1); row.addWidget(b2); row.addWidget(b3); row.addStretch(); l.addLayout(row); self.tabs.addTab(tab,'Flatpak')

    def install_flatpak_base(self):
        body=r'''apt-get update
apt-get install -y --show-progress flatpak plasma-discover-backend-flatpak xdg-desktop-portal xdg-desktop-portal-kde desktop-file-utils locales
'''
        self.start(body,root=True,label='Instalando base Flatpak')

    def install_flatpak_user(self):
        apps=[a for a,c in self.flat_checks.items() if c.isChecked()]
        if not apps: QMessageBox.information(self,'Sin selección','No seleccionaste aplicaciones Flatpak.'); return
        body=shell_array('APPS',apps)+r'''
export XDG_DATA_DIRS="$HOME/.local/share/flatpak/exports/share:/var/lib/flatpak/exports/share:${XDG_DATA_DIRS:-/usr/local/share:/usr/share}"
flatpak --user remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak --user repair || true
flatpak --user install -y --noninteractive flathub "${APPS[@]}"
echo '[Flatpak] Verificación user:'
for app in "${APPS[@]}"; do flatpak --user info "$app" >/dev/null 2>&1 && echo "[OK user] $app" || echo "[ERROR] $app no aparece en user"; done
update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
kbuildsycoca6 --noincremental 2>/dev/null || kbuildsycoca5 --noincremental 2>/dev/null || true
echo '[Flatpak] Si no aparece en el menú, probá abrir con: flatpak run ID_DE_APP o cerrá sesión y volvé a entrar.'
'''
        self.start(body,root=False,label='Instalando Flatpaks para usuario')

    def refresh_kde_menu(self):
        self.start("""update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
kbuildsycoca6 --noincremental 2>/dev/null || kbuildsycoca5 --noincremental 2>/dev/null || true
echo 'Menú KDE actualizado. Si no aparece, cerrá sesión y volvé a entrar.'
""",root=False,label='Actualizando menú KDE')

    def make_repos(self):
        tab=QWidget(); l=QVBoxLayout(tab); l.addWidget(QLabel('Repositorios Debian 13/Trixie oficiales con contrib, non-free y non-free-firmware. Crea backup automático.'))
        b=QPushButton('Configurar Debian 13/Trixie Stable + backports + firmware'); b.clicked.connect(self.set_sources); l.addWidget(b)
        s=QPushButton('Permitir sudo al usuario actual de forma segura'); s.clicked.connect(self.enable_sudo); l.addWidget(s); l.addStretch(); self.tabs.addTab(tab,'Repositorios/Sudo')

    def set_sources(self):
        body=r'''
STAMP=$(date +%F_%H%M%S)
cp -a /etc/apt/sources.list /etc/apt/sources.list.bak.$STAMP 2>/dev/null || true
mkdir -p /etc/apt/sources.list.d
for f in /etc/apt/sources.list.d/debian-kde-forge*.sources /etc/apt/sources.list.d/debian-kde-forge*.list; do [ -e "$f" ] && mv "$f" "$f.bak.$STAMP"; done
cat >/etc/apt/sources.list <<'EOF'
deb https://deb.debian.org/debian trixie main contrib non-free non-free-firmware
deb-src https://deb.debian.org/debian trixie main contrib non-free non-free-firmware

deb https://deb.debian.org/debian trixie-updates main contrib non-free non-free-firmware
deb-src https://deb.debian.org/debian trixie-updates main contrib non-free non-free-firmware

deb https://deb.debian.org/debian trixie-backports main contrib non-free non-free-firmware
deb-src https://deb.debian.org/debian trixie-backports main contrib non-free non-free-firmware

deb https://security.debian.org/debian-security trixie-security main contrib non-free non-free-firmware
deb-src https://security.debian.org/debian-security trixie-security main contrib non-free non-free-firmware
EOF
apt-get update
'''
        self.start(body,root=True,label='Configurando sources.list')

    def enable_sudo(self):
        user=current_user()
        body=f'''
apt-get update
apt-get install -y sudo
usermod -aG sudo {shlex.quote(user)}
echo '%sudo ALL=(ALL:ALL) ALL' >/etc/sudoers.d/90-debian-kde-forge-sudo
chmod 0440 /etc/sudoers.d/90-debian-kde-forge-sudo
visudo -cf /etc/sudoers.d/90-debian-kde-forge-sudo
echo 'Usuario {user} agregado al grupo sudo. Cerrá sesión y volvé a entrar para aplicar el grupo.'
'''
        self.start(body,root=True,label='Configurando sudo')

    def make_drivers(self):
        tab=QWidget(); l=QVBoxLayout(tab)
        for txt,body,root in [('Detectar GPU',"lspci -nn | grep -Ei 'vga|3d|display|nvidia|amd|intel' || true\n",False),('Instalar NVIDIA propietario',"apt-get update\napt-get install -y --show-progress nvidia-driver firmware-misc-nonfree nvidia-settings linux-headers-amd64 dkms\nupdate-initramfs -u || true\n",True),('Instalar firmware general',"apt-get update\napt-get install -y --show-progress firmware-linux firmware-linux-nonfree firmware-misc-nonfree firmware-realtek firmware-iwlwifi firmware-amd-graphics intel-microcode amd64-microcode\n",True),('Instalar Vulkan/Mesa',"apt-get update\napt-get install -y --show-progress mesa-vulkan-drivers vulkan-tools libvulkan1 mesa-utils\n",True)]:
            b=QPushButton(txt); b.clicked.connect(lambda _,bo=body,ro=root,la=txt:self.start(bo,ro,la)); l.addWidget(b)
        l.addStretch(); self.tabs.addTab(tab,'Drivers')

    def make_kde(self):
        tab=QWidget(); l=QVBoxLayout(tab); b1=QPushButton('Crear backup KDE completo'); b1.clicked.connect(self.kde_backup); b2=QPushButton('Restaurar backup KDE .tar.gz'); b2.clicked.connect(self.kde_restore); l.addWidget(b1); l.addWidget(b2); l.addStretch(); self.tabs.addTab(tab,'Backup KDE')

    def kde_backup(self):
        target,_=QFileDialog.getSaveFileName(self,'Guardar backup',str(Path.home()/f'backup-kde-{datetime.date.today()}.tar.gz'),'Tar GZ (*.tar.gz)')
        if not target: return
        with tarfile.open(target,'w:gz') as tar:
            for rel in KDE_CONFIG_PATHS:
                p=Path.home()/rel
                if p.exists(): tar.add(p,arcname=rel)
        self.log(f'Backup KDE creado: {target}\n')
    def kde_restore(self):
        source,_=QFileDialog.getOpenFileName(self,'Seleccionar backup',str(Path.home()),'Tar GZ (*.tar.gz)')
        if not source: return
        if QMessageBox.question(self,'Confirmar','Esto sobrescribe configuraciones KDE actuales. ¿Continuar?')!=QMessageBox.StandardButton.Yes: return
        with tarfile.open(source,'r:gz') as tar: tar.extractall(Path.home())
        self.log(f'Backup KDE restaurado: {source}\n')

    def make_opt(self):
        tab=QWidget(); l=QVBoxLayout(tab); b=QPushButton('Aplicar optimización gaming/productividad'); b.clicked.connect(self.optimize); l.addWidget(b); l.addStretch(); self.tabs.addTab(tab,'Optimización')
    def optimize(self):
        body=r'''apt-get update
PKGS=(gamemode mangohud goverlay vkbasalt vulkan-tools mesa-vulkan-drivers libvulkan1 steam-devices obs-studio ffmpeg kdenlive handbrake pipewire pipewire-audio wireplumber pavucontrol linux-headers-amd64 dkms cpufrequtils irqbalance earlyoom)
INSTALL=()
for pkg in "${PKGS[@]}"; do
  candidate="$(apt-cache policy "$pkg" 2>/dev/null | awk '/Candidate:/ {print $2; exit}')"
  if [ -n "$candidate" ] && [ "$candidate" != "(none)" ]; then INSTALL+=("$pkg"); else echo "[omitido] $pkg sin candidato instalable"; fi
done
[ ${#INSTALL[@]} -gt 0 ] && apt-get install -y --show-progress "${INSTALL[@]}" || true
systemctl enable --now irqbalance earlyoom || true
U=${SUDO_USER:-}
[ -n "$U" ] && usermod -aG video,audio,render,input,plugdev,sudo "$U" || true
cat >/etc/sysctl.d/99-debian-kde-forge-gaming.conf <<'EOF'
vm.swappiness=10
vm.vfs_cache_pressure=50
fs.inotify.max_user_watches=1048576
EOF
sysctl --system || true
'''
        self.start(body,root=True,label='Optimización gaming/productividad')

    def make_status(self):
        tab=QWidget(); l=QVBoxLayout(tab); self.table=QTableWidget(0,4); self.table.setHorizontalHeaderLabels(['Paquete/App','Tipo','Estado','Detalle']); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch); l.addWidget(self.table); b=QPushButton('Comprobar estado'); b.clicked.connect(self.refresh_status); l.addWidget(b); self.tabs.addTab(tab,'Estado')

    def refresh_status(self):
        if not hasattr(self,'table'): return
        items=[]
        for pkgs in CATEGORIES.values(): items += [(p,'APT') for p in pkgs]
        items += [(a,'Flatpak') for a in FLATPAKS.values()]
        self.table.setRowCount(0)
        for name,typ in items:
            state='No'; detail='-'
            try:
                if typ=='APT':
                    r=subprocess.run(['dpkg-query','-W','-f=${Version}',name],capture_output=True,text=True,timeout=2)
                    if r.returncode==0: state='Sí'; detail=r.stdout.strip()
                else:
                    ru=subprocess.run(['flatpak','--user','info',name],capture_output=True,text=True,timeout=2)
                    rs=subprocess.run(['flatpak','--system','info',name],capture_output=True,text=True,timeout=2)
                    if ru.returncode==0: state='Sí'; detail='Flatpak user'
                    elif rs.returncode==0: state='Sí'; detail='Flatpak system'
            except Exception as e: detail=str(e)
            row=self.table.rowCount(); self.table.insertRow(row)
            for c,v in enumerate([name,typ,state,detail]): self.table.setItem(row,c,QTableWidgetItem(v))

if __name__=='__main__':
    app=QApplication(sys.argv)
    if not is_debian(): QMessageBox.critical(None,'Debian requerido','Diseñado para Debian Stable/Testing.'); sys.exit(1)
    w=Forge(); w.show(); sys.exit(app.exec())
