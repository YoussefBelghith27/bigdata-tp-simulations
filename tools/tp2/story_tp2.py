"""Scénario de la simulation TP2 : Database Tools, mongoimport de restaurants.json, puis les 26 requêtes.
Les sorties mongosh viennent du fichier réel sorties_tp2.txt (exécution sur le PC de Youssef)."""
import re
from screens import *

SRC = "/mnt/user-data/uploads/TP2_MongoDB_Restaurants/Compte_Rendu/sorties_tp2.txt"
R = {}
_t = open(SRC, encoding="utf-8", errors="replace").read()
_p = re.split(r"^#### (\S+)\n", _t, flags=re.M)[1:]
for i in range(0, len(_p), 2):
    lines = _p[i + 1].rstrip("\n").split("\n")
    cmd = lines[0][len("Restaurants> "):]
    body = lines[1:]
    if body and body[-1].strip() == "Restaurants>":
        body = body[:-1]
    R[_p[i]] = (cmd, "\n".join(body))

TV = "100.19.1"
TBIN = r"C:\Program Files\MongoDB\Tools\100\bin"
BIN = r"C:\Program Files\MongoDB\Server\7.0\bin"
SHDIR = r"C:\Users\ASUS\AppData\Local\Programs\mongosh"
MSI_T = f"mongodb-database-tools-windows-x86_64-{TV}.msi"
TOOLS_T = f"MongoDB Database Tools {TV} Setup"
WP = "C:\\Users\\ASUS>"
DIR = r"Desktop\terminal\BigData_Avance\TP\TP2_MongoDB_Restaurants\Fichiers_TP"
FP = "C:\\Users\\ASUS\\" + DIR + ">"
RP = "Restaurants> "

slides = []
def dur(text, base=3200): return max(5200, min(11000, base + 55 * len(text)))
def show(html, step, text, d=None, cap=None): slides.append(dict(html=html, step=step, text=text, kind="show", dur=d or dur(text), cap=cap))
def click(html, step, text, hint, cap=None): slides.append(dict(html=html, step=step, text=text, kind="click", hint=hint, cap=cap))
def tbox(html, step, text, answers, cap=None): slides.append(dict(html=html, step=step, text=text, kind="type", box=True, answers=answers, cap=cap))
def tcon(con, prompt, step, text, answers, out=None, mongo=False, cap=None):
    slides.append(dict(html=con.html(prompt), step=step, text=text, kind="type", x=prompt_x(prompt), answers=answers, cap=cap))
    con.add_cmd(prompt, answers[0])
    if out is not None:
        con.add_out(out, mongo=mongo)

def compact(cmd):
    """Supprime les espaces hors chaînes/regex : { a: 1 } -> {a:1}."""
    out, q = [], None
    for ch in cmd:
        if q:
            out.append(ch)
            if ch == q: q = None
        elif ch in "\"'":
            q = ch; out.append(ch)
        elif ch == " ":
            continue
        else:
            out.append(ch)
    s = "".join(out)
    return s.replace("db.restaurant.find", "db.restaurant.find")

def variants(cmd):
    v = [cmd, compact(cmd)]
    v2 = re.sub(r"\s*([{}\[\]:,])\s*", r"\1", cmd)
    return list(dict.fromkeys(v + [v2]))

# ====================================================================== Intro
show(title_card("TP 2 · Requêtes MongoDB sur la base Restaurants", "Import de restaurants.json avec mongoimport, puis 26 requêtes find() dans mongosh",
                ["Importer 3772 restaurants dans Restaurants.restaurant avec mongoimport",
                 "Projections, filtres, opérateurs $gt / $lt / $ne / $in / $nin / $not", "Tableaux : grades.score, $elemMatch, index grades.1 et coord.0",
                 "Expressions régulières, tri, pagination et $exists"]),
     "Introduction", "TP2 – Requêtes MongoDB sur la base Restaurants. Sorties mongosh réelles ; écrans Windows reconstitués (résultats attendus).", 9000)

c2 = Console("Invite de commandes", WP)
c2.add_out("Microsoft Windows [version 10.0.26100.4652]\n(c) Microsoft Corporation. Tous droits réservés.\n")

# ====================================================================== Partie B : import
PB = "B · Importation"
tcon(c2, WP, PB, "MongoDB, mongosh et les Database Tools sont déjà installés (TP1). Placez-vous dans le dossier qui contient restaurants.json.", ["cd " + DIR, "cd " + DIR + "\\"], "")
tcon(c2, FP, PB, "Importez le fichier dans la base Restaurants, collection restaurant (commande de l'énoncé).",
     ["mongoimport --db Restaurants --collection restaurant --file restaurants.json", "mongoimport --db=Restaurants --collection=restaurant --file=restaurants.json",
      "mongoimport -d Restaurants -c restaurant --file restaurants.json"],
     "2026-11-14T13:12:41.208+0100\tconnected to: mongodb://localhost/\n2026-11-14T13:12:41.497+0100\t3772 document(s) imported successfully. 0 document(s) failed to import.\n", cap="import")
