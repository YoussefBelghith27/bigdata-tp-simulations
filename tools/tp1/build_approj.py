"""Construit le projet ActivePresenter (.approj, base SQLite) du TP1 à partir d'un projet modèle du site WAN.

Modèles (TP2 VPN MPLS) : diapo 0 = écran commenté, 1 = saisie console, 32 = saisie dans un champ, 34 = clic.
Chaque nouvelle diapo reprend le modèle, change l'image de fond, les textes, la réponse attendue et la zone.
"""
import sqlite3, json, re, shutil, uuid, copy, html, sys, pathlib, io
from PIL import Image

TEMPLATE = "/home/claude/wan-tp-simulations/activepresenter/TP2_VPN_MPLS_Simulation.approj"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/tp1/build/TP1_Installation_MongoDB_Simulation.approj"
META = json.load(open(sys.argv[2] if len(sys.argv) > 2 else "/home/claude/tp1/build/slides_meta.json"))
DESC = sys.argv[3] if len(sys.argv) > 3 else "TP1 Big Data Avancée – Installation de MongoDB 7.0 et mongosh (Youssef Belghith)"
E = html.escape

def load(s):  # garde les entiers « +N » propres à ActivePresenter
    return json.loads(re.sub(r'([:\[,])\+(\d+)', r'\1"__P\2"', s))

def dump(d):
    return re.sub(r'"__P(\d+)"', r'+\1', json.dumps(d, ensure_ascii=False, separators=(",", ":")))

shutil.copy(TEMPLATE, OUT)
c = sqlite3.connect(OUT)
T = {k: load(c.execute("select contents from slides where [index]=?", (i,)).fetchone()[0]) for k, i in
     [("show", 0), ("con", 1), ("box", 32), ("click", 34)]}

# on retire les diapos et les images de fond du modèle (on garde curseurs, thème, réglages)
c.execute("delete from slides")
c.execute("delete from resources where type=4 and subtype=1")

P = '<p style="text-align:center;line-height: 1.20; margin-top: 0px; margin-bottom: 0px; ">'
def para(inner):
    return P + inner + "</p>"

def set_rect(ctrl, x, y, w, h):
    for r in ctrl["states"][0]["respvalues"]:
        r.update(x=int(x * 1000), y=int(y * 1000), w=int(w * 1000), h=int(h * 1000))

def set_html(ctrl, h):
    ctrl["states"][0]["htmltext"] = h

for k, m in enumerate(META):
    im = Image.open(m["png"]).convert("RGB").quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG)
    buf = io.BytesIO(); im.save(buf, "PNG", optimize=True); data = buf.getvalue()
    c.execute("insert into resources(name,deleted,type,subtype,groupid,hint,data,uuid) values('',0,4,1,0,?,?,?)",
              ('{\n   "width": 1242,\n   "height": 1060,\n   "format": "png",\n   "file": ""\n}\n', data, str(uuid.uuid4())))
    rid = c.execute("select last_insert_rowid()").fetchone()[0]
    kind = m["kind"]
    key = "show" if kind == "show" else "click" if kind == "click" else ("box" if m.get("box") else "con")
    d = copy.deepcopy(T[key])
    d["id"] = 3000 + k
    d["background_image"]["states"][0]["imageid"] = rid
    sub = para(f'<span style="font-weight:bold;">{E(m["step"])}</span> — {E(m["text"])}')
    if kind == "show":
        d["duration"] = m["dur"]
        set_html(d["controls"][0], sub)
        d["name"] = f"{k+1:02d} · {m['step']}"
    else:
        ctl, hint, fb, subc = d["controls"]
        set_html(subc, sub)
        if kind == "click":
            x, y, w, h = m["box"]
            set_rect(ctl, x, y, w, h)
            set_html(hint, para(E(m["hint"])))
            set_html(fb, para("Ce n'est pas le bon endroit. " + E(m["hint"])))
            d["name"] = f"{k+1:02d} · clic"
        else:
            ans = m["answers"]
            proto = ctl["evtman"]["values"][0]
            ctl["evtman"]["values"] = [dict(proto, evalue=a, case_sensitive=False) for a in ans]
            if m.get("box"):
                x, y, w, h = m["box"]
                set_rect(ctl, x, y, w, h)
            else:
                set_rect(ctl, m["x"], 1039, 1166 - m["x"], 20)
            set_html(hint, para(f'Tapez : <span style="font-weight:bold;">{E(ans[0])}</span> puis Entrée'))
            set_html(fb, para(f'Saisie incorrecte. Réessayez : <span style="font-weight:bold;">{E(ans[0])}</span>'))
            ctl["itext"] = "Saisie" if m.get("box") else "Commande"
            d["name"] = f"{k+1:02d} · {ans[0][:60]}"
    c.execute("insert into slides(proj_id,cont_id,[index],name,contents,thumbnail) values(1,0,?,?,?,NULL)", (k, d["name"], dump(d)))

name = pathlib.Path(OUT).stem
c.execute("update projects set name=?, description=?, author=?, modified=CURRENT_TIMESTAMP", (name, DESC, "Youssef Belghith"))
c.commit()
c.execute("vacuum")
c.close()
print(OUT, len(META), "diapositives")
