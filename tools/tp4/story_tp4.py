"""Scénario TP4 Cassandra : cluster Docker à 3 nœuds, CQL (keyspace, tables, CRUD), observation du cluster.
Réel : docker --version / compose version / compose up -d et journaux (logs du PC de Youssef), tokens Murmur3 calculés.
Reconstitué : sorties cqlsh / nodetool (format exact de Cassandra 4.1)."""
import re, struct
from screens import *
from cassandra.murmur3 import murmur3

LOGD = "/mnt/user-data/uploads/TP/TP4_Cassandra/Simulation_Docker/logs/"
DIRP = "PS C:\\Users\\ASUS\\Desktop\\terminal\\BigData_Avance\\TP\\TP4_Cassandra\\Simulation_Docker> "
CQ, CK = "cqlsh> ", "cqlsh:rsi3_bibliotheque> "
IP = {"cassandra1": "172.18.0.2", "cassandra2": "172.18.0.4", "cassandra3": "172.18.0.3"}
HID = {"cassandra1": "3f6c1a2e-8b4d-4e1f-9a57-2c0d6e9b1a43", "cassandra2": "a81d5c07-4f2e-49b3-b6c8-71e0f3d29c15", "cassandra3": "d2b94e61-0c7a-4a8f-85d3-9e46b17f0c28"}

slides = []
def sclear(c):
    """Efface l'écran en gardant la dernière commande et sa sortie."""
    ps = [E(p) for p in (DIRP, CQ, CK)]
    idx = [i for i, l in enumerate(c.lines) if any(l.startswith(p) for p in ps)]
    if idx: c.lines = c.lines[idx[-1]:]
LOG = []   # (prompt, cmd, out, cap) pour le compte rendu
def dur(text, base=3200): return max(5200, min(11000, base + 55 * len(text)))
def show(html, step, text, d=None, cap=None): slides.append(dict(html=html, step=step, text=text, kind="show", dur=d or dur(text), cap=cap))
def tcon(con, prompt, step, text, answers, out=None, mongo=False, cap=None):
    slides.append(dict(html=con.html(prompt), step=step, text=text, kind="type", x=prompt_x(prompt), answers=answers, cap=cap))
    LOG.append((prompt, answers[0], out or "", cap))
    con.add_cmd(prompt, answers[0])
    if out is not None: con.add_out(out, mongo=mongo)
def pre(con, prompt, cmd, out, step, text, cap=None):
    """Commande longue déjà tapée (multi-lignes) : diapo commentée."""
    LOG.append((prompt, cmd, out or "", cap))
    for j, l in enumerate(cmd.split("\n")):
        if j == 0: con.add_cmd(prompt, l)
        else: con.add_raw('<span class="w">' + E(("   ... " if prompt != DIRP else "") + l) + "</span>")
    if out is not None: con.add_out(out)
    show(con.html(prompt, cursor=False), step, text, cap=cap)

def table(cols, rows):
    """Format exact de cqlsh : en-têtes alignés à gauche, valeurs à droite."""
    w = [max(len(c), *(len(r[i]) for r in rows)) if rows else len(c) for i, c in enumerate(cols)]
    out = ["", " " + " | ".join(c.ljust(w[i]) for i, c in enumerate(cols)), "-" + "-+-".join("-" * x for x in w) + "-"]
    out += [" " + " | ".join(r[i].rjust(w[i]) for i in range(len(cols))) for r in rows]
    out += ["", f"({len(rows)} rows)" if len(rows) != 1 else "(1 rows)", ""]
    return "\n".join(out)

def nodetool_status(states, ks=True):
    load = {"cassandra1": "118.62 KiB", "cassandra2": "112.37 KiB", "cassandra3": "109.95 KiB"}
    hdr = "Datacenter: datacenter1\n=======================\nStatus=Up/Down\n|/ State=Normal/Leaving/Joining/Moving\n--  Address     Load        Tokens  Owns (effective)  Host ID                               Rack"
    lines = [f"{states[n]}  {IP[n]:<11} {load[n]:<11} 16      {'100.0%' if ks else '?':<17} {HID[n]}  rack1" for n in ["cassandra1", "cassandra3", "cassandra2"]]
    note = "" if ks else "\n\nNote: Non-system keyspaces don't have the same replication settings, effective ownership information is meaningless"
    return hdr + "\n" + "\n".join(lines) + note + "\n"