show(c2.html(FP), PB, "3772 documents importés, 0 échec. Chaque ligne du fichier JSON devient un document ; la base et la collection sont créées automatiquement.", 8500)
tcon(c2, FP, PB, "Ouvrez mongosh directement sur la base Restaurants.", ["mongosh Restaurants", 'mongosh "mongodb://127.0.0.1:27017/Restaurants"'],
     """Current Mongosh Log ID: 6af8521ac93e44b1a7b0f2d1
Connecting to:          mongodb://127.0.0.1:27017/Restaurants?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.12.0
Using MongoDB:          7.0.43
Using Mongosh:          2.12.0

For mongosh info see: https://www.mongodb.com/docs/mongodb-shell/

------
   The server generated these startup warnings when booting
   2026-11-14T12:49:13.204+01:00: Access control is not enabled for the database. Read and write access to data and configuration is unrestricted
------
""")
tcon(c2, RP, PB, "Invite Restaurants> : vérifiez le nombre de documents.", variants("db.restaurant.countDocuments()"), R["Q25b"][1] + "\n", mongo=True, cap="count")

# ====================================================================== Partie C : requêtes
Q = {
 1: "Afficher tous les documents de la collection restaurant.",
 2: "Afficher restaurant_id, name, borough et cuisine de tous les documents.",
 3: "Mêmes champs, en excluant _id.",
 4: "Tous les restaurants du Bronx.",
 5: "Les 5 premiers restaurants du Bronx.",
 6: "Les 5 restaurants du Bronx situés après les 5 premiers.",
 7: "Restaurants ayant obtenu un score supérieur à 90.",
 8: "Un score supérieur à 80 et inférieur à 100 (dans la même note).",
 9: "Restaurants dont la coordonnée coord[0] est inférieure à -95.754168.",
 10: "Pas de cuisine 'American ', score > 70 et coord[0] < -65.754168 (avec $and).",
 11: "Même requête sans l'opérateur $and.",
 12: "Pas American, grade A, hors Brooklyn, trié par cuisine décroissante.",
 13: "Id, nom, borough et cuisine des restaurants dont le nom contient 'Wil'.",
 14: "Restaurants dont le nom se termine par 'ces'.",
 15: "Restaurants contenant 'Reg' quelque part dans le nom.",
 16: "Restaurants du Bronx de cuisine américaine ou chinoise.",
 17: "Restaurants de Staten Island, Queens, Bronx ou Brooklyn.",
 18: "Restaurants n'appartenant à aucun de ces quatre arrondissements.",
 19: "Restaurants dont aucun score ne dépasse 10.",
 20: "Cuisine ni American ni Chinese, ou nom commençant par 'Wil'.",
 21: "Grade A, score 11, le 2014-08-11 (dans le même élément de grades).",
 22: "Le 2e élément de grades : grade A, score 9, le 2014-08-11.",
 23: "Le 2e élément de coord compris entre 42 et 52.",
 24: "Tous les restaurants triés par nom croissant.",
 25: "Toutes les adresses contiennent-elles une rue (street) ?",
 26: "Restaurants dont le nom commence par 'Mad'.",
}
NOTE = {
 1: "find() sans filtre : 20 documents par page, « it » pour la suite.",
 2: "Projection { champ: 1 } : _id est inclus par défaut.",
 4: "309 restaurants dans le Bronx (countDocuments).",
 7: "\"grades.score\" teste chaque élément du tableau grades.",
 8: "$elemMatch impose que les deux conditions portent sur la même note.",
 9: "coord.0 = premier élément du tableau coord (longitude).",
 11: "Plusieurs conditions dans le même filtre = ET implicite.",
 12: "2017 restaurants correspondent ; sort({ cuisine: -1 }) trie de Z à A.",
 14: "Regex /ces$/ : $ = fin de chaîne.",
 16: "$in : la cuisine vaut l'une des valeurs de la liste (91 restaurants).",
 17: "1889 restaurants dans ces quatre arrondissements.",
 18: "$nin : 1883 restaurants, tous à Manhattan (seul autre arrondissement du jeu de données).",
 19: "$not { $gt: 10 } : aucun score > 10 (340 restaurants).",
 20: "$or entre un filtre regex et un $nin (2403 restaurants).",
 22: "grades.1 = deuxième élément du tableau (index à partir de 0).",
 25: "Aucun document sans rue : 3772 adresses avec street sur 3772.",
 26: "Regex /^Mad/ : ^ = début de chaîne.",
}
PC = "C · Requêtes"
def qstep(n): return f"Q{n}"
for n in range(1, 27):
    cmd, out = R[f"Q{n}"]
    prev = NOTE.get(n - 1, "")
    text = (prev + " " if prev and n > 1 else "") + f"Q{n} : {Q[n]}"
    tcon(c2, RP, f"{PC} {(n-1)//9*9+1}–{min((n-1)//9*9+9, 26)}", text, variants(cmd), (out + "\n") if out else "", mongo=True, cap=f"Q{n}")
    extra = {4: "Q4c", 12: "Q12c", 16: "Q16c", 17: "Q17c", 18: "Q18c", 19: "Q19c", 20: "Q20c", 25: "Q25a"}
    if n in extra:
        cc, co = R[extra[n]]
        tcon(c2, RP, f"{PC} {(n-1)//9*9+1}–{min((n-1)//9*9+9, 26)}", "Comptez les documents renvoyés par cette requête.", variants(cc), co + "\n", mongo=True, cap=extra[n])
show(c2.html(RP), "Fin", NOTE[26] + " TP2 terminé : 3772 restaurants importés et 26 requêtes (projections, opérateurs, tableaux, regex, tri, pagination) exécutées.", 10000)
