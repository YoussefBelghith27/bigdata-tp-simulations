"""Scénario TP6 : Spark sur cluster Hadoop — RDD, DataFrame, Spark SQL, Hive.
Toutes les sorties PySpark sont RÉELLES (exécution PySpark 3.5.3 des activités, session.json), lancées avec
master local[2] sur une copie locale de l'arborescence HDFS. Affichage : schéma file: remplacé par hdfs://hadoop-master:9000,
et valeurs propres à YARN de l'activité 1 (master, applicationId, URL) reconstituées."""
import json, os, re
from screens import *

RUN = "/home/claude/tp6/run/"
S = json.load(open(RUN + "session.json"))
OUTS = {}
for s in S:
    o = s["out"].replace("file:/user/", "hdfs://hadoop-master:9000/user/")
    if "Traceback" in o:
        lines = o.split("\n")
        jerr = next(l for l in lines if l.startswith("py4j.protocol.Py4JJavaError"))
        exc = next(l for l in lines if "FileAlreadyExistsException" in l)
        o = 'Traceback (most recent call last):\n  File "<stdin>", line 1, in <module>\n  ...\n' + jerr + "\n" + exc + "\n"
    OUTS.setdefault(" ".join(s["cell"].split()), []).append(o.rstrip("\n"))
def out(cell):
    k = " ".join(cell.split())
    return OUTS[k].pop(0) if len(OUTS[k]) > 1 else OUTS[k][0]

HM = "root@hadoop-master:/# "
PY = ">>> "
APP = "application_1794660372418_0007"

class UConsole(Console):
    def html(self, prompt=None, cursor=True, typed=None):
        return super().html(prompt, cursor, typed).replace('<div class="cb">', '<div class="cb" style="background:#300a24">').replace('<div class="ct">', '<div class="ct" style="background:#2b2b2b">')

slides, LOG = [], []
def dur(text, base=3200): return max(5200, min(11000, base + 55 * len(text)))
def show(html, step, text, d=None, cap=None): slides.append(dict(html=html, step=step, text=text, kind="show", dur=d or dur(text), cap=cap))
def tcon(con, prompt, step, text, answers, o=None, cap=None):
    slides.append(dict(html=con.html(prompt), step=step, text=text, kind="type", x=prompt_x(prompt), answers=answers, cap=cap))
    LOG.append((prompt, answers[0], o or "", cap)); con.add_cmd(prompt, answers[0])
    if o is not None: con.add_out(o + ("\n" if o and not o.endswith("\n") else ""))
def sclear(c):
    ps = [E(p) for p in (HM, PY)]
    idx = [i for i, l in enumerate(c.lines) if any(l.startswith(p) for p in ps)]
    if idx: c.lines = c.lines[idx[-1]:]

def comp(cmd):
    out, q = [], None
    for ch in cmd:
        if q:
            out.append(ch)
            if ch == q: q = None
        elif ch in "\"'": q = ch; out.append(ch)
        elif ch == " ": continue
        else: out.append(ch)
    return "".join(out)
def V(cmd): return list(dict.fromkeys([cmd, comp(cmd), cmd.replace('"', "'"), comp(cmd).replace('"', "'")]))

def py(con, cell, step, text, cap=None, o=None):
    """Cellule PySpark réelle : saisie si une ligne, sinon déjà tapée (>>> / ...)."""
    res = o if o is not None else out(cell)
    if "\n" not in cell and len(cell) <= 105:
        tcon(con, PY, step, text, V(cell), res, cap=cap)
    else:
        LOG.append((PY, cell, res, cap))
        for j, l in enumerate(cell.split("\n")):
            if j == 0: con.add_cmd(PY, l)
            else: con.add_raw(E("... ") + '<span class="w">' + E(l) + "</span>")
        if not cell.startswith(("def ", "class ")) and not cell.split("\n")[0].rstrip().endswith(":"):
            pass
        else:
            con.add_raw(E("... "))
        if res: con.add_out(res + "\n")
        show(con.html(PY, cursor=False), step, text, cap=cap)