LA = [("154", "2154889522", "Goscinny", "Rene", "Asterix et Cleopatre"), ("987", "2154889589", "Bruchez", "Rudi", "NoSQL"),
      ("987", "2154889597", "Bruchez", "Rudi", "Bases de donnees distribuees")]
CLA = ["id_auteur", "isbn", "nom_auteur", "prenom_auteur", "titre"]
CV = ["isbn", "date_vente", "id_vente", "montant", "quantite"]

# ================================================================= Introduction
show(title_card("TP 4 · Cassandra : CQL, modélisation et cluster à 3 nœuds", "Docker Desktop, cqlsh, tables orientées requêtes et réplication RF = 3",
                ["Cluster ClusterRSI3 : 3 conteneurs cassandra:4.1 (docker compose)", "nodetool status : 3 nœuds UN (Up/Normal)",
                 "Keyspace rsi3_bibliotheque (RF = 3), tables livres_par_auteur et ventes_par_livre", "CRUD, ALLOW FILTERING et table livres_par_titre",
                 "Panne puis retour du nœud cassandra3"]),
     "Introduction", "TP4 – Cassandra. docker --version et compose up viennent de mon PC ; les sorties cqlsh et nodetool sont reconstituées (résultats attendus).", 9500)

# ================================================================= 1. Cluster
P1 = "1 · Cluster Docker"
ps = Console("Windows PowerShell", DIRP)
ps.add_out("Windows PowerShell\nCopyright (C) Microsoft Corporation. Tous droits réservés.\n")
tcon(ps, DIRP, P1, "Docker Desktop est démarré. Vérifiez la version de Docker.", ["docker --version"], "Docker version 29.8.1, build 4a63305\n")
tcon(ps, DIRP, P1, "Puis celle de Docker Compose.", ["docker compose version"], "Docker Compose version v5.5.1\n", cap="docker_version")
up = open(LOGD + "02a_compose_up.txt", encoding="utf-8-sig").read().split("\n")[1:]
seen, upl = set(), []
for l in up:
    if l.strip() and l not in seen and "Pulling fs layer" not in l:
        seen.add(l); upl.append(l)
tcon(ps, DIRP, P1, "Depuis le dossier de compose.yaml, créez et démarrez les 3 nœuds.", ["docker compose up -d"], "\n".join(upl) + "\n", cap="compose_up")
PSO = """NAME         IMAGE           COMMAND                  SERVICE      CREATED         STATUS         PORTS
cassandra1   cassandra:4.1   "docker-entrypoint.s…"   cassandra1   3 minutes ago   Up 3 minutes   7000-7001/tcp, 7199/tcp, 9160/tcp, 0.0.0.0:9042->9042/tcp, [::]:9042->9042/tcp
cassandra2   cassandra:4.1   "docker-entrypoint.s…"   cassandra2   3 minutes ago   Up 3 minutes   7000-7001/tcp, 7199/tcp, 9042/tcp, 9160/tcp
cassandra3   cassandra:4.1   "docker-entrypoint.s…"   cassandra3   3 minutes ago   Up 3 minutes   7000-7001/tcp, 7199/tcp, 9042/tcp, 9160/tcp
"""
tcon(ps, DIRP, P1, "Volumes, réseau cassandra-net et conteneurs créés. Vérifiez les conteneurs.", ["docker compose ps"], PSO, cap="compose_ps")
UN3 = {"cassandra1": "UN", "cassandra2": "UN", "cassandra3": "UN"}
tcon(ps, DIRP, P1, "Trois conteneurs Up ; seul cassandra1 publie le port CQL 9042. Après quelques minutes, affichez l'état Cassandra.",
     ["docker exec -it cassandra1 nodetool status"], nodetool_status(UN3, ks=False), cap="status1")
tcon(ps, DIRP, P1, "3 nœuds UN (Up/Normal), 16 tokens chacun dans datacenter1. Ouvrez le shell CQL.", ["docker exec -it cassandra1 cqlsh"],
     "Connected to ClusterRSI3 at 127.0.0.1:9042\n[cqlsh 6.1.0 | Cassandra 4.1.10 | CQL spec 3.4.6 | Native protocol v5]\nUse HELP for help.\n")

# ================================================================= 2. CQL
P2 = "2 · Keyspace et tables"
pre(ps, CQ, "CREATE KEYSPACE IF NOT EXISTS rsi3_bibliotheque\nWITH replication = {'class': 'NetworkTopologyStrategy', 'datacenter1': 3}\nAND durable_writes = true;", "",
    P2, "6.1 : keyspace rsi3_bibliotheque, réplication RF = 3 dans datacenter1 (chaque ligne existe sur les 3 nœuds).")
