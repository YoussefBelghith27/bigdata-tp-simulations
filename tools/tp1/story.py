"""Scénario de la simulation TP1 : liste ordonnée de diapositives (écran html + interaction)."""
import json
from screens import *

S = json.load(open("/home/claude/tp1/run/session.json"))
OUT = {}
for x in S:
    OUT.setdefault(x["cmd"], []).append(x["out"])

V, VSH = "7.0.34", "2.14.2"
SRV = f"MongoDB {V} 2008R2Plus SSL (64 bit)"
SRV_T = SRV + " Setup"
MSI_SRV = f"mongodb-windows-x86_64-{V}-signed.msi"
MSI_SH = f"mongosh-{VSH}-x64.msi"
SH_T = "MongoDB Shell Setup"
BIN = r"C:\Program Files\MongoDB\Server\7.0\bin"
SHDIR = r"C:\Users\ASUS\AppData\Local\Programs\mongosh"
WP = "C:\\Users\\ASUS>"
AP = "C:\\WINDOWS\\system32>"

slides = []

def dur(text, base=3200):
    return max(5200, min(11000, base + 55 * len(text)))

def show(html, step, text, d=None, cap=None):
    slides.append(dict(html=html, step=step, text=text, kind="show", dur=d or dur(text), cap=cap))

def click(html, step, text, hint, cap=None):
    slides.append(dict(html=html, step=step, text=text, kind="click", hint=hint, cap=cap))

def tbox(html, step, text, answers, cap=None):
    slides.append(dict(html=html, step=step, text=text, kind="type", box=True, answers=answers, cap=cap))

def tcon(con, prompt, step, text, answers, out=None, mongo=False, cap=None):
    slides.append(dict(html=con.html(prompt), step=step, text=text, kind="type", x=prompt_x(prompt), answers=answers, cap=cap))
    con.add_cmd(prompt, answers[0])
    if out is not None:
        con.add_out(out, mongo=mongo)

def mout(cmd):
    return OUT[cmd].pop(0)

# ====================================================================== Introduction
show(title_card("TP 1 · Installation de MongoDB 7.0 et mongosh", "Windows 11 : installation, variable Path, service, port 27017 et première base etudiant",
                ["Installer MongoDB Community Server 7.0 (msi)", "Installer le shell mongosh 2.x", "Ajouter les dossiers bin au Path",
                 "Vérifier versions, service et port 27017 depuis cmd", "Créer la base etudiant et découvrir les commandes CRUD"]),
     "Introduction", "TP1 – Installation de MongoDB 7.0 et de mongosh sous Windows 11. Écrans Windows reconstitués : résultats attendus.", 9000)

# ====================================================================== Partie 1
P1 = "Partie 1 · Serveur MongoDB 7.0"
pg = mdb_page("server", "8.2.2", "Windows x64", "msi")
tbox(desktop(browser("", "Nouvel onglet", '<div style="height:100%;background:#f7f9fb"></div>', focus=True, typed="", tgt_url=True), ("browser",)),
     P1, "Étape 1 : ouvrez la page de téléchargement de MongoDB Community Server.",
     ["mongodb.com/try/download/community", "https://www.mongodb.com/try/download/community", "www.mongodb.com/try/download/community", "https://mongodb.com/try/download/community"])
click(desktop(browser("mongodb.com/try/download/community", "Download MongoDB Community Server", mdb_page("server", "8.2.2", "Windows x64", "msi", t="version")), ("browser",)),
      P1, "Étape 2 : la page propose la 8.x par défaut. Ouvrez la liste Version pour choisir la 7.0.", "Cliquez sur la liste Version")
items = ["8.2.2 (current)", "8.0.16", f"{V}", "6.0.26"]
click(desktop(browser("mongodb.com/try/download/community", "Download MongoDB Community Server", mdb_page("server", "8.2.2", "Windows x64", "msi", open_menu=2, t=2, items=items)), ("browser",)),
      P1, f"Choisissez la dernière 7.0 : {V}. Ne prenez pas la 8.x.", f"Cliquez sur {V}")
click(desktop(browser("mongodb.com/try/download/community", "Download MongoDB Community Server", mdb_page("server", V, "Windows x64", "msi", t="download")), ("browser",)),
      P1, "Version 7.0, Platform Windows x64, Package msi : lancez le téléchargement.", "Cliquez sur Download")
show(desktop(browser("mongodb.com/try/download/community", "Download MongoDB Community Server", mdb_page("server", V, "Windows x64", "msi"),
                     extra=dl_flyout(MSI_SRV, "629 Mo")), ("browser",)),
     P1, f"Le fichier {MSI_SRV} est enregistré dans Téléchargements.")