def pyb(con, cells, step, text, cap=None):
    """Plusieurs cellules réelles déjà exécutées, regroupées en une diapo commentée."""
    for cell in cells:
        res = out(cell)
        LOG.append((PY, cell, res, cap))
        for j, l in enumerate(cell.split("\n")):
            if j == 0: con.add_cmd(PY, l)
            else: con.add_raw(E("... ") + '<span class="w">' + E(l) + "</span>")
        if cell.split("\n")[0].rstrip().endswith(":"): con.add_raw(E("... "))
        if res: con.add_out(res + "\n")
    show(con.html(PY, cursor=False), step, text, cap=cap)

def hls(path, entries):
    """Sortie de hdfs dfs -ls reconstituée à partir des tailles réelles des fichiers produits."""
    lines = [f"Found {len(entries)} items"]
    for name, isdir, size in entries:
        lines.append(f"{'drwxr-xr-x' if isdir else '-rw-r--r--'}   {'-' if isdir else '3'} root supergroup {size:>10} 2026-11-15 19:17 {path}/{name}")
    return "\n".join(lines)
def real_ls(path):
    p = path
    ents = []
    for n in sorted(os.listdir(p)):
        if n.startswith("."): continue
        f = os.path.join(p, n)
        ents.append((n, os.path.isdir(f), 0 if os.path.isdir(f) else os.path.getsize(f)))
    return hls(path, ents)
def cat(path):
    import glob
    return "".join(open(f).read() for f in sorted(glob.glob(path))).rstrip("\n")

# ================================================================= Intro
show(title_card("TP 6 · Spark sur un cluster Hadoop", "RDD, DataFrame, Spark SQL et Hive — Spark sur YARN, données dans HDFS",
                ["SparkContext, parallelize, partitions et glom()", "Transformations, actions et RDD clé-valeur", "Texte et CSV HDFS, cache, repartition, saveAsTextFile",
                 "spark-submit sur YARN, DataFrame et Spark SQL, Parquet", "Spark + Hive : lire rsi3.restaurants, écrire des tables"]),
     "Introduction", "TP6 – Spark sur le cluster du TP5. Toutes les sorties PySpark sont réelles (Spark 3.5.3) ; messages YARN/HDFS reconstitués.", 9500)

# ================================================================= Préparation
P0 = "Préparation"
c = UConsole("root@hadoop-master: /", HM)
c.add_out("")
tcon(c, HM, P0, "Dans le conteneur hadoop-master (cluster du TP5 démarré), créez le répertoire de travail Spark.", ["hdfs dfs -mkdir -p /user/student/spark"], "")
for l in ["cat > /tmp/texte.txt << 'EOF'", "Spark est un moteur de traitement distribué", "Hadoop fournit HDFS et YARN pour Spark", "Spark lit les données depuis HDFS", "EOF"]:
    c.add_raw((E(HM) if l.startswith("cat") else E("> ")) + '<span class="w">' + E(l) + "</span>")
show(c.html(HM, cursor=False), P0, "Le petit document texte du TP est créé dans /tmp (hors de /user/student/input, réservé à la table Hive).", 7000)
tcon(c, HM, P0, "Envoyez-le dans HDFS.", ["hdfs dfs -put -f /tmp/texte.txt /user/student/spark/texte.txt"], "")
tcon(c, HM, P0, "Vérifiez son contenu.", ["hdfs dfs -cat /user/student/spark/texte.txt"], cat("/user/student/spark/texte.txt"))
BANNER = f"""Python 3.10.12 (main, Feb  4 2025, 14:57:36) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
Setting default log level to "WARN".
To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).
2026-11-15 19:20:41,307 INFO yarn.Client: Submitting application {APP} to ResourceManager
Welcome to Spark version 3.5.3

Using Python version 3.10.12 (main, Feb  4 2025 14:57:36)
Spark context Web UI available at http://hadoop-master:4040
Spark context available as 'sc' (master = yarn, app id = {APP}).
SparkSession available as 'spark'."""
tcon(c, HM, P0, "Lancez le shell PySpark sur YARN.", ["pyspark --master yarn --deploy-mode client", "pyspark --master yarn"], BANNER)

