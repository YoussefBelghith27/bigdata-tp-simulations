"""Scénario TP5 : cluster Hadoop 3.3.6 (Docker) — HDFS, blocs/panne, YARN, MapReduce Streaming, Spark, Hive.
Réel : contenu du CSV, sorties des mappers/reducers (exécutés), sortie Spark (pyspark 3.5.3 exécuté),
       agrégats Hive (calculés sur le CSV), valeur de pi (algorithme de Halton de Hadoop), tailles et nombres de blocs.
Reconstitué : messages HDFS / YARN / jps / beeline (format Hadoop 3.3.6)."""
import csv, subprocess, collections, math
from decimal import Decimal, ROUND_HALF_UP
from screens import *

PACK = "/tmp/tp5x/tp5-hadoop"
CSVF = PACK + "/data/restaurants.csv"
ROWS = list(csv.reader(open(CSVF, encoding="utf-8")))[1:]
SIZE = 3809818
def run(cmd): return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, cwd=PACK, env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"}).stdout
CITY = run("cat data/restaurants.csv | python3 scripts/mapper.py | sort | python3 scripts/reducer.py")
CUIS = run("cat data/restaurants.csv | python3 scripts/mapper_cuisine.py | sort | python3 scripts/reducer_moyenne.py")
SPARK = "Sfax\t9138\nKairouan\t4631\nTunis\t16695\nBizerte\t5227\nTozeur\t2247\nHammamet\t6872\nDjerba\t6133\nMonastir\t5374\nGabes\t3031\nMahdia\t3838\nSousse\t9188\nNabeul\t7626"  # sortie réelle pyspark

VM = "etudiant@ubuntu-vm:~/tp5-hadoop$ "
HM = "root@hadoop-master:/# "
BL = "0: jdbc:hive2://hive-server:10000/default> "
BR = "0: jdbc:hive2://hive-server:10000/rsi3> "

class UConsole(Console):
    def html(self, prompt=None, cursor=True, typed=None):
        return super().html(prompt, cursor, typed).replace('<div class="cb">', '<div class="cb" style="background:#300a24">').replace('<div class="ct">', '<div class="ct" style="background:#2b2b2b">')

slides, LOG = [], []
def sclear(c):
    """Efface l'écran en gardant la dernière commande et sa sortie (sinon la sortie ne serait jamais visible)."""
    ps = [E(p) for p in (VM, HM, BL, BR)]
    idx = [i for i, l in enumerate(c.lines) if any(l.startswith(p) for p in ps)]
    if idx: c.lines = c.lines[idx[-1]:]
def dur(text, base=3200): return max(5200, min(11000, base + 55 * len(text)))
def show(html, step, text, d=None, cap=None): slides.append(dict(html=html, step=step, text=text, kind="show", dur=d or dur(text), cap=cap))
def tcon(con, prompt, step, text, answers, out=None, cap=None):
    slides.append(dict(html=con.html(prompt), step=step, text=text, kind="type", x=prompt_x(prompt), answers=answers, cap=cap))
    LOG.append((prompt, answers[0], out or "", cap)); con.add_cmd(prompt, answers[0])
    if out is not None: con.add_out(out)
def pre(con, prompt, cmd, out, step, text, cap=None, nextp=None):
    LOG.append((prompt, cmd, out or "", cap))
    for j, l in enumerate(cmd.split("\n")):
        if j == 0: con.add_cmd(prompt, l)
        else: con.add_raw('<span class="w">' + E(("> " if prompt == VM or prompt == HM else ". . . . . . . . . . . . . . . . . . . . . . .> ") + l) + "</span>")
    if out is not None: con.add_out(out)
    show(con.html(nextp or prompt, cursor=False), step, text, cap=cap)

def bee(cols, rows, secs):
    w = [max(len(c), *(len(str(r[i])) for r in rows)) for i, c in enumerate(cols)]
    sep = "+" + "+".join("-" * (x + 2) for x in w) + "+"
    out = [sep, "|" + "|".join(" " + c.center(w[i]) + " " for i, c in enumerate(cols)) + "|", sep]
    out += ["|" + "|".join(" " + str(r[i]).ljust(w[i]) + " " for i in range(len(cols))) + "|" for r in rows]
    out += [sep, f"{len(rows)} row{'s' if len(rows) > 1 else ''} selected ({secs} seconds)"]
    return "\n".join(out)

