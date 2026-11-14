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
  },
  "wide": {
   "name": "Bases orientées colonnes",
   "desc": "Modéliser à partir des requêtes et distribuer les partitions sur un anneau de nœuds."
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
   "title": "Requêtes MongoDB sur la base Restaurants",
   "desc": "Import de restaurants.json (3772 documents) avec mongoimport, puis les 26 requêtes de l'énoncé : projections, pagination, $gt / $lt / $ne, $elemMatch, positions dans les tableaux, $in / $nin / $not / $or, expressions régulières, tri et $exists.",
   "cmds": [
    "mongoimport --db Restaurants --collection restaurant --file restaurants.json",
    "{ grades: { $elemMatch: { score: { $gt: 80, $lt: 100 } } } }",
    "{ name: /^Mad/ }"
   ],
   "cr": "cr/CR_TP2_Requetes_Restaurants.pdf",
   "approj": "activepresenter/TP2_Requetes_Restaurants_Simulation.approj",
   "tool": "mongosh 2.12 · Database Tools 100.19",
   "origin": "Sorties mongosh réelles (mon poste), écrans Windows reconstitués",
   "real": false,
   "slides": 41,
   "commands": 38,
   "clicks": 0
  },
  {
   "id": "tp3-replication-sharding",
   "group": "dist",
   "num": "TP3",
   "title": "Haute disponibilité et sharding",
   "desc": "Replica Set rs0 (1 Primary, 3 Secondary, 1 Arbiter) : réplication, oplog, panne du Primary et élection. Puis cluster shardé : configRS, trois shards en Replica Set, mongos, shard key matricule, chunks, routage ciblé ou diffusé (explain) et panne d'un shard à deux membres.",
   "cmds": [
    "mongod --dbpath C:\\mongodb\\tp3\\data\\node1 --port 27017 --replSet rs0",
    "rs.status()",
    "sh.shardCollection('universite.etudiants',{matricule:1})",
    "db.etudiants.getShardDistribution()"
   ],
   "cr": "cr/CR_TP3_Replication_Sharding.pdf",
   "approj": "activepresenter/TP3_Replication_Sharding_Simulation.approj",
   "tool": "mongod · mongos · mongosh",
   "origin": "Sorties mongosh réelles, fenêtres mongod reconstituées",
   "real": false,
   "slides": 73,
   "commands": 56,
   "clicks": 0
  },
  {
   "id": "tp4-cassandra",
   "group": "wide",
   "num": "TP4",
   "title": "Cassandra : CQL, modélisation et cluster à 3 nœuds",
   "desc": "Cluster ClusterRSI3 de 3 conteneurs cassandra:4.1 sous Docker Desktop, nodetool status, keyspace rsi3_bibliotheque en RF = 3, tables livres_par_auteur et ventes_par_livre, CRUD, refus de la recherche par titre (ALLOW FILTERING), table livres_par_titre, puis arrêt et retour de cassandra3.",
   "cmds": [
    "docker compose up -d",
    "docker exec -it cassandra1 nodetool status",
    "PRIMARY KEY ((isbn), date_vente, id_vente)",
    "docker stop cassandra3"
   ],
   "cr": "cr/CR_TP4_Cassandra.pdf",
   "approj": "activepresenter/TP4_Cassandra_Simulation.approj",
   "tool": "Docker Desktop · Cassandra 4.1 · cqlsh",
   "origin": "Docker réel (mon poste), sorties cqlsh/nodetool reconstituées",
   "real": false,
   "slides": 37,
   "commands": 26,
   "clicks": 0
  }
 ]
};