# ================================================================= Partie A
A1 = "A · SparkContext et RDD"
sclear(c)
tcon(c, PY, A1, "Activité 1 : sc est le SparkContext créé par le shell.", ["sc"], "<SparkContext master=yarn appName=PySparkShell>", cap="a1")
tcon(c, PY, A1, "Gestionnaire de ressources utilisé.", V("print(sc.master)"), "yarn")
tcon(c, PY, A1, "Identifiant de l'application, visible dans YARN (port 8088).", V("print(sc.applicationId)"), APP, cap="a1_id")
pyb(c, ["print(sc.version)", "print(sc.defaultParallelism)"], A1, "Spark 3.5.3 ; parallélisme par défaut 2 (2 exécuteurs × 1 cœur).")
py(c, "nombres = sc.parallelize(range(1, 11))", A1, "Activité 2 : créez un RDD de 1 à 10 avec parallelize (rien n'est encore calculé).")
py(c, "print(nombres.collect())", A1, "collect() est une action : elle lance un job.")
pyb(c, ["print(type(nombres))", "grand = sc.parallelize(range(1, 101), 4)", "print(grand.getNumPartitions())"], A1, "Le type est un RDD (PipelinedRDD) ; un second RDD est imposé sur 4 partitions.")
py(c, "rdd = sc.parallelize(range(1, 13), 3)", A1, "Activité 3 : 12 éléments sur 3 partitions.")
py(c, "print(rdd.glom().collect())", A1, "glom() montre le contenu de chaque partition.", cap="glom")
pyb(c, ["print(rdd.glom().map(len).collect())", "print(rdd.mapPartitionsWithIndex(\n    lambda i, it: [(i, sum(it))]).collect())"], A1, "Taille et somme de chaque partition : [4, 4, 4] et [(0, 10), (1, 26), (2, 42)].")
py(c, "print(sc.parallelize(range(1, 13), 5).glom().collect())", A1, "Exercice : avec 5 partitions la répartition n'est plus équilibrée (2, 2, 3, 2, 3).")

A2 = "A · Transformations et actions"
sclear(c)
py(c, "carres = nombres.map(lambda x: x * x)", A2, "Activité 4 : map, un élément de sortie par entrée (transformation lazy).")
py(c, "print(carres.collect())", A2, "Déclenchez le calcul des carrés.")
pyb(c, ["pairs = nombres.filter(lambda x: x % 2 == 0)", "print(pairs.collect())"], A2, "filter garde les éléments pairs.")
py(c, 'phrases = sc.parallelize([\n    "spark traite les données",\n    "spark utilise les RDD",\n    "les données sont distribuées"])', A2, "Trois phrases à découper.")
py(c, "mots = phrases.flatMap(lambda p: p.split())", A2, "flatMap découpe et aplatit.")
py(c, "print(mots.collect())", A2, "12 mots dans une seule liste.")
pyb(c, ["uniques = mots.distinct()", "print(uniques.count())"], A2, "distinct supprime les doublons (shuffle) : 8 mots distincts.")
py(c, "print(phrases.map(lambda p: p.split()).collect())", A2, "Avec map : une liste de mots par phrase, pas aplatie.", cap="flatmap")
sclear(c)
py(c, "print(nombres.count())", A2, "Activité 5 : chaque action déclenche un job. count().")
py(c, "print(nombres.reduce(lambda a, b: a + b))", A2, "Somme avec reduce (fonction associative et commutative).")
pyb(c, ["print(nombres.top(3))", "print(nombres.sum(), nombres.max(), nombres.mean())"], A2, "top(3), puis somme, maximum et moyenne : un job par action.")
py(c, "print(sc.parallelize(range(1, 7)).reduce(lambda a, b: a * b))", A2, "Exercice : produit de 1 à 6.")

A3 = "A · Clé-valeur"
sclear(c)
py(c, "paires = mots.map(lambda m: (m, 1))", A3, "Activité 6 : schéma (mot, 1) comme le mapper du TP5.")
py(c, "freq = paires.reduceByKey(lambda a, b: a + b)", A3, "reduceByKey additionne par clé (combiner avant le shuffle).")
pyb(c, ["tri = freq.sortBy(lambda kv: kv[1], ascending=False)"], A3, "Tri par fréquence décroissante (encore lazy).")
py(c, "print(tri.take(5))", A3, "Les 5 mots les plus fréquents.", cap="freq")
py(c, "freq2 = paires.groupByKey().mapValues(sum)", A3, "Même calcul avec groupByKey (toutes les valeurs traversent le réseau).")
py(c, "print(sorted(freq2.collect()))", A3, "Résultat identique, mais moins efficace.")