def halton_pi(nMaps, nSamples):
    inside = 0
    for i in range(nMaps):
        for j in range(nSamples):
            pt = []
            for b in (2, 3):
                k, x, f = i * nSamples + j + 1, 0.0, 1.0 / b
                while k > 0: x += (k % b) * f; k //= b; f /= b
                pt.append(x - 0.5)
            inside += pt[0] ** 2 + pt[1] ** 2 <= 0.25
    return (Decimal(4) * inside / Decimal(nMaps * nSamples)).quantize(Decimal(10) ** -20)

cities = [l.split("\t") for l in CITY.strip().split("\n")]
cuis = [l.split("\t") for l in CUIS.strip().split("\n")]
def havg(c):
    v = [float(r[4]) for r in ROWS if r[3] == c]
    return str(float(Decimal(repr(sum(v) / len(v))).quantize(Decimal("0.01"), ROUND_HALF_UP)))
prices = collections.Counter(r[5] for r in ROWS).most_common()

# ================================================================= Introduction
show(title_card("TP 5 · Cluster Hadoop : HDFS, YARN, MapReduce, Spark et Hive", "1 master + 3 workers sous Docker (VM Ubuntu), Spark sur YARN, Hive sur HDFS",
                ["Valider le cluster : 3 DataNodes, 3 NodeManagers", "HDFS : import, quotas, corbeille, snapshots",
                 "Blocs, réplication et panne d'un DataNode", "YARN et MapReduce Streaming (Python)", "Spark sur YARN et requêtes Hive (même résultat partout)"]),
     "Introduction", "TP5 – Cluster Hadoop. Résultats de calcul réels (scripts, Spark, agrégats) ; messages Hadoop/YARN/Hive reconstitués.", 9000)

# ================================================================= Partie 1
P1 = "1 · Cluster"
vm = UConsole("etudiant@ubuntu-vm: ~/tp5-hadoop", VM)
vm.add_out("")
UP = "\n".join([" Network tp5-hadoop_default  Created", " Volume \"tp5-hadoop_nn_data\"  Created", " Volume \"tp5-hadoop_dn1_data\"  Created",
                " Volume \"tp5-hadoop_dn2_data\"  Created", " Volume \"tp5-hadoop_dn3_data\"  Created"] +
               [f" Container {c}  Started" for c in ["hadoop-master", "hadoop-worker1", "hadoop-worker2", "hadoop-worker3"]]) + "\n"
tcon(vm, VM, P1, "Images construites (docker compose build). Démarrez d'abord Hadoop : le master et les 3 workers.",
     ["docker compose up -d hadoop-master hadoop-worker1 hadoop-worker2 hadoop-worker3"], UP)
