# Partie 8 : nombre total de restaurants vu par Spark (à comparer avec Hive COUNT(*))
from pyspark import SparkConf, SparkContext

sc = SparkContext(conf=SparkConf().setAppName("TP5-count"))
brut = sc.textFile("/user/student/input/restaurants.csv")
entete = brut.first()
restos = brut.filter(lambda l: l != entete)
print("restos.count() =", restos.count())
sc.stop()