tcon(ps, CQ, P2, "Utilisez ce keyspace.", ["USE rsi3_bibliotheque;", "use rsi3_bibliotheque;", "USE rsi3_bibliotheque"], "")
pre(ps, CK, "CREATE TABLE IF NOT EXISTS livres_par_auteur (\n  id_auteur int, isbn text, nom_auteur text, prenom_auteur text, titre text,\n  PRIMARY KEY ((id_auteur), isbn)\n) WITH CLUSTERING ORDER BY (isbn ASC);", "",
    P2, "6.2 : table conçue pour « livres d'un auteur » : clé de partition id_auteur, clustering isbn.")
ins = "\n".join(f"INSERT INTO livres_par_auteur (id_auteur, isbn, nom_auteur, prenom_auteur, titre) VALUES ({a}, '{i}', '{n}', '{p}', '{t}');" for a, i, n, p, t in LA)
for l in ins.split("\n"): ps.add_cmd(CK, l)
ps.add_out("")
show(ps.html(CK, cursor=False), P2, "Les 3 livres du script sont insérés (nom et prénom de l'auteur dupliqués dans chaque ligne : pas de jointure en CQL).", 8000)
tcon(ps, CK, P2, "Lisez les livres de l'auteur 987.", ["SELECT * FROM livres_par_auteur WHERE id_auteur = 987;", "select * from livres_par_auteur where id_auteur = 987;", "SELECT * FROM livres_par_auteur WHERE id_auteur=987;"],
     table(CLA, [r for r in LA if r[0] == "987"]), cap="sel987")
pre(ps, CK, "CREATE TABLE IF NOT EXISTS ventes_par_livre (\n  isbn text, date_vente date, id_vente int, quantite int, montant decimal,\n  PRIMARY KEY ((isbn), date_vente, id_vente)\n) WITH CLUSTERING ORDER BY (date_vente DESC, id_vente ASC);", "",
    P2, "6.3 : ventes d'un livre par date : partition isbn, clustering date_vente (décroissant) puis id_vente.")
V0 = [("2154889589", "2017-06-02", "12", "35.00", "1"), ("2154889589", "2017-09-12", "20", "70.00", "2")]
for v in V0:
    ps.add_cmd(CK, f"INSERT INTO ventes_par_livre (isbn, date_vente, id_vente, quantite, montant) VALUES ('{v[0]}', '{v[1]}', {v[2]}, {v[4]}, {v[3]});")
ps.add_out("")
sortv = lambda vs: sorted(vs, key=lambda v: (v[1], -int(v[2])), reverse=True)
tcon(ps, CK, P2, "2 ventes insérées. Affichez les ventes du livre 2154889589.", ["SELECT * FROM ventes_par_livre WHERE isbn = '2154889589';", "select * from ventes_par_livre where isbn = '2154889589';", "SELECT * FROM ventes_par_livre WHERE isbn='2154889589';"],
     table(CV, sortv(V0)), cap="selventes")

# ================================================================= 3. CRUD
P3 = "3 · CRUD et requêtes"
sclear(ps)
pre(ps, CK, "INSERT INTO livres_par_auteur (id_auteur, isbn, nom_auteur, prenom_auteur, titre)\nVALUES (154, '2154889530', 'Goscinny', 'Rene', 'Asterix le Gaulois');", "",
    P3, "Les dates sorties triées de la plus récente à la plus ancienne. Travail 1 : troisième livre pour l'auteur 154 (ISBN 2154889530).")
A154 = [r for r in LA if r[0] == "154"] + [("154", "2154889530", "Goscinny", "Rene", "Asterix le Gaulois")]
tcon(ps, CK, P3, "Travail 2 : affichez les livres de l'auteur 154.", ["SELECT * FROM livres_par_auteur WHERE id_auteur = 154;", "select * from livres_par_auteur where id_auteur = 154;", "SELECT * FROM livres_par_auteur WHERE id_auteur=154;"],
     table(CLA, sorted(A154, key=lambda r: r[1])), cap="sel154")
pre(ps, CK, "UPDATE livres_par_auteur SET titre = 'Asterix le Gaulois - Edition collector'\nWHERE id_auteur = 154 AND isbn = '2154889530';", "",
    P3, "2 lignes, triées par isbn. Travail 3 : UPDATE du titre, avec la clé primaire complète (id_auteur + isbn).")
