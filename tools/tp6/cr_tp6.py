"""Compte rendu TP5 (cluster Hadoop, HDFS, YARN, MapReduce, Spark, Hive) en PDF A4."""
import pathlib, html, base64, re
from playwright.sync_api import sync_playwright
from render import Renderer, FONTS
from screens import CSS as SCSS
import story_tp6 as st

E = html.escape
B = pathlib.Path("/home/claude/tp6/build"); D = B / "crcap"; D.mkdir(parents=True, exist_ok=True)
OUT = B / "CR_TP6_Spark_Cluster_Hadoop.pdf"
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
SHORT = {}
def block(title, entries, maxl=36):
    lines = []
    for prompt, cmd, o in entries:
        prompt = SHORT.get(prompt, prompt)
        for j, l in enumerate(cmd.split("\n")):
            for k, p in enumerate(wrapl((prompt if j == 0 else ("... " if prompt == ">>> " else "> ")) + l)):
                lines.append((E(p[:len(prompt)]) + f'<span class="w">{E(p[len(prompt):])}</span>') if (j == 0 and k == 0) else f'<span class="w">{E(p)}</span>')
        ol = o.strip("\n").split("\n") if o.strip() else []
        for l in ol[:maxl]:
            for p in wrapl(l): lines.append(E(p))
        if len(ol) > maxl: lines.append(f'<span class="k">… ({len(ol) - maxl} lignes de plus)</span>')
    return f"""<div id="cap" style="width:{W}px;background:#300a24;border-radius:8px;overflow:hidden;border:1px solid #333">
      <div style="height:30px;background:#2b2b2b;color:#ddd;font:12px UI;display:flex;align-items:center;padding:0 12px;gap:8px">
      <span style="font:10px MONO;border:1px solid #555;border-radius:2px;padding:0 3px">&gt;_</span>{E(title)}</div>
      <div style="font:14px/18px MONO;color:#ccc;white-space:pre;padding:10px 12px">{"\n".join(lines)}</div></div>"""

def all_caps(*names): return [by_cap(n) for n in names]
CAPS = {
 "c1_sc": ("pyspark --master yarn", all_caps("a1", "a1_id"), 6),
 "c2_glom": ("pyspark", all_caps("glom"), 6),
 "c3_trans": ("pyspark", all_caps("flatmap", "freq"), 8),
 "c4_texte": ("pyspark", all_caps("texte"), 8),
 "c5_csv": ("pyspark", all_caps("a8_ville", "a8_moy"), 8),
 "c6_cache": ("pyspark", all_caps("cache", "repart"), 8),
 "c7_save": ("pyspark / hdfs", all_caps("exists", "ls_out"), 10),
 "c8_submit": ("hadoop-master", all_caps("submit", "yarn"), 12),
 "c9_schema": ("pyspark", all_caps("schema"), 12),
 "c10_df": ("pyspark", all_caps("df_ville", "df_cuisine"), 20),
 "c11_sql": ("pyspark", all_caps("sql_ville", "explain"), 20),
 "c12_parquet": ("pyspark / hdfs", all_caps("pruning", "ls_part", "du"), 18),
 "c13_hive": ("pyspark (catalogue Hive)", all_caps("hive_read", "tables"), 20),
 "c14_dfhive": ("hadoop-master", all_caps("df_hive"), 20),
}
with Renderer() as r:
    for name, (ttl, ent, mx) in CAPS.items():
        r.pg.set_content(f"<!doctype html><meta charset=utf-8><style>{FONTS}{SCSS}body{{width:auto;height:auto;overflow:visible;background:#fff}}</style>{block(ttl, ent, mx)}")
        r.pg.evaluate("document.fonts.ready"); r.pg.wait_for_timeout(50)
        r.pg.locator("#cap").screenshot(path=str(D / f"{name}.png"))

def img(name, w="100%", fig=None):
    b = base64.b64encode((D / f"{name}.png").read_bytes()).decode()
    return f'<figure><img src="data:image/png;base64,{b}" style="width:{w}">' + (f'<figcaption>{fig}</figcaption>' if fig else "") + "</figure>"