dl_rows = [(MSI_SRV, "14/11/2026 12:47", "Package Windows Installer", "644 112 Ko", "msi")]
click(desktop(explorer(["Ce PC", "Téléchargements"], dl_rows, t=0, nav_on="Téléchargements"), ("explorer",)),
      P1, "Étape 3 : dans Téléchargements, double-cliquez sur le fichier .msi pour lancer l'installateur.", "Double-cliquez sur le fichier .msi")
p = msi_side(f"Welcome to the {SRV} Setup Wizard", f"The Setup Wizard will install {E(SRV)} on your computer. Click Next to continue or Cancel to exit the Setup Wizard.")
click(desktop(msi(SRV_T, p, [("Back", "dis"), ("Next", "def"), ("|", ""), ("Cancel", "")], t="Next")),
      P1, "L'assistant d'installation s'ouvre. Cliquez sur Next.", "Cliquez sur Next")
lic = '<div style="background:#fff;border:1px solid #7a7a7a;height:170px;padding:8px;line-height:1.5;overflow:hidden"><b>Server Side Public License</b><br>VERSION 1, OCTOBER 16, 2018<br><br>Copyright © 2018 MongoDB, Inc.<br><br>Everyone is permitted to copy and distribute verbatim copies of this license document, but changing it is not allowed.<br><br>TERMS AND CONDITIONS …</div>'
def licpage(on, t):
    return msi_banner("End-User License Agreement", "Please read the following license agreement carefully",
        lic + f'<div style="margin-top:10px"><span class="chk{" on" if on else ""}"{" data-t" if t == "chk" else ""}></span>I accept the terms in the License Agreement</div>')
click(desktop(msi(SRV_T, licpage(False, "chk"), [("Print", ""), ("Back", ""), ("Next", "dis"), ("|", ""), ("Cancel", "")])),
      P1, "Étape 4 : licence SSPL. Cochez la case d'acceptation.", "Cochez I accept the terms…")
click(desktop(msi(SRV_T, licpage(True, None), [("Print", ""), ("Back", ""), ("Next", "def"), ("|", ""), ("Cancel", "")], t="Next")),
      P1, "Licence acceptée : le bouton Next est actif.", "Cliquez sur Next")
setup = msi_banner("Choose Setup Type", "Choose the setup type that best suits your needs",
    '<div style="display:flex;gap:12px;margin:6px 0 16px"><span class="b" style="width:90px;height:26px" data-t>Complete</span><div style="line-height:1.45">All program features will be installed. Requires the most disk space. Recommended for most users.</div></div>'
    '<div style="display:flex;gap:12px"><span class="b" style="width:90px;height:26px">Custom</span><div style="line-height:1.45">Allows users to choose which program features will be installed and where they will be installed. Recommended for advanced users.</div></div>')
click(desktop(msi(SRV_T, setup, [("Back", ""), ("Next", "dis"), ("|", ""), ("Cancel", "")])),
      P1, "Étape 5 : type d'installation Complete (tous les composants, dossier par défaut).", "Cliquez sur Complete")
svc = msi_banner("Service Configuration", "Specify optional settings to configure MongoDB as a service.",
    '<div><span class="chk on"></span>Install MongoD as a Service</div>'
    '<div style="margin:7px 0 0 18px"><span class="rad on"></span>Run service as Network Service user</div>'
    '<div style="margin:5px 0 0 18px"><span class="rad"></span>Run service as a local or domain user:</div>'
    '<div style="margin:4px 0 0 40px;line-height:2;color:#888">Account Domain: <span class="fld dis" style="width:220px">.</span><br>Account Name: &nbsp;&nbsp;<span class="fld dis" style="width:220px">MongoDB</span><br>Account Password: <span class="fld dis" style="width:205px"></span></div>'
    '<div style="margin-top:6px;line-height:2.05">Service Name: &nbsp;&nbsp;<span class="fld" style="width:300px">MongoDB</span><br>'
    f'Data Directory: &nbsp;<span class="fld" style="width:300px;background:#fff8c4">{E(BIN[:-3])}data\\</span><br>'
    f'Log Directory: &nbsp;&nbsp;<span class="fld" style="width:300px;background:#fff8c4">{E(BIN[:-3])}log\\</span></div>')
show(desktop(msi(SRV_T, svc, [("Back", ""), ("Next", "def"), ("|", ""), ("Cancel", "")])),
     P1, "Étape 6 : MongoDB installé comme service Windows (compte Network Service, nom MongoDB). Notez les dossiers data et log.", 9500, cap="service")
click(desktop(msi(SRV_T, svc, [("Back", ""), ("Next", "def"), ("|", ""), ("Cancel", "")], t="Next")),
      P1, "On garde ces réglages par défaut.", "Cliquez sur Next")
def compass(on, t):
    return msi_banner("Install MongoDB Compass", "Optionally install MongoDB Compass",
        f'<div style="margin:8px 0 12px"><span class="chk{" on" if on else ""}"{" data-t" if t == "chk" else ""}></span>Install MongoDB Compass</div>'
        '<div style="line-height:1.5;color:#333">MongoDB Compass is the official graphical user interface for MongoDB.<br><br>By checking below this script will be executed after the installation and will download and install the latest version of Compass.</div>')