A4 = "A · Texte et CSV HDFS"
sclear(c)
pyb(c, ['chemin = "/user/student/spark/texte.txt"'], A4, "Activité 7 : le document texte stocké dans HDFS.")
py(c, "lignes = sc.textFile(chemin)", A4, "Un élément du RDD = une ligne.")
pyb(c, ['print("Lignes :", lignes.count())', "mots = lignes.flatMap(lambda l: l.split())", 'print("Mots :", mots.count())', 'print("Mots distincts :", mots.distinct().count())'],
    A4, "3 lignes, 20 mots, 17 mots distincts.")
py(c, "freq = mots.map(lambda m: (m.lower(), 1)).reduceByKey(lambda a, b: a + b)", A4, "Fréquences sans tenir compte de la casse.")
py(c, "print(freq.sortBy(lambda kv: -kv[1]).take(5))", A4, "Mots les plus fréquents.", cap="texte")
pyb(c, ['avec_hdfs = lignes.filter(lambda l: "HDFS" in l)', "print(avec_hdfs.collect())", 'print("Plus longue ligne :", lignes.map(len).max())'], A4, "Lignes contenant HDFS et longueur de la plus longue ligne (43).")
sclear(c)
pyb(c, ["import csv"], A4, "Activité 8 : le CSV restaurants (80 000 lignes).")
py(c, 'brut = sc.textFile("/user/student/input/restaurants.csv")', A4, "Chargez le fichier depuis HDFS.")
py(c, "entete = brut.first()", A4, "Isolez l'en-tête.")
pyb(c, ["donnees = brut.filter(lambda l: l != entete)", "def parse(ligne):\n    return next(csv.reader([ligne]))", "restos = donnees.map(parse)"], A4, "On retire l'en-tête et on parse chaque ligne avec le module csv.")
py(c, "print(restos.take(2))", A4, "Deux premiers restaurants parsés.")
py(c, "par_ville = restos.map(lambda r: (r[2], 1)).reduceByKey(lambda a, b: a + b)", A4, "Comptage par ville.")
py(c, "print(par_ville.sortBy(lambda kv: -kv[1]).collect())", A4, "Mêmes effectifs que Hadoop Streaming et Hive au TP5.", cap="a8_ville")
for cell in ["def valide(r):\n    try:\n        float(r[4]); return True\n    except (ValueError, IndexError):\n        return False", "valides = restos.filter(valide)",
             "somme = valides.map(lambda r: (r[3], (float(r[4]), 1))) \\\n               .reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1]))"]:
    out(cell)
sclear(c)
c.add_cmd(PY, "def valide(r): ...                      # garde les notes convertibles en float"); c.add_cmd(PY, "valides = restos.filter(valide)")
c.add_cmd(PY, "somme = valides.map(lambda r: (r[3], (float(r[4]), 1))).reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1]))")
show(c.html(PY, cursor=False), A4, "Moyenne par cuisine : on agrège un couple (somme, effectif), car une moyenne de moyennes serait fausse.", 8500)
py(c, "moyennes = somme.mapValues(lambda s: round(s[0] / s[1], 2))", A4, "Divisez la somme par l'effectif.")
py(c, "print(moyennes.sortBy(lambda kv: -kv[1]).collect())", A4, "Moyennes identiques à AVG(rating) de Hive.", cap="a8_moy")
py(c, "print(par_ville.values().sum(), restos.count())", A4, "Contrôle : la somme des effectifs par ville vaut le nombre de restaurants.")

A5 = "A · Cache, partitions, sauvegarde"
sclear(c)
for cell in ["import time", "from pyspark import StorageLevel", "def chrono(rdd):\n    t0 = time.time()\n    n = rdd.count()\n    return n, round(time.time() - t0, 3)"]:
    out(cell)