PS = """NAME             IMAGE              COMMAND            SERVICE          STATUS          PORTS
hadoop-master    tp5-hadoop:3.3.6   "/entrypoint.sh"   hadoop-master    Up 2 minutes    0.0.0.0:8088->8088/tcp, 0.0.0.0:9870->9870/tcp, 0.0.0.0:18080->18080/tcp, 0.0.0.0:19888->19888/tcp
hadoop-worker1   tp5-hadoop:3.3.6   "/entrypoint.sh"   hadoop-worker1   Up 2 minutes
hadoop-worker2   tp5-hadoop:3.3.6   "/entrypoint.sh"   hadoop-worker2   Up 2 minutes
hadoop-worker3   tp5-hadoop:3.3.6   "/entrypoint.sh"   hadoop-worker3   Up 2 minutes
"""
tcon(vm, VM, P1, "Vérifiez les conteneurs.", ["docker compose ps"], PS, cap="ps")
tcon(vm, VM, P1, "4 conteneurs Up. Ouvrez un shell dans le master.", ["docker exec -it hadoop-master bash"], "")
hm = UConsole("root@hadoop-master: /", HM)
for l in vm.lines: hm.add_raw(l)
hm.add_cmd(VM, "docker exec -it hadoop-master bash"); hm.lines.pop() if False else None
hm.lines = vm.lines[:]
REPORT = """Configured Capacity: 126433849344 (117.75 GB)
Present Capacity: 98571264000 (91.80 GB)
DFS Remaining: 98570485760 (91.80 GB)
DFS Used: 778240 (760 KB)
DFS Used%: 0.00%
Replicated Blocks:
	Under replicated blocks: 0
	Blocks with corrupt replicas: 0
	Missing blocks: 0
	Missing blocks (with replication factor 1): 0
	Low redundancy blocks with highest priority to recover: 0
	Pending deletion blocks: 0
Erasure Coded Block Groups:
	Low redundancy block groups: 0
	Block groups with corrupt internal blocks: 0
	Missing block groups: 0
	Low redundancy blocks with highest priority to recover: 0
	Pending deletion blocks: 0

-------------------------------------------------
Live datanodes (3):

Name: 172.19.0.3:9866 (hadoop-worker1.tp5-hadoop_default)
Hostname: hadoop-worker1
Decommission Status : Normal
Configured Capacity: 42144616448 (39.25 GB)
DFS Used: 259413 (253.33 KB)
Non DFS Used: 7581048832 (7.06 GB)
DFS Remaining: 32856828589 (30.60 GB)
""".replace("\t", "        ")
tcon(hm, HM, P1, "Rapport HDFS (30 premières lignes).", ["hdfs dfsadmin -report | head -30"], REPORT, cap="report")
tcon(hm, HM, P1, "Live datanodes (3). Le NameNode est-il sorti du mode sans échec ?", ["hdfs dfsadmin -safemode get"], "Safe mode is OFF\n")
NODES = """2026-11-14 14:06:12,418 INFO client.DefaultNoHARMFailoverProxyProvider: Connecting to ResourceManager at hadoop-master/172.19.0.2:8032
Total Nodes:3
         Node-Id             Node-State Node-Http-Address       Number-of-Running-Containers
hadoop-worker1:41235            RUNNING hadoop-worker1:8042                                0
hadoop-worker2:37781            RUNNING hadoop-worker2:8042                                0
hadoop-worker3:44109            RUNNING hadoop-worker3:8042                                0
"""
tcon(hm, HM, P1, "Safe mode OFF. Listez les NodeManagers YARN.", ["yarn node -list -all"], NODES, cap="nodes")
tcon(hm, HM, P1, "3 nœuds RUNNING. Affichez les processus Java du master.", ["jps"], "412 NameNode\n598 SecondaryNameNode\n803 ResourceManager\n1187 JobHistoryServer\n2310 Jps\n", cap="jps")
tcon(hm, HM, P1, "NameNode, SecondaryNameNode, ResourceManager, JobHistoryServer. Revenez à la VM.", ["exit"], "exit\n")
tcon(hm, VM, P1, "Processus d'un worker.", ["docker exec hadoop-worker1 jps"], "245 DataNode\n371 NodeManager\n902 Jps\n", cap="jps_w")

# ================================================================= Partie 2
P2 = "2 · HDFS"
tcon(hm, VM, P2, "Worker = DataNode + NodeManager. Copiez restaurants.csv (80 000 lignes, 3,7 Mo) dans le master.",
     ["docker cp data/restaurants.csv hadoop-master:/tmp/restaurants.csv"], "Successfully copied 3.81MB to hadoop-master:/tmp/restaurants.csv\n")
tcon(hm, VM, P2, "Ouvrez de nouveau un shell dans le master.", ["docker exec -it hadoop-master bash"], "")
tcon(hm, HM, P2, "Créez le répertoire d'entrée dans HDFS.", ["hdfs dfs -mkdir -p /user/student/input"], "")
tcon(hm, HM, P2, "Envoyez le CSV dans HDFS.", ["hdfs dfs -put -f /tmp/restaurants.csv /user/student/input/"], "")
tcon(hm, HM, P2, "Listez le répertoire (tailles lisibles).", ["hdfs dfs -ls -h /user/student/input"],
     "Found 1 items\n-rw-r--r--   3 root supergroup      3.6 M 2026-11-14 14:08 /user/student/input/restaurants.csv\n", cap="ls")
