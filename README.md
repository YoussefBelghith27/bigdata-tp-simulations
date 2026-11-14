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
| TP3 | Réplication et sharding | à venir | à venir | à venir |

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

## Organisation des fichiers

```
index.html            page d'accueil
simulation.html       lecteur de simulation (simulation.html?tp=<identifiant>)
assets/               styles, catalogue des TP, lecteur
sims/                 données de chaque simulation (écrans + interactions)
cr/                   comptes rendus PDF
activepresenter/      projets ActivePresenter (.approj)
tp1/, tp2/            captures du compte rendu et sorties réelles de mongosh
tools/                scripts de génération (écrans, simulation, .approj, PDF)
```

## Origine des écrans

Les sorties de **mongosh** viennent d'**exécutions réelles**. Pour le TP2, ce sont celles de mon poste (MongoDB 7.0.43, mongosh 2.12.0). Pour le TP1, elles viennent d'une session MongoDB 7.0 / mongosh 2.x rejouée, avec les numéros de version de mon poste. Les écrans propres à Windows sont **reconstitués** à partir de l'énoncé : installateurs MSI, pages de téléchargement, Explorateur, fenêtre Path, `where`, `sc query`, `net start/stop` et `netstat`. Ce sont des résultats attendus, signalés comme tels dans la simulation et dans le compte rendu.
