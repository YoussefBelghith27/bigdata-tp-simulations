import csv
from pyspark import SparkConf, SparkContext
ENTREE = "/user/student/input/restaurants.csv"
SORTIE = "/user/student/spark/output_script"
def parse(ligne):
    return next(csv.reader([ligne]))
def main():
    conf = SparkConf().setAppName("TP6-RDD-Restaurants")
    sc = SparkContext(conf=conf)                        # créer le contexte
    brut = sc.textFile(ENTREE)
    entete = brut.first()
    restos = brut.filter(lambda l: l != entete).map(parse)
    restos.cache()
    print("Nombre de restaurants :", restos.count())
    par_ville = (restos.map(lambda r: (r[2], 1))
                       .reduceByKey(lambda a, b: a + b))       # addition
    par_ville.map(lambda kv: kv[0] + "," + str(kv[1])) \
             .coalesce(1).saveAsTextFile(SORTIE)
    for ville, n in par_ville.sortBy(lambda kv: -kv[1]).take(5):
        print("TOP", ville, n)
    sc.stop()                                          # libérer les ressources
if __name__ == "__main__":
    main()