head = open(CSVF, "rb").read(1024).decode("utf-8", "ignore")
tcon(hm, HM, P2, "Le 3 est le facteur de réplication. Lisez le début du fichier (1 Ko).", ["hdfs dfs -head /user/student/input/restaurants.csv"], head.rsplit("\n", 1)[0] + "\n" + head.rsplit("\n", 1)[1])
hm.add_out("")
tcon(hm, HM, P2, "Comparez taille logique et espace occupé.", ["hdfs dfs -du -h /user/student/input"], "3.6 M  10.9 M  /user/student/input/restaurants.csv\n", cap="du")
tcon(hm, HM, P2, "3,6 Mo de données, 10,9 Mo sur disque (× 3 répliques). Récupérez le fichier et comparez-le à l'original.",
     ["hdfs dfs -get /user/student/input/restaurants.csv /tmp/restaurants_local.csv && diff /tmp/restaurants.csv /tmp/restaurants_local.csv && echo \"IDENTIQUES\""], "IDENTIQUES\n")
sclear(hm)
pre(hm, HM, "hdfs dfs -mkdir -p /user/student/quota /user/student/tp/a/b /user/student/snap /user/student/blocs /user/student/mr\nhdfs dfs -touchz /user/student/tp/a/b/vide.txt\nhdfs dfs -put /tmp/restaurants.csv /user/student/snap/ /user/student/mr/".replace("\nhdfs", " && \\\nhdfs"), "", P2,
    "Fichier identique après l'aller-retour. On prépare les répertoires des exercices suivants (2.2 : -mkdir -p, -touchz, -put).")
tcon(hm, HM, P2, "2.3 Quotas : limitez /user/student/quota à 10 Mo, réplication comprise.", ["hdfs dfsadmin -setSpaceQuota 10m /user/student/quota"], "")
tcon(hm, HM, P2, "Tentez d'y copier le CSV de 3,6 Mo.", ["hdfs dfs -put /tmp/restaurants.csv /user/student/quota/"],
     "put: The DiskSpace quota of /user/student/quota is exceeded: quota = 10485760 B = 10 MB but diskspace consumed = 402653184 B = 384 MB\n", cap="quota")
tcon(hm, HM, P2, "Refusé : HDFS réserve un bloc entier par réplique à l'écriture (128 Mo × 3 = 384 Mo). 2.4 Corbeille : supprimez un fichier.",
     ["hdfs dfs -rm /user/student/tp/a/b/vide.txt"],
     "2026-11-14 14:11:02,734 INFO fs.TrashPolicyDefault: Moved: 'hdfs://hadoop-master:9000/user/student/tp/a/b/vide.txt' to trash at: hdfs://hadoop-master:9000/user/root/.Trash/Current/user/student/tp/a/b/vide.txt\n", cap="trash")
pre(hm, HM, "hdfs dfs -mv /user/root/.Trash/Current/user/student/tp/a/b/vide.txt /user/student/tp/a/b/", "", P2,
    "fs.trash.interval = 1440 : le fichier est dans la corbeille (de root, qui exécute les commandes) ; on le restaure avec -mv.")
tcon(hm, HM, P2, "2.5 Snapshots : rendez /user/student/snap « snapshottable ».", ["hdfs dfsadmin -allowSnapshot /user/student/snap"], "Allowing snapshot on /user/student/snap succeeded\n")
tcon(hm, HM, P2, "Créez le snapshot s1.", ["hdfs dfs -createSnapshot /user/student/snap s1"], "Created snapshot /user/student/snap/.snapshot/s1\n")
tcon(hm, HM, P2, "« Accident » : suppression définitive, sans corbeille.", ["hdfs dfs -rm -skipTrash /user/student/snap/restaurants.csv"], "Deleted /user/student/snap/restaurants.csv\n")
tcon(hm, HM, P2, "Le fichier existe toujours dans le snapshot.", ["hdfs dfs -ls /user/student/snap/.snapshot/s1"],
     "Found 1 items\n-rw-r--r--   3 root supergroup    3809818 2026-11-14 14:12 /user/student/snap/.snapshot/s1/restaurants.csv\n")
