-- TP5 Partie 7 : requêtes HiveQL (exécution : beeline -u jdbc:hive2://hive-server:10000/default -n student -f /opt/scripts/requetes_tp5.hql)

-- 7.3 Base et table externe sur le CSV déjà présent dans HDFS
CREATE DATABASE IF NOT EXISTS rsi3;
USE rsi3;

DROP TABLE IF EXISTS restaurants;
CREATE EXTERNAL TABLE restaurants (
  restaurant_id INT, name STRING, city STRING, cuisine STRING,
  rating DOUBLE, price_range STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/student/input'
TBLPROPERTIES ('skip.header.line.count'='1');

SELECT * FROM restaurants LIMIT 5;
SELECT COUNT(*) AS total FROM restaurants;
SELECT city, COUNT(*) AS nb_restaurants FROM restaurants GROUP BY city ORDER BY nb_restaurants DESC;
SELECT cuisine, ROUND(AVG(rating), 2) AS moyenne FROM restaurants GROUP BY cuisine;
DESCRIBE FORMATTED restaurants;
EXPLAIN SELECT city, COUNT(*) FROM restaurants GROUP BY city;

-- 7.4 Table gérée (données copiées dans /user/hive/warehouse)
DROP TABLE IF EXISTS restaurants_geree;
CREATE TABLE restaurants_geree STORED AS TEXTFILE AS SELECT * FROM restaurants;
DESCRIBE FORMATTED restaurants_geree;
DROP TABLE restaurants_geree;

-- Exercice 1 : table restaurants_par_ville (CTAS)
DROP TABLE IF EXISTS restaurants_par_ville;
CREATE TABLE restaurants_par_ville AS
SELECT city, COUNT(*) AS nb_restaurants FROM restaurants GROUP BY city;
SELECT * FROM restaurants_par_ville ORDER BY nb_restaurants DESC;
DESCRIBE FORMATTED restaurants_par_ville;

-- Exercice 2a : nombre de restaurants par price_range
SELECT price_range, COUNT(*) AS nb FROM restaurants GROUP BY price_range ORDER BY nb DESC;

-- Exercice 2b : meilleur restaurant (note max) par ville ; égalités départagées par l'id
SELECT city, restaurant_id, name, rating FROM (
  SELECT city, restaurant_id, name, rating,
         ROW_NUMBER() OVER (PARTITION BY city ORDER BY rating DESC, restaurant_id) AS rn
  FROM restaurants) t
WHERE rn = 1 ORDER BY city;

-- Exercice 4 : preuve du rôle de skip.header.line.count
DROP TABLE IF EXISTS restaurants_sans_entete;
CREATE EXTERNAL TABLE restaurants_sans_entete (
  restaurant_id INT, name STRING, city STRING, cuisine STRING,
  rating DOUBLE, price_range STRING)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/student/input';
SELECT * FROM restaurants_sans_entete LIMIT 2;          -- 1re ligne : id NULL, name = 'name'...
SELECT COUNT(*) AS total_avec_entete FROM restaurants_sans_entete;
DROP TABLE restaurants_sans_entete;                       -- externe : le CSV reste dans HDFS
