# Big Data Avancée – simulations des TP MongoDB

Site des travaux pratiques du module **Big Data Avancée** (NoSQL, MongoDB 7.0), RSI3, ISET Nabeul, réalisé par **Youssef Belghith** (RSI31, 2026–2027).

**Site en ligne :** https://youssefbelghith27.github.io/bigdata-tp-simulations/

Chaque TP propose :

- une **simulation interactive** jouable dans le navigateur : sous-titres explicatifs, clics guidés dans les installateurs et les fenêtres Windows, commandes à taper dans cmd et dans mongosh, mode démo et score ;
- son **compte rendu** au format PDF ;
- le **projet ActivePresenter** (.approj) de la simulation, modifiable.

| TP | Sujet | Simulation | Compte rendu | ActivePresenter |
|---|---|---|---|---|
| TP1 | Installation de MongoDB 7.0 et de mongosh sous Windows 11 | [Lancer](https://youssefbelghith27.github.io/bigdata-tp-simulations/simulation.html?tp=tp1-installation) | [PDF](cr/CR_TP1_Installation_MongoDB.pdf) | [.approj](activepresenter/TP1_Installation_MongoDB_Simulation.approj) |
| TP2 | Requêtes MongoDB sur la base Restaurants (mongoimport + 26 requêtes) | [Lancer](https://youssefbelghith27.github.io/bigdata-tp-simulations/simulation.html?tp=tp2-resto) | [PDF](cr/CR_TP2_Requetes_Restaurants.pdf) | [.approj](activepresenter/TP2_Requetes_Restaurants_Simulation.approj) |
| TP3 | Haute disponibilité et sharding (Replica Set, failover, cluster shardé) | [Lancer](https://youssefbelghith27.github.io/bigdata-tp-simulations/simulation.html?tp=tp3-replication-sharding) | [PDF](cr/CR_TP3_Replication_Sharding.pdf) | [.approj](activepresenter/TP3_Replication_Sharding_Simulation.approj) |
| TP4 | Cassandra : CQL, modélisation et cluster Docker à 3 nœuds | [Lancer](https://youssefbelghith27.github.io/bigdata-tp-simulations/simulation.html?tp=tp4-cassandra) | [PDF](cr/CR_TP4_Cassandra.pdf) | [.approj](activepresenter/TP4_Cassandra_Simulation.approj) |
| TP5 | Cluster Hadoop : HDFS, YARN, MapReduce, Spark et Hive | [Lancer](https://youssefbelghith27.github.io/bigdata-tp-simulations/simulation.html?tp=tp5-hadoop) | [PDF](cr/CR_TP5_Hadoop_Spark_Hive.pdf) | [.approj](activepresenter/TP5_Hadoop_Spark_Hive_Simulation.approj) |
| TP6 | Spark sur un cluster Hadoop : RDD, DataFrame, Spark SQL et Hive | [Lancer](https://youssefbelghith27.github.io/bigdata-tp-simulations/simulation.html?tp=tp6-spark) | [PDF](cr/CR_TP6_Spark_Cluster_Hadoop.pdf) | [.approj](activepresenter/TP6_Spark_Cluster_Hadoop_Simulation.approj) |

## TP1 en bref

92 diapositives : 29 clics guidés et 50 saisies.

1. Installation de MongoDB Community Server 7.0 (msi) : licence, type Complete, service MongoDB, Compass décoché.
2. Installation de mongosh 2.x.
3. Recherche des dossiers `bin` puis ajout au **Path** système (`sysdm.cpl`).
4. Vérifications dans cmd : `where`, `mongod --version`, `mongosh --version`, `sc query MongoDB`, `net stop/start MongoDB`, `netstat -an | findstr 27017`.
5. Base `etudiant` dans mongosh : `insertOne`, `insertMany`, `find` avec `$gt`, `$gte`/`$lte` et `$or`, projection, tri, `updateOne`/`updateMany`/`$inc`, `deleteOne`/`deleteMany`.
6. Exercices B1 à B5, puis nettoyage avec `drop()` et `dropDatabase()`.

Les captures du compte rendu sont dans [`tp1/captures/`](tp1/captures). La sortie brute de la session mongosh est dans [`tp1/sortie_mongosh_reelle.txt`](tp1/sortie_mongosh_reelle.txt).

## TP2 en bref

41 diapositives, 38 saisies. MongoDB, mongosh et les Database Tools sont déjà installés depuis le TP1, donc la simulation commence directement dans cmd.

1. Import avec `mongoimport --db Restaurants --collection restaurant --file restaurants.json` : 3772 documents.
2. Les 26 requêtes de l'énoncé dans `mongosh Restaurants`, avec un comptage (`countDocuments`) pour les plus volumineuses.

La sortie réelle des requêtes, exécutées sur mon poste, est dans [`tp2/sortie_mongosh_reelle.txt`](tp2/sortie_mongosh_reelle.txt), avec le script [`tp2/tp2_requetes.js`](tp2/tp2_requetes.js).

## TP3 en bref

73 diapositives, 56 saisies. Plusieurs fenêtres `mongod` tournent en parallèle ; elles sont affichées côte à côte.

1. **Replica Set rs0** : les cinq `mongod` de 27017 à 27021, puis `rs.initiate()`. Le rôle de chaque membre est vérifié, la réplication est lue sur un Secondary et l'oplog est consulté.
2. **Failover** : Ctrl+C sur le Primary, élection de 27018, écriture qui continue, puis retour de 27017 comme Secondary.
3. **Cluster shardé** : configRS, shardRS1 à shardRS3 et `mongos`. 30 000 documents sont shardés sur `matricule`, découpés en 3 chunks (un par shard) et répartis avec `getShardDistribution()`.
4. **Routage** : `explain()` donne SINGLE_SHARD avec la shard key et SHARD_MERGE sans elle.
5. **Panne d'un shard à deux membres** : sans majorité, aucune élection n'a lieu et la plage de données de ce shard devient indisponible.

Les sorties réelles sont dans [`tp3/sortie_mongosh_reelle.txt`](tp3/sortie_mongosh_reelle.txt).

## TP4 en bref

37 diapositives, 26 saisies, dans PowerShell et cqlsh.

1. `docker compose up -d` lance 3 conteneurs `cassandra:4.1`. `nodetool status` montre 3 nœuds UN.
2. Keyspace `rsi3_bibliotheque` (NetworkTopologyStrategy, RF = 3), avec les tables `livres_par_auteur` et `ventes_par_livre`.
3. CRUD (INSERT, SELECT, UPDATE, DELETE avec clé complète) et recherche par titre refusée sans `ALLOW FILTERING`. La table `livres_par_titre` est alimentée par BATCH et les tokens Murmur3 sont affichés.
4. `nodetool describecluster` et journaux de cassandra2, puis `docker stop cassandra3` (DN) et `docker start cassandra3` (retour à UN).

Origine des sorties :
- `docker --version`, `docker compose up -d` et les journaux viennent de mon poste (dossier [`tp4/logs_docker_reels/`](tp4/logs_docker_reels)), tout comme le problème réel de collision de tokens traité dans le compte rendu.
- Les sorties `cqlsh` et `nodetool` sont reconstituées au format de Cassandra 4.1.
- Les tokens Murmur3 sont calculés.

Le fichier CQL complet est [`tp4/TP4_Requetes.cql`](tp4/TP4_Requetes.cql).

## TP5 en bref

60 diapositives, 50 saisies, dans le terminal de la VM Ubuntu, le conteneur hadoop-master et Beeline.

1. Le cluster compte 3 DataNodes et 3 NodeManagers (validé avec jps).
2. HDFS : import et `-du`, quota dépassé (un bloc de 128 Mo est réservé par réplique), corbeille, snapshot.
3. Blocs et panne : 1 bloc pour le CSV, 22 blocs de 1 Mo pour gros.txt, arrêt de hadoop-worker1 sans perte de lecture.
4. YARN refuse 8192 Mo par map, puis `pi` réussit (3.14000000000000000000).
5. Comptage par ville en Hadoop Streaming, puis Spark sur YARN et Hive donnent les mêmes 12 effectifs.

Origine des sorties :
- Les calculs sont réels : scripts Python exécutés, sortie PySpark, agrégats calculés sur le CSV et `pi` recalculé avec la séquence de Halton de Hadoop (voir [`tp5/sorties_reelles.txt`](tp5/sorties_reelles.txt)).
- Les messages HDFS, YARN et Hive sont reconstitués.

## TP6 en bref

101 diapositives, 68 saisies : les 19 activités, dans le shell PySpark et le conteneur hadoop-master.

1. **RDD** : SparkContext, `parallelize`, `glom()`, transformations et actions, `reduceByKey`, document texte et CSV, `cache()`, `repartition`/`coalesce`, `saveAsTextFile` et l'erreur « already exists ».
2. **spark-submit** : `spark_tp_rdd.py` sur YARN (l'application TP6-RDD se termine en SUCCEEDED).
3. **DataFrame et Spark SQL** : schéma, `groupBy`/`agg`, vue temporaire, `explain()`, CSV et Parquet (partitionné par ville).
4. **Spark + Hive** : lecture de `rsi3.restaurants`, création de `villes_spark` et `cuisines_spark`, puis l'application `spark_df_hive.py`.

Origine des sorties :
- Toutes les sorties PySpark sont réelles (Spark 3.5.3, voir [`tp6/sortie_pyspark_reelle.txt`](tp6/sortie_pyspark_reelle.txt)).
- Les valeurs propres à YARN (master, applicationId, liste des applications) sont reconstituées.

Les scripts complétés sont dans [`tp6/scripts/`](tp6/scripts).

## Organisation des fichiers

```
index.html            page d'accueil
simulation.html       lecteur de simulation (simulation.html?tp=<identifiant>)
assets/               styles, catalogue des TP, lecteur
sims/                 données de chaque simulation (écrans + interactions)
cr/                   comptes rendus PDF
activepresenter/      projets ActivePresenter (.approj)
tp1/ … tp6/           captures du compte rendu et sorties réelles de mongosh
tools/                scripts de génération (écrans, simulation, .approj, PDF)
```

## Origine des écrans

Les sorties de **mongosh** viennent d'**exécutions réelles**. Pour le TP2, ce sont celles de mon poste (MongoDB 7.0.43, mongosh 2.12.0). Pour le TP1, elles viennent d'une session MongoDB 7.0 / mongosh 2.x rejouée, avec les numéros de version de mon poste. Les écrans propres à Windows sont **reconstitués** à partir de l'énoncé : installateurs MSI, pages de téléchargement, Explorateur, fenêtre Path, `where`, `sc query`, `net start/stop` et `netstat`. Ce sont des résultats attendus, signalés comme tels dans la simulation et dans le compte rendu.