click(desktop(msi(SRV_T, compass(True, "chk"), [("Back", ""), ("Next", "def"), ("|", ""), ("Cancel", "")])),
      P1, "Étape 7 : Compass (interface graphique) est inutile pour ce TP. Décochez-le.", "Décochez Install MongoDB Compass")
click(desktop(msi(SRV_T, compass(False, None), [("Back", ""), ("Next", "def"), ("|", ""), ("Cancel", "")], t="Next")),
      P1, "Compass décoché.", "Cliquez sur Next")
ready = msi_banner(f"Ready to install {SRV}", "", '<div style="line-height:1.5;margin-top:4px">Click Install to begin the installation. Click Back to review or change any of your installation settings. Click Cancel to exit the wizard.</div>')
click(desktop(msi(SRV_T, ready, [("Back", ""), ("🛡 Install", "def"), ("|", ""), ("Cancel", "")], t="🛡 Install")),
      P1, "Tout est prêt : lancez l'installation.", "Cliquez sur Install")
click(desktop(msi(SRV_T, ready, [("Back", ""), ("🛡 Install", "def"), ("|", ""), ("Cancel", "")]) + uac("Windows Installer", "MongoDB, Inc.", t="Oui")),
      P1, "Windows demande l'élévation des droits (UAC) : l'installation d'un service exige un compte administrateur.", "Cliquez sur Oui")
prog = msi_banner(f"Installing {SRV}", f"Please wait while the Setup Wizard installs {SRV}.",
    '<div style="margin-top:10px">Status: &nbsp;Copying new files</div><div style="margin-top:10px;height:18px;border:1px solid #bcbcbc;background:#e6e6e6"><div style="width:62%;height:100%;background:#06b025"></div></div>')
show(desktop(msi(SRV_T, prog, [("Back", "dis"), ("Next", "dis"), ("|", ""), ("Cancel", "")])),
     P1, "Copie des fichiers dans C:\\Program Files\\MongoDB\\Server\\7.0 et création du service MongoDB.", 6000)
fin = msi_side(f"Completed the {SRV} Setup Wizard", "Click the Finish button to exit the Setup Wizard.")
click(desktop(msi(SRV_T, fin, [("Back", "dis"), ("Finish", "def"), ("|", ""), ("Cancel", "dis")], t="Finish")),
      P1, "Installation du serveur terminée.", "Cliquez sur Finish")

# ====================================================================== Partie 2
P2 = "Partie 2 · mongosh"
tbox(desktop(browser("", "Nouvel onglet", '<div style="height:100%;background:#f7f9fb"></div>', focus=True, typed="", tgt_url=True), ("browser",)),
     P2, "Étape 8 : depuis la 6.0, le shell mongo n'existe plus. Ouvrez la page de téléchargement de mongosh.",
     ["mongodb.com/try/download/shell", "https://www.mongodb.com/try/download/shell", "www.mongodb.com/try/download/shell", "https://mongodb.com/try/download/shell"])
click(desktop(browser("mongodb.com/try/download/shell", "MongoDB Shell Download", mdb_page("shell", VSH, "Windows x64 (10+)", "msi", t="download")), ("browser",)),
      P2, f"Étape 9 : version {VSH}, Windows 64-bit (10+), msi. mongosh 2.x est compatible avec MongoDB 7.0.", "Cliquez sur Download")
sh_rows = [(MSI_SH, "14/11/2026 12:55", "Package Windows Installer", "113 820 Ko", "msi")] + dl_rows
click(desktop(explorer(["Ce PC", "Téléchargements"], sh_rows, t=0, nav_on="Téléchargements"), ("explorer",)),
      P2, f"Étape 10 : lancez {MSI_SH}.", "Double-cliquez sur le fichier mongosh")
p = msi_side(f"Welcome to the MongoDB Shell '{VSH}' Setup Wizard", "The Setup Wizard will install MongoDB Shell on your computer. Click Next to continue or Cancel to exit the Setup Wizard.")
click(desktop(msi(SH_T, p, [("Back", "dis"), ("Next", "def"), ("|", ""), ("Cancel", "")], t="Next")), P2, "Assistant d'installation de mongosh.", "Cliquez sur Next")
dest = msi_banner("Destination Folder", "Click Next to install to the default folder or click Change to choose another.",
    f'<div style="margin-top:6px">Install MongoDB Shell to:</div><div style="margin:6px 0 0 0;font-weight:600;background:#fff8c4;display:inline-block;padding:2px 4px">{E(SHDIR)}\\</div><div style="margin-top:6px;color:#0066cc">Change...</div>'
    '<div style="margin-top:18px"><span class="chk"></span>Install just for you (ASUS)</div>')
