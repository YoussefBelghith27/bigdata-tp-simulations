import subprocess, json
CMDS = [
 ("test", "db.version()"),
 ("test", "db"),
 ("test", "show dbs"),
 ("test", "use etudiant"),
 ("etudiant", 'db.etudiants.insertOne({ nom: "Ben Ali", prenom: "Sami", age: 21, filiere: "Reseaux", niveau: "L3" })'),
 ("etudiant", 'db.etudiants.insertMany([ { nom: "Trabelsi", prenom: "Amira", age: 20, filiere: "Reseaux", niveau: "L3", moyenne: 14.5 }, { nom: "Gharbi", prenom: "Yassine", age: 22, filiere: "Informatique", niveau: "L3", moyenne: 12 }, { nom: "Mansour", prenom: "Lina", age: 21, filiere: "Reseaux", niveau: "L2", moyenne: 16 }, { nom: "Jlassi", prenom: "Omar", age: 23, filiere: "Informatique", niveau: "L3", moyenne: 9.5 } ])'),
 ("etudiant", "show dbs"),
 ("etudiant", "show collections"),
 ("etudiant", "db.etudiants.countDocuments()"),
 ("etudiant", "db.stats()"),
 ("etudiant", "db.etudiants.find()"),
 ("etudiant", "db.etudiants.findOne()"),
 ("etudiant", 'db.etudiants.findOne({ nom: "Gharbi" })'),
 ("etudiant", 'db.etudiants.find({ filiere: "Reseaux" })'),
 ("etudiant", 'db.etudiants.find({ filiere: "Reseaux", niveau: "L3" })'),
 ("etudiant", "db.etudiants.find({ age: { $gt: 21 } })"),
 ("etudiant", "db.etudiants.find({ moyenne: { $gte: 12, $lte: 15 } })"),
 ("etudiant", 'db.etudiants.find({ $or: [ { niveau: "L2" }, { age: 23 } ] })'),
 ("etudiant", "db.etudiants.find({}, { nom: 1, prenom: 1, _id: 0 })"),
 ("etudiant", "db.etudiants.find({}, { nom: 1, age: 1, _id: 0 }).sort({ age: 1 })"),
 ("etudiant", "db.etudiants.find({}, { nom: 1, moyenne: 1, _id: 0 }).sort({ moyenne: -1 })"),
 ("etudiant", "db.etudiants.find().limit(2)"),
 ("etudiant", 'db.etudiants.updateOne({ nom: "Ben Ali" }, { $set: { moyenne: 13.5 } })'),
 ("etudiant", 'db.etudiants.updateMany({ filiere: "Reseaux" }, { $set: { campus: "Tunis" } })'),
 ("etudiant", 'db.etudiants.updateOne({ nom: "Jlassi" }, { $inc: { age: 1 } })'),
 ("etudiant", "db.etudiants.find({}, { _id: 0 })"),
 ("etudiant", 'db.etudiants.deleteOne({ nom: "Jlassi" })'),
 ("etudiant", 'db.etudiants.deleteMany({ niveau: "L2" })'),
 # Exercices
 ("etudiant", 'db.etudiants.insertMany([ { nom: "Belghith", prenom: "Youssef", age: 21, filiere: "Reseaux", niveau: "L3", moyenne: 15.5 }, { nom: "Hammami", prenom: "Nour", age: 20, filiere: "Informatique", niveau: "L3", moyenne: 13 }, { nom: "Saidi", prenom: "Karim", age: 22, filiere: "Reseaux", niveau: "L2", moyenne: 10.75 } ])'),
 ("etudiant", 'db.etudiants.find({ filiere: "Reseaux" }, { _id: 0 })'),
 ("etudiant", "db.etudiants.find({ moyenne: { $gte: 12 } }, { nom: 1, moyenne: 1, _id: 0 }).sort({ moyenne: -1 })"),
 ("etudiant", 'db.etudiants.updateOne({ nom: "Saidi" }, { $set: { moyenne: 12.25 } })'),
 ("etudiant", 'db.etudiants.findOne({ nom: "Saidi" }, { nom: 1, moyenne: 1, _id: 0 })'),
 ("etudiant", 'db.etudiants.deleteOne({ nom: "Hammami" })'),
 ("etudiant", "db.etudiants.countDocuments()"),
 # nettoyage
 ("etudiant", "db.etudiants.drop()"),
 ("etudiant", "db.dropDatabase()"),
]
out = []
for dbn, c in CMDS:
    r = subprocess.run(["mongosh", "--quiet", f"mongodb://127.0.0.1:27017/{dbn}", "--eval", c], capture_output=True, text=True)
    o = (r.stdout + r.stderr).rstrip("\n")
    out.append({"db": dbn, "cmd": c, "out": o})
    print(f"{dbn}> {c}\n{o}\n")
json.dump(out, open("/home/claude/tp1/run/session.json", "w"), ensure_ascii=False, indent=1)
