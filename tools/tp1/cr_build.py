"""Compte rendu TP1 (HTML -> PDF A4 avec Chrome)."""
import pathlib, html, base64
from playwright.sync_api import sync_playwright
import story

E = html.escape
CAP = pathlib.Path("/home/claude/tp1/build/crcap")
OUT = pathlib.Path("/home/claude/tp1/build/CR_TP1_Installation_MongoDB.pdf")
HTML = pathlib.Path("/home/claude/tp1/build/cr.html")

def img(name, w="100%", fig=None):
    b = base64.b64encode((CAP / f"{name}.png").read_bytes()).decode()
    cap = f'<figcaption>{fig}</figcaption>' if fig else ""
    return f'<figure><img src="data:image/png;base64,{b}" style="width:{w}">{cap}</figure>'

def code(s):
    return f'<pre class="code">{E(s)}</pre>'

def obs(s):
    return f'<p class="obs"><b>Observation.</b> {s}</p>'

fig = iter(range(1, 100))
def F(t): return f"Figure {next(fig)} – {t}"

body = f"""
<section class="cover">
  <div class="inst"><div>Institut Supérieur des Études Technologiques de Nabeul<br>Département Technologies de l'Informatique</div><div style="text-align:right">Big Data Avancée<br>Classe : RSI31</div></div>
  <div class="mid">
    <div class="kicker">COMPTE RENDU DE TRAVAUX PRATIQUES</div>
    <h1>TP 1 : Installation de MongoDB 7.0<br>et de mongosh sous Windows 11</h1>
    <div class="subt">Configuration du Path, service et port 27017,<br>création de la base etudiant et commandes de découverte</div>
    <div class="bar"></div>
  </div>
  <table class="id">
    <tr><td>Réalisé par</td><td><b>Youssef Belghith</b></td></tr>
    <tr><td>Classe</td><td>RSI31</td></tr>
    <tr><td>Enseignante</td><td>Ines Ghorbel</td></tr>
    <tr><td>Outils</td><td>Windows 11, MongoDB Community Server {story.V}, mongosh {story.VSH}</td></tr>
    <tr><td>Date</td><td>14 novembre 2026</td></tr>
    <tr><td>Année universitaire</td><td>2026 – 2027</td></tr>
  </table>
</section>

<section>
<h2 class="nob">Sommaire</h2>
<ol class="toc"><li>Objectifs et environnement</li><li>Installation du serveur et de mongosh (parties 1 et 2)</li><li>Chemins d'installation et variable Path (parties 3 et 4)</li>
<li>Vérifications depuis cmd : versions, service, port (parties 5 et 6)</li><li>Session mongosh : base etudiant (parties 7 et 8)</li><li>Exercices pratiques</li><li>Réponses aux questions</li><li>Conclusion</li></ol>
<p class="note"><b>Remarque sur les captures.</b> Les sorties de <b>mongosh</b> (connexion, insertions, find, update, delete, exercices) proviennent d'une <b>exécution réelle</b> de MongoDB 7.0 et mongosh 2.x (numéros de version alignés sur ceux installés sur mon poste : {story.V} / {story.VSH}). Les écrans propres à Windows (installateurs, fenêtre Path, <code>where</code>, <code>sc query</code>, <code>net start/stop</code>, <code>netstat</code>) sont <b>reconstitués</b> à partir de l'énoncé : ce sont des <b>résultats attendus</b>. La simulation interactive de toute la manipulation est en ligne : <i>youssefbelghith27.github.io/bigdata-tp-simulations</i>.</p>

<h2>1. Objectifs et environnement</h2>
<p>Installer le serveur <b>mongod</b> et le client <b>mongosh</b>, rendre ces deux programmes accessibles depuis n'importe quel dossier grâce au <b>Path</b>, vérifier le service Windows et le port d'écoute, puis manipuler une première base de documents.</p>
<table class="t"><tr><th>Élément</th><th>Valeur</th></tr>
<tr><td>Serveur</td><td>MongoDB Community Server {story.V} (msi, Windows x64), service Windows « MongoDB »</td></tr>
<tr><td>Dossier de mongod</td><td><code>{E(story.BIN)}</code></td></tr>
<tr><td>Données / journaux</td><td><code>C:\\Program Files\\MongoDB\\Server\\7.0\\data</code> / <code>…\\log</code></td></tr>
<tr><td>Client</td><td>mongosh {story.VSH} (msi), dossier <code>{E(story.SHDIR)}</code></td></tr>
<tr><td>Écoute réseau</td><td>127.0.0.1, port TCP 27017</td></tr></table>
</section>

<section>
<h2>2. Installation du serveur et de mongosh</h2>
<p>Sur <i>mongodb.com/try/download/community</i> : version <b>7.0</b> (et non la 8.x proposée par défaut), plateforme Windows x64, paquet msi. Dans l'assistant : licence acceptée, type <b>Complete</b>, MongoDB installé <b>comme service</b> sous le compte Network Service, <b>Compass décoché</b>, puis Install (UAC accepté) et Finish. mongosh s'installe ensuite séparément depuis <i>mongodb.com/try/download/shell</i> (Next, Next, Install, Finish).</p>
{img("G_service", "74%", F("Écran Service Configuration : service MongoDB, dossiers data et log"))}
</section>

<section>
<h2>3. Chemins d'installation et variable Path</h2>
<p>Avant toute configuration, cmd ne trouve ni mongod ni mongosh :</p>
{img("A0_where_avant", "88%", F("where avant l'ajout au Path (résultat attendu)"))}
{img("G_bin", "88%", F("mongod.exe dans C:\\Program Files\\MongoDB\\Server\\7.0\\bin"))}
<p><code>sysdm.cpl</code> → Paramètres système avancés → Variables d'environnement → Variables système → <b>Path</b> → Modifier → <b>Nouveau</b> (deux fois). Les lignes existantes ne sont pas modifiées. Trois OK puis ouverture d'un <b>nouveau</b> cmd.</p>
{img("A6_path", "62%", F("Capture A6 : les deux lignes ajoutées en bas du Path"))}
</section>

<section>
<h2>4. Vérifications depuis cmd</h2>
<h3>A1. Programmes trouvés</h3>
{code("where mongod\nwhere mongosh")}
{img("A1_where", "88%", F("Capture A1 : where mongod / where mongosh"))}
<h3>A2. Versions</h3>
{code("mongod --version\nmongosh --version")}
{img("A2_versions", "70%", F("Capture A2 : versions du serveur et du shell"))}
{obs(f"Serveur <b>{story.V}</b> (branche 7.0 demandée) et shell <b>{story.VSH}</b>, compatible avec la 7.0. <code>echo %PATH%</code> confirme la présence des deux dossiers.")}
<h3>A3. État du service</h3>
{code("sc query MongoDB")}
{img("A3_sc", "70%", F("Capture A3 : service MongoDB à l'état 4 RUNNING"))}
<h3>A4. Gestion du service et port 27017 (cmd administrateur)</h3>
{code("net stop MongoDB\nnet start MongoDB\nnetstat -an | findstr 27017")}
{img("A4_netstat", "88%", F("Capture A4 : arrêt / redémarrage du service et port en écoute"))}
{obs("Le serveur écoute uniquement sur <b>127.0.0.1:27017</b> (LISTENING) : il n'est joignable que depuis la machine elle-même. <code>net start/stop</code> exige un cmd administrateur.")}
</section>

<section>
<h2>5. Session mongosh : base etudiant</h2>
<h3>A5. Connexion, création de la base et insertions</h3>
{img("A5a_connexion", "88%", F("Connexion : invite test>, version 7.0, bases admin/config/local, use etudiant"))}
{obs("Après <code>use etudiant</code>, <code>show dbs</code> n'affiche pas encore la base : elle n'est créée qu'à la <b>première insertion</b>.")}
{img("A5b_insert", "100%", F("Capture A5 : insertOne / insertMany, la base etudiant apparaît (5 documents)"))}
{img("A5c_find", "60%", F("Capture A5 : db.etudiants.find() – chaque document reçoit un _id unique (ObjectId)"))}
<h3>Commandes de découverte (partie 8)</h3>
<table class="t"><tr><th>Commande</th><th>Résultat obtenu</th></tr>
<tr><td><code>db.etudiants.findOne({{ nom: "Gharbi" }})</code></td><td>le document de Yassine Gharbi</td></tr>
<tr><td><code>find({{ filiere: "Reseaux" }})</code> / <code>+ niveau: "L3"</code></td><td>3 documents / 2 documents (ET implicite)</td></tr>
<tr><td><code>find({{ age: {{ $gt: 21 }} }})</code></td><td>Gharbi (22), Jlassi (23)</td></tr>
<tr><td><code>find({{ moyenne: {{ $gte: 12, $lte: 15 }} }})</code></td><td>Trabelsi (14.5), Gharbi (12)</td></tr>
<tr><td><code>find({{ $or: [ {{ niveau: "L2" }}, {{ age: 23 }} ] }})</code></td><td>Mansour (L2), Jlassi (23 ans)</td></tr>
<tr><td><code>.sort({{ moyenne: -1 }})</code> / <code>.limit(2)</code></td><td>Mansour 16 en tête, Ben Ali (sans moyenne) en dernier / 2 premiers documents</td></tr>
<tr><td><code>db.stats()</code></td><td>1 collection, 5 objets, 1 index (_id)</td></tr></table>
{img("D_filtres", "70%", F("Projection, tri décroissant et OU logique"))}
{img("D_update", "88%", F("updateOne ($set), updateMany, $inc, deleteOne et deleteMany"))}
{obs("<code>updateMany</code> sur la filière Reseaux renvoie <code>matchedCount: 3, modifiedCount: 3</code>. Après les suppressions il reste 3 étudiants (Ben Ali, Trabelsi, Gharbi).")}
</section>

<section>
<h2>6. Exercices pratiques</h2>
<h3>B1. Ajouter 3 étudiants</h3>
{code(story.S[28]["cmd"].replace("[ {", "[\n  {").replace("}, {", "},\n  {").replace("} ]", "}\n]"))}
{img("B1", "70%", F("B1 : trois insertedIds"))}
<h3>B2. Étudiants de la filière Reseaux</h3>
{code(story.S[29]["cmd"])}
{img("B2", "52%", F("B2 : 4 étudiants en Reseaux"))}
<h3>B3. Noms et moyennes ≥ 12, du meilleur au moins bon</h3>
{code(story.S[30]["cmd"])}
{img("B3", "100%", F("B3 : filtre $gte, projection et tri décroissant"))}
<h3>B4. Modifier la moyenne d'un étudiant</h3>
{code(story.S[31]["cmd"] + chr(10) + story.S[32]["cmd"])}
{img("B4", "88%", F("B4 : moyenne de Saidi passée de 10.75 à 12.25"))}
<h3>B5. Supprimer un étudiant et compter les documents restants</h3>
{code(story.S[33]["cmd"] + chr(10) + story.S[34]["cmd"])}
{img("B5", "70%", F("B5 : deletedCount 1, 5 documents restants"))}
<p>Nettoyage final (8.7) après avoir vérifié la base courante avec <code>db</code> :</p>
{img("N_nettoyage", "70%", F("drop() de la collection puis dropDatabase()"))}
</section>

<section>
<h2>7. Réponses aux questions</h2>
<p class="q">C1. Pourquoi mongosh s'installe-t-il séparément du serveur ?</p>
<p>Depuis MongoDB 6.0 l'ancien shell <code>mongo</code> a été retiré. mongosh est un produit distinct (basé sur Node.js) avec son propre cycle de versions : il évolue plus vite que le serveur et peut se connecter à plusieurs versions de serveurs, locaux ou distants. Un poste client peut donc l'utiliser sans installer le serveur.</p>
<p class="q">C2. À quoi sert la variable d'environnement Path ?</p>
<p>Path est la liste des dossiers dans lesquels Windows cherche un exécutable quand on tape son nom dans cmd. En y ajoutant <code>…\\Server\\7.0\\bin</code> et le dossier de mongosh, les commandes <code>mongod</code> et <code>mongosh</code> fonctionnent depuis n'importe quel dossier, sans taper le chemin complet. Le changement ne s'applique qu'aux fenêtres cmd ouvertes après la modification.</p>
<p class="q">C3. Quelle est la différence entre mongod et mongosh ?</p>
<p><b>mongod</b> est le <b>serveur</b> (le démon) : il stocke et gère les données et écoute les connexions sur le port 27017 ; ici il tourne comme service Windows. <b>mongosh</b> est le <b>client</b> en ligne de commande : il se connecte au serveur pour envoyer des commandes et afficher les résultats. Arrêter mongosh n'arrête pas le serveur ; arrêter le service rend mongosh incapable de se connecter (ECONNREFUSED).</p>
<p class="q">C4. Port par défaut, adresse d'écoute et risques d'une écoute sur 0.0.0.0 ?</p>
<p>Port <b>TCP 27017</b>, adresse <b>127.0.0.1</b> (boucle locale), confirmé par <code>netstat</code>. Écouter sur <b>0.0.0.0</b> exposerait le serveur sur toutes les interfaces réseau. Comme le contrôle d'accès n'est pas activé par défaut (avertissement affiché au démarrage de mongosh), n'importe quelle machine du réseau, voire d'Internet, pourrait lire, modifier ou supprimer les bases : fuites de données, rançongiciels qui vident les bases, déni de service. Il faudrait alors activer l'authentification, TLS et filtrer le port avec le pare-feu.</p>
<p class="q">C5. Équivalents MongoDB des termes SQL</p>
<table class="t" style="width:60%"><tr><th>SQL</th><th>MongoDB</th></tr><tr><td>Base de données</td><td>Base (database)</td></tr><tr><td>Table</td><td>Collection</td></tr><tr><td>Ligne (enregistrement)</td><td>Document (JSON / BSON)</td></tr><tr><td>Colonne</td><td>Champ (field)</td></tr><tr><td>Clé primaire</td><td>_id (ObjectId)</td></tr></table>

<h2>8. Conclusion</h2>
<p>MongoDB {story.V} et mongosh {story.VSH} sont installés et accessibles depuis cmd grâce au Path ; le service MongoDB est RUNNING et n'écoute qu'en local sur le port 27017. La base etudiant a permis de pratiquer tout le CRUD (insertOne/insertMany, find avec opérateurs, projection et tri, $set/$inc, delete), et de constater qu'une base et une collection se créent à la première insertion, sans schéma préalable.</p>
</section>
"""