click(desktop(msi(SH_T, dest, [("Back", ""), ("Next", "def"), ("|", ""), ("Cancel", "")], t="Next")),
      P2, "mongosh s'installe dans le profil de l'utilisateur (AppData\\Local\\Programs). Notez ce dossier.", "Cliquez sur Next")
ready2 = msi_banner("Ready to install MongoDB Shell", "", '<div style="line-height:1.5;margin-top:4px">Click Install to begin the installation. Click Back to review or change any of your installation settings.</div>')
click(desktop(msi(SH_T, ready2, [("Back", ""), ("Install", "def"), ("|", ""), ("Cancel", "")], t="Install")), P2, "Lancez l'installation.", "Cliquez sur Install")
fin2 = msi_side("Completed the MongoDB Shell Setup Wizard", "Click the Finish button to exit the Setup Wizard.")
click(desktop(msi(SH_T, fin2, [("Back", "dis"), ("Finish", "def"), ("|", ""), ("Cancel", "dis")], t="Finish")), P2, "mongosh est installé.", "Cliquez sur Finish")

# ====================================================================== Partie 3
P3 = "Partie 3 · Chemins"
bin_rows = [("InstallCompass.ps1", "28/10/2026 09:12", "Script Windows PowerShell", "2 Ko", "txt"),
            ("mongod.cfg", "14/11/2026 12:49", "Fichier CFG", "1 Ko", "txt"),
            ("mongod.exe", "28/10/2026 09:12", "Application", "63 211 Ko", "exe"),
            ("mongod.pdb", "28/10/2026 09:12", "Fichier PDB", "811 632 Ko", "dll"),
            ("mongos.exe", "28/10/2026 09:12", "Application", "39 846 Ko", "exe"),
            ("mongos.pdb", "28/10/2026 09:12", "Fichier PDB", "502 908 Ko", "dll")]
bp = ["Ce PC", "Disque local (C:)", "Program Files", "MongoDB", "Server", "7.0", "bin"]
click(desktop(explorer(bp, bin_rows, sel_row=2, t="path"), ("explorer",)),
      P3, "Étape 11 : mongod.exe se trouve dans C:\\Program Files\\MongoDB\\Server\\7.0\\bin. Cliquez dans la barre d'adresse pour copier le chemin.", "Cliquez dans la barre d'adresse", cap="bin")
show(desktop(explorer(bp, bin_rows, sel_row=2, path_sel=True), ("explorer",)),
     P3, "Le chemin complet est sélectionné : Ctrl + C pour le copier.")
sh_files = [("LICENSE-crypt-library", "06/11/2026 15:20", "Fichier", "8 Ko", "txt"), ("LICENSE-mongosh", "06/11/2026 15:20", "Fichier", "12 Ko", "txt"),
            ("mongosh.exe", "06/11/2026 15:20", "Application", "121 304 Ko", "exe"), ("mongosh_crypt_v1.dll", "06/11/2026 15:20", "Extension de l'application", "47 112 Ko", "dll"),
            ("README", "06/11/2026 15:20", "Fichier", "4 Ko", "txt"), ("THIRD_PARTY_NOTICES", "06/11/2026 15:20", "Fichier", "206 Ko", "txt")]
show(desktop(explorer(["Ce PC", "Disque local (C:)", "Utilisateurs", "ASUS", "AppData", "Local", "Programs", "mongosh"], sh_files, sel_row=2), ("explorer",)),
     P3, "Étape 12 : mongosh.exe est dans AppData\\Local\\Programs\\mongosh (dossier masqué : Afficher > Éléments masqués).", 8500)
tbox(desktop(run_dialog("", t="field")), P3, "Étape 13 : ouvrez une invite de commandes avec Win + R.", ["cmd", "cmd.exe"])
c1 = Console("Invite de commandes", WP)
c1.add_out("Microsoft Windows [version 10.0.26100.4652]\n(c) Microsoft Corporation. Tous droits réservés.\n")
NF = "INFORMATION : impossible de trouver des fichiers pour le(s) modèle(s) spécifié(s)."
tcon(c1, WP, P3, "Cherchez où se trouve mongod.", ["where mongod"], NF + "\n")
tcon(c1, WP, P3, "Windows ne trouve pas mongod : son dossier n'est pas dans le Path. Testez aussi mongosh.", ["where mongosh"], NF + "\n")
show(c1.html(WP, cursor=True), P3, "Les deux commandes échouent : il faut ajouter les dossiers bin au Path (partie 4).")