tcon(hm, HM, P2, "Restaurez-le depuis s1.", ["hdfs dfs -cp /user/student/snap/.snapshot/s1/restaurants.csv /user/student/snap/"], "", cap="snapshot")

# ================================================================= Partie 3
P3 = "3 · Blocs et panne"
sclear(hm)
FSCK = f"""Connecting to namenode via http://hadoop-master:9870/fsck?ugi=root&files=1&blocks=1&locations=1&path=%2Fuser%2Fstudent%2Finput%2Frestaurants.csv
FSCK started by root (auth:SIMPLE) from /172.19.0.2 for path /user/student/input/restaurants.csv at Sat Nov 14 14:14:20 CET 2026

/user/student/input/restaurants.csv {SIZE} bytes, replicated: replication=3, 1 block(s):  OK
0. BP-1388419054-172.19.0.2-1794660318861:blk_1073741825_1001 len={SIZE} Live_repl=3  [DatanodeInfoWithStorage[172.19.0.3:9866,DS-6f1c2a0e,DISK], DatanodeInfoWithStorage[172.19.0.5:9866,DS-a83d41b7,DISK], DatanodeInfoWithStorage[172.19.0.4:9866,DS-2c9e07f4,DISK]]

Status: HEALTHY
 Number of data-nodes:	3
 Number of racks:		1
 Total dirs:			0
 Total symlinks:		0
""".replace("\t", "    ")
tcon(hm, HM, P3, "Examinez les blocs du CSV.", ["hdfs fsck /user/student/input/restaurants.csv -files -blocks -locations"], FSCK, cap="fsck")
tcon(hm, HM, P3, "3,7 Mo < 128 Mo : 1 seul bloc, 3 répliques sur les 3 DataNodes. Générez un fichier d'environ 22 Mo.",
     ["seq 1 3000000 > /tmp/gros.txt && ls -lh /tmp/gros.txt"], "-rw-r--r-- 1 root root 22M Nov 14 14:15 /tmp/gros.txt\n")
tcon(hm, HM, P3, "Écrivez-le avec des blocs de 1 Mo.", ["hdfs dfs -D dfs.blocksize=1048576 -put /tmp/gros.txt /user/student/blocs/"], "")
NB = math.ceil(22888896 / 1048576)
tcon(hm, HM, P3, "Comptez les blocs et la réplication moyenne.", ["hdfs fsck /user/student/blocs/gros.txt | grep -E \"Total blocks|Average block replication\""],
     f" Total blocks (validated):	{NB} (avg. block size 1040404 B)\n Average block replication:	3.0\n".replace("\t", "    "), cap="blocs")
sclear(hm)
tcon(hm, VM if False else HM, P3, f"{NB} blocs × 3 répliques = {NB*3} copies réparties sur les DataNodes. Simulez une panne : quittez le conteneur.", ["exit"], "exit\n")
tcon(hm, VM, P3, "Depuis la VM, arrêtez hadoop-worker1.", ["docker stop hadoop-worker1"], "hadoop-worker1\n")
tcon(hm, VM, P3, "Relisez la dernière ligne du fichier depuis le master.", ["docker exec hadoop-master bash -c \"hdfs dfs -cat /user/student/blocs/gros.txt | tail -1\""], "3000000\n")
REP2 = "Live datanodes (2):\nName: 172.19.0.4:9866 (hadoop-worker2.tp5-hadoop_default)\nName: 172.19.0.5:9866 (hadoop-worker3.tp5-hadoop_default)\nDead datanodes (1):\nName: 172.19.0.3:9866 (hadoop-worker1.tp5-hadoop_default)\n"
tcon(hm, VM, P3, "Lecture réussie grâce aux 2 autres répliques. Après environ 50 s, relisez le rapport.",
     ["docker exec hadoop-master bash -c \"hdfs dfsadmin -report | grep -E 'Live|Dead|^Name:'\""], REP2, cap="panne")
