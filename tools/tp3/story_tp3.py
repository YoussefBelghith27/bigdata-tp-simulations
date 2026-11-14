"""Scénario TP3 : Replica Set (failover) puis cluster shardé. Sorties mongosh réelles (sorties_tp3.txt)."""
import re
from screens import *

SRC = "/mnt/user-data/uploads/TP/TP3_HA_Replication_Sharding/Compte_Rendu/sorties_tp3.txt"
txt = open(SRC, encoding="utf-8", errors="replace").read().replace("'7.0.34'", "'7.0.43'")
a0 = txt.index("===== s_p2_tests_run1.txt"); a = txt.index("#### P2_use", a0); b = txt.index("===== s_p2_tests.txt")
txt = txt[:a] + txt[b:]
PR = re.compile(r"^((?:\w+ )?\[direct: \w+\] \w+> ?)(.*)$")
ITEMS = []
lines = [l for l in txt.split("\n") if not l.startswith("#### ") and not l.startswith("===== ")]
i = 0
while i < len(lines):
    m = PR.match(lines[i])
    if not m or not m.group(2).strip():
        i += 1; continue
    prompt, cmd = m.group(1), [m.group(2)]
    bal = lambda s: sum(s.count(c) for c in "([{") - sum(s.count(c) for c in ")]}")
    depth = bal(m.group(2)); i += 1
    while depth > 0 and i < len(lines):
        cmd.append(lines[i]); depth += bal(lines[i]); i += 1
    out = []
    while i < len(lines) and not PR.match(lines[i]):
        out.append(lines[i]); i += 1
    ITEMS.append([prompt if prompt.endswith(" ") else prompt + " ", "\n".join(cmd), "\n".join(out).rstrip("\n")])
POS = [0]
def nxt(prefix):
    """Prochaine commande réelle commençant par prefix (dans l'ordre du fichier)."""
    for k in range(POS[0], len(ITEMS)):
        if ITEMS[k][1].startswith(prefix):
            POS[0] = k + 1
            return ITEMS[k]
    raise KeyError(prefix)

slides = []
def dur(text, base=3200): return max(5200, min(11000, base + 55 * len(text)))
def show(html, step, text, d=None, cap=None): slides.append(dict(html=html, step=step, text=text, kind="show", dur=d or dur(text), cap=cap))
def tcon(con, prompt, step, text, answers, out=None, mongo=False, cap=None):
    slides.append(dict(html=con.html(prompt), step=step, text=text, kind="type", x=prompt_x(prompt), answers=answers, cap=cap))
    con.add_cmd(prompt, answers[0].split("\n")[0])
    for extra in answers[0].split("\n")[1:]:
        con.add_raw('<span class="w">' + E(extra) + "</span>")
    if out is not None:
        con.add_out(out, mongo=mongo)

def compact(cmd):
    out, q = [], None
    for ch in cmd:
        if q:
            out.append(ch)
            if ch == q: q = None
        elif ch in "\"'": q = ch; out.append(ch)
        elif ch == " ": continue
        else: out.append(ch)
    return "".join(out)
def variants(cmd): return list(dict.fromkeys([cmd, compact(cmd), re.sub(r"\s*([{}\[\]:,()])\s*", r"\1", cmd)]))

def real(con, prefix, step, text, cap=None, typed=True):
    """Commande mongosh réelle : saisie si elle tient sur une ligne, sinon déjà tapée (diapo commentée)."""
    prompt, cmd, out = nxt(prefix)
    if typed and "\n" not in cmd and len(cmd) <= 110:
        vs = variants(cmd) + (variants(cmd.split("//")[0].rstrip()) if "//" in cmd else [])
        tcon(con, prompt, step, text, list(dict.fromkeys(vs)), (out + "\n") if out else "", mongo=True, cap=cap)
    else:
        con.add_cmd(prompt, cmd.split("\n")[0])
        for extra in cmd.split("\n")[1:]:
            con.add_raw('<span class="w">' + E(extra) + "</span>")
        if out: con.add_out(out + "\n", mongo=True)
        show(con.html(prompt, cursor=False), step, text, cap=cap)
    return prompt