# ====================================================================== Partie 4
P4 = "Partie 4 · Variable Path"
tbox(desktop(run_dialog("", t="field")), P4, "Étape 14 : ouvrez les propriétés système avec Win + R.", ["sysdm.cpl"])
click(desktop(sysprops("Nom de l'ordinateur", t="Paramètres système avancés")), P4, "Étape 15 : passez à l'onglet des paramètres avancés.", "Cliquez sur Paramètres système avancés")
click(desktop(sysprops("Paramètres système avancés", t="env")), P4, "Ouvrez la fenêtre des variables d'environnement.", "Cliquez sur Variables d'environnement…")
click(desktop(envvars(t="Path")), P4, "Étape 16 : dans Variables système (en bas), sélectionnez la ligne Path.", "Cliquez sur la ligne Path")
click(desktop(envvars(sel_path=True, t="Modifier")), P4, "Path sélectionné : ouvrez l'éditeur.", "Cliquez sur Modifier…")
base = ["%SystemRoot%\\system32", "%SystemRoot%", "%SystemRoot%\\System32\\Wbem", "%SYSTEMROOT%\\System32\\WindowsPowerShell\\v1.0\\",
        "%SYSTEMROOT%\\System32\\OpenSSH\\", "C:\\Program Files\\Git\\cmd", "C:\\Program Files\\nodejs\\"]
click(desktop(editpath(base, t="Nouveau")), P4, "Étape 17 : on ajoute une ligne, sans toucher aux lignes existantes.", "Cliquez sur Nouveau")
tbox(desktop(editpath(base + [""], editing=len(base), t="field")), P4, "Collez (ou tapez) le dossier bin du serveur.", [BIN, BIN + "\\"])
e1 = base + [BIN]
click(desktop(editpath(e1, sel=len(e1) - 1, t="Nouveau")), P4, "Étape 18 : where mongosh n'avait rien trouvé, ajoutez aussi son dossier.", "Cliquez sur Nouveau")
tbox(desktop(editpath(e1 + [""], editing=len(e1), t="field")), P4, "Tapez le dossier de mongosh relevé à l'étape 12.", [SHDIR, SHDIR + "\\"])
e2 = e1 + [SHDIR]
click(desktop(editpath(e2, sel=len(e2) - 1, t="OK")), P4, "Étape 19 : les deux lignes sont ajoutées en bas du Path. Validez.", "Cliquez sur OK", cap="path")
click(desktop(envvars(sel_path=True, t="OK")), P4, "Validez aussi la fenêtre Variables d'environnement (puis OK dans Propriétés système).", "Cliquez sur OK")
show(desktop("", ()), P4, "Étape 20 : fermez les anciens cmd. Le nouveau Path ne s'applique qu'aux fenêtres ouvertes après la modification.", 7500)

# ====================================================================== Partie 5
P5 = "Partie 5 · Versions"
tbox(desktop(run_dialog("", t="field")), P5, "Étape 21 : ouvrez un nouveau cmd.", ["cmd", "cmd.exe"])
c2 = Console("Invite de commandes", WP)
c2.add_out("Microsoft Windows [version 10.0.26100.4652]\n(c) Microsoft Corporation. Tous droits réservés.\n")
tcon(c2, WP, P5, "Étape 22 : vérifiez que cmd trouve maintenant mongod.", ["where mongod"], BIN + "\\mongod.exe\n")
tcon(c2, WP, P5, "mongod.exe est trouvé grâce au Path. Vérifiez mongosh.", ["where mongosh"], SHDIR + "\\mongosh.exe\n", cap="where")
mv = f'''db version v{V}
Build Info: {{
    "version": "{V}",
    "modules": [],
    "allocator": "tcmalloc",
    "environment": {{
        "distmod": "windows",
        "distarch": "x86_64",
        "target_arch": "x86_64"
    }}
}}
'''
tcon(c2, WP, P5, "Étape 23 : affichez la version du serveur.", ["mongod --version"], mv)
tcon(c2, WP, P5, f"Serveur en version {V}. Affichez la version du shell.", ["mongosh --version"], VSH + "\n", cap="version")
PATHV = r"C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0\;C:\WINDOWS\System32\OpenSSH\;C:\Program Files\Git\cmd;C:\Program Files\nodejs\;" + BIN + ";" + SHDIR + r";C:\Users\ASUS\AppData\Local\Microsoft\WindowsApps;"
tcon(c2, WP, P5, f"mongosh {VSH}. Étape 24 (optionnelle) : affichez le Path.", ["echo %PATH%", "echo %path%"], PATHV + "\n")

# ====================================================================== Partie 6
P6 = "Partie 6 · Service et port"
SCQ = """
NOM_SERVICE: MongoDB
        TYPE                   : 10  WIN32_OWN_PROCESS
        ÉTAT                   : 4  RUNNING
                                (STOPPABLE, NOT_PAUSABLE, ACCEPTS_SHUTDOWN)
        CODE_SORTIE_WIN32      : 0  (0x0)
        CODE_SORTIE_SERVICE    : 0  (0x0)
        POINT_DE_CONTRÔLE      : 0x0
        INDICATION_ATTENTE     : 0x0
"""
tcon(c2, WP, P6, "Les deux dossiers apparaissent dans le Path. Étape 25 : interrogez l'état du service MongoDB.", ["sc query MongoDB", "sc query mongodb"], SCQ, cap="sc")
c3 = Console("Administrateur : Invite de commandes", AP)
c3.add_out("Microsoft Windows [version 10.0.26100.4652]\n(c) Microsoft Corporation. Tous droits réservés.\n")
tcon(c3, AP, P6, "ÉTAT 4 RUNNING. Étape 26 : dans un cmd lancé en administrateur, arrêtez le service.", ["net stop MongoDB", "net stop mongodb"],
     "Le service MongoDB Server (MongoDB) s'arrête.\nLe service MongoDB Server (MongoDB) a été arrêté.\n")
