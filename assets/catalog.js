window.CATALOG = {
 "groups": {
  "install": {
   "name": "Mise en place",
   "desc": "Installer le serveur et le shell, préparer Windows et prendre en main mongosh."
  },
  "query": {
   "name": "Interroger les données",
   "desc": "Importer un jeu de données réel et écrire des requêtes de filtrage et de projection."
  },
  "dist": {
   "name": "Haute disponibilité et distribution",
   "desc": "Répliquer les données pour survivre aux pannes, puis les répartir sur plusieurs serveurs."
  }
 },
 "tps": [
  {
   "id": "tp1-installation",
   "group": "install",
   "num": "TP1",
   "title": "Installation de MongoDB 7.0 et de mongosh",
   "desc": "Installateurs MSI du serveur et du shell, ajout des dossiers bin au Path, vérification des versions, du service MongoDB et du port 27017, puis création de la base etudiant et commandes CRUD de découverte.",
   "cmds": [
    "where mongod",
    "sc query MongoDB",
    "netstat -an | findstr 27017",
    "db.etudiants.insertMany([...])",
    "db.etudiants.find({ age: { $gt: 21 } })"
   ],
   "cr": "cr/CR_TP1_Installation_MongoDB.pdf",
   "approj": "activepresenter/TP1_Installation_MongoDB_Simulation.approj",
   "tool": "Windows 11 · MongoDB 7.0 · mongosh 2.x",
   "origin": "Sorties mongosh réelles, écrans Windows reconstitués",
   "real": false,
   "slides": 92,
   "commands": 50,
   "clicks": 29
  },
  {
   "id": "tp2-resto",
   "group": "query",
   "num": "TP2",
   "title": "Requêtes sur la collection restaurants",
   "desc": "Import de restaurants.json avec mongoimport, puis 26 requêtes : projections, opérateurs de comparaison, $elemMatch, expressions régulières, $in / $nin et $exists.",
   "cmds": [
    "mongoimport",
    "$elemMatch",
    "$regex"
   ],
   "tool": "mongosh · Database Tools",
   "soon": true
  },
  {
   "id": "tp3-replication-sharding",
   "group": "dist",
   "num": "TP3",
   "title": "Réplication et sharding",
   "desc": "Replica set à 5 nœuds avec arbitre et bascule du primaire, puis cluster shardé : 3 serveurs de configuration, 3 shards et un routeur mongos.",
   "cmds": [
    "rs.initiate()",
    "rs.status()",
    "sh.shardCollection()"
   ],
   "tool": "mongod · mongos",
   "soon": true
  }
 ]
};