tcon(ps, CK, P3, "Vérifiez la modification.", ["SELECT * FROM livres_par_auteur WHERE id_auteur = 154 AND isbn = '2154889530';", "select * from livres_par_auteur where id_auteur = 154 and isbn = '2154889530';"],
     table(CLA, [("154", "2154889530", "Goscinny", "Rene", "Asterix le Gaulois - Edition collector")]), cap="update")
tcon(ps, CK, P3, "Titre modifié. Travail 4 : supprimez ce livre.", ["DELETE FROM livres_par_auteur WHERE id_auteur = 154 AND isbn = '2154889530';", "delete from livres_par_auteur where id_auteur = 154 and isbn = '2154889530';"], "")
tcon(ps, CK, P3, "Vérifiez sa disparition.", ["SELECT * FROM livres_par_auteur WHERE id_auteur = 154;", "select * from livres_par_auteur where id_auteur = 154;", "SELECT * FROM livres_par_auteur WHERE id_auteur=154;"],
     table(CLA, [LA[0]]), cap="delete")
sclear(ps)
pre(ps, CK, "INSERT INTO ventes_par_livre (isbn, date_vente, id_vente, quantite, montant)\nVALUES ('2154889589', '2017-11-20', 25, 3, 105.00);", "",
    P3, "Seul « Asterix et Cleopatre » reste. Travail 5 : nouvelle vente pour le livre 2154889589.")
V1 = V0 + [("2154889589", "2017-11-20", "25", "105.00", "3")]
tcon(ps, CK, P3, "Affichez toutes ses ventes.", ["SELECT * FROM ventes_par_livre WHERE isbn = '2154889589';", "select * from ventes_par_livre where isbn = '2154889589';", "SELECT * FROM ventes_par_livre WHERE isbn='2154889589';"],
     table(CV, sortv(V1)), cap="vente")
ERR = 'InvalidRequest: Error from server: code=2200 [Invalid query] message="Cannot execute this query as it might involve data filtering and thus may have unpredictable performance. If you want to execute this query despite the performance unpredictability, use ALLOW FILTERING"\n'
tcon(ps, CK, P3, "La vente du 20/11 apparaît en tête. Travail 6 : cherchez un livre par titre, sans id_auteur.",
     ["SELECT * FROM livres_par_auteur WHERE titre = 'NoSQL';", "select * from livres_par_auteur where titre = 'NoSQL';", "SELECT * FROM livres_par_auteur WHERE titre='NoSQL';"], ERR, cap="filtering")
tcon(ps, CK, P3, "Refusé : titre n'est pas dans la clé, Cassandra devrait parcourir toutes les partitions. Forcez avec ALLOW FILTERING.",
     ["SELECT * FROM livres_par_auteur WHERE titre = 'NoSQL' ALLOW FILTERING;", "select * from livres_par_auteur where titre = 'NoSQL' allow filtering;"], table(CLA, [LA[1]]))
sclear(ps)
pre(ps, CK, "CREATE TABLE IF NOT EXISTS livres_par_titre (\n  titre text, isbn text, id_auteur int, nom_auteur text, prenom_auteur text,\n  PRIMARY KEY ((titre), isbn)\n);", "",
    P3, "Ça marche mais scanne tout le cluster. Travail 7 : une table dédiée, partitionnée par titre.")
bat = "BEGIN BATCH\n" + "\n".join(f"  INSERT INTO livres_par_titre (titre, isbn, id_auteur, nom_auteur, prenom_auteur) VALUES ('{t}', '{i}', {a}, '{n}', '{p}');" for a, i, n, p, t in LA) + "\nAPPLY BATCH;"
pre(ps, CK, bat, "", P3, "Alimentation par BATCH logué : les deux tables restent cohérentes.")
tcon(ps, CK, P3, "Recherche par titre, sans ALLOW FILTERING.", ["SELECT * FROM livres_par_titre WHERE titre = 'NoSQL';", "select * from livres_par_titre where titre = 'NoSQL';", "SELECT * FROM livres_par_titre WHERE titre='NoSQL';"],
     table(["titre", "isbn", "id_auteur", "nom_auteur", "prenom_auteur"], [("NoSQL", "2154889589", "987", "Bruchez", "Rudi")]), cap="partitre")