tcon(c3, AP, P6, "Service arrêté : mongosh ne pourrait plus se connecter (ECONNREFUSED). Redémarrez-le.", ["net start MongoDB", "net start mongodb"],
     "Le service MongoDB Server (MongoDB) démarre..\nLe service MongoDB Server (MongoDB) a démarré.\n")
tcon(c3, AP, P6, "Étape 27 : observez le port d'écoute du serveur.", ["netstat -an | findstr 27017", "netstat -an |findstr 27017", "netstat -an|findstr 27017"],
     "  TCP    127.0.0.1:27017        0.0.0.0:0              LISTENING\n", cap="netstat")
show(c3.html(AP), P6, "MongoDB écoute sur 127.0.0.1:27017 : accès local uniquement, aucune machine du réseau ne peut s'y connecter (sécurisé par défaut).", 9000)

# ====================================================================== Partie 7
P7 = "Partie 7 · Base etudiant"
LOGID = "6af84905c5b8bcb0ee3391bb"
BANNER = f"""Current Mongosh Log ID: {LOGID}
Connecting to:          mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+{VSH}
Using MongoDB:          {V}
Using Mongosh:          {VSH}

For mongosh info see: https://www.mongodb.com/docs/mongodb-shell/


To help improve our products, pseudo-anonymous usage data is collected from interactive and agentic sessions only, and sent to MongoDB periodically (https://www.mongodb.com/legal/privacy-policy).
You can opt-out by running the disableTelemetry() command.

------
   The server generated these startup warnings when booting
   2026-11-14T12:49:13.204+01:00: Access control is not enabled for the database. Read and write access to data and configuration is unrestricted
------
"""
c4 = Console("Invite de commandes", WP)
c4.add_out("Microsoft Windows [version 10.0.26100.4652]\n(c) Microsoft Corporation. Tous droits réservés.\n")
tcon(c4, WP, P7, "Étape 28 : connectez-vous au serveur local avec le shell.", ["mongosh", 'mongosh "mongodb://127.0.0.1:27017"', "mongosh mongodb://127.0.0.1:27017"], BANNER)
T, ET = "test> ", "etudiant> "
def m(prompt, step, text, cmd, answers=None, cap=None):
    tcon(c4, prompt, step, text, answers or [cmd], mout(cmd) + "\n", mongo=True, cap=cap)
m(T, P7, "Connecté à 127.0.0.1:27017, invite test> (base par défaut). Étape 29 : version du serveur.", "db.version()")
m(T, P7, "Affichez la base courante.", "db")
m(T, P7, "Listez les bases existantes.", "show dbs")
m(T, P7, "Seules admin, config et local existent. Étape 30 : sélectionnez la base etudiant.", "use etudiant")
cmd1 = 'db.etudiants.insertOne({ nom: "Ben Ali", prenom: "Sami", age: 21, filiere: "Reseaux", niveau: "L3" })'
m(ET, P7, "La base n'existera qu'à la première insertion. Étape 31 : insérez un premier document.", cmd1,
  [cmd1, 'db.etudiants.insertOne({nom: "Ben Ali", prenom: "Sami", age: 21, filiere: "Reseaux", niveau: "L3"})',
   'db.etudiants.insertOne({nom:"Ben Ali",prenom:"Sami",age:21,filiere:"Reseaux",niveau:"L3"})'])
cmd2 = S[5]["cmd"]
show(c4.html(ET), P7, "acknowledged: true et un insertedId : la collection etudiants a été créée automatiquement avec un _id unique.", 8000)
c4.add_cmd(ET, cmd2); c4.add_out(mout(cmd2) + "\n", mongo=True)
show(c4.html(ET), P7, "Étape 32 : insertMany() ajoute 4 étudiants d'un coup (commande longue tapée ici pour vous). insertedIds liste les 4 identifiants.", 9500, cap="insert")

