-- =====================================================================
-- TP Cassandra - L3 RSI (RSI3) - ISET Nabeul
-- Etudiant : BELGHITH Youssef
-- Fichier CQL : creations, insertions, requetes et operations CRUD
-- Execution :  docker cp TP_Cassandra_BELGHITH_Youssef.cql cassandra1:/tmp/tp.cql
--              docker exec -it cassandra1 cqlsh -f /tmp/tp.cql
-- (ou copier-coller les blocs un par un dans cqlsh)
-- =====================================================================

-- ---------------------------------------------------------------------
-- 6.1  Keyspace : RF = 3 dans le datacenter "datacenter1"
-- ---------------------------------------------------------------------
CREATE KEYSPACE IF NOT EXISTS rsi3_bibliotheque
WITH replication = {'class': 'NetworkTopologyStrategy', 'datacenter1': 3}
AND durable_writes = true;

USE rsi3_bibliotheque;

-- ---------------------------------------------------------------------
-- 6.2  Table livres_par_auteur  (requete : livres d'un auteur tries par ISBN)
--      cle de partition = id_auteur ; colonne de clustering = isbn
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS livres_par_auteur (
  id_auteur int,
  isbn text,
  nom_auteur text,
  prenom_auteur text,
  titre text,
  PRIMARY KEY ((id_auteur), isbn)
) WITH CLUSTERING ORDER BY (isbn ASC);

INSERT INTO livres_par_auteur (id_auteur, isbn, nom_auteur, prenom_auteur, titre)
VALUES (154, '2154889522', 'Goscinny', 'Rene', 'Asterix et Cleopatre');
INSERT INTO livres_par_auteur (id_auteur, isbn, nom_auteur, prenom_auteur, titre)
VALUES (987, '2154889589', 'Bruchez', 'Rudi', 'NoSQL');
INSERT INTO livres_par_auteur (id_auteur, isbn, nom_auteur, prenom_auteur, titre)
VALUES (987, '2154889597', 'Bruchez', 'Rudi', 'Bases de donnees distribuees');

SELECT * FROM livres_par_auteur WHERE id_auteur = 987;

-- ---------------------------------------------------------------------
-- 6.3  Table ventes_par_livre  (requete : ventes d'un livre par date)
--      cle de partition = isbn ; clustering = date_vente DESC, id_vente ASC
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ventes_par_livre (
  isbn text,
  date_vente date,
  id_vente int,
  quantite int,
  montant decimal,
  PRIMARY KEY ((isbn), date_vente, id_vente)
) WITH CLUSTERING ORDER BY (date_vente DESC, id_vente ASC);

INSERT INTO ventes_par_livre (isbn, date_vente, id_vente, quantite, montant)
VALUES ('2154889589', '2017-06-02', 12, 1, 35.00);
INSERT INTO ventes_par_livre (isbn, date_vente, id_vente, quantite, montant)
VALUES ('2154889589', '2017-09-12', 20, 2, 70.00);

SELECT * FROM ventes_par_livre WHERE isbn = '2154889589';

-- =====================================================================
-- 7. TRAVAIL DEMANDE - CRUD ET REQUETES
-- =====================================================================

-- 7.1  Ajouter un troisieme livre a l'auteur 154 (ISBN choisi : 2154889530)
INSERT INTO livres_par_auteur (id_auteur, isbn, nom_auteur, prenom_auteur, titre)
VALUES (154, '2154889530', 'Goscinny', 'Rene', 'Asterix le Gaulois');

-- 7.2  Afficher tous les livres de l'auteur 154
SELECT * FROM livres_par_auteur WHERE id_auteur = 154;

-- 7.3  Modifier le titre d'un livre puis verifier
--      (UPDATE exige la cle primaire COMPLETE : id_auteur + isbn)
UPDATE livres_par_auteur
SET titre = 'Asterix le Gaulois - Edition collector'
WHERE id_auteur = 154 AND isbn = '2154889530';

SELECT * FROM livres_par_auteur WHERE id_auteur = 154 AND isbn = '2154889530';

-- 7.4  Supprimer le livre ajoute puis verifier sa disparition
DELETE FROM livres_par_auteur WHERE id_auteur = 154 AND isbn = '2154889530';

SELECT * FROM livres_par_auteur WHERE id_auteur = 154;

-- 7.5  Ajouter une vente au livre 2154889589 puis afficher toutes ses ventes
INSERT INTO ventes_par_livre (isbn, date_vente, id_vente, quantite, montant)
VALUES ('2154889589', '2017-11-20', 25, 3, 105.00);

SELECT * FROM ventes_par_livre WHERE isbn = '2154889589';

-- 7.6  Recherche par titre sans id_auteur
--      -> REFUSEE : "Cannot execute this query as it might involve data
--         filtering ... use ALLOW FILTERING"  (titre n'est pas dans la cle)
-- SELECT * FROM livres_par_auteur WHERE titre = 'NoSQL';
--      Avec ALLOW FILTERING elle passe, mais elle scanne TOUTES les
--      partitions de TOUS les noeuds (a eviter en production) :
SELECT * FROM livres_par_auteur WHERE titre = 'NoSQL' ALLOW FILTERING;

-- 7.7  Table supplementaire pour la recherche par titre
--      cle de partition = titre ; isbn en clustering (plusieurs livres
--      peuvent avoir le meme titre)
CREATE TABLE IF NOT EXISTS livres_par_titre (
  titre text,
  isbn text,
  id_auteur int,
  nom_auteur text,
  prenom_auteur text,
  PRIMARY KEY ((titre), isbn)
);

-- Alimentation : on ecrit dans les 2 tables en meme temps (BATCH logue)
-- pour garder les donnees dupliquees coherentes.
BEGIN BATCH
  INSERT INTO livres_par_titre (titre, isbn, id_auteur, nom_auteur, prenom_auteur)
  VALUES ('Asterix et Cleopatre', '2154889522', 154, 'Goscinny', 'Rene');
  INSERT INTO livres_par_titre (titre, isbn, id_auteur, nom_auteur, prenom_auteur)
  VALUES ('NoSQL', '2154889589', 987, 'Bruchez', 'Rudi');
  INSERT INTO livres_par_titre (titre, isbn, id_auteur, nom_auteur, prenom_auteur)
  VALUES ('Bases de donnees distribuees', '2154889597', 987, 'Bruchez', 'Rudi');
APPLY BATCH;

-- Requete efficace : lecture d'une seule partition, sans ALLOW FILTERING
SELECT * FROM livres_par_titre WHERE titre = 'NoSQL';

-- ---------------------------------------------------------------------
-- Bonus (observation de la distribution)
-- ---------------------------------------------------------------------
-- Token Murmur3 calcule pour chaque cle de partition :
SELECT token(id_auteur), id_auteur, isbn FROM livres_par_auteur;
-- Verification du schema :
DESCRIBE KEYSPACE rsi3_bibliotheque;
