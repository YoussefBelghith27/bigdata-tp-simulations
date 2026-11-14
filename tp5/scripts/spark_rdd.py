import csv
from pyspark import SparkConf, SparkContext

def parse(ligne):
    return next(csv.reader([ligne]))

sc = SparkContext(conf=SparkConf().setAppName("TP5-villes"))
brut = sc.textFile("/user/student/input/restaurants.csv")
entete = brut.first()
villes = (brut.filter(lambda l: l != entete).map(parse)
              .map(lambda r: (r[2], 1)).reduceByKey(lambda a, b: a + b))
villes.map(lambda kv: kv[0] + "\t" + str(kv[1])).coalesce(1).saveAsTextFile("/user/student/spark_output")
sc.stop()
