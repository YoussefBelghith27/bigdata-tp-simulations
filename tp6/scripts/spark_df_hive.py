from pyspark.sql import SparkSession, functions as F
def main():
    spark = (SparkSession.builder
             .appName("TP6-DF-Hive")
             .enableHiveSupport()                                            # activer le support Hive
             .getOrCreate())
    df = spark.table("rsi3.restaurants").filter(F.col("restaurant_id").isNotNull())
    print("Restaurants :", df.count())
    res = (df.groupBy("city")
             .agg(F.count("*").alias("nb"), F.round(F.avg("rating"), 2).alias("note_moyenne"))
             .orderBy(F.desc("nb")))
    res.show(10, False)
    res.write.mode("overwrite").format("hive").saveAsTable("rsi3.synthese_villes")
    res.coalesce(1).write.mode("overwrite").option("header", True) \
       .csv("/user/student/spark/synthese_villes_csv")
    spark.stop()
if __name__ == "__main__":
    main()
