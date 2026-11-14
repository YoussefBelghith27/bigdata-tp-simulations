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
| TP2 | Requêtes sur la collection restaurants | à venir | à venir | à venir |
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

## Organisation des fichiers

```
index.html            page d'accueil
simulation.html       lecteur de simulation (simulation.html?tp=<identifiant>)
assets/               styles, catalogue des TP, lecteur
sims/                 données de chaque simulation (écrans + interactions)
cr/                   comptes rendus PDF
activepresenter/      projets ActivePresenter (.approj)
tp1/                  captures du compte rendu et sortie réelle de mongosh
tools/tp1/            scripts de génération (session réelle, écrans, simulation, .approj, PDF)
```

## Origine des écrans

Les sorties de **mongosh** viennent d'une **exécution réelle** de MongoDB 7.0.34 et mongosh 2.14.2 : connexion, bases, insertions, requêtes, mises à jour, suppressions et exercices. Les écrans propres à Windows sont **reconstitués** à partir de l'énoncé : installateurs MSI, pages de téléchargement, Explorateur, fenêtre Path, `where`, `sc query`, `net start/stop` et `netstat`. Ce sont des résultats attendus, signalés comme tels dans la simulation et dans le compte rendu.
