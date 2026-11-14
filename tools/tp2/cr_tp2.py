"""Compte rendu TP2 : captures partielles (sorties réelles de sorties_tp2.txt) + PDF A4."""
import pathlib, html, base64
from playwright.sync_api import sync_playwright
from render import Renderer, FONTS
from screens import color_mongo, CSS as SCSS
import story_tp2 as st

E = html.escape
B = pathlib.Path("/home/claude/tp2/build"); D = B / "crcap"; D.mkdir(parents=True, exist_ok=True)
OUT = B / "CR_TP2_Requetes_Restaurants.pdf"
W = 980; COLS = int((W - 24) // 8.203125)
RP = st.RP

def wrapl(s):
    r = []
    while len(s) > COLS: r.append(s[:COLS]); s = s[COLS:]
    r.append(s); return r

def block(title, entries, maxl=18):
    lines = []
    for prompt, cmd, o, mongo in entries:
        for j, p in enumerate(wrapl(prompt + cmd)):
            lines.append((E(p[:len(prompt)]) + f'<span class="w">{E(p[len(prompt):])}</span>') if j == 0 else f'<span class="w">{E(p)}</span>')
        if o:
            ol = o.split("\n")
            cut = len(ol) > maxl
            for l in ol[:maxl]:
                for p in wrapl(l):
                    lines.append(color_mongo(p) if mongo else E(p))
            if cut:
                lines.append(f'<span class="k">… ({len(ol) - maxl} lignes de plus)</span>')
    return f"""<div id="cap" style="width:{W}px;background:#0c0c0c;border-radius:8px;overflow:hidden;border:1px solid #333">
      <div style="height:30px;background:#202020;color:#ddd;font:12px UI;display:flex;align-items:center;padding:0 12px;gap:8px">
      <span style="font:10px MONO;border:1px solid #555;border-radius:3px;padding:0 3px">&gt;_</span>{E(title)}</div>
      <div style="font:14px/18px MONO;color:#ccc;white-space:pre;padding:10px 12px">{"\n".join(lines)}</div></div>"""

R = st.R
EXTRA = {4: "Q4c", 12: "Q12c", 16: "Q16c", 17: "Q17c", 18: "Q18c", 19: "Q19c", 20: "Q20c", 25: "Q25a"}
MAXL = {1: 16, 2: 14, 3: 12, 4: 14, 5: 14, 6: 14, 7: 16, 8: 16, 12: 12, 17: 10, 18: 10, 19: 10, 20: 10, 21: 22, 22: 22, 23: 18, 24: 14, 26: 20}
CAPS = {
 "import": ("Invite de commandes", [(st.FP, "mongoimport --db Restaurants --collection restaurant --file restaurants.json",
            "2026-11-14T13:12:41.208+0100\tconnected to: mongodb://localhost/\n2026-11-14T13:12:41.497+0100\t3772 document(s) imported successfully. 0 document(s) failed to import.", False),
            (st.FP, "mongosh Restaurants", "...", False), (RP, R["Q25b"][0], R["Q25b"][1], True)]),
 "tools": ("Invite de commandes", [("C:\\Users\\ASUS>", "mongoimport --version", "'mongoimport' n'est pas reconnu en tant que commande interne\nou externe, un programme exécutable ou un fichier de commandes.", False),
            ("C:\\Users\\ASUS>", "(après installation des Database Tools et ajout au Path, dans un nouveau cmd)", None, False),
            ("C:\\Users\\ASUS>", "mongoimport --version", f"mongoimport version: {st.TV}\n   os: windows\n   arch: amd64\n   compiler: gc", False)]),
}
for n in range(1, 27):
    ent = [(RP, R[f"Q{n}"][0], R[f"Q{n}"][1], True)]
    if n in EXTRA:
        ent.append((RP, R[EXTRA[n]][0], R[EXTRA[n]][1], True))
    CAPS[f"Q{n}"] = ("Invite de commandes – mongosh", ent)

with Renderer() as r:
    for name, (title, ent) in CAPS.items():
        mx = MAXL.get(int(name[1:]) if name.startswith("Q") else 0, 18)
        r.pg.set_content(f"<!doctype html><meta charset=utf-8><style>{FONTS}{SCSS}body{{width:auto;height:auto;overflow:visible;background:#fff}}</style>{block(title, ent, mx)}")
        r.pg.evaluate("document.fonts.ready"); r.pg.wait_for_timeout(50)
        r.pg.locator("#cap").screenshot(path=str(D / f"{name}.png"))
from PIL import Image

def img(name, w="100%", fig=None):
    b = base64.b64encode((D / f"{name}.png").read_bytes()).decode()
    return f'<figure><img src="data:image/png;base64,{b}" style="width:{w}">' + (f'<figcaption>{fig}</figcaption>' if fig else "") + "</figure>"
def code(s): return f'<pre class="code">{E(s)}</pre>'
def obs(s): return f'<p class="obs"><b>Observation.</b> {s}</p>'

QE = {  # énoncés (reformulés courts)
 1: "Afficher tous les documents de la collection restaurant.", 2: "Afficher restaurant_id, name, borough et cuisine de tous les documents.",
 3: "Afficher restaurant_id, name, borough et cuisine en excluant le champ _id.", 4: "Afficher tous les restaurants de l'arrondissement Bronx.",
 5: "Afficher les 5 premiers restaurants du Bronx.", 6: "Afficher les 5 restaurants du Bronx situés après les 5 premiers.",
 7: "Trouver les restaurants ayant obtenu un score supérieur à 90.", 8: "Trouver les restaurants ayant obtenu un score supérieur à 80 mais inférieur à 100.",
 9: "Trouver les restaurants dont la latitude (coord[0]) est inférieure à -95.754168.",
 10: "Pas de cuisine « American », score supérieur à 70 et latitude inférieure à -65.754168.", 11: "Même requête que la 10, sans l'opérateur $and.",
 12: "Pas de cuisine « American », grade « A », hors Brooklyn, trié par cuisine décroissante.", 13: "Id, nom, arrondissement et cuisine des restaurants dont le nom contient « Wil ».",
 14: "Restaurants dont le nom se termine par « ces ».", 15: "Restaurants contenant « Reg » quelque part dans le nom.",
 16: "Restaurants du Bronx qui préparent une cuisine américaine ou chinoise.", 17: "Restaurants de Staten Island, Queens, Bronx ou Brooklyn.",
 18: "Restaurants n'appartenant pas à Staten Island, Queens, Bronx ou Brooklyn.", 19: "Restaurants ayant obtenu un score ne dépassant pas 10.",
 20: "Cuisine autre que « American » et « Chinese », ou nom commençant par « Wil ».", 21: "Grade « A » et score 11 à la date ISODate(\"2014-08-11T00:00:00Z\").",
 22: "Deuxième élément de grades : grade « A », score 9, le 2014-08-11.", 23: "Deuxième élément de coord compris entre 42 et 52 (id, nom, adresse).",
 24: "Trier les restaurants par nom croissant (toutes les colonnes).", 25: "Savoir si toutes les adresses contiennent une rue (street).",
 26: "Nom, arrondissement, coordonnées et cuisine des restaurants dont le nom commence par « Mad ».",
}
OBS = {
 1: "20 documents affichés par page (« Type \"it\" for more ») sur 3772.", 2: "La projection inclut _id par défaut.", 3: "_id: 0 est la seule exclusion autorisée dans une projection d'inclusion.",
 4: "309 restaurants dans le Bronx.", 5: "limit(5) renvoie les 5 premiers documents.", 6: "skip(5) saute les 5 premiers, puis limit(5) : pagination.",
 7: "« grades.score » est testé sur chaque élément du tableau : un seul score > 90 suffit.", 8: "$elemMatch impose que > 80 et < 100 portent sur la même note.",
 9: "coord.0 désigne le premier élément du tableau coord. 3 restaurants hors de New York.",
 10: "Dans les données, la cuisine est « American » suivie d'une espace, d'où la valeur \"American \".", 11: "Plusieurs critères dans le même filtre = ET implicite : même résultat que la Q10.",
 12: "2017 restaurants ; sort({ cuisine: -1 }) trie de Z à A.", 13: "Regex /Wil/ : « Wil » n'importe où, sensible à la casse.", 14: "$ ancre la regex en fin de chaîne.",
 15: "/.*Reg.*/ équivaut à /Reg/.", 16: "$in : 91 restaurants.", 17: "$in sur borough : 1889 restaurants.", 18: "$nin : 1883 restaurants, tous à Manhattan (seul autre arrondissement du jeu de données).",
 19: "$not { $gt: 10 } : aucun score supérieur à 10 (340 restaurants). Un simple { $lte: 10 } garderait ceux qui ont au moins un score ≤ 10.",
 20: "$or entre une regex et un $nin : 2403 restaurants.", 21: "$elemMatch : date, grade et score dans le même élément.", 22: "grades.1 = deuxième élément (indices à partir de 0).",
 23: "coord.1 entre 42 et 52.", 24: "sort({ name: 1 }) trie par ordre alphabétique.", 25: "Aucun document sans street : 3772 adresses avec rue sur 3772 documents.",
 26: "^ ancre la regex en début de chaîne.",
}
sec = ""
for n in range(1, 27):
    cmds = R[f"Q{n}"][0] + (("\n" + R[EXTRA[n]][0]) if n in EXTRA else "")
    w = "100%" if len(R[f"Q{n}"][0]) > 105 else "88%"
    sec += f'<div class="qq"><h3>Question {n}. {E(QE[n])}</h3>{code(cmds)}{img(f"Q{n}", w)}<p class="obs">{OBS[n]}</p></div>'

body = f"""
<section class="cover">
  <div class="inst"><div>Institut Supérieur des Études Technologiques de Nabeul<br>Département Technologies de l'Informatique</div><div style="text-align:right">Big Data Avancée<br>Classe : RSI31</div></div>
  <div class="mid"><div class="kicker">COMPTE RENDU DE TRAVAUX PRATIQUES</div>
    <h1>TP 2 : Requêtes MongoDB<br>sur la base Restaurants</h1>
    <div class="subt">Importation avec mongoimport, projections, opérateurs,<br>tableaux, expressions régulières, tri et pagination</div><div class="bar"></div></div>
  <table class="id"><tr><td>Réalisé par</td><td><b>Youssef Belghith</b></td></tr><tr><td>Classe</td><td>RSI31</td></tr>
    <tr><td>Enseignante</td><td>Ines Ghorbel</td></tr><tr><td>Outils</td><td>MongoDB 7.0.43, mongosh 2.12.0, Database Tools {st.TV}</td></tr>
    <tr><td>Base / collection</td><td>Restaurants / restaurant (3772 documents)</td></tr><tr><td>Date</td><td>14 novembre 2026</td></tr></table>
</section>
<section>
<h2 class="nob">1. Objectif</h2>
<p>Importer le jeu de données <code>restaurants.json</code> dans MongoDB avec <b>mongoimport</b>, puis interroger la collection <code>restaurant</code> avec <code>find()</code>. Chaque question donne la commande et une <b>capture partielle</b> de la sortie.</p>
<p class="note"><b>Remarque sur les captures.</b> Les sorties des requêtes sont celles de l'<b>exécution réelle</b> sur mon poste (fichier <code>sorties_tp2.txt</code>). La fenêtre cmd de la simulation est reconstituée. Simulation interactive : <i>youssefbelghith27.github.io/bigdata-tp-simulations</i>.</p>
<h2>2. Importation de la base</h2>
<p>MongoDB, mongosh et les <b>MongoDB Database Tools</b> (qui fournissent mongoimport) sont déjà installés et présents dans le Path.</p>
{code("cd " + st.DIR + chr(10) + "mongoimport --db Restaurants --collection restaurant --file restaurants.json" + chr(10) + "mongosh Restaurants")}
{img("import", "100%", "Figure 1 – Capture A : importation de restaurants.json (3772 documents)")}
{obs("3772 documents importés, 0 échec. La base <code>Restaurants</code> et la collection <code>restaurant</code> sont créées à l'import.")}
</section>
<section><h2 class="nob">3. Requêtes</h2>{sec}</section>
<section><h2 class="nob">4. Synthèse des opérateurs utilisés</h2>
<table class="t"><tr><th>Besoin</th><th>Syntaxe</th><th>Questions</th></tr>
<tr><td>Projection / exclusion de _id</td><td><code>{{ champ: 1, _id: 0 }}</code></td><td>2, 3, 13–20</td></tr>
<tr><td>Pagination</td><td><code>.limit(n)</code>, <code>.skip(n)</code></td><td>5, 6</td></tr>
<tr><td>Comparaison</td><td><code>$gt $lt $ne</code></td><td>7–12, 23</td></tr>
<tr><td>Même élément d'un tableau</td><td><code>$elemMatch</code></td><td>8, 21</td></tr>
<tr><td>Élément par position</td><td><code>"address.coord.0"</code>, <code>"grades.1.score"</code></td><td>9–11, 22, 23</td></tr>
<tr><td>Listes de valeurs</td><td><code>$in</code>, <code>$nin</code></td><td>16–18, 20</td></tr>
<tr><td>Négation / OU</td><td><code>$not</code>, <code>$or</code>, <code>$and</code></td><td>10, 19, 20</td></tr>
<tr><td>Expressions régulières</td><td><code>/Wil/</code>, <code>/ces$/</code>, <code>/^Mad/</code></td><td>13–15, 20, 26</td></tr>
<tr><td>Tri / existence d'un champ</td><td><code>.sort()</code>, <code>$exists</code></td><td>12, 24, 25</td></tr></table>
<h2>5. Conclusion</h2>
<p>Les 3772 restaurants ont été importés avec mongoimport (Database Tools installés séparément) et interrogés avec 26 requêtes find(). Le TP montre la puissance du modèle document : on filtre directement dans les sous-documents (<code>address</code>) et dans les tableaux (<code>grades</code>, <code>coord</code>), par valeur, par position ou avec <code>$elemMatch</code>, sans jointure. Attention aux données réelles : la cuisine « American » est stockée avec une espace finale.</p>
</section>"""

src = open("/home/claude/tp1/gen/cr_build.py").read()
CSS = src.split('CSS = """')[1].split('"""')[0] + ".qq{page-break-inside:avoid;margin-bottom:6px} section.cover + section{page-break-before:always}"
FONTCSS = src.split('FONTCSS = f"""')[1].split('"""')[0].replace("{{", "{").replace("}}", "}")
H = B / "cr2.html"
H.write_text(f"<!doctype html><html lang=fr><head><meta charset=utf-8><style>{FONTCSS}{CSS}</style></head><body>{body}</body></html>")
foot = '<div style="width:100%;font-size:7.5pt;color:#6b7a84;padding:0 16mm;display:flex;justify-content:space-between;font-family:sans-serif"><span>TP 2 – Requêtes MongoDB (base Restaurants) · Youssef Belghith · RSI31</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(); pg.goto(H.as_uri()); pg.wait_for_timeout(500)
    pg.pdf(path=str(OUT), format="A4", print_background=True, display_header_footer=True, header_template="<div></div>", footer_template=foot,
           margin={"top": "16mm", "bottom": "18mm", "left": "16mm", "right": "16mm"})
    b.close()
print(OUT, OUT.stat().st_size // 1024, "Ko")