def code(s): return f'<pre class="code">{E(s)}</pre>'
def obs(s): return f'<p class="obs"><b>Observation.</b> {s}</p>'
def qa(q, a): return f'<p class="q">{q}</p><p>{a}</p>'
fn = iter(range(1, 60))
def F(t): return f"Figure {next(fn)} – {t}"


body = f"""
<section class="cover">
  <div class="inst"><div>Institut Supérieur des Études Technologiques de Nabeul<br>Département Technologies de l'Informatique</div><div style="text-align:right">Écosystème Big Data avancé<br>Classe : RSI31</div></div>
  <div class="mid"><div class="kicker">COMPTE RENDU DE TRAVAUX PRATIQUES</div>
    <h1>TP 6 : Spark sur un cluster Hadoop<br>RDD, DataFrame, Spark SQL et Hive</h1>
    <div class="subt">Spark 3.5.3 sur YARN, données dans HDFS,<br>catalogue Hive (Metastore) partagé avec Beeline</div><div class="bar"></div></div>
  <table class="id"><tr><td>Réalisé par</td><td><b>Youssef Belghith</b></td></tr><tr><td>Classe</td><td>RSI31</td></tr>
    <tr><td>Enseignante</td><td>Ines Ghorbel</td></tr><tr><td>Environnement</td><td>Cluster du TP5 : Hadoop 3.3.6, Spark 3.5.3, Hive 3.1.3</td></tr>
    <tr><td>Date</td><td>15 novembre 2026</td></tr></table>
</section>
<section>
<h2 class="nob">Partie A – Spark RDD (activités 1 à 12)</h2>
<p class="note"><b>Remarque sur les captures.</b> Toutes les sorties PySpark sont <b>réelles</b> : les activités ont été exécutées avec Spark 3.5.3 (mode local[2]) sur une copie de l'arborescence <code>/user/student</code> et sur la même table externe <code>rsi3.restaurants</code>. Les chemins sont affichés avec le schéma <code>hdfs://hadoop-master:9000</code>. Sont <b>reconstitués</b> : les valeurs propres à YARN de l'activité 1 (master, applicationId), les messages <code>yarn.Client</code> et la liste des applications YARN. Simulation : <i>youssefbelghith27.github.io/bigdata-tp-simulations</i>.</p>
<h3>Activité 1 – SparkContext</h3>
{img("c1_sc", "70%", F("sc, master yarn et identifiant de l'application"))}
<table class="t"><tr><th>Propriété</th><th>Valeur observée</th><th>Signification</th></tr>
<tr><td>sc.version</td><td>3.5.3</td><td>version de Spark</td></tr><tr><td>sc.master</td><td>yarn</td><td>gestionnaire de ressources (local[2] en local)</td></tr>
<tr><td>sc.appName</td><td>PySparkShell</td><td>nom de l'application dans YARN</td></tr><tr><td>sc.applicationId</td><td>application_…_0007</td><td>identifiant YARN (local-… en local)</td></tr>
<tr><td>sc.defaultParallelism</td><td>2</td><td>partitions par défaut de parallelize</td></tr></table>
{obs("Après <code>sc.stop()</code>, <code>sc.parallelize([1])</code> échoue : le contexte est arrêté et un seul SparkContext actif est permis.")}
<h3>Activités 2 à 4 – RDD, partitions, transformations</h3>
{img("c2_glom", "80%", F("glom() : [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]"))}
{img("c3_trans", "100%", F("map(split) contre flatMap(split) ; fréquences avec reduceByKey"))}
{obs("Avec 5 partitions pour 12 éléments, la répartition devient [[1, 2], [3, 4], [5, 6, 7], [8, 9], [10, 11, 12]] : déséquilibrée. 20 partitions laisseraient des partitions vides. Une tâche Spark traite une partition.")}
<h3>Activités 5 à 7 – Actions, clé-valeur, document texte</h3>
{img("c4_texte", "88%", F("Document texte HDFS : spark 3 fois, hdfs 2 fois"))}
{obs("Résultats : 10, top(3) = [10, 9, 8], somme 55, moyenne 5.5, produit de 1 à 6 = 720 ; texte : 3 lignes, 20 mots, 17 distincts, plus longue ligne 43 caractères. <code>reduce(a - b)</code> n'est pas fiable car la soustraction n'est ni associative ni commutative.")}
<h3>Activité 8 – CSV restaurants</h3>
{img("c5_csv", "100%", F("Effectifs par ville et note moyenne par cuisine (RDD)"))}
{obs("par_ville.values().sum() = restos.count() = 80 000 ; les effectifs et les moyennes sont identiques à Hadoop Streaming et à Hive (TP5).")}
<h3>Activités 9 à 11 – Persistance, partitions, sauvegarde</h3>
{img("c6_cache", "100%", F("cache() : le 2e count() lit la mémoire ; repartition(6) équilibre les partitions"))}
{img("c7_save", "100%", F("FileAlreadyExistsException sur un répertoire existant ; fichiers _SUCCESS et part-* produits"))}
{obs("Le CSV donne 2 partitions (petit fichier : minimum 2). repartition(6) donne environ 13 333 lignes par partition, coalesce(2) fusionne sans shuffle. Pour 3 workers à 2 cœurs, viser 2 à 3 partitions par cœur, soit 12 à 18.")}
<h3>Activité 12 – spark-submit sur YARN</h3>
{img("c8_submit", "100%", F("spark_tp_rdd.py en mode client (sortie réelle du script) et application TP6-RDD SUCCEEDED"))}
</section>
<section>
<h2 class="nob">Partie B – DataFrame et Spark SQL (activités 13 à 16)</h2>
{img("c9_schema", "60%", F("Schéma inféré du CSV"))}
{img("c10_df", "88%", F("groupBy ville et agrégation par cuisine avec l'API DataFrame"))}
{img("c11_sql", "100%", F("Requête SQL sur la vue temporaire et plan physique (HashAggregate, Exchange)"))}
{img("c12_parquet", "100%", F("Partition pruning sur le Parquet partitionné, répertoires city=… et tailles CSV / Parquet"))}
{obs("Le Parquet (≈ 557 Ko) est près de 7 fois plus petit que le CSV (3,6 Mo) : format colonnaire compressé (snappy) qui garde le schéma. Avec partitionBy(\"city\"), un filtre sur la ville ne lit qu'un répertoire (PartitionFilters).")}
</section>
<section>
<h2 class="nob">Partie C – Spark et Hive (activités 17 à 19)</h2>
{code("<!-- $SPARK_HOME/conf/hive-site.xml -->" + chr(10) + "<property><name>hive.metastore.uris</name><value>thrift://hive-metastore:9083</value></property>" + chr(10) + "# spark-defaults.conf" + chr(10) + "spark.sql.catalogImplementation   hive")}
{img("c13_hive", "88%", F("Table Hive rsi3.restaurants lue par Spark, puis tables villes_spark et cuisines_spark créées"))}
{img("c14_dfhive", "88%", F("Application spark_df_hive.py : 80 000 restaurants, synthèse par ville écrite dans Hive et dans HDFS"))}
{obs("La table externe ignore l'en-tête (skip.header.line.count) : COUNT(*) vaut 80 000 dans Spark comme dans Beeline. Spark utilise ses propres exécuteurs sur YARN, pas de MapReduce : l'agrégation est bien plus rapide que dans Beeline.")}
<h2>Questions de synthèse</h2>
{qa("1. Transformation et action ; intérêt de l'évaluation paresseuse ?", "Une transformation (map, filter, reduceByKey) décrit un nouveau RDD sans calcul ; une action (count, collect, saveAsTextFile) lance un job. Spark connaît ainsi toute la chaîne avant d'exécuter : il regroupe les étapes sans shuffle, n'exécute que le nécessaire et peut recalculer une partition perdue grâce au lineage.")}
{qa("2. Pourquoi reduceByKey plutôt que groupByKey ?", "reduceByKey combine les valeurs dans chaque partition avant le shuffle (comme un combiner) : moins de données sur le réseau et moins de mémoire. groupByKey envoie toutes les valeurs de chaque clé.")}
{qa("3. RDD, DataFrame ou Spark SQL ? Apport de Catalyst ?", "RDD pour des données non structurées ou un contrôle fin ; DataFrame et SQL pour des données tabulaires (code déclaratif, plus court). Catalyst optimise le plan : élagage des colonnes, filtres poussés à la lecture, agrégation partielle, et Tungsten génère un code efficace.")}
{qa("4. cache, repartition, coalesce ?", "cache() pour un RDD/DataFrame réutilisé par plusieurs actions ; repartition(n) pour augmenter ou rééquilibrer (shuffle) ; coalesce(n) pour réduire sans shuffle, par exemple coalesce(1) avant d'écrire un petit résultat.")}
{qa("5. CSV ou Parquet ; partitionBy ?", "CSV : texte lisible, volumineux, sans types. Parquet : colonnaire, compressé (557 Ko contre 3,6 Mo ici), schéma conservé, lecture des seules colonnes utiles. partitionBy crée un répertoire par valeur et permet de ne lire que les partitions filtrées.")}
{qa("6. Chemin d'une requête spark.sql sur une table Hive ?", "Le driver demande au Metastore (via thrift, données dans PostgreSQL) le schéma et la LOCATION de la table ; Catalyst construit le plan ; YARN fournit les conteneurs des exécuteurs ; ceux-ci lisent les blocs dans HDFS, agrègent, et le résultat remonte au driver.")}
{qa("7. --deploy-mode client ou cluster ?", "client : le driver tourne sur hadoop-master, les print s'affichent dans la console (idéal pour tester). cluster : le driver tourne dans un conteneur YARN, l'application survit à la fermeture du terminal et les affichages se lisent avec yarn logs ; il faut fournir hive-site.xml avec --files.")}
{qa("8. Spark, Hive et Streaming sur le comptage par ville ?", "Les trois donnent les mêmes 12 effectifs (total 80 000). Streaming : scripts mapper/reducer, plusieurs lectures disque. Hive : une requête SQL traduite en job MapReduce, lente au démarrage. Spark : quelques lignes, calcul en mémoire, le plus rapide et le plus polyvalent (RDD, DataFrame, SQL, Hive).")}
<h2>Conclusion</h2>
<p>Spark exploite le cluster du TP5 : YARN alloue les exécuteurs, HDFS stocke les entrées et les sorties, et le Metastore Hive sert de catalogue partagé avec Beeline. Les RDD ont permis de comprendre partitions, transformations, actions et shuffle ; les DataFrame et Spark SQL expriment les mêmes calculs en moins de code, avec un plan optimisé. Tous les moteurs donnent des résultats identiques sur restaurants.csv.</p>
</section>"""
body = re.sub(r'(<h3>.*?</h3>\s*<figure>.*?</figure>)', r'<div style="break-inside:avoid">\1</div>', body, flags=re.S)
src = open("/home/claude/tp1/gen/cr_build.py").read()
CSS = src.split('CSS = """')[1].split('"""')[0] + " section.cover + section{page-break-before:always}"
FONTCSS = src.split('FONTCSS = f"""')[1].split('"""')[0].replace("{{", "{").replace("}}", "}")
H = B / "cr6.html"
H.write_text(f"<!doctype html><html lang=fr><head><meta charset=utf-8><style>{FONTCSS}{CSS}</style></head><body>{body}</body></html>")
foot = '<div style="width:100%;font-size:7.5pt;color:#6b7a84;padding:0 16mm;display:flex;justify-content:space-between;font-family:sans-serif"><span>TP 6 – Spark sur cluster Hadoop · Youssef Belghith · RSI31</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(); pg.goto(H.as_uri()); pg.wait_for_timeout(500)
    pg.pdf(path=str(OUT), format="A4", print_background=True, display_header_footer=True, header_template="<div></div>", footer_template=foot,
           margin={"top": "16mm", "bottom": "18mm", "left": "16mm", "right": "16mm"})
    b.close()
print(OUT, OUT.stat().st_size // 1024, "Ko")