tok = sorted([(murmur3(struct.pack(">i", int(a))), a, i) for a, i, *_ in LA], key=lambda x: x[0])
tcon(ps, CK, P3, "Une seule partition lue. Bonus : affichez le token Murmur3 de chaque clé de partition.",
     ["SELECT token(id_auteur), id_auteur, isbn FROM livres_par_auteur;", "select token(id_auteur), id_auteur, isbn from livres_par_auteur;"],
     table(["system.token(id_auteur)", "id_auteur", "isbn"], [(str(t), a, i) for t, a, i in tok]), cap="token")
tcon(ps, CK, P3, "Le token détermine les nœuds responsables de chaque partition. Quittez cqlsh.", ["exit", "exit;", "quit", "quit;"], "")

# ================================================================= 4. Cluster
P4 = "4 · Observation du cluster"
sclear(ps)
tcon(ps, DIRP, P4, "Revoyez l'état du cluster pour le keyspace du TP.", ["docker exec -it cassandra1 nodetool status rsi3_bibliotheque", "docker exec -it cassandra1 nodetool status"],
     nodetool_status(UN3), cap="status_ks")
DC = f"""Cluster Information:
\tName: ClusterRSI3
\tSnitch: org.apache.cassandra.locator.GossipingPropertyFileSnitch
\tDynamicEndPointSnitch: enabled
\tPartitioner: org.apache.cassandra.dht.Murmur3Partitioner
\tSchema versions:
\t\t8a3b6f21-5c4e-3d07-9f12-b6e04a7c2d91: [{IP['cassandra1']}, {IP['cassandra3']}, {IP['cassandra2']}]

Stats for all nodes:
\tLive: 3
\tJoining: 0
\tMoving: 0
\tLeaving: 0
\tUnreachable: 0

Data Centers:
\tdatacenter1 #Nodes: 3 #Down: 0

Database versions:
\t4.1.10: [{IP['cassandra1']}:7000, {IP['cassandra3']}:7000, {IP['cassandra2']}:7000]

Keyspaces:
\tsystem_auth -> Replication class: SimpleStrategy {{replication_factor=1}}
\tsystem_distributed -> Replication class: SimpleStrategy {{replication_factor=3}}
\tsystem_traces -> Replication class: SimpleStrategy {{replication_factor=2}}
\trsi3_bibliotheque -> Replication class: NetworkTopologyStrategy {{datacenter1=3}}
\tsystem_schema -> Replication class: LocalStrategy {{}}
\tsystem -> Replication class: LocalStrategy {{}}
""".replace("\t", "        ")
tcon(ps, DIRP, P4, "Avec RF = 3, chaque nœud possède 100 % des données. Décrivez le cluster.", ["docker exec -it cassandra1 nodetool describecluster"], DC, cap="describe")
raw = open(LOGD + "99_logs_erreur.txt", encoding="utf-8-sig").read().split("\n")
c2 = [l for l in raw if l.startswith("cassandra2")]
keep = [l for l in c2 if any(k in l for k in ["state jump to NORMAL", "No gossip backlog", "Ensured sufficient", "Starting listening for CQL", "Startup complete", "changing ownership"])][:8]
tcon(ps, DIRP, P4, "Un seul schéma, 3 nœuds vivants, rsi3_bibliotheque en NetworkTopologyStrategy. Consultez les journaux de cassandra2.",
     ["docker compose logs --tail=50 cassandra2"], "\n".join(l[:300] for l in keep) + "\n", cap="logs")
sclear(ps)
tcon(ps, DIRP, P4, "Extrait réel : cassandra2 passe NORMAL puis « Startup complete ». Arrêtez le troisième nœud.", ["docker stop cassandra3"], "cassandra3\n")
DN = dict(UN3, cassandra3="DN")
tcon(ps, DIRP, P4, "Relancez nodetool status.", ["docker exec -it cassandra1 nodetool status rsi3_bibliotheque", "docker exec -it cassandra1 nodetool status"], nodetool_status(DN), cap="status_dn")
tcon(ps, DIRP, P4, "cassandra3 passe DN (Down/Normal) : les 2 autres répliques servent toujours les lectures et écritures (QUORUM = 2 sur 3). Redémarrez-le.",
     ["docker start cassandra3"], "cassandra3\n")
tcon(ps, DIRP, P4, "Attendez une minute puis vérifiez son retour.", ["docker exec -it cassandra1 nodetool status rsi3_bibliotheque", "docker exec -it cassandra1 nodetool status"], nodetool_status(UN3), cap="status_back")
show(ps.html(DIRP, cursor=False), "Fin", "cassandra3 est de nouveau UN et rattrape les écritures manquées (hinted handoff). Limite : les 3 nœuds partagent le même PC.", 9500)