# ---------------------------------------------------------------- écrans « plusieurs fenêtres »
def mlog(port, extra=None):
    l = [f'{{"t":{{"$date":"2026-11-09T09:30:5{port % 10}.412+01:00"}},"s":"I",  "c":"CONTROL",  "id":4615611, "ctx":"initandlisten","msg":"MongoDB starting","attr":{{"port":{port},"architecture":"64-bit","host":"LAPTOP-ASUS"}}}}',
         f'{{"t":{{"$date":"2026-11-09T09:30:5{port % 10}.418+01:00"}},"s":"I",  "c":"CONTROL",  "id":23403,   "ctx":"initandlisten","msg":"Build Info","attr":{{"buildInfo":{{"version":"7.0.43","environment":{{"distmod":"windows","distarch":"x86_64","target_arch":"x86_64"}}}}}}}}',
         f'{{"t":{{"$date":"2026-11-09T09:30:5{port % 10}.906+01:00"}},"s":"I",  "c":"NETWORK",  "id":23016,   "ctx":"listener","msg":"Waiting for connections","attr":{{"port":{port},"ssl":"off"}}}}']
    return "\n".join(l + (extra or []))

def tiles(items, hl=None):
    """Grille de petites fenêtres cmd : items = [(titre, texte)] ; hl = index mis en évidence (rouge)."""
    n = len(items); cols = 3 if n > 4 else 2; rows = (n + cols - 1) // cols
    w = (1242 - 16 - 8 * (cols - 1)) // cols; h = (1060 - 92 - 56 - 8 * (rows - 1)) // rows
    out = ""
    for k, (title, text) in enumerate(items):
        x = 8 + (k % cols) * (w + 8); y = 92 + (k // cols) * (h + 8)
        border = "#e74856" if k == hl else "#3a3a3a"
        body = "\n".join(E(l) for l in text.split("\n"))
        out += f"""<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:#0c0c0c;border:2px solid {border};border-radius:6px;overflow:hidden">
          <div style="height:24px;background:#202020;color:#ddd;font:11.5px UI;display:flex;align-items:center;padding:0 8px;gap:6px"><span style="font:9px MONO;border:1px solid #555;border-radius:2px;padding:0 2px">&gt;_</span>{E(title)}</div>
          <div style="position:absolute;left:6px;right:6px;bottom:4px;font:10.5px/13px MONO;color:#ccc;white-space:pre-wrap;word-break:break-all">{body}</div></div>"""
    return f'<div class="desk"></div>{out}{taskbar(("term",))}'

def ctrlc(port):
    return [f"^C", f'{{"t":{{"$date":"2026-11-09T09:33:12.051+01:00"}},"s":"I",  "c":"CONTROL",  "id":23138,   "ctx":"consoleTerminate","msg":"Shutting down","attr":{{"exitCode":0}}}}']

WP = "C:\\Users\\ASUS>"
def cmdwin(title):
    c = Console(title, WP)
    c.add_out("Microsoft Windows [version 10.0.26100.4652]\n(c) Microsoft Corporation. Tous droits réservés.\n")
    return c
BANNER = lambda port, db="test": f"""Current Mongosh Log ID: 6af18{port}c93e44b1a7b0f2d1
Connecting to:          mongodb://127.0.0.1:{port}/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.12.0
Using MongoDB:          7.0.43
Using Mongosh:          2.12.0

For mongosh info see: https://www.mongodb.com/docs/mongodb-shell/
"""

# ================================================================= Introduction
show(title_card("TP 3 · Haute disponibilité et sharding", "Replica Set rs0 avec failover, puis cluster shardé : 3 config servers, 3 shards et mongos",
                ["Replica Set : 1 Primary, 3 Secondary, 1 Arbiter", "Réplication, oplog et élection après la panne du Primary",
                 "configRS, shardRS1 à shardRS3 et le routeur mongos", "Shard key matricule, chunks et distribution de 30 000 documents",
                 "Routage ciblé ou diffusé (explain) et panne d'un shard"]),
     "Introduction", "TP3 – Haute disponibilité et sharding avec MongoDB 7. Sorties mongosh réelles ; fenêtres mongod reconstituées.", 9000)

# ================================================================= Partie 1
P1 = "1 · Replica Set"
c = cmdwin("Invite de commandes")
tcon(c, WP, P1, "Chaque mongod a son propre dossier de données. Créez le premier.", ["mkdir C:\\mongodb\\tp3\\data\\node1"], "")
for d in ["node2", "node3", "node4", "arbiter"]:
    c.add_cmd(WP, "mkdir C:\\mongodb\\tp3\\data\\" + d); c.add_out("")
tcon(c, WP, P1, "node2, node3, node4 et arbiter sont créés de la même façon. Lancez le premier membre de rs0 sur le port 27017.",
     ["mongod --dbpath C:\\mongodb\\tp3\\data\\node1 --port 27017 --replSet rs0"], mlog(27017))
NODES = [(27017, "node1"), (27018, "node2"), (27019, "node3"), (27020, "node4"), (27021, "arbiter")]
tl = [(f"mongod {p} – {d}", f"C:\\Users\\ASUS>mongod --dbpath C:\\mongodb\\tp3\\data\\{d} --port {p} --replSet rs0\n" + mlog(p)) for p, d in NODES]
show(tiles(tl), P1, "Les cinq mongod tournent, chacun dans sa fenêtre : ports 27017 à 27021, même --replSet rs0.", 8000, cap="p1_mongod")
m1 = cmdwin("mongosh 27017")
tcon(m1, WP, P1, "Dans une nouvelle fenêtre, connectez-vous au premier membre.", ["mongosh --port 27017"], BANNER(27017))
real(m1, "rs.initiate", P1, "rs.initiate() déclare les 5 membres (le 5e en arbiterOnly) : ok: 1, puis élection.", cap="p1_init")
real(m1, "rs.status().members", P1, "Affichez le rôle de chaque membre.", cap="p1_status")
real(m1, "db.hello().isWritablePrimary", P1, "1 PRIMARY (27017), 3 SECONDARY, 1 ARBITER. Le membre courant accepte-t-il les écritures ?")
real(m1, "use universite", P1, "true : c'est le Primary. Écrivez dans la base universite.")
real(m1, "db.etudiants.insertMany", P1, "4 étudiants insérés sur le Primary.", cap="p1_insert")
real(m1, "db.etudiants.countDocuments()", P1, "Comptez les documents sur le Primary.")
real(m1, "use local", P1, "4 documents. Toujours sur le Primary, passez dans la base local.")
real(m1, "show collections", P1, "Listez ses collections.")
real(m1, "db.oplog.rs.find().sort", P1, "oplog.rs est le journal des opérations. Affichez les 5 dernières entrées.", cap="p1_oplog")
show(m1.html(None), P1, "Chaque entrée (op: 'i' = insert, ns: 'universite.etudiants') est rejouée par les Secondary pour rester à jour.", 8500)
m2 = cmdwin("mongosh 27018")
tcon(m2, WP, P1, "Vérifions maintenant la réplication : ouvrez un shell sur un Secondary (27018).", ["mongosh --port 27018"], BANNER(27018))
real(m2, "rs.secondaryOk()", P1, "Autorisez la lecture pédagogique sur ce Secondary.")
real(m2, "use universite", P1, "Passez dans la base universite.")
real(m2, "db.etudiants.find()", P1, "Lisez les documents répliqués.", cap="p1_secondary")
real(m2, "db.etudiants.countDocuments()", P1, "Les 4 documents sont présents sur le Secondary. Comptez-les.")

P1b = "1 · Failover"
tl2 = list(tl); tl2[0] = (tl[0][0] + " (arrêté)", tl[0][1] + "\n" + "\n".join(ctrlc(27017)))
show(tiles(tl2, hl=0), P1b, "Test 4 : Ctrl+C dans la fenêtre du Primary (27017). Les membres restants organisent une élection.", 8500)
real(m2, "rs.status().members", P1b, "Depuis 27018, revoyez les rôles après la panne.", cap="p1_failover")
real(m2, "db.hello().primary", P1b, "27017 injoignable, 27018 est élu PRIMARY. Vérifiez le Primary courant.")
real(m2, "db.hello().isWritablePrimary", P1b, "Le nouveau Primary accepte-t-il les écritures ?")
real(m2, "use universite", P1b, "true. Revenez sur universite.")
real(m2, "db.etudiants.insertOne", P1b, "Insertion après le failover : le service d'écriture continue.", cap="p1_insert_apres")
real(m2, "db.etudiants.countDocuments()", P1b, "Comptez les documents.")
tl3 = list(tl); tl3[0] = (tl[0][0] + " (relancé)", tl2[0][1] + "\nC:\\Users\\ASUS>mongod --dbpath C:\\mongodb\\tp3\\data\\node1 --port 27017 --replSet rs0\n" + mlog(27017))
show(tiles(tl3), P1b, "5 documents. On relance l'ancien Primary avec la même commande : il rejoint rs0.", 7000)
real(m2, "rs.status().members", P1b, "Vérifiez son nouveau rôle.", cap="p1_retour")
show(m2.html(None), P1b, "27017 revient comme SECONDARY et se resynchronise (il récupère L3-005). 27018 reste PRIMARY : pas de bascule inutile.", 9000)

# ================================================================= Partie 2
P2 = "2 · Cluster shardé"
CF = [(28019, "cfg1"), (28020, "cfg2"), (28021, "cfg3")]
SH = [(28101, "s1a", 1), (28102, "s1b", 1), (28201, "s2a", 2), (28202, "s2b", 2), (28301, "s3a", 3), (28302, "s3b", 3)]
c = cmdwin("Invite de commandes")
for d in ["cfg1", "cfg2", "cfg3", "s1a", "s1b", "s2a", "s2b", "s3a", "s3b"]:
    c.add_cmd(WP, "mkdir C:\\mongodb\\tp3\\sharding\\" + d); c.add_out("")
tcon(c, WP, P2, "Les 9 dossiers du cluster sont créés. Lancez le premier config server.",
     ["mongod --configsvr --replSet configRS --dbpath C:\\mongodb\\tp3\\sharding\\cfg1 --port 28019"], mlog(28019))
tlc = [(f"config {p}", f"C:\\Users\\ASUS>mongod --configsvr --replSet configRS --dbpath C:\\mongodb\\tp3\\sharding\\{d} --port {p}\n" + mlog(p)) for p, d in CF] + \
      [(f"shard {p}", f"C:\\Users\\ASUS>mongod --shardsvr --replSet shardRS{r} --dbpath C:\\mongodb\\tp3\\sharding\\{d} --port {p}\n" + mlog(p)) for p, d, r in SH[:3]]
show(tiles(tlc), P2, "3 config servers (configRS, --configsvr) et 6 membres de shards (--shardsvr), deux par Replica Set shardRS1 à shardRS3.", 9000, cap="p2_mongod")
mc = cmdwin("mongosh 28019")
tcon(mc, WP, P2, "Initialisez configRS depuis 28019.", ["mongosh --port 28019"], BANNER(28019))
real(mc, "rs.initiate", P2, "rs.initiate() avec configsvr: true et 3 membres.")
real(mc, "rs.status().members", P2, "Vérifiez configRS.", cap="p2_cfg")
ms = cmdwin("mongosh 28101")
tcon(ms, WP, P2, "1 PRIMARY + 2 SECONDARY. Initialisez maintenant shardRS1 depuis 28101.", ["mongosh --port 28101"], BANNER(28101))
real(ms, "rs.initiate", P2, "shardRS1 : 2 membres (28101, 28102). shardRS2 et shardRS3 s'initialisent de la même façon.")
real(ms, "rs.status().members", P2, "Vérifiez shardRS1.")
for pre in ["rs.initiate", "rs.status().members", "rs.initiate", "rs.status().members"]:
    nxt(pre)
mm = cmdwin("mongos 28000")
tcon(mm, WP, P2, "Lancez le routeur mongos, relié aux 3 config servers.", ["mongos --configdb configRS/localhost:28019,localhost:28020,localhost:28021 --port 28000"],
     mlog(28000).replace('"ctx":"initandlisten","msg":"MongoDB starting"', '"ctx":"mongosMain","msg":"MongoS starting"'))
mo = cmdwin("mongosh 28000 (mongos)")
tcon(mo, WP, P2, "Connectez-vous à mongos : c'est le point d'entrée du cluster.", ["mongosh --port 28000"], BANNER(28000))
real(mo, "sh.addShard('shardRS1", P2, "Déclarez le premier shard.")
real(mo, "sh.addShard('shardRS2", P2, "Puis le deuxième.")
real(mo, "sh.addShard('shardRS3", P2, "Puis le troisième.")
real(mo, "sh.status()", P2, "shardAdded: 'shardRS3'. Affichez l'état du cluster.", cap="p2_shards")

P2b = "2 · Données et chunks"
real(mo, "use universite", P2b, "3 shards actifs. Passez dans universite.")
real(mo, "db.etudiants.drop()", P2b, "Repartez d'une collection vide.")
real(mo, "for (let i=1", P2b, "Boucle de l'énoncé : 30 000 insertOne() via mongos (commande déjà tapée).")
real(mo, "db.etudiants.countDocuments()", P2b, "Vérifiez le nombre de documents.", cap="p2_count")
real(mo, "db.etudiants.createIndex", P2b, "30000. La collection n'est pas vide : shardCollection exige d'abord un index sur la shard key.")
real(mo, "sh.shardCollection", P2b, "Shardez universite.etudiants sur matricule.", cap="p2_shard")
real(mo, "sh.splitAt('universite.etudiants',{matricule:10000})", P2b, "Créez une frontière de chunk à 10000.")
real(mo, "sh.splitAt('universite.etudiants',{matricule:20000})", P2b, "Puis à 20000 : trois chunks.")
real(mo, "sh.moveChunk('universite.etudiants',{matricule:15000}", P2b, "Le balancer ne déplace pas de si petits volumes : envoyez le chunk 10000–20000 sur shardRS2.")
real(mo, "sh.moveChunk('universite.etudiants',{matricule:25000}", P2b, "Et le chunk 20000–MaxKey sur shardRS3.")
real(mo, "sh.status()", P2b, "Observez les chunks.", cap="p2_chunks")
real(mo, "db.etudiants.getShardDistribution()", P2b, "Un chunk par shard. Affichez la distribution réelle.", cap="p2_distrib")

P2c = "2 · Routage"
real(mo, "db.etudiants.find({matricule:500})", P2c, "≈ 10 000 documents (33 %) par shard. Requête sur la shard key.")
real(mo, "db.etudiants.find({matricule:{$gte:100", P2c, "Intervalle sur la shard key : un seul chunk concerné.")
real(mo, "db.etudiants.find({nom:", P2c, "Même étudiant, mais sans la shard key.")
real(mo, "db.etudiants.find({filiere:", P2c, "Filtre sur filiere, sans shard key.")
real(mo, "db.etudiants.countDocuments({filiere:", P2c, "Comptez les BigData.")
real(mo, "e = db.etudiants.find({matricule:500})", P2c, "explain() avec la shard key, résumé en 4 champs : SINGLE_SHARD, 1 document examiné sur shardRS1.", cap="p2_explain1", typed=False)
real(mo, "e = db.etudiants.find({nom:", P2c, "Sans shard key : SHARD_MERGE sur les 3 shards, 30 000 documents examinés.", cap="p2_explain2", typed=False)

P2d = "2 · Panne d'un shard"
ps = cmdwin("mongosh 28101")
real(ps, "rs.status().members", P2d, "Avant la panne : sur shardRS1, 28101 est PRIMARY.")
tlp = [(f"shard {p}" + (" (arrêté)" if p == 28101 else ""), f"C:\\Users\\ASUS>mongod --shardsvr --replSet shardRS{r} --dbpath C:\\mongodb\\tp3\\sharding\\{d} --port {p}\n" + mlog(p) + ("\n" + "\n".join(ctrlc(p)) if p == 28101 else "")) for p, d, r in SH]
show(tiles(tlp, hl=0), P2d, "Ctrl+C sur le Primary de shardRS1 (28101). Il ne reste qu'un membre sur deux.", 7500)
pz = cmdwin("mongosh 28102")
real(pz, "rs.status().members", P2d, "Sur le survivant 28102, affichez les rôles.", cap="p2_panne1")
real(pz, "db.hello().isWritablePrimary", P2d, "28102 reste SECONDARY. Peut-il écrire ?")
real(mo, "db.etudiants.find({matricule:500})", P2d, "false : 1 vote sur 2, pas de majorité, pas d'élection. Depuis mongos, lisez matricule 500 (chunk de shardRS1).", cap="p2_panne2")
real(mo, "db.etudiants.find({matricule:25000})", P2d, "Échec : shardRS1 n'a plus de Primary. Lisez matricule 25000 (chunk de shardRS3).")
real(mo, "db.etudiants.insertOne", P2d, "shardRS3 répond. Tentez une écriture dans la plage de shardRS1.")
real(pz, "rs.status().members", P2d, "Écriture refusée. Après redémarrage de 28101, revoyez shardRS1.", cap="p2_retour")
real(mo, "db.etudiants.find({matricule:500})", P2d, "shardRS1 retrouve un Primary. La lecture de matricule 500 fonctionne à nouveau.")
show(mo.html(None), "Fin", "Avec 2 membres, une panne bloque le shard : en production, il faut 3 membres votants par Replica Set. Réplication = continuité, sharding = répartition.", 10000)