c.add_cmd(PY, "import time"); c.add_cmd(PY, "from pyspark import StorageLevel"); c.add_cmd(PY, "def chrono(rdd): ...                     # (n, durée d'un count())")
py(c, 'print("sans cache :", chrono(valides), chrono(valides))', A5, "Activité 9 : deux count() sans persistance (fichier relu à chaque fois).")
py(c, "valides.cache()", A5, "Mettez le RDD en cache (effet à la première action).")
py(c, 'print("cache()    :", chrono(valides), chrono(valides))', A5, "Le 2e count() lit le cache : plus rapide.", cap="cache")
py(c, "print(valides.is_cached, valides.getStorageLevel())", A5, "cache() = MEMORY_ONLY (sérialisé, 1 réplique).")
pyb(c, ["valides.unpersist()"], A5, "unpersist() libère le cache ; persist(MEMORY_AND_DISK) déverserait sur disque ce qui ne tient pas en mémoire.")
sclear(c)
py(c, 'print("Partitions initiales :", restos.getNumPartitions())', A5, "Activité 10 : partitions du RDD restos.")
py(c, "plus = restos.repartition(6)", A5, "repartition(6) : shuffle complet.")
py(c, "print(plus.getNumPartitions(), plus.glom().map(len).collect())", A5, "6 partitions équilibrées.", cap="repart")
pyb(c, ["moins = plus.coalesce(2)", "print(moins.getNumPartitions(), moins.glom().map(len).collect())"], A5, "coalesce(2) fusionne sans shuffle : 2 partitions.")
sclear(c)
pyb(c, ['sortie = "/user/student/spark/output_villes"', 'resultat = par_ville.map(lambda kv: kv[0] + "," + str(kv[1]))'], A5, "Activité 11 : chemin de sortie HDFS et lignes de texte ville,nombre.")
py(c, "resultat.saveAsTextFile(sortie)", A5, "Sauvegardez (un fichier part par partition).")
py(c, 'resultat.coalesce(1).saveAsTextFile(sortie + "_un_fichier")', A5, "Version en un seul fichier.")
py(c, "resultat.saveAsTextFile(sortie)", A5, "Exercice : relancez la même sauvegarde.", cap="exists")
show(c.html(PY, cursor=False), A5, "FileAlreadyExistsException : comme en MapReduce, le répertoire de sortie ne doit pas exister (hdfs dfs -rm -r).", 8000)

# ================================================================= Contrôle HDFS + spark-submit
A6 = "A · spark-submit sur YARN"
t = UConsole("root@hadoop-master: / (2e terminal)", HM)
t.add_out("")
tcon(t, HM, A6, "Dans un second terminal du conteneur, contrôlez la sortie.", ["hdfs dfs -ls /user/student/spark/output_villes"], real_ls("/user/student/spark/output_villes"), cap="ls_out")
tcon(t, HM, A6, "_SUCCESS + 2 fichiers part (2 partitions). Lisez-les.", ["hdfs dfs -cat /user/student/spark/output_villes/part-*"], cat("/user/student/spark/output_villes/part-*"))
tcon(t, HM, A6, "Activité 12 : supprimez l'ancienne sortie du script.", ["hdfs dfs -rm -r -f /user/student/spark/output_script"], "")
RDDO = open(RUN + "rdd_out.txt").read().rstrip("\n")
LOGL = "2026-11-15 19:31:08,512 INFO yarn.Client: Submitting application application_1794660372418_0008 to ResourceManager\n2026-11-15 19:31:22,904 INFO yarn.Client: Application report for application_1794660372418_0008 (state: RUNNING)\n"
SUB = "spark-submit --master yarn --deploy-mode client --name TP6-RDD --num-executors 2 --executor-memory 512m --executor-cores 1 /opt/scripts/spark_tp_rdd.py"
tcon(t, HM, A6, "Soumettez spark_tp_rdd.py en mode client (affichages dans la console).", [SUB, "spark-submit --master yarn --deploy-mode client /opt/scripts/spark_tp_rdd.py"], LOGL + RDDO, cap="submit")
APPS = """Total number of applications (application-types: [], states: [NEW, NEW_SAVING, SUBMITTED, ACCEPTED, RUNNING, FINISHED, FAILED, KILLED] and tags: []):3
                Application-Id      Application-Name        Application-Type          User           Queue                   State             Final-State             Progress                        Tracking-URL
application_1794660372418_0008               TP6-RDD                   SPARK          root         default                FINISHED               SUCCEEDED                 100% http://hadoop-master:18080/history/application_1794660372418_0008/1
application_1794660372418_0007          PySparkShell                   SPARK          root         default                 RUNNING               UNDEFINED                  10% http://hadoop-master:4040
application_1794660372418_0006       QuasiMonteCarlo               MAPREDUCE          root         default                FINISHED               SUCCEEDED                 100% http://hadoop-master:19888/jobhistory/job/job_1794660372418_0006"""
tcon(t, HM, A6, "TOP 5 identique à Hive. Listez les applications YARN.", ["yarn application -list -appStates ALL"], APPS, cap="yarn")
tcon(t, HM, A6, "TP6-RDD FINISHED / SUCCEEDED ; le shell PySpark est toujours RUNNING. Lisez la sortie du script.", ["hdfs dfs -cat /user/student/spark/output_script/part-*"], cat("/user/student/spark/output_script/part-*"))