FS2 = f" Under-replicated blocks:	{NB + 1} ({round((NB+1)/(NB+1+2)*100, 2)} %)\n Mis-replicated blocks:		0 (0.0 %)\nStatus: HEALTHY\n".replace("\t", "    ")
tcon(hm, VM, P3, "worker1 déclaré mort (recheck-interval réduit à 10 s). Cherchez les blocs sous-répliqués.",
     ["docker exec hadoop-master bash -c \"hdfs fsck / | grep -i -E 'under|mis-replicated|Status'\""], FS2)
tcon(hm, VM, P3, f"Blocs à 2 répliques sur 3 : sans 4e nœud, pas de ré-réplication possible. Redémarrez le worker.", ["docker start hadoop-worker1"], "hadoop-worker1\n")
REP3 = "Live datanodes (3):\nName: 172.19.0.3:9866 (hadoop-worker1.tp5-hadoop_default)\nName: 172.19.0.4:9866 (hadoop-worker2.tp5-hadoop_default)\nName: 172.19.0.5:9866 (hadoop-worker3.tp5-hadoop_default)\n"
tcon(hm, VM, P3, "Une minute plus tard (block report), vérifiez.", ["docker exec hadoop-master bash -c \"hdfs dfsadmin -report | grep -E 'Live|Dead|^Name:'\""], REP3, cap="retour")

# ================================================================= Partie 4
P4 = "4 · YARN"
sclear(hm)
tcon(hm, VM, P4, "3 DataNodes, 0 bloc sous-répliqué. Revenez dans le master pour YARN.", ["docker exec -it hadoop-master bash"], "")
JAR = "$HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.6.jar"
pre(hm, HM, f"hadoop jar {JAR} pi \\\n  -Dmapreduce.map.memory.mb=8192 4 1000",
    "Number of Maps  = 4\nSamples per Map = 1000\nWrote input for Map #0\nWrote input for Map #1\nWrote input for Map #2\nWrote input for Map #3\nStarting Job\n"
    "2026-11-14 14:19:41,305 ERROR security.UserGroupInformation: PriviledgedActionException as:root cause:java.io.IOException: org.apache.hadoop.yarn.exceptions.InvalidResourceRequestException: Invalid resource request! Cannot allocate containers as requested resource is greater than maximum allowed allocation. Requested resource type=[memory-mb], Requested resource=<memory:8192, vCores:1>, maximum allowed allocation=<memory:2048, vCores:2>\n",
    P4, "4.3 : 8192 Mo par map > yarn.scheduler.maximum-allocation-mb (2048) : InvalidResourceRequestException.", cap="pi_ko")
PI = halton_pi(4, 1000)
sclear(hm)
pre(hm, HM, f"hadoop jar {JAR} pi \\\n  -Dmapreduce.map.memory.mb=512 4 1000",
    "Number of Maps  = 4\nSamples per Map = 1000\nStarting Job\n2026-11-14 14:20:12,881 INFO impl.YarnClientImpl: Submitted application application_1794660372418_0001\n"
    "2026-11-14 14:20:12,935 INFO mapreduce.Job: Running job: job_1794660372418_0001\n2026-11-14 14:20:31,226 INFO mapreduce.Job:  map 100% reduce 0%\n"
    "2026-11-14 14:20:37,302 INFO mapreduce.Job:  map 100% reduce 100%\n2026-11-14 14:20:38,331 INFO mapreduce.Job: Job job_1794660372418_0001 completed successfully\n"
    "\t\tLaunched map tasks=4\n\t\tLaunched reduce tasks=1\n".replace("\t", "    ") + f"Job Finished in 27.214 seconds\nEstimated value of Pi is {PI}\n",
    P4, f"Avec 512 Mo : 4 maps + 1 reduce, job réussi. Estimated value of Pi is {PI} (séquence de Halton, déterministe).", cap="pi_ok")