# ====================================================================== Partie 8
P8 = "Partie 8 · Découverte"
m(ET, P8, "8.1 : la base etudiant contient maintenant des données. Relistez les bases.", "show dbs")
m(ET, P8, "etudiant apparaît enfin. Affichez les collections.", "show collections")
m(ET, P8, "Comptez les documents.", "db.etudiants.countDocuments()")
m(ET, P8, "5 documents. 8.2 : lisez tous les documents.", "db.etudiants.find()", cap="find")
m(ET, P8, "find() renvoie un tableau de documents JSON. Cherchez un étudiant précis.", 'db.etudiants.findOne({ nom: "Gharbi" })',
  ['db.etudiants.findOne({ nom: "Gharbi" })', 'db.etudiants.findOne({nom: "Gharbi"})', 'db.etudiants.findOne({nom:"Gharbi"})'])
m(ET, P8, "8.3 : filtrez sur la filière Reseaux.", 'db.etudiants.find({ filiere: "Reseaux" })',
  ['db.etudiants.find({ filiere: "Reseaux" })', 'db.etudiants.find({filiere: "Reseaux"})', 'db.etudiants.find({filiere:"Reseaux"})'])
m(ET, P8, "3 étudiants en Reseaux. Âge strictement supérieur à 21 ($gt).", "db.etudiants.find({ age: { $gt: 21 } })",
  ["db.etudiants.find({ age: { $gt: 21 } })", "db.etudiants.find({age: {$gt: 21}})", "db.etudiants.find({age:{$gt:21}})"])
m(ET, P8, "Gharbi (22) et Jlassi (23). Moyenne entre 12 et 15 ($gte / $lte).", "db.etudiants.find({ moyenne: { $gte: 12, $lte: 15 } })",
  ["db.etudiants.find({ moyenne: { $gte: 12, $lte: 15 } })", "db.etudiants.find({moyenne: {$gte: 12, $lte: 15}})", "db.etudiants.find({moyenne:{$gte:12,$lte:15}})"])
m(ET, P8, "OU logique : niveau L2 ou âge 23.", 'db.etudiants.find({ $or: [ { niveau: "L2" }, { age: 23 } ] })',
  ['db.etudiants.find({ $or: [ { niveau: "L2" }, { age: 23 } ] })', 'db.etudiants.find({$or: [{niveau: "L2"}, {age: 23}]})', 'db.etudiants.find({$or:[{niveau:"L2"},{age:23}]})'])
m(ET, P8, "8.4 : projection, n'affichez que nom et prénom (sans _id).", "db.etudiants.find({}, { nom: 1, prenom: 1, _id: 0 })",
  ["db.etudiants.find({}, { nom: 1, prenom: 1, _id: 0 })", "db.etudiants.find({}, {nom: 1, prenom: 1, _id: 0})", "db.etudiants.find({},{nom:1,prenom:1,_id:0})"])
m(ET, P8, "Triez par moyenne décroissante (projection nom + moyenne pour la lisibilité).", "db.etudiants.find({}, { nom: 1, moyenne: 1, _id: 0 }).sort({ moyenne: -1 })",
  ["db.etudiants.find({}, { nom: 1, moyenne: 1, _id: 0 }).sort({ moyenne: -1 })", "db.etudiants.find({}, {nom: 1, moyenne: 1, _id: 0}).sort({moyenne: -1})",
   "db.etudiants.find({},{nom:1,moyenne:1,_id:0}).sort({moyenne:-1})"])
m(ET, P8, "Ben Ali, sans moyenne, finit en dernier. 8.5 : donnez-lui une moyenne ($set).", 'db.etudiants.updateOne({ nom: "Ben Ali" }, { $set: { moyenne: 13.5 } })',
  ['db.etudiants.updateOne({ nom: "Ben Ali" }, { $set: { moyenne: 13.5 } })', 'db.etudiants.updateOne({nom: "Ben Ali"}, {$set: {moyenne: 13.5}})', 'db.etudiants.updateOne({nom:"Ben Ali"},{$set:{moyenne:13.5}})'])
m(ET, P8, "matchedCount 1, modifiedCount 1. Ajoutez le campus à toute la filière Reseaux.", 'db.etudiants.updateMany({ filiere: "Reseaux" }, { $set: { campus: "Tunis" } })',
  ['db.etudiants.updateMany({ filiere: "Reseaux" }, { $set: { campus: "Tunis" } })', 'db.etudiants.updateMany({filiere: "Reseaux"}, {$set: {campus: "Tunis"}})', 'db.etudiants.updateMany({filiere:"Reseaux"},{$set:{campus:"Tunis"}})'])
m(ET, P8, "3 documents modifiés. Incrémentez l'âge de Jlassi ($inc).", 'db.etudiants.updateOne({ nom: "Jlassi" }, { $inc: { age: 1 } })',
  ['db.etudiants.updateOne({ nom: "Jlassi" }, { $inc: { age: 1 } })', 'db.etudiants.updateOne({nom: "Jlassi"}, {$inc: {age: 1}})', 'db.etudiants.updateOne({nom:"Jlassi"},{$inc:{age:1}})'])