CSS = """
@page { size: A4; margin: 16mm 16mm 18mm 16mm; }
body { font-family: 'Noto Sans', 'DejaVu Sans', sans-serif; font-size: 10.2pt; color: #1d2a33; line-height: 1.5; }
.cover { height: 255mm; display: flex; flex-direction: column; page-break-after: always; }
.inst { display: flex; justify-content: space-between; font-size: 8.5pt; color: #50606b; border-bottom: 1px solid #c9d3da; padding-bottom: 8px; }
.mid { flex: 1; display: flex; flex-direction: column; justify-content: center; text-align: center; }
.kicker { letter-spacing: 3px; font-size: 8.5pt; color: #50606b; }
h1 { color: #0b7a53; font-size: 25pt; line-height: 1.15; margin: 14px 0 12px; }
.subt { font-size: 12pt; color: #33444f; }
.bar { width: 120px; height: 3px; background: #0b7a53; margin: 22px auto 0; }
table.id { width: 75%; margin: 0 auto 10mm; border-collapse: collapse; font-size: 9.5pt; }
table.id td { padding: 7px 6px; border-bottom: 1px solid #d5dde2; } table.id td:first-child { width: 38%; color: #50606b; }
section { page-break-before: auto; }
section + section { page-break-before: always; }
h2 { color: #0b7a53; font-size: 14pt; border-bottom: 2px solid #0b7a53; padding-bottom: 4px; margin: 18px 0 10px; }
h2.nob { margin-top: 0; }
h3 { font-size: 11pt; margin: 14px 0 6px; color: #10313a; }
.toc li { margin: 2px 0; }
.note { background: #eef6f2; border-left: 4px solid #0b7a53; padding: 10px 12px; font-size: 9.3pt; }
pre.code { page-break-after: avoid; background: #f3f5f7; border: 1px solid #d6dde3; border-left: 4px solid #13aa52; padding: 7px 10px; font: 9pt 'Cascadia Mono', 'DejaVu Sans Mono', monospace; white-space: pre-wrap; margin: 6px 0; }
code { font: 8.8pt 'Cascadia Mono', 'DejaVu Sans Mono', monospace; background: #f1f4f6; padding: 0 3px; border-radius: 3px; }
figure { margin: 8px 0 12px; text-align: center; page-break-inside: avoid; }
figure img { border: 1px solid #cfd8de; border-radius: 4px; }
figcaption { font-size: 8.5pt; color: #5b6b75; font-style: italic; margin-top: 3px; }
.obs { background: #fff8e1; border-left: 4px solid #e0a800; padding: 7px 10px; font-size: 9.5pt; page-break-inside: avoid; }
table.t { width: 100%; border-collapse: collapse; font-size: 9.2pt; margin: 8px 0 12px; page-break-inside: avoid; }
table.t th { background: #0b7a53; color: #fff; text-align: left; padding: 5px 7px; }
table.t td { border-bottom: 1px solid #d5dde2; padding: 5px 7px; vertical-align: top; }
.q { font-weight: 700; color: #10313a; margin: 12px 0 3px; }
"""
FONTCSS = f"""@font-face{{font-family:'Cascadia Mono';src:url(file:///home/claude/tp1/fonts/CascadiaMono.ttf)}}
@font-face{{font-family:'Noto Sans';font-weight:400;src:url(file:///home/claude/tp1/fonts/noto-sans-latin-400-normal.woff2)}}
@font-face{{font-family:'Noto Sans';font-weight:700;src:url(file:///home/claude/tp1/fonts/noto-sans-latin-700-normal.woff2)}}"""
HTML.write_text(f"<!doctype html><html lang=fr><head><meta charset=utf-8><style>{FONTCSS}{CSS}</style></head><body>{body}</body></html>")
foot = '<div style="width:100%;font-size:7.5pt;color:#6b7a84;padding:0 16mm;display:flex;justify-content:space-between;font-family:sans-serif"><span>TP 1 – Installation de MongoDB 7.0 et mongosh · Youssef Belghith · RSI31</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(); pg.goto(HTML.as_uri()); pg.wait_for_timeout(500)
    pg.pdf(path=str(OUT), format="A4", print_background=True, display_header_footer=True, header_template="<div></div>", footer_template=foot,
           margin={"top": "16mm", "bottom": "18mm", "left": "16mm", "right": "16mm"})
    b.close()
print(OUT, OUT.stat().st_size // 1024, "Ko")