# ================================================================= Partie B
B1 = "B · DataFrame"
sclear(c)
py(c, 'df = (spark.read.option("header", True)\n          .option("inferSchema", True)\n          .csv("/user/student/input/restaurants.csv"))', B1, "Activité 13 : retour au shell PySpark. Lecture du CSV en DataFrame (en-tête + inférence des types).")
py(c, "df.printSchema()", B1, "Schéma inféré.", cap="schema")
pyb(c, ["df.show(5)", "print(df.count())", "print(sc is spark.sparkContext)"], B1, "5 premières lignes ; 80 000 lignes comme restos.count() ; la SparkSession contient le même SparkContext.")
sclear(c)
pyb(c, ["from pyspark.sql import functions as F", 'df.filter(F.col("rating") >= 4.5).show(5)'], B1, "Activité 14 : restaurants notés au moins 4,5.")
py(c, 'df.groupBy("city").count().orderBy(F.desc("count")).show()', B1, "Comptage par ville, en déclaratif.", cap="df_ville")
sclear(c)
py(c, '(df.groupBy("cuisine")\n   .agg(F.count("*").alias("nb"), F.round(F.avg("rating"), 2).alias("moyenne"))\n   .orderBy(F.desc("moyenne")).show())', B1, "Effectif et note moyenne par cuisine.", cap="df_cuisine")

B2 = "B · Spark SQL et Parquet"
sclear(c)
py(c, 'df.createOrReplaceTempView("restaurants")', B2, "Activité 15 : vue temporaire (rien n'est écrit dans HDFS ni dans le Metastore).")
py(c, 'spark.sql("""\n  SELECT city, COUNT(*) AS nb_restaurants\n  FROM restaurants\n  GROUP BY city\n  ORDER BY nb_restaurants DESC""").show()', B2, "La requête SQL du TP5, exécutée par Spark.", cap="sql_ville")
sclear(c)
py(c, 'spark.sql("""SELECT city, name, rating FROM restaurants\n             WHERE rating = (SELECT MAX(rating) FROM restaurants)""").show(5)', B2, "Sous-requête : les restaurants à la note maximale (5.0).")
py(c, 'df.groupBy("city").count().explain()', B2, "Plan physique : HashAggregate partiel, Exchange (shuffle), HashAggregate final.", cap="explain")
sclear(c)
py(c, 'villes = df.groupBy("city").count()', B2, "Activité 16 : écriture dans différents formats.")
pyb(c, ['villes.coalesce(1).write.mode("overwrite").csv("/user/student/spark/df_villes_csv", header=True)', 'df.write.mode("overwrite").parquet("/user/student/spark/restaurants_parquet")'], B2, "Écriture en CSV (avec en-tête, un fichier) puis du DataFrame complet en Parquet.")
py(c, 'print(spark.read.parquet("/user/student/spark/restaurants_parquet").count())', B2, "Relecture : 80 000 lignes.")
py(c, 'df.write.mode("overwrite").partitionBy("city").parquet("/user/student/spark/restaurants_par_ville")', B2, "Parquet partitionné par ville.")
py(c, 'spark.read.parquet("/user/student/spark/restaurants_par_ville").filter("city = \'Tunis\'").explain()', B2, "PartitionFilters : seul le répertoire city=Tunis est lu (partition pruning).", cap="pruning")
du = lambda p: sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fn in os.walk(p) for f in fn if not f.startswith("."))
def h(n): return f"{n/1024/1024:.1f} M" if n > 1024 * 1024 else f"{n/1024:.1f} K" if n > 1024 else f"{n}"
DU = "\n".join(f"{h(du(p)):<9}{h(du(p)*3):<9}{p}" for p in ["/user/student/input/restaurants.csv", "/user/student/spark/restaurants_parquet", "/user/student/spark/restaurants_par_ville"] if True)
DU = DU.replace(f"{h(du('/user/student/input/restaurants.csv'))}", "3.6 M", 1)
t.add_out("")
tcon(t, HM, B2, "Dans le 2e terminal, listez le Parquet partitionné.", ["hdfs dfs -ls /user/student/spark/restaurants_par_ville"], real_ls("/user/student/spark/restaurants_par_ville"), cap="ls_part")
tcon(t, HM, B2, "Un sous-répertoire city=… par ville. Comparez les tailles CSV et Parquet.",
     ["hdfs dfs -du -h /user/student/input/restaurants.csv /user/student/spark/restaurants_parquet /user/student/spark/restaurants_par_ville"],
     "\n".join(f"{h(os.path.getsize(p) if os.path.isfile(p) else du(p)):<8} {h((os.path.getsize(p) if os.path.isfile(p) else du(p))*3):<8} {p}" for p in ["/user/student/input/restaurants.csv", "/user/student/spark/restaurants_parquet", "/user/student/spark/restaurants_par_ville"]), cap="du")