APPS = """Total number of applications (application-types: [], states: [NEW, NEW_SAVING, SUBMITTED, ACCEPTED, RUNNING, FINISHED, FAILED, KILLED] and tags: []):1
                Application-Id      Application-Name        Application-Type          User           Queue                   State             Final-State             Progress                        Tracking-URL
application_1794660372418_0001       QuasiMonteCarlo               MAPREDUCE          root         default                FINISHED               SUCCEEDED                 100% http://hadoop-master:19888/jobhistory/job/job_1794660372418_0001
"""
tcon(hm, HM, P4, "Listez toutes les applications YARN.", ["yarn application -list -appStates ALL"], APPS, cap="apps")

# ================================================================= Partie 5
P5 = "5 · MapReduce Streaming"
sclear(hm)
tcon(hm, HM, P5, "QuasiMonteCarlo FINISHED / SUCCEEDED. 5.2 : testez d'abord mapper et reducer en local, avec des tubes Unix.",
     ["cat /tmp/restaurants.csv | python3 /opt/scripts/mapper.py | sort | python3 /opt/scripts/reducer.py"], CITY, cap="local")
pre(hm, HM, "hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-3.3.6.jar \\\n  -files /opt/scripts/mapper.py,/opt/scripts/reducer.py \\\n  -mapper \"python3 mapper.py\" -reducer \"python3 reducer.py\" \\\n  -input /user/student/mr/restaurants.csv -output /user/student/mr/output_city",
    "2026-11-14 14:23:05,117 INFO mapreduce.Job: Running job: job_1794660372418_0002\n2026-11-14 14:23:29,563 INFO mapreduce.Job: Job job_1794660372418_0002 completed successfully\n"
    "\t\tLaunched map tasks=2\n\t\tLaunched reduce tasks=1\n\t\tMap input records=80001\n\t\tMap output records=80000\n\t\tReduce input records=80000\n\t\tReduce output records=12\n".replace("\t", "    ")
    + "2026-11-14 14:23:29,701 INFO streaming.StreamJob: Output directory: /user/student/mr/output_city\n",
    P5, "Même traitement sur le cluster (Hadoop Streaming) : 80 001 lignes lues (en-tête comprise), 80 000 émises, 12 villes en sortie.", cap="streaming")
tcon(hm, HM, P5, "Lisez le résultat du job.", ["hdfs dfs -cat /user/student/mr/output_city/part-00000"], CITY, cap="output_city")
sclear(hm)
tcon(hm, HM, P5, "Identique au test local. 5.3 c : note moyenne par cuisine (reducer complété : division par l'effectif n).",
     ["cat /tmp/restaurants.csv | python3 /opt/scripts/mapper_cuisine.py | sort | python3 /opt/scripts/reducer_moyenne.py"], CUIS, cap="cuisine")
show(hm.html(HM, cursor=False), P5, "Piège : réutiliser ce reducer comme combiner ferait une moyenne de moyennes. Version _v2 : émettre somme,effectif.", 8500)

# ================================================================= Partie 6
P6 = "6 · Spark sur YARN"
sclear(hm)
SPI = "Pi is roughly 3.1414631141463113"
pre(hm, HM, "spark-submit --class org.apache.spark.examples.SparkPi \\\n  --master yarn --deploy-mode client \\\n  $SPARK_HOME/examples/jars/spark-examples_2.12-3.5.3.jar 100",
    "2026-11-14 14:26:44,102 INFO yarn.Client: Submitting application application_1794660372418_0004 to ResourceManager\n"
    "2026-11-14 14:26:58,570 INFO scheduler.DAGScheduler: Job 0 finished: reduce at SparkPi.scala:38, took 6.874512 s\n" + SPI + "\n",
    P6, "spark-defaults.conf : spark.master = yarn, archive des jars dans HDFS, journaux dans hdfs:///spark-logs. SparkPi tourne sur YARN.", cap="sparkpi")
tcon(hm, HM, P6, "6.4 : Spark lit le CSV dans HDFS et compte les restaurants par ville.", ["spark-submit --master yarn --deploy-mode client /opt/scripts/spark_rdd.py"],
     "2026-11-14 14:28:02,331 INFO yarn.Client: Submitting application application_1794660372418_0005 to ResourceManager\n2026-11-14 14:28:15,904 INFO scheduler.DAGScheduler: Job 1 finished: runJob at SparkHadoopWriter.scala:83, took 3.412806 s\n")
