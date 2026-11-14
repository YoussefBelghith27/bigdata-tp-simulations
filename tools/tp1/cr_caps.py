"""Captures partielles pour le compte rendu : blocs console recadrés + recadrage des écrans GUI."""
import json, pathlib, html
from PIL import Image
from render import Renderer, FONTS
from screens import color_mongo, CSS
import story

E = html.escape
D = pathlib.Path("/home/claude/tp1/build/crcap"); D.mkdir(parents=True, exist_ok=True)
S = json.load(open("/home/claude/tp1/run/session.json"))
def out(i): return S[i]["out"]

WP, AP, ET, T = "C:\\Users\\ASUS>", "C:\\WINDOWS\\system32>", "etudiant> ", "test> "
W = 980
COLS = int((W - 24) // 8.203125)

def wrapl(s):
    r = []
    while len(s) > COLS: r.append(s[:COLS]); s = s[COLS:]
    r.append(s); return r

def block(title, entries):
    lines = []
    for e in entries:
        if e[0] == "raw":
            lines += [E(x) for x in e[1].split("\n")]; continue
        prompt, cmd, o, mongo = e
        for j, p in enumerate(wrapl(prompt + cmd)):
            lines.append((E(p[:len(prompt)]) + f'<span class="w">{E(p[len(prompt):])}</span>') if j == 0 else f'<span class="w">{E(p)}</span>')
        if o is not None:
            for l in o.split("\n"):
                for p in wrapl(l):
                    lines.append(color_mongo(p) if mongo else E(p))
    body = "\n".join(lines)
    return f"""<div id="cap" style="width:{W}px;background:#0c0c0c;border-radius:8px;overflow:hidden;border:1px solid #333">
      <div style="height:30px;background:#202020;color:#ddd;font:12px UI;display:flex;align-items:center;padding:0 12px;gap:8px">
      <span style="font:10px MONO;border:1px solid #555;border-radius:3px;padding:0 3px">&gt;_</span>{E(title)}</div>
      <div style="font:14px/18px MONO;color:#ccc;white-space:pre;padding:10px 12px">{body}</div></div>"""

CAPS = {
 "A1_where": ("Invite de commandes", [(WP, "where mongod", story.BIN + "\\mongod.exe", False), (WP, "where mongosh", story.SHDIR + "\\mongosh.exe", False)]),
 "A0_where_avant": ("Invite de commandes", [(WP, "where mongod", "INFORMATION : impossible de trouver des fichiers pour le(s) modèle(s) spécifié(s).", False),
                                           (WP, "where mongosh", "INFORMATION : impossible de trouver des fichiers pour le(s) modèle(s) spécifié(s).", False)]),
 "A2_versions": ("Invite de commandes", [(WP, "mongod --version", story.mv.rstrip(), False), (WP, "mongosh --version", story.VSH, False)]),
 "A3_sc": ("Invite de commandes", [(WP, "sc query MongoDB", story.SCQ.rstrip(), False)]),
 "A4_netstat": ("Administrateur : Invite de commandes", [(AP, "net stop MongoDB", "Le service MongoDB Server (MongoDB) s'arrête.\nLe service MongoDB Server (MongoDB) a été arrêté.", False),
                (AP, "net start MongoDB", "Le service MongoDB Server (MongoDB) démarre..\nLe service MongoDB Server (MongoDB) a démarré.", False),
                (AP, "netstat -an | findstr 27017", "  TCP    127.0.0.1:27017        0.0.0.0:0              LISTENING", False)]),
 "A5a_connexion": ("Invite de commandes", [(WP, "mongosh", "\n".join(story.BANNER.split("\n")[:4]) + "\n...", False),
                (T, "db.version()", out(0), True), (T, "db", out(1), True), (T, "show dbs", out(2), True), (T, "use etudiant", out(3), True)]),
 "A5b_insert": ("Invite de commandes", [(ET, S[4]["cmd"], out(4), True), (ET, S[5]["cmd"], out(5), True), (ET, "show dbs", out(6), True), (ET, "show collections", out(7), True), (ET, "db.etudiants.countDocuments()", out(8), True)]),
 "A5c_find": ("Invite de commandes", [(ET, "db.etudiants.find()", out(10), True)]),
 "D_filtres": ("Invite de commandes", [(ET, S[18]["cmd"], out(18), True), (ET, S[20]["cmd"], out(20), True), (ET, S[17]["cmd"], "\n".join(out(17).split("\n")), True)]),
 "D_update": ("Invite de commandes", [(ET, S[22]["cmd"], out(22), True), (ET, S[23]["cmd"], out(23), True), (ET, S[24]["cmd"], out(24), True), (ET, S[26]["cmd"], out(26), True), (ET, S[27]["cmd"], out(27), True)]),
 "B1": ("Invite de commandes", [(ET, S[28]["cmd"], out(28), True)]),
 "B2": ("Invite de commandes", [(ET, S[29]["cmd"], out(29), True)]),
 "B3": ("Invite de commandes", [(ET, S[30]["cmd"], out(30), True)]),
 "B4": ("Invite de commandes", [(ET, S[31]["cmd"], out(31), True), (ET, S[32]["cmd"], out(32), True)]),
 "B5": ("Invite de commandes", [(ET, S[33]["cmd"], out(33), True), (ET, S[34]["cmd"], out(34), True)]),
 "N_nettoyage": ("Invite de commandes", [(ET, "db", "etudiant", True), (ET, S[35]["cmd"], out(35), True), (ET, S[36]["cmd"], out(36), True), (ET, "exit", None, False)]),
}

with Renderer() as r:
    for name, (title, entries) in CAPS.items():
        r.pg.set_content(f"<!doctype html><meta charset=utf-8><style>{FONTS}{CSS}body{{width:auto;height:auto;overflow:visible;background:#fff}}</style>{block(title, entries)}")
        r.pg.evaluate("document.fonts.ready"); r.pg.wait_for_timeout(60)
        r.pg.locator("#cap").screenshot(path=str(D / f"{name}.png"))

# recadrage des écrans GUI (coordonnées dans l'écran 1242x1060)
C = pathlib.Path("/home/claude/tp1/build/cap")
for src, name, box in [("service", "G_service", (249, 150, 994, 736)), ("path", "A6_path", (312, 162, 1014, 812)),
                       ("bin", "G_bin", (70, 110, 1170, 380))]:
    Image.open(C / f"{src}.png").crop(box).save(D / f"{name}.png")
print(sorted(p.name for p in D.iterdir()))