# ================================================================= Partie C
C1 = "C · Spark + Hive"
sclear(c)
show(c.html(PY, cursor=False), C1, "Activité 17 : hive-site.xml (thrift://hive-metastore:9083) copié dans $SPARK_HOME/conf et spark.sql.catalogImplementation = hive ajouté ; shell relancé.", 9000)
py(c, 'spark.conf.get("spark.sql.catalogImplementation")', C1, "Catalogue utilisé.")
pyb(c, ['spark.sql("SHOW DATABASES").show()', 'spark.sql("USE rsi3")'], C1, "Spark voit la base rsi3 créée avec Beeline au TP5, et l'utilise.")
sclear(c)
py(c, 'spark.sql("""SELECT city, COUNT(*) AS nb\n             FROM restaurants\n             WHERE restaurant_id IS NOT NULL\n             GROUP BY city ORDER BY nb DESC""").show()', C1, "La table Hive rsi3.restaurants interrogée par le moteur Spark (pas de MapReduce).", cap="hive_read")
sclear(c)
py(c, 'spark.sql("""\n  CREATE TABLE IF NOT EXISTS rsi3.villes_spark\n  STORED AS PARQUET\n  AS SELECT city, COUNT(*) AS nb_restaurants\n     FROM rsi3.restaurants WHERE restaurant_id IS NOT NULL\n     GROUP BY city""")', C1, "Activité 18 : table de synthèse créée par Spark (CTAS, format Parquet).")
py(c, 'moy = (spark.table("rsi3.restaurants").filter("restaurant_id IS NOT NULL")\n           .groupBy("cuisine").agg(F.round(F.avg("rating"), 2).alias("moyenne")))', C1, "Moyenne par cuisine depuis la table Hive.")
py(c, 'moy.write.mode("overwrite").format("hive").saveAsTable("rsi3.cuisines_spark")', C1, "Écrite comme table Hive (lisible par Beeline).")
py(c, 'spark.sql("SHOW TABLES IN rsi3").show()', C1, "Les deux tables Spark rejoignent restaurants dans le Metastore.", cap="tables")
tcon(t, HM, C1, "Les fichiers de la table gérée sont dans le warehouse Hive.", ["hdfs dfs -ls /user/hive/warehouse/rsi3.db/villes_spark"], real_ls("/user/hive/warehouse/rsi3.db/villes_spark"))
HV = open(RUN + "hive_out.txt").read().rstrip("\n")
tcon(t, HM, C1, "Activité 19 : application complète DataFrame + Hive sur YARN.", ["spark-submit --master yarn --deploy-mode client /opt/scripts/spark_df_hive.py"],
     "2026-11-15 19:44:51,207 INFO yarn.Client: Submitting application application_1794660372418_0010 to ResourceManager\n" + HV, cap="df_hive")
tcon(t, HM, C1, "Table rsi3.synthese_villes et CSV écrits. Lisez le CSV produit.", ["hdfs dfs -cat /user/student/spark/synthese_villes_csv/part-*"], cat("/user/student/spark/synthese_villes_csv/part-*"))
show(t.html(HM, cursor=False), "Fin", "RDD, DataFrame, Spark SQL et Spark + Hive donnent les mêmes effectifs que Streaming et Hive du TP5. Spark calcule, YARN alloue, HDFS stocke, le Metastore décrit.", 10000)