tcon(hm, HM, P6, "Lisez la sortie écrite dans HDFS.", ["hdfs dfs -cat /user/student/spark_output/part-*"], SPARK + "\n", cap="spark_out")

# ================================================================= Partie 7
P7 = "7 · Hive"
sclear(hm)
tcon(hm, HM, P7, "Mêmes 12 villes, mêmes effectifs (ordre non trié). Connectez-vous à HiveServer2 avec Beeline (Metastore PostgreSQL démarré).",
     ["beeline -u jdbc:hive2://hive-server:10000/default -n student"],
     "Connecting to jdbc:hive2://hive-server:10000/default\nConnected to: Apache Hive (version 3.1.3)\nDriver: Hive JDBC (version 3.1.3)\nTransaction isolation: TRANSACTION_REPEATABLE_READ\nBeeline version 3.1.3 by Apache Hive\n")
tcon(hm, BL, P7, "Créez la base rsi3.", ["CREATE DATABASE IF NOT EXISTS rsi3;", "create database if not exists rsi3;"], "No rows affected (0.412 seconds)\n")
tcon(hm, BL, P7, "Utilisez-la.", ["USE rsi3;", "use rsi3;"], "No rows affected (0.058 seconds)\n")
pre(hm, BR, "CREATE EXTERNAL TABLE restaurants (\nrestaurant_id INT, name STRING, city STRING, cuisine STRING,\nrating DOUBLE, price_range STRING)\nROW FORMAT DELIMITED FIELDS TERMINATED BY ','\nSTORED AS TEXTFILE\nLOCATION '/user/student/input'\nTBLPROPERTIES ('skip.header.line.count'='1');",
    "No rows affected (0.287 seconds)\n", P7, "Table EXTERNE posée sur /user/student/input : Hive décrit le CSV sans le déplacer ; l'en-tête est ignoré.", cap="hive_table")
tcon(hm, BR, P7, "Comptez les lignes.", ["SELECT COUNT(*) AS total FROM restaurants;", "select count(*) as total from restaurants;", "SELECT COUNT(*) FROM restaurants;"],
     bee(["total"], [[80000]], "24.618") + "\n", cap="hive_count")
CQ = "SELECT city, COUNT(*) AS nb_restaurants FROM restaurants GROUP BY city ORDER BY nb_restaurants DESC;"
tcon(hm, BR, P7, "80 000, comme Spark. Restaurants par ville (job MapReduce lancé par Hive).", [CQ, CQ.lower().replace("count(*) as nb_restaurants", "count(*) as nb_restaurants")],
     bee(["city", "nb_restaurants"], sorted(cities, key=lambda c: -int(c[1])), "41.205") + "\n", cap="hive_city")
sclear(hm)
AQ = "SELECT cuisine, ROUND(AVG(rating), 2) AS moyenne FROM restaurants GROUP BY cuisine;"
tcon(hm, BR, P7, "Mêmes effectifs que Streaming et Spark. Note moyenne par cuisine.", [AQ, AQ.lower()],
     bee(["cuisine", "moyenne"], [[c, havg(c)] for c, _ in cuis], "26.734") + "\n", cap="hive_avg")
PQ = "SELECT price_range, COUNT(*) AS nb FROM restaurants GROUP BY price_range ORDER BY nb DESC;"
tcon(hm, BR, P7, "Mêmes moyennes que reducer_moyenne.py. Exercice : restaurants par gamme de prix.", [PQ, PQ.lower()],
     bee(["price_range", "nb"], [[p, n] for p, n in prices], "39.880") + "\n", cap="hive_price")
show(hm.html(BR, cursor=False), "Fin", "Validation : HDFS, YARN, MapReduce, Streaming, Spark et Hive donnent les mêmes résultats sur restaurants.csv. Hive et Spark s'appuient sur HDFS et YARN.", 10000)
