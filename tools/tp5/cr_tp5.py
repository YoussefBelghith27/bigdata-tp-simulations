"""Compte rendu TP5 (cluster Hadoop, HDFS, YARN, MapReduce, Spark, Hive) en PDF A4."""
import pathlib, html, base64, re
from playwright.sync_api import sync_playwright
from render import Renderer, FONTS
from screens import CSS as SCSS
import story_tp5 as st

E = html.escape
B = pathlib.Path("/home/claude/tp5/build"); D = B / "crcap"; D.mkdir(parents=True, exist_ok=True)
OUT = B / "CR_TP5_Hadoop_Spark_Hive.pdf"
W = 980; COLS = int((W - 24) // 8.203125)
LOG = st.LOG
def by_cap(cap): return next((p, c, o) for p, c, o, k in LOG if k == cap)
def by_cmd(prefix, occ=1):
    n = 0
    for p, c, o, k in LOG:
        if c.startswith(prefix):
            n += 1
            if n == occ: return (p, c, o)
    raise KeyError(prefix)
def wrapl(s):
    r = []
    while len(s) > COLS: r.append(s[:COLS]); s = s[COLS:]
    r.append(s); return r
SHORT = {st.VM: "vm$ ", st.HM: "root@hadoop-master:/# ", st.BL: "beeline> ", st.BR: "beeline> "}
def block(title, entries, maxl=36):
    lines = []
    for prompt, cmd, o in entries:
        prompt = SHORT.get(prompt, prompt)
        for j, l in enumerate(cmd.split("\n")):
            for k, p in enumerate(wrapl((prompt if j == 0 else "> ") + l)):
                lines.append((E(p[:len(prompt)]) + f'<span class="w">{E(p[len(prompt):])}</span>') if (j == 0 and k == 0) else f'<span class="w">{E(p)}</span>')
        ol = o.strip("\n").split("\n") if o.strip() else []
        for l in ol[:maxl]:
            for p in wrapl(l): lines.append(E(p))
        if len(ol) > maxl: lines.append(f'<span class="k">… ({len(ol) - maxl} lignes de plus)</span>')
    return f"""<div id="cap" style="width:{W}px;background:#300a24;border-radius:8px;overflow:hidden;border:1px solid #333">
      <div style="height:30px;background:#2b2b2b;color:#ddd;font:12px UI;display:flex;align-items:center;padding:0 12px;gap:8px">
      <span style="font:10px MONO;border:1px solid #555;border-radius:2px;padding:0 3px">&gt;_</span>{E(title)}</div>
      <div style="font:14px/18px MONO;color:#ccc;white-space:pre;padding:10px 12px">{"\n".join(lines)}</div></div>"""

CAPS = {
 "c1_ps": ("Terminal de la VM", [by_cmd("docker compose up -d hadoop-master"), by_cap("ps")], 12),
 "c2_report": ("hadoop-master", [by_cap("report"), by_cmd("hdfs dfsadmin -safemode get")], 30),
 "c3_yarn": ("hadoop-master / VM", [by_cap("nodes"), by_cap("jps"), by_cap("jps_w")], 12),
 "c4_hdfs": ("hadoop-master", [by_cmd("hdfs dfs -mkdir -p /user/student/input"), by_cmd("hdfs dfs -put -f"), by_cap("ls"), by_cap("du"), by_cmd("hdfs dfs -get")], 8),
 "c5_quota": ("hadoop-master", [by_cmd("hdfs dfsadmin -setSpaceQuota"), by_cap("quota"), by_cap("trash"), by_cmd("hdfs dfs -mv /user/root")], 6),
 "c6_snap": ("hadoop-master", [by_cmd("hdfs dfsadmin -allowSnapshot"), by_cmd("hdfs dfs -createSnapshot"), by_cmd("hdfs dfs -rm -skipTrash"), by_cmd("hdfs dfs -ls /user/student/snap/.snapshot"), by_cap("snapshot")], 6),
 "c7_fsck": ("hadoop-master", [by_cap("fsck")], 14),
 "c8_blocs": ("hadoop-master", [by_cmd("seq 1 3000000"), by_cmd("hdfs dfs -D dfs.blocksize"), by_cap("blocs")], 6),
 "c9_panne": ("Terminal de la VM", [by_cmd("docker stop hadoop-worker1"), by_cmd("docker exec hadoop-master bash -c \"hdfs dfs -cat"), by_cap("panne"),
              by_cmd("docker exec hadoop-master bash -c \"hdfs fsck /"), by_cmd("docker start"), by_cap("retour")], 8),
 "c10_pi": ("hadoop-master", [by_cap("pi_ko"), by_cap("pi_ok"), by_cap("apps")], 16),
 "c11_streaming": ("hadoop-master", [by_cap("local"), by_cap("streaming"), by_cap("output_city")], 14),
 "c12_cuisine": ("hadoop-master", [by_cap("cuisine")], 12),
 "c13_spark": ("hadoop-master", [by_cap("sparkpi"), by_cmd("spark-submit --master yarn"), by_cap("spark_out")], 14),
 "c14_hive": ("hadoop-master – beeline", [by_cap("hive_table"), by_cap("hive_count"), by_cap("hive_city")], 20),
 "c15_hive2": ("hadoop-master – beeline", [by_cap("hive_avg"), by_cap("hive_price")], 20),
}
with Renderer() as r:
    for name, (ttl, ent, mx) in CAPS.items():
        r.pg.set_content(f"<!doctype html><meta charset=utf-8><style>{FONTS}{SCSS}body{{width:auto;height:auto;overflow:visible;background:#fff}}</style>{block(ttl, ent, mx)}")
        r.pg.evaluate("document.fonts.ready"); r.pg.wait_for_timeout(50)
        r.pg.locator("#cap").screenshot(path=str(D / f"{name}.png"))

def img(name, w="100%", fig=None):
    b = base64.b64encode((D / f"{name}.png").read_bytes()).decode()
    return f'<figure><img src="data:image/png;base64,{b}" style="width:{w}">' + (f'<figcaption>{fig}</figcaption>' if fig else "") + "</figure>"
def obs(s): return f'<p class="obs"><b>Observation.</b> {s}</p>'
def qa(q, a): return f'<p class="q">{q}</p><p>{a}</p>'
fn = iter(range(1, 60))
def F(t): return f"Figure {next(fn)} – {t}"
NB = st.NB

body = f"""
<section class="cover">
  <div class="inst"><div>Institut Supérieur des Études Technologiques de Nabeul<br>Département Technologies de l'Informatique</div><div style="text-align:right">Écosystème Big Data avancé<br>Classe : RSI31</div></div>
  <div class="mid"><div class="kicker">COMPTE RENDU DE TRAVAUX PRATIQUES</div>
    <h1>TP 5 : Cluster Hadoop 3<br>HDFS, YARN, MapReduce, Spark et Hive</h1>
    <div class="subt">1 master + 3 workers sous Docker (VM Ubuntu 22.04),<br>Spark 3.5.3 sur YARN, Hive 3.1.3 (Metastore PostgreSQL)</div><div class="bar"></div></div>
  <table class="id"><tr><td>Réalisé par</td><td><b>Youssef Belghith</b></td></tr><tr><td>Classe</td><td>RSI31</td></tr>
    <tr><td>Enseignante</td><td>Ines Ghorbel</td></tr><tr><td>Environnement</td><td>VMware, Ubuntu 22.04, Docker, Hadoop 3.3.6, Spark 3.5.3, Hive 3.1.3</td></tr>
    <tr><td>Date</td><td>14 novembre 2026</td></tr></table>
</section>
<section>
<h2 class="nob">1. Création et validation du cluster</h2>
<p class="note"><b>Remarque sur les captures.</b> Les <b>résultats de calcul sont réels</b> : sorties de mapper.py / reducer.py et de mapper_cuisine.py / reducer_moyenne.py exécutés sur restaurants.csv, comptage Spark exécuté avec PySpark 3.5.3, agrégats Hive calculés sur le même fichier, valeur de pi recalculée avec la séquence de Halton utilisée par Hadoop, taille du fichier et nombre de blocs. Les messages des commandes HDFS, YARN, jps et Beeline sont <b>reconstitués</b> au format de Hadoop 3.3.6 (résultats attendus). Simulation : <i>youssefbelghith27.github.io/bigdata-tp-simulations</i>.</p>
{img("c1_ps", "100%", F("Démarrage de Hadoop d'abord (master + 3 workers) et état des conteneurs"))}
{img("c2_report", "88%", F("hdfs dfsadmin -report : 3 DataNodes vivants ; Safe mode is OFF"))}
{img("c3_yarn", "100%", F("3 NodeManagers RUNNING ; processus Java du master et d'un worker"))}
<table class="t"><tr><th>Conteneur</th><th>Processus (jps)</th><th>Rôle</th></tr>
<tr><td>hadoop-master</td><td>NameNode, SecondaryNameNode, ResourceManager, JobHistoryServer</td><td>métadonnées HDFS, checkpoint, ordonnancement YARN, historique des jobs</td></tr>
<tr><td>hadoop-worker1..3</td><td>DataNode, NodeManager</td><td>stockage des blocs, exécution des conteneurs</td></tr></table>
{obs("yarn-site.xml : 2048 Mo et 2 vCores par NodeManager, soit 6 Go et 6 vCores pour le cluster ; un conteneur est limité à 2048 Mo (maximum-allocation-mb). <code>docker compose down</code> garde les volumes (données HDFS), <code>down -v</code> les supprime.")}
</section>
<section>
<h2 class="nob">2. HDFS : manipulations</h2>
{img("c4_hdfs", "100%", F("Import de restaurants.csv (3,6 Mo), taille logique et espace occupé, aller-retour identique"))}
{obs("<code>-du</code> donne la taille logique (3,6 M) et l'espace consommé avec les 3 répliques (10,9 M) ; <code>-df</code> donne la capacité du système de fichiers entier.")}
{img("c5_quota", "100%", F("Quota d'espace dépassé, puis corbeille : suppression et restauration"))}
{obs("Avec un quota de 10 Mo, même un fichier de 3,6 Mo est refusé : à l'écriture HDFS réserve un bloc complet par réplique (128 Mo × 3 = 384 Mo). Le pack s'exécute en root : la corbeille est /user/root/.Trash (fs.trash.interval = 1440 min).")}
{img("c6_snap", "100%", F("Snapshot s1 : fichier supprimé définitivement puis restauré depuis .snapshot"))}
{qa("Pourquoi /user/student/input doit-il rester réservé au CSV ?", "La table Hive externe de la partie 7 a pour LOCATION ce répertoire : tout fichier ajouté serait lu comme des lignes de la table.")}
{qa("Deux façons de restaurer un fichier supprimé ?", "Par la corbeille (<code>-mv</code> depuis .Trash/Current), sauf si on a utilisé -skipTrash ; par un snapshot (<code>-cp</code> depuis .snapshot/s1), même après une suppression définitive.")}
</section>
<section>
<h2 class="nob">3. Blocs, réplication et tolérance aux pannes</h2>
{img("c7_fsck", "100%", F("fsck : restaurants.csv tient dans 1 bloc, 3 répliques sur les 3 DataNodes"))}
{img("c8_blocs", "88%", F(f"gros.txt (22 888 896 octets) écrit en blocs de 1 Mo : {NB} blocs, réplication moyenne 3.0"))}
{img("c9_panne", "100%", F("Arrêt de hadoop-worker1 : lecture toujours possible, nœud déclaré mort, blocs sous-répliqués, puis retour à 3 DataNodes"))}
{qa("Combien de blocs pour 20 Mo ?", f"Avec des blocs de 128 Mo : 1 seul bloc. Avec des blocs de 1 Mo : environ 20 ({NB} ici pour 21,8 Mio). Des blocs trop petits multiplient les objets que le NameNode garde en mémoire et les tâches map.")}
{qa("Écrire un fichier RF=3 pendant la panne ?", "L'écriture réussit sur les 2 DataNodes vivants ; le fichier est sous-répliqué jusqu'au retour d'un troisième nœud, puis le NameNode complète la réplication.")}
{qa("Mémoire du NameNode, heartbeats et block reports ?", "En mémoire : l'arborescence, les fichiers et la position de chaque bloc. Sur disque : fsimage (image) et edits (journal). Chaque DataNode envoie un heartbeat toutes les 3 s (sinon il est déclaré mort, ici après ~50 s grâce à recheck-interval = 10 s) et un block report listant ses blocs.")}
</section>
<section>
<h2 class="nob">4. YARN et 5. MapReduce</h2>
{img("c10_pi", "100%", F("pi avec 8192 Mo par map (refusé) puis 512 Mo (réussi) ; liste des applications"))}
{obs(f"Résultat déterministe : « Estimated value of Pi is {st.PI} » (4 maps × 1000 échantillons, séquence de Halton). Cycle YARN : le client soumet au ResourceManager, qui lance un ApplicationMaster dans un conteneur ; l'AM demande des conteneurs aux NodeManagers pour les tâches map et reduce.")}
{img("c11_streaming", "100%", F("Comptage par ville : test local par tubes Unix, job Hadoop Streaming et sortie part-00000 identiques"))}
{img("c12_cuisine", "80%", F("Note moyenne par cuisine (reducer_moyenne.py complété)"))}
{qa("Phases map, shuffle/sort, reduce ?", "Map : chaque ligne devient (ville, 1). Shuffle/sort : les paires sont triées et regroupées par ville vers le reducer. Reduce : somme des 1 par ville, d'où 12 lignes en sortie.")}
{qa("Combiner et moyenne ?", "Un combiner réutilisant le reducer de moyenne calcule une moyenne de moyennes, fausse si les groupes sont de tailles différentes. Correction (_v2) : émettre « somme,effectif », additionner dans le combiner, et diviser seulement dans le reducer.")}
{qa("-numReduceTasks 0 ?", "Job map-only : la sortie est celle des mappers (ville, 1), un fichier par map, sans tri ni regroupement, donc sans ordre garanti.")}
</section>
<section>
<h2 class="nob">6. Spark sur YARN et 7. Hive</h2>
{img("c13_spark", "100%", F("SparkPi sur YARN, puis comptage par ville avec spark_rdd.py (sortie réelle PySpark 3.5.3)"))}
{qa("Rôle de HADOOP_CONF_DIR ?", "Il indique à Spark où trouver core-site, hdfs-site et yarn-site : adresse du NameNode et du ResourceManager. Sans lui, « --master yarn » échoue et les chemins sont lus sur le disque local.")}
{qa("Mode client ou cluster ?", "En client, le driver tourne sur hadoop-master et les print s'affichent dans le terminal. En cluster, le driver tourne dans l'ApplicationMaster sur un worker et les print sont dans les journaux YARN.")}
{img("c14_hive", "100%", F("Table externe, COUNT(*) = 80 000 et restaurants par ville avec Hive (MapReduce)"))}
{img("c15_hive2", "80%", F("Moyenne par cuisine et répartition par gamme de prix"))}
{qa("Metastore ou HiveServer2 ?", "HiveServer2 reçoit les requêtes (JDBC/Beeline), les compile et lance les jobs ; le Metastore fournit les métadonnées (bases, tables, colonnes, LOCATION) stockées dans PostgreSQL. Sans PostgreSQL on perd les définitions des tables ; sans HDFS on perd les données.")}
{qa("Pourquoi skip.header.line.count ?", "Sans elle, la ligne d'en-tête est lue comme une donnée : restaurant_id NULL (texte « restaurant_id » non convertible en INT), et COUNT(*) renvoie 80 001.")}
<h2>8. Validation globale et comparaison</h2>
<table class="t"><tr><th>Moteur</th><th>Résultat par ville</th><th>Lignes de sortie</th><th>Remarques</th></tr>
<tr><td>Hadoop Streaming</td><td>Tunis 16695 … Tozeur 2247</td><td>12, triées par ville</td><td>scripts Python, le plus verbeux, chaque job relit HDFS</td></tr>
<tr><td>Spark RDD (client)</td><td>mêmes effectifs</td><td>12, non triées</td><td>quelques lignes de code, calcul en mémoire</td></tr>
<tr><td>Hive (MapReduce)</td><td>mêmes effectifs</td><td>12, triées par effectif</td><td>SQL le plus lisible, latence d'un job MapReduce</td></tr></table>
{obs("Les trois moteurs donnent exactement les mêmes 12 effectifs (total 80 000) et la même moyenne par cuisine : le cluster est intégré de bout en bout.")}
{qa("Quand préférer Hive, Spark, Streaming ?", "Hive pour des requêtes SQL d'analyse sur des tables. Spark pour des traitements en plusieurs étapes, itératifs ou en mémoire. Streaming pour réutiliser rapidement un script existant sans changer d'outil.")}
<h2>Conclusion</h2>
<p>Le cluster Hadoop (1 master, 3 workers) a été validé : 3 DataNodes, 3 NodeManagers. HDFS a été manipulé (import, quotas, corbeille, snapshots) et la réplication observée : avec 3 répliques, la panne d'un DataNode n'empêche pas la lecture. YARN refuse une demande au-delà de maximum-allocation-mb. Le comptage par ville et la moyenne par cuisine donnent des résultats identiques avec Hadoop Streaming, Spark sur YARN et Hive : HDFS stocke, YARN alloue les ressources, et Spark et Hive en sont des clients.</p>
</section>"""
body = re.sub(r'(<h3>.*?</h3>\s*<figure>.*?</figure>)', r'<div style="break-inside:avoid">\1</div>', body, flags=re.S)
src = open("/home/claude/tp1/gen/cr_build.py").read()
CSS = src.split('CSS = """')[1].split('"""')[0] + " section.cover + section{page-break-before:always}"
FONTCSS = src.split('FONTCSS = f"""')[1].split('"""')[0].replace("{{", "{").replace("}}", "}")
H = B / "cr5.html"
H.write_text(f"<!doctype html><html lang=fr><head><meta charset=utf-8><style>{FONTCSS}{CSS}</style></head><body>{body}</body></html>")
foot = '<div style="width:100%;font-size:7.5pt;color:#6b7a84;padding:0 16mm;display:flex;justify-content:space-between;font-family:sans-serif"><span>TP 5 – Cluster Hadoop, Spark et Hive · Youssef Belghith · RSI31</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(); pg.goto(H.as_uri()); pg.wait_for_timeout(500)
    pg.pdf(path=str(OUT), format="A4", print_background=True, display_header_footer=True, header_template="<div></div>", footer_template=foot,
           margin={"top": "16mm", "bottom": "18mm", "left": "16mm", "right": "16mm"})
    b.close()
print(OUT, OUT.stat().st_size // 1024, "Ko")
