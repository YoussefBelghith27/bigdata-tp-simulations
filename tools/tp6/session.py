"""Exécute réellement les activités 1 à 18 du TP6 dans un shell PySpark émulé (InteractiveConsole),
et enregistre (cellule, sortie). Les chemins /user/student/... existent localement (copie de l'arborescence HDFS)."""
import code, io, json, sys, contextlib, os
os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
from pyspark.sql import SparkSession
spark = (SparkSession.builder.appName("PySparkShell").master("local[2]")
         .config("spark.sql.warehouse.dir", "/user/hive/warehouse")
         .config("spark.ui.showConsoleProgress", "false")
         .enableHiveSupport().getOrCreate())
sc = spark.sparkContext
sc.setLogLevel("ERROR")
ns = {"spark": spark, "sc": sc}
con = code.InteractiveConsole(ns)
CELLS = [l for l in open(sys.argv[1]).read().split("\n#--\n") if l.strip()]
res = []
for cell in CELLS:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        more = False
        for line in cell.split("\n"):
            more = con.push(line)
        if more:
            con.push("")
    out = buf.getvalue()
    res.append({"cell": cell, "out": out})
    print(">>>", cell.split("\n")[0][:80], "|", out[:120].replace("\n", " / "), file=sys.__stdout__)
json.dump(res, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
spark.stop()
