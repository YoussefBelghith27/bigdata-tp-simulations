"""Compte rendu TP3 : captures partielles (sorties réelles) + PDF A4."""
import pathlib, html, base64, re
from playwright.sync_api import sync_playwright
from render import Renderer, FONTS
from screens import color_mongo, CSS as SCSS
import story_tp3 as st

E = html.escape
B = pathlib.Path("/home/claude/tp3/build"); D = B / "crcap"; D.mkdir(parents=True, exist_ok=True)
OUT = B / "CR_TP3_Replication_Sharding.pdf"
W = 980; COLS = int((W - 24) // 8.203125)
IT = st.ITEMS

def find(prefix, start=0, occ=1):
    n = 0
    for k in range(start, len(IT)):
        if IT[k][1].startswith(prefix):
            n += 1
            if n == occ: return IT[k]
    raise KeyError(prefix)

def wrapl(s):
    r = []
    while len(s) > COLS: r.append(s[:COLS]); s = s[COLS:]
    r.append(s); return r

def block(title, entries, maxl=18):
    lines = []
    for prompt, cmd, o in entries:
        for j, l in enumerate(cmd.split("\n")):
            for k, p in enumerate(wrapl((prompt if j == 0 else "") + l)):
                if j == 0 and k == 0:
                    lines.append(E(p[:len(prompt)]) + f'<span class="w">{E(p[len(prompt):])}</span>')
                else:
                    lines.append(f'<span class="w">{E(p)}</span>')
        if o:
            ol = o.split("\n")
            for l in ol[:maxl]:
                for p in wrapl(l): lines.append(color_mongo(p))
            if len(ol) > maxl: lines.append(f'<span class="k">… ({len(ol) - maxl} lignes de plus)</span>')
    return f"""<div id="cap" style="width:{W}px;background:#0c0c0c;border-radius:8px;overflow:hidden;border:1px solid #333">
      <div style="height:30px;background:#202020;color:#ddd;font:12px UI;display:flex;align-items:center;padding:0 12px;gap:8px">
      <span style="font:10px MONO;border:1px solid #555;border-radius:2px;padding:0 3px">&gt;_</span>{E(title)}</div>
      <div style="font:14px/18px MONO;color:#ccc;white-space:pre;padding:10px 12px">{"\n".join(lines)}</div></div>"""

FE = "rs.status().members"
CAPS = {
 "c01_init": ("mongosh 27017", [find("rs.initiate")], 12),
 "c02_status": ("mongosh 27017", [find(FE), find("db.hello().isWritablePrimary")], 18),
 "c03_insert": ("mongosh 27017 (Primary)", [find("db.etudiants.insertMany"), find("db.etudiants.countDocuments()")], 18),
 "c04_secondary": ("mongosh 27018 (Secondary)", [find("rs.secondaryOk()"), find("db.etudiants.find()"), find("db.etudiants.countDocuments()", occ=2)], 14),
 "c05_oplog": ("mongosh 27017", [find("db.oplog.rs.find().sort")], 24),
 "c06_failover": ("mongosh 27018", [find(FE, occ=2), find("db.hello().primary"), find("db.hello().isWritablePrimary", occ=2), find("db.etudiants.insertOne")], 18),
 "c07_retour": ("mongosh 27018", [find(FE, occ=3)], 18),
 "c08_cfg": ("mongosh 28019 / 28101", [find(FE, occ=4), find(FE, occ=5), find(FE, occ=6), find(FE, occ=7)], 18),
 "c09_addshard": ("mongos 28000", [find("sh.addShard('shardRS3")], 6),
 "c10_status": ("mongos 28000", [find("sh.status()")], 28),
 "c11_load": ("mongos 28000", [find("for (let i=1"), find("db.etudiants.countDocuments()", start=30), find("db.etudiants.createIndex"), find("sh.shardCollection")], 6),
 "c12_chunks": ("mongos 28000", [find("sh.status()", occ=2)], 200),
 "c13_distrib": ("mongos 28000", [find("db.etudiants.getShardDistribution()")], 48),
 "c14_routage": ("mongos 28000", [find("db.etudiants.find({matricule:500})"), find("db.etudiants.find({nom:"), find("db.etudiants.countDocuments({filiere:")], 10),
 "c15_explain": ("mongos 28000", [find("e = db.etudiants.find({matricule:500})"), find("e = db.etudiants.find({nom:")], 20),
 "c16_panne": ("mongosh 28102 / mongos", [find(FE, occ=9), find("db.hello().isWritablePrimary", occ=3), find("db.etudiants.find({matricule:500})   //"),
                find("db.etudiants.find({matricule:25000})"), find("db.etudiants.insertOne({matricule:600")], 10),
 "c17_retour": ("mongosh 28102 / mongos", [find(FE, occ=10), find("db.etudiants.find({matricule:500})", occ=3)], 10),
}
# c12 : ne garder que la partie « collections / chunks » du sh.status()
p, c, o = CAPS["c12_chunks"][1][0]
o = "\n".join(["…"] + o.split("\n")[o.split("\n").index("    collections: {", len(o.split("\n")) - 30):])
CAPS["c12_chunks"] = ("mongos 28000", [(p, c, o)], 40)

with Renderer() as r:
    for name, (title, ent, mx) in CAPS.items():
        r.pg.set_content(f"<!doctype html><meta charset=utf-8><style>{FONTS}{SCSS}body{{width:auto;height:auto;overflow:visible;background:#fff}}</style>{block(title, ent, mx)}")
        r.pg.evaluate("document.fonts.ready"); r.pg.wait_for_timeout(50)
        r.pg.locator("#cap").screenshot(path=str(D / f"{name}.png"))
from PIL import Image
Image.open(B / "cap" / "p1_mongod.png").crop((0, 84, 1242, 1012)).save(D / "c00_mongod.png")
Image.open(B / "cap" / "p2_mongod.png").crop((0, 84, 1242, 1012)).save(D / "c08b_mongod.png")

def img(name, w="100%", fig=None):
    b = base64.b64encode((D / f"{name}.png").read_bytes()).decode()
    return f'<figure><img src="data:image/png;base64,{b}" style="width:{w}">' + (f'<figcaption>{fig}</figcaption>' if fig else "") + "</figure>"
def code(s): return f'<pre class="code">{E(s)}</pre>'
def obs(s): return f'<p class="obs"><b>Observation.</b> {s}</p>'
fn = iter(range(1, 50))
def F(t): return f"Figure {next(fn)} – {t}"

body = f"""
<section class="cover">
  <div class="inst"><div>Institut Supérieur des Études Technologiques de Nabeul<br>Département Technologies de l'Informatique</div><div style="text-align:right">Atelier Écosystème Big Data avancé<br>Classe : RSI31</div></div>
  <div class="mid"><div class="kicker">COMPTE RENDU DE TRAVAUX PRATIQUES</div>
    <h1>TP 3 : MongoDB 7<br>Haute disponibilité et sharding</h1>
    <div class="subt">Replica Set, oplog, failover,<br>cluster shardé : config servers, shards, chunks et mongos</div><div class="bar"></div></div>
  <table class="id"><tr><td>Réalisé par</td><td><b>Youssef Belghith</b></td></tr><tr><td>Classe</td><td>RSI31</td></tr>
    <tr><td>Enseignante</td><td>Ines Ghorbel</td></tr><tr><td>Environnement</td><td>MongoDB 7.0.43, mongosh 2.12.0, Windows CMD</td></tr>
    <tr><td>Date</td><td>14 novembre 2026</td></tr></table>
</section>
<section>
<h2 class="nob">Partie 1 – Réplication : Replica Set rs0</h2>
<p class="note"><b>Remarque sur les captures.</b> Les sorties mongosh viennent d'une <b>exécution réelle</b> des scripts du TP (fichier <code>sorties_tp3.txt</code>). Les fenêtres <code>mongod</code> sont reconstituées. Simulation interactive : <i>youssefbelghith27.github.io/bigdata-tp-simulations</i>.</p>
<table class="t"><tr><th>Membre</th><th>Port</th><th>dbpath</th><th>Rôle obtenu</th></tr>
<tr><td>node1</td><td>27017</td><td><code>C:\\mongodb\\tp3\\data\\node1</code></td><td>PRIMARY</td></tr>
<tr><td>node2 / node3 / node4</td><td>27018–27020</td><td><code>…\\node2</code> à <code>…\\node4</code></td><td>SECONDARY</td></tr>
<tr><td>arbiter</td><td>27021</td><td><code>…\\arbiter</code></td><td>ARBITER (vote, sans données)</td></tr></table>
{code("mkdir C:\\mongodb\\tp3\\data\\node1   (idem node2, node3, node4, arbiter)" + chr(10) + "mongod --dbpath C:\\mongodb\\tp3\\data\\node1 --port 27017 --replSet rs0   (une fenêtre par membre)")}
{img("c00_mongod", "80%", F("Les cinq processus mongod de rs0 (reconstitué)"))}
<h3>Initialisation et Test 1 : état du Replica Set</h3>
{img("c01_init", "80%", F("rs.initiate() depuis mongosh --port 27017"))}
{img("c02_status", "80%", F("1 PRIMARY, 3 SECONDARY, 1 ARBITER ; isWritablePrimary vaut true sur 27017"))}
<h3>Test 2 : écriture sur le Primary, lecture sur un Secondary</h3>
{img("c03_insert", "80%", F("insertMany sur le Primary (4 documents)"))}
{img("c04_secondary", "80%", F("Lecture sur 27018 après rs.secondaryOk() : mêmes 4 documents"))}
<h3>Test 3 : oplog</h3>
{img("c05_oplog", "80%", F("local.oplog.rs : entrées op 'i' sur universite.etudiants"))}
{obs("Chaque insertion apparaît dans l'oplog (op: 'i', ns: 'universite.etudiants', o: le document). Les Secondary relisent ce journal pour rejouer les écritures.")}
<h3>Test 4 : failover</h3>
<p>Ctrl+C dans la fenêtre du Primary (27017), puis connexion à 27018 :</p>
{img("c06_failover", "80%", F("27017 injoignable, 27018 élu PRIMARY, l'écriture L3-005 réussit"))}
{img("c07_retour", "80%", F("27017 relancé : il revient comme SECONDARY"))}
{obs("Avec 4 votants restants sur 5 (majorité = 3), une élection a lieu en quelques secondes : le service d'écriture continue. L'ancien Primary se resynchronise et récupère L3-005.")}
</section>
<section>
<h2 class="nob">Partie 2 – Sharding : distribution des données</h2>
<table class="t"><tr><th>Composant</th><th>Ports</th><th>Replica Set</th></tr>
<tr><td>Config servers (--configsvr)</td><td>28019, 28020, 28021</td><td>configRS</td></tr>
<tr><td>Shard 1 / 2 / 3 (--shardsvr)</td><td>28101–28102 / 28201–28202 / 28301–28302</td><td>shardRS1 / shardRS2 / shardRS3</td></tr>
<tr><td>Routeur mongos</td><td>28000</td><td>– (--configdb configRS/…)</td></tr></table>
{img("c08b_mongod", "80%", F("Config servers et membres des shards (reconstitué)"))}
{img("c08_cfg", "80%", F("configRS : 1 PRIMARY + 2 SECONDARY ; chaque shardRS : 1 PRIMARY + 1 SECONDARY"))}
{code("mongos --configdb configRS/localhost:28019,localhost:28020,localhost:28021 --port 28000" + chr(10) + "mongosh --port 28000" + chr(10) + "sh.addShard('shardRS1/localhost:28101,localhost:28102')   (idem shardRS2, shardRS3)")}
{img("c09_addshard", "80%", F("sh.addShard() : shardAdded"))}
{img("c10_status", "80%", F("sh.status() : les 3 shards connus de mongos"))}
<h3>Données, shard key et chunks</h3>
{img("c11_load", "88%", F("30 000 documents, index sur matricule puis shardCollection"))}
{obs("La collection contient déjà des données : <code>sh.shardCollection</code> exige un index sur la shard key, d'où <code>createIndex({{matricule:1}})</code> (ajouté par rapport à l'énoncé).")}
{code("sh.splitAt('universite.etudiants',{matricule:10000})" + chr(10) + "sh.splitAt('universite.etudiants',{matricule:20000})" + chr(10) + "sh.moveChunk('universite.etudiants',{matricule:15000},'shardRS2')" + chr(10) + "sh.moveChunk('universite.etudiants',{matricule:25000},'shardRS3')")}
{obs("Le balancer ne déplace pas de chunks pour un volume aussi faible : les deux <code>moveChunk</code> (ajoutés) placent un chunk par shard.")}
{img("c12_chunks", "100%", F("sh.status() : 3 chunks, MinKey–10000 sur shardRS1, 10000–20000 sur shardRS2, 20000–MaxKey sur shardRS3"))}
{img("c13_distrib", "62%", F("getShardDistribution() : environ 10 000 documents (33,33 %) par shard"))}
<h3>Routage des requêtes et explain()</h3>
{img("c14_routage", "80%", F("Requêtes avec et sans shard key"))}
{img("c15_explain", "88%", F("explain : SINGLE_SHARD (1 document examiné) contre SHARD_MERGE sur 3 shards (30 000 examinés)"))}
{obs("Avec matricule, mongos connaît le chunk concerné et n'interroge qu'un shard. Sans matricule, la requête est diffusée à tous les shards puis fusionnée.")}
<h3>Panne d'un shard à deux membres</h3>
{img("c16_panne", "100%", F("28101 arrêté : 28102 reste SECONDARY, les opérations sur la plage de shardRS1 échouent"))}
{img("c17_retour", "80%", F("Après redémarrage : shardRS1 a de nouveau un PRIMARY"))}
{obs("Le survivant n'a qu'1 vote sur 2 : pas de majorité, donc pas d'élection. Les données de shardRS3 restent accessibles, celles de shardRS1 non. Il faut 3 membres votants par shard en production.")}
</section>
<section>
<h2 class="nob">Réponses aux questions</h2>
<p class="q">1. Différence entre Primary et Secondary ?</p><p>Le <b>Primary</b> est le seul membre qui accepte les écritures (isWritablePrimary: true). Les <b>Secondary</b> conservent une copie des données en rejouant l'oplog du Primary ; ils peuvent servir des lectures (secondaryOk / readPreference) et remplacer le Primary lors d'une élection.</p>
<p class="q">2. Rôle de l'Arbiter ?</p><p>Il vote lors des élections sans stocker de données. Il permet d'obtenir un nombre impair de votants à moindre coût (ici 5 votants : majorité à 3).</p>
<p class="q">3. Que se passe-t-il lorsque le Primary tombe ?</p><p>Les autres membres ne reçoivent plus ses battements de cœur et déclenchent une élection. Un Secondary obtenant la majorité devient Primary (ici 27018) et les écritures reprennent. L'ancien Primary, relancé, revient comme Secondary et se resynchronise.</p>
<p class="q">4. Rôle de l'oplog ?</p><p>Collection plafonnée <code>local.oplog.rs</code> qui journalise chaque écriture du Primary sous une forme rejouable. Les Secondary la lisent pour se tenir à jour ; elle sert aussi à rattraper un membre revenu après une panne.</p>
<p class="q">5. Pourquoi chaque mongod a-t-il un dbpath différent ?</p><p>Chaque processus verrouille et écrit ses propres fichiers (données, journal, mongod.lock). Deux mongod sur le même dossier se corrompraient ou refuseraient de démarrer ; de même chaque processus a son propre port.</p>
<p class="q">6. Différence entre shard et chunk ?</p><p>Un <b>shard</b> est un serveur (ici un Replica Set) qui stocke une partie des données. Un <b>chunk</b> est une plage contiguë de valeurs de la shard key (ex. matricule 10000 à 20000) : c'est l'unité de répartition et de migration entre shards.</p>
<p class="q">7. Rôle de mongos ?</p><p>Routeur et point d'entrée unique du cluster : il reçoit les requêtes des clients, consulte la table des chunks et les envoie au(x) shard(s) concerné(s), puis fusionne les résultats.</p>
<p class="q">8. Rôle des Config Servers ?</p><p>Ils stockent les métadonnées du cluster (liste des shards, collections shardées, chunks et leur emplacement). Ils forment un Replica Set (configRS) pour rester disponibles.</p>
<p class="q">9. Pourquoi la shard key est-elle importante ?</p><p>Elle détermine la répartition des données et la possibilité de cibler les requêtes. Une clé à faible cardinalité ou monotone peut déséquilibrer le cluster ou concentrer les écritures sur un shard ; elle ne se change pas facilement ensuite.</p>
<p class="q">10. Requête avec ou sans matricule ?</p><p>Avec matricule (shard key), mongos cible un seul shard : SINGLE_SHARD, 1 document examiné. Sans matricule, il interroge tous les shards (SHARD_MERGE) et 30 000 documents sont examinés.</p>
<p class="q">11. Complémentarité réplication / sharding ?</p><p>Le sharding répartit les données et la charge sur plusieurs shards (montée en charge) ; la réplication, à l'intérieur de chaque shard et des config servers, garde plusieurs copies pour survivre aux pannes (haute disponibilité). Le test de panne montre qu'un shard mal répliqué devient le point faible du cluster.</p>
<h2>Conclusion</h2><p>Le Replica Set rs0 a été construit, la réplication et l'oplog observés, et le failover vérifié : 27018 élu Primary, écriture maintenue. Le cluster shardé (configRS, 3 shards, mongos) répartit 30 000 étudiants en trois chunks d'environ 10 000 documents. Les requêtes sur la shard key sont ciblées, les autres sont diffusées. Le test de panne illustre la règle de la majorité : un shard à deux membres ne survit pas à la perte de son Primary.</p>
</section>"""

body = re.sub(r'(<h3>.*?</h3>\s*(?:<p>.*?</p>\s*)?(?:<pre.*?</pre>\s*)?<figure>.*?</figure>)', r'<div style="break-inside:avoid">\1</div>', body, flags=re.S)
src = open("/home/claude/tp1/gen/cr_build.py").read()
CSS = src.split('CSS = """')[1].split('"""')[0] + " section.cover + section{page-break-before:always}"
FONTCSS = src.split('FONTCSS = f"""')[1].split('"""')[0].replace("{{", "{").replace("}}", "}")
H = B / "cr3.html"
H.write_text(f"<!doctype html><html lang=fr><head><meta charset=utf-8><style>{FONTCSS}{CSS}</style></head><body>{body}</body></html>")
foot = '<div style="width:100%;font-size:7.5pt;color:#6b7a84;padding:0 16mm;display:flex;justify-content:space-between;font-family:sans-serif"><span>TP 3 – Haute disponibilité et sharding · Youssef Belghith · RSI31</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(); pg.goto(H.as_uri()); pg.wait_for_timeout(500)
    pg.pdf(path=str(OUT), format="A4", print_background=True, display_header_footer=True, header_template="<div></div>", footer_template=foot,
           margin={"top": "16mm", "bottom": "18mm", "left": "16mm", "right": "16mm"})
    b.close()
print(OUT, OUT.stat().st_size // 1024, "Ko")