m(ET, P8, "Vérifiez les modifications (sans _id).", "db.etudiants.find({}, { _id: 0 })",
  ["db.etudiants.find({}, { _id: 0 })", "db.etudiants.find({}, {_id: 0})", "db.etudiants.find({},{_id:0})"])
m(ET, P8, "moyenne 13.5 pour Ben Ali, campus Tunis, Jlassi passe à 24 ans. 8.6 : supprimez Jlassi.", 'db.etudiants.deleteOne({ nom: "Jlassi" })',
  ['db.etudiants.deleteOne({ nom: "Jlassi" })', 'db.etudiants.deleteOne({nom: "Jlassi"})', 'db.etudiants.deleteOne({nom:"Jlassi"})'])
m(ET, P8, "deletedCount 1. Supprimez tous les étudiants de niveau L2.", 'db.etudiants.deleteMany({ niveau: "L2" })',
  ['db.etudiants.deleteMany({ niveau: "L2" })', 'db.etudiants.deleteMany({niveau: "L2"})', 'db.etudiants.deleteMany({niveau:"L2"})'])

# ====================================================================== Exercices
PX = "Exercices"
cmdx = S[28]["cmd"]
c4.add_cmd(ET, cmdx); c4.add_out(mout(cmdx) + "\n", mongo=True)
show(c4.html(ET), PX, "B1 : ajout de 3 étudiants de mon choix (Belghith, Hammami, Saidi) avec insertMany().", 8000, cap="b1")
m(ET, PX, "B2 : affichez uniquement les étudiants de la filière Reseaux.", 'db.etudiants.find({ filiere: "Reseaux" }, { _id: 0 })',
  ['db.etudiants.find({ filiere: "Reseaux" }, { _id: 0 })', 'db.etudiants.find({filiere: "Reseaux"}, {_id: 0})', 'db.etudiants.find({filiere:"Reseaux"},{_id:0})'], cap="b2")
m(ET, PX, "B3 : noms et moyennes des étudiants ayant au moins 12, du meilleur au moins bon.",
  "db.etudiants.find({ moyenne: { $gte: 12 } }, { nom: 1, moyenne: 1, _id: 0 }).sort({ moyenne: -1 })",
  ["db.etudiants.find({ moyenne: { $gte: 12 } }, { nom: 1, moyenne: 1, _id: 0 }).sort({ moyenne: -1 })",
   "db.etudiants.find({moyenne: {$gte: 12}}, {nom: 1, moyenne: 1, _id: 0}).sort({moyenne: -1})",
   "db.etudiants.find({moyenne:{$gte:12}},{nom:1,moyenne:1,_id:0}).sort({moyenne:-1})"], cap="b3")
m(ET, PX, "B4 : modifiez la moyenne de Saidi (10.75 → 12.25).", 'db.etudiants.updateOne({ nom: "Saidi" }, { $set: { moyenne: 12.25 } })',
  ['db.etudiants.updateOne({ nom: "Saidi" }, { $set: { moyenne: 12.25 } })', 'db.etudiants.updateOne({nom: "Saidi"}, {$set: {moyenne: 12.25}})', 'db.etudiants.updateOne({nom:"Saidi"},{$set:{moyenne:12.25}})'])
m(ET, PX, "Vérifiez la nouvelle moyenne.", 'db.etudiants.findOne({ nom: "Saidi" }, { nom: 1, moyenne: 1, _id: 0 })',
  ['db.etudiants.findOne({ nom: "Saidi" }, { nom: 1, moyenne: 1, _id: 0 })', 'db.etudiants.findOne({nom: "Saidi"}, {nom: 1, moyenne: 1, _id: 0})', 'db.etudiants.findOne({nom:"Saidi"},{nom:1,moyenne:1,_id:0})'], cap="b4")
m(ET, PX, "B5 : supprimez l'étudiante Hammami.", 'db.etudiants.deleteOne({ nom: "Hammami" })',
  ['db.etudiants.deleteOne({ nom: "Hammami" })', 'db.etudiants.deleteOne({nom: "Hammami"})', 'db.etudiants.deleteOne({nom:"Hammami"})'])
m(ET, PX, "Puis affichez le nombre de documents restants.", "db.etudiants.countDocuments()", cap="b5")
m(ET, "Nettoyage", "Il reste 5 étudiants. 8.7 : vérifiez toujours la base courante avec db avant de supprimer, puis supprimez la collection.", "db.etudiants.drop()")
m(ET, "Nettoyage", "Supprimez la base etudiant.", "db.dropDatabase()")
tcon(c4, ET, "Nettoyage", "Base supprimée ({ ok: 1, dropped: 'etudiant' }). Quittez mongosh.", ["exit", "exit()", "quit", "quit()"], None)
c4.add_raw("")
show(c4.html(WP), "Fin", "TP1 terminé : MongoDB 7.0 et mongosh installés, Path configuré, service RUNNING sur 127.0.0.1:27017, CRUD de base maîtrisé sur la base etudiant.", 10000)
