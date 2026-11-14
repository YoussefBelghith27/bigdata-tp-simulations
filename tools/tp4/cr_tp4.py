"""Compte rendu TP4 Cassandra (captures partielles + réponses) en PDF A4."""
import pathlib, html, base64, re
from playwright.sync_api import sync_playwright
from render import Renderer, FONTS
from screens import CSS as SCSS
import story_tp4 as st

E = html.escape
B = pathlib.Path("/home/claude/tp4/build"); D = B / "crcap"; D.mkdir(parents=True, exist_ok=True)
OUT = B / "CR_TP4_Cassandra.pdf"
W = 980; COLS = int((W - 24) // 8.203125)
LOG = st.LOG

def by_cmd(prefix, occ=1):
    n = 0
    for p, c, o, cap in LOG:
        if c.startswith(prefix):
            n += 1
            if n == occ: return (p, c, o)
    raise KeyError(prefix)
def by_cap(cap): return next((p, c, o) for p, c, o, k in LOG if k == cap)

def wrapl(s):
    r = []
    while len(s) > COLS: r.append(s[:COLS]); s = s[COLS:]
    r.append(s); return r
def block(title, entries, maxl=40):
    lines = []
    for prompt, cmd, o in entries:
        for j, l in enumerate(cmd.split("\n")):
            for k, p in enumerate(wrapl((prompt if j == 0 else ("   ... " if prompt.startswith("cqlsh") else "")) + l)):
                lines.append((E(p[:len(prompt)]) + f'<span class="w">{E(p[len(prompt):])}</span>') if (j == 0 and k == 0) else f'<span class="w">{E(p)}</span>')
        ol = o.strip("\n").split("\n") if o.strip() else []
        for l in ol[:maxl]:
            for p in wrapl(l): lines.append(E(p))
        if len(ol) > maxl: lines.append(f'<span class="k">… ({len(ol) - maxl} lignes de plus)</span>')
    return f"""<div id="cap" style="width:{W}px;background:#0c0c0c;border-radius:8px;overflow:hidden;border:1px solid #333">
      <div style="height:30px;background:#202020;color:#ddd;font:12px UI;display:flex;align-items:center;padding:0 12px;gap:8px">
      <span style="font:10px MONO;border:1px solid #555;border-radius:2px;padding:0 3px">&gt;_</span>{E(title)}</div>
      <div style="font:14px/18px MONO;color:#ccc;white-space:pre;padding:10px 12px">{"\n".join(lines)}</div></div>"""

PS = "PS ...\\Simulation_Docker> "
def short(e): return (PS if e[0] == st.DIRP else e[0], e[1], e[2])
CAPS = {
 "c1_versions": [by_cap("docker_version")[0:0] or by_cmd("docker --version"), by_cap("docker_version")],
 "c2_up": [by_cap("compose_up"), by_cap("compose_ps")],
 "c3_status": [by_cap("status1")],
 "c4_tables": [by_cmd("CREATE KEYSPACE"), by_cmd("USE "), by_cap("sel987"), by_cap("selventes")],
 "c5_crud": [by_cmd("INSERT INTO livres_par_auteur (id_auteur, isbn, nom_auteur, prenom_auteur, titre)\nVALUES (154"), by_cap("sel154"), by_cmd("UPDATE"), by_cap("update"), by_cmd("DELETE"), by_cap("delete")],
 "c6_vente": [by_cmd("INSERT INTO ventes_par_livre (isbn, date_vente, id_vente, quantite, montant)\nVALUES ('2154889589', '2017-11-20'"), by_cap("vente")],
 "c7_titre": [by_cap("filtering"), by_cmd("SELECT * FROM livres_par_auteur WHERE titre = 'NoSQL' ALLOW"), by_cap("partitre"), by_cap("token")],
 "c8_cluster": [by_cap("status_ks"), by_cap("describe")],
 "c9_logs": [by_cap("logs")],
 "c10_panne": [by_cmd("docker stop"), by_cap("status_dn"), by_cmd("docker start"), by_cap("status_back")],
}
raw = open(st.LOGD + "99_logs_erreur.txt", encoding="utf-8-sig").read().split("\n")
coll = [l[:240] for l in raw if "Token collision" in l or "TokenMetadata.addBootstrapTokens(TokenMetadata.java:378)" in l or "ERROR [GossipStage" in l][:3]
CAPS["c0_collision"] = [(PS, "docker compose logs --tail=60", "\n".join(coll))]

with Renderer() as r:
    for name, ent in CAPS.items():
        ttl = "Windows PowerShell" + (" – cqlsh" if any(e[0].startswith("cqlsh") for e in ent) else "")
        r.pg.set_content(f"<!doctype html><meta charset=utf-8><style>{FONTS}{SCSS}body{{width:auto;height:auto;overflow:visible;background:#fff}}</style>{block(ttl, [short(e) for e in ent])}")
        r.pg.evaluate("document.fonts.ready"); r.pg.wait_for_timeout(50)
        r.pg.locator("#cap").screenshot(path=str(D / f"{name}.png"))

def img(name, w="100%", fig=None):
    b = base64.b64encode((D / f"{name}.png").read_bytes()).decode()
    return f'<figure><img src="data:image/png;base64,{b}" style="width:{w}">' + (f'<figcaption>{fig}</figcaption>' if fig else "") + "</figure>"
def obs(s): return f'<p class="obs"><b>Observation.</b> {s}</p>'
def qa(q, a): return f'<p class="q">{q}</p><p>{a}</p>'
fn = iter(range(1, 50))
def F(t): return f"Figure {next(fn)} – {t}"

body = f"""
<section class="cover">
  <div class="inst"><div>Institut Supérieur des Études Technologiques de Nabeul<br>Département Technologies de l'Informatique</div><div style="text-align:right">Écosystème Big Data avancé<br>Classe : RSI31</div></div>
  <div class="mid"><div class="kicker">COMPTE RENDU DE TRAVAUX PRATIQUES</div>
    <h1>TP 4 : Cassandra<br>CQL, modélisation et cluster à 3 nœuds</h1>
    <div class="subt">Docker Desktop, keyspace RF = 3, tables orientées requêtes,<br>CRUD et observation du cluster</div><div class="bar"></div></div>
  <table class="id"><tr><td>Réalisé par</td><td><b>Youssef Belghith</b></td></tr><tr><td>Classe</td><td>RSI31</td></tr>
    <tr><td>Enseignante</td><td>Ines Ghorbel</td></tr><tr><td>Environnement</td><td>Windows 11, Docker Desktop (WSL 2), Cassandra 4.1</td></tr>
    <tr><td>Date</td><td>14 novembre 2026</td></tr></table>
</section>
<section>
<h2 class="nob">1. Démarrage et vérification du cluster</h2>
<p class="note"><b>Remarque sur les captures.</b> <code>docker --version</code>, <code>docker compose version</code>, <code>docker compose up -d</code> et les journaux viennent de <b>mon poste</b> (dossier <code>Simulation_Docker/logs</code>). Les sorties <code>cqlsh</code> et <code>nodetool</code> sont <b>reconstituées</b> au format exact de Cassandra 4.1 (résultats attendus) ; les tokens Murmur3 sont calculés avec l'algorithme du partitionneur. Simulation interactive : <i>youssefbelghith27.github.io/bigdata-tp-simulations</i>.</p>
{img("c1_versions", "80%", F("Versions de Docker et Docker Compose (mon poste)"))}
{img("c2_up", "100%", F("docker compose up -d (mon poste) puis docker compose ps"))}
{img("c3_status", "100%", F("nodetool status : 3 nœuds UN dans datacenter1, 16 tokens chacun"))}
<h3>Problème rencontré au premier lancement</h3>
{img("c0_collision", "100%", F("Extrait réel des journaux : collision de tokens au bootstrap"))}
{obs("cassandra2 et cassandra3 ont démarré en même temps et ont tiré des tokens en collision (« Bootstrap Token collision »). Solution : démarrer les nœuds un par un, en attendant que chacun soit UN : <code>docker compose up -d cassandra1</code>, puis <code>cassandra2</code>, puis <code>cassandra3</code> (ou <code>docker compose down -v</code> puis relance séquentielle).")}
<h2>2. Analyse de compose.yaml</h2>
{qa("Pourquoi les trois conteneurs doivent-ils partager un réseau Docker ?", "Les nœuds échangent l'état du cluster par gossip (port 7000) et se joignent par leur nom (cassandra1 est le seed). Le réseau bridge <code>cassandra-net</code> leur fournit la connectivité et la résolution DNS des noms ; sans lui, chaque nœud formerait un cluster isolé.")}
{qa("Un nœud seed est-il un nœud maître ?", "Non. Cassandra est pair-à-pair, sans maître : tous les nœuds peuvent coordonner lectures et écritures. Le seed n'est qu'un point de contact pour qu'un nouveau nœud découvre la topologie par gossip.")}
{qa("docker compose down ou down -v ?", "<code>down</code> supprime conteneurs et réseau mais conserve les volumes (les données). <code>down -v</code> supprime aussi les volumes : réinitialisation complète, données effacées.")}
</section>
<section>
<h2 class="nob">3. Keyspace et tables</h2>
{img("c4_tables", "100%", F("Keyspace RF = 3, livres de l'auteur 987 et ventes du livre 2154889589"))}
{qa("À quoi sert un keyspace ? Que signifie RF = 3 ?", "Le keyspace regroupe des tables et fixe leur stratégie de réplication. RF = 3 : chaque partition est stockée sur 3 nœuds du datacenter1, donc ici sur les trois.")}
{qa("Pourquoi RF = 3 ne garantit-il pas la disponibilité ici ?", "Les trois répliques sont des conteneurs sur le même PC : une panne de l'hôte, du disque ou de Docker les arrête toutes en même temps.")}
{qa("livres_par_auteur : clé de partition, clustering, duplication ?", "Clé de partition <code>id_auteur</code> (tous les livres d'un auteur sur les mêmes nœuds), clustering <code>isbn</code> (tri dans la partition). Le nom et le prénom sont dupliqués car CQL ne fait pas de jointure : la table contient tout ce que la requête affiche.")}
{qa("ventes_par_livre : rôle d'isbn, date_vente et id_vente ?", "<code>isbn</code> partitionne : les ventes d'un livre sont lues dans une seule partition. <code>date_vente</code> trie les ventes (DESC : plus récente d'abord) et <code>id_vente</code> distingue deux ventes le même jour, ce qui rend la clé unique.")}
<h2>4. Travail demandé : CRUD et requêtes</h2>
{img("c5_crud", "100%", F("Travaux 1 à 4 : ajout, lecture, mise à jour et suppression du livre 2154889530"))}
{obs("UPDATE et DELETE exigent la clé primaire complète (id_auteur et isbn). En CQL, INSERT et UPDATE sont des « upserts ».")}
{img("c6_vente", "100%", F("Travail 5 : la nouvelle vente apparaît en tête (tri date_vente DESC)"))}
{img("c7_titre", "100%", F("Travaux 6 et 7 : recherche par titre refusée, ALLOW FILTERING, puis table livres_par_titre ; tokens Murmur3"))}
{obs("Le titre n'appartient pas à la clé : Cassandra devrait lire toutes les partitions de tous les nœuds, d'où le refus. ALLOW FILTERING force ce parcours complet (à éviter). La bonne réponse est une table <code>livres_par_titre</code> partitionnée par titre, alimentée en même temps que livres_par_auteur (BATCH).")}
</section>
<section>
<h2 class="nob">5. Observation du cluster et de la réplication</h2>
{img("c8_cluster", "100%", F("nodetool status rsi3_bibliotheque (100 % par nœud) et nodetool describecluster"))}
{img("c9_logs", "100%", F("docker compose logs --tail=50 cassandra2 (extrait réel)"))}
{img("c10_panne", "100%", F("docker stop cassandra3 : état DN, puis retour à UN après docker start"))}
{obs("Pendant la panne, les deux autres répliques continuent de servir les données (un QUORUM de 2 sur 3 reste atteignable). Au retour, cassandra3 rattrape les écritures manquées grâce aux hints.")}
<h2>6. Questions de synthèse</h2>
{qa("Modélisation Cassandra et normalisation relationnelle ?", "En relationnel on normalise puis on joint à la lecture. En Cassandra on dénormalise : une table par requête, données dupliquées, pas de jointure ; on paie en stockage et en écritures pour des lectures sur une seule partition.")}
{qa("Pourquoi partir de la requête attendue ?", "Seules les requêtes qui fournissent la clé de partition (et respectent l'ordre du clustering) sont efficaces. La table doit donc être construite autour de la question posée (ex. livres par auteur, ventes par livre).")}
{qa("Clé primaire, clé de partition, clustering ?", "La clé primaire complète identifie une ligne : <code>((isbn), date_vente, id_vente)</code>. La clé de partition (<code>isbn</code>) choisit les nœuds via le token. Les colonnes de clustering ordonnent et distinguent les lignes dans la partition.")}
{qa("Limites de trois nœuds sur un seul ordinateur ?", "Pas de vraie tolérance aux pannes (même hôte), ressources partagées (mémoire, disque), performances non représentatives et collisions possibles au démarrage simultané (vécu ici).")}
{qa("Contrôles après une migration relationnel vers Cassandra ?", "Comparer les nombres de lignes par table et par clé, vérifier un échantillon de valeurs, les types (date, decimal), la cohérence des tables dupliquées, que chaque requête métier fonctionne sans ALLOW FILTERING, et la réplication (nodetool status, RF).")}
<h2>Conclusion</h2>
<p>Le cluster ClusterRSI3 à 3 nœuds a été démarré sous Docker (après correction de la collision de tokens par un démarrage séquentiel). Le keyspace rsi3_bibliotheque réplique chaque partition sur les 3 nœuds. Les tables sont conçues pour leurs requêtes : partition id_auteur ou isbn, clustering isbn ou date_vente/id_vente. La recherche par titre a demandé une table dédiée. L'arrêt de cassandra3 n'a pas interrompu le service, mais les trois nœuds partageant le même PC, le montage illustre la réplication sans protéger contre la panne de l'hôte.</p>
</section>"""
body = re.sub(r'(<h3>.*?</h3>\s*<figure>.*?</figure>)', r'<div style="break-inside:avoid">\1</div>', body, flags=re.S)
src = open("/home/claude/tp1/gen/cr_build.py").read()
CSS = src.split('CSS = """')[1].split('"""')[0] + " section.cover + section{page-break-before:always}"
FONTCSS = src.split('FONTCSS = f"""')[1].split('"""')[0].replace("{{", "{").replace("}}", "}")
H = B / "cr4.html"
H.write_text(f"<!doctype html><html lang=fr><head><meta charset=utf-8><style>{FONTCSS}{CSS}</style></head><body>{body}</body></html>")
foot = '<div style="width:100%;font-size:7.5pt;color:#6b7a84;padding:0 16mm;display:flex;justify-content:space-between;font-family:sans-serif"><span>TP 4 – Cassandra · Youssef Belghith · RSI31</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(); pg.goto(H.as_uri()); pg.wait_for_timeout(500)
    pg.pdf(path=str(OUT), format="A4", print_background=True, display_header_footer=True, header_template="<div></div>", footer_template=foot,
           margin={"top": "16mm", "bottom": "18mm", "left": "16mm", "right": "16mm"})
    b.close()
print(OUT, OUT.stat().st_size // 1024, "Ko")
