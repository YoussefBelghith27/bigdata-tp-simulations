// TP2 MongoDB - execute toutes les requetes et affiche les resultats comme dans mongosh
// Lancement : mongosh Restaurants --quiet tp2_requetes.js > sorties_tp2.txt
const Q = [
 ["Q1", 'db.restaurant.find()', () => db.restaurant.find()],
 ["Q2", 'db.restaurant.find({}, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1 })', () => db.restaurant.find({}, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1 })],
 ["Q3", 'db.restaurant.find({}, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })', () => db.restaurant.find({}, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })],
 ["Q4", 'db.restaurant.find({ borough: "Bronx" })', () => db.restaurant.find({ borough: "Bronx" })],
 ["Q4c", 'db.restaurant.countDocuments({ borough: "Bronx" })', () => db.restaurant.countDocuments({ borough: "Bronx" })],
 ["Q5", 'db.restaurant.find({ borough: "Bronx" }).limit(5)', () => db.restaurant.find({ borough: "Bronx" }).limit(5)],
 ["Q6", 'db.restaurant.find({ borough: "Bronx" }).skip(5).limit(5)', () => db.restaurant.find({ borough: "Bronx" }).skip(5).limit(5)],
 ["Q7", 'db.restaurant.find({ "grades.score": { $gt: 90 } }, { name: 1, borough: 1, grades: 1, _id: 0 })', () => db.restaurant.find({ "grades.score": { $gt: 90 } }, { name: 1, borough: 1, grades: 1, _id: 0 })],
 ["Q8", 'db.restaurant.find({ grades: { $elemMatch: { score: { $gt: 80, $lt: 100 } } } }, { name: 1, borough: 1, grades: 1, _id: 0 })', () => db.restaurant.find({ grades: { $elemMatch: { score: { $gt: 80, $lt: 100 } } } }, { name: 1, borough: 1, grades: 1, _id: 0 })],
 ["Q9", 'db.restaurant.find({ "address.coord.0": { $lt: -95.754168 } }, { name: 1, "address.coord": 1, _id: 0 })', () => db.restaurant.find({ "address.coord.0": { $lt: -95.754168 } }, { name: 1, "address.coord": 1, _id: 0 })],
 ["Q10", 'db.restaurant.find({ $and: [ { cuisine: { $ne: "American " } }, { "grades.score": { $gt: 70 } }, { "address.coord.0": { $lt: -65.754168 } } ] }, { name: 1, cuisine: 1, "address.coord": 1, _id: 0 })', () => db.restaurant.find({ $and: [ { cuisine: { $ne: "American " } }, { "grades.score": { $gt: 70 } }, { "address.coord.0": { $lt: -65.754168 } } ] }, { name: 1, cuisine: 1, "address.coord": 1, _id: 0 })],
 ["Q11", 'db.restaurant.find({ cuisine: { $ne: "American " }, "grades.score": { $gt: 70 }, "address.coord.0": { $lt: -65.754168 } }, { name: 1, cuisine: 1, "address.coord": 1, _id: 0 })', () => db.restaurant.find({ cuisine: { $ne: "American " }, "grades.score": { $gt: 70 }, "address.coord.0": { $lt: -65.754168 } }, { name: 1, cuisine: 1, "address.coord": 1, _id: 0 })],
 ["Q12", 'db.restaurant.find({ cuisine: { $ne: "American " }, "grades.grade": "A", borough: { $ne: "Brooklyn" } }, { name: 1, borough: 1, cuisine: 1, _id: 0 }).sort({ cuisine: -1 })', () => db.restaurant.find({ cuisine: { $ne: "American " }, "grades.grade": "A", borough: { $ne: "Brooklyn" } }, { name: 1, borough: 1, cuisine: 1, _id: 0 }).sort({ cuisine: -1 })],
 ["Q12c", 'db.restaurant.countDocuments({ cuisine: { $ne: "American " }, "grades.grade": "A", borough: { $ne: "Brooklyn" } })', () => db.restaurant.countDocuments({ cuisine: { $ne: "American " }, "grades.grade": "A", borough: { $ne: "Brooklyn" } })],
 ["Q13", 'db.restaurant.find({ name: /Wil/ }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })', () => db.restaurant.find({ name: /Wil/ }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })],
 ["Q14", 'db.restaurant.find({ name: /ces$/ }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })', () => db.restaurant.find({ name: /ces$/ }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })],
 ["Q15", 'db.restaurant.find({ name: /.*Reg.*/ }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })', () => db.restaurant.find({ name: /.*Reg.*/ }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })],
 ["Q16", 'db.restaurant.find({ borough: "Bronx", cuisine: { $in: ["American ", "Chinese"] } }, { name: 1, borough: 1, cuisine: 1, _id: 0 })', () => db.restaurant.find({ borough: "Bronx", cuisine: { $in: ["American ", "Chinese"] } }, { name: 1, borough: 1, cuisine: 1, _id: 0 })],
 ["Q16c", 'db.restaurant.countDocuments({ borough: "Bronx", cuisine: { $in: ["American ", "Chinese"] } })', () => db.restaurant.countDocuments({ borough: "Bronx", cuisine: { $in: ["American ", "Chinese"] } })],
 ["Q17", 'db.restaurant.find({ borough: { $in: ["Staten Island", "Queens", "Bronx", "Brooklyn"] } }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })', () => db.restaurant.find({ borough: { $in: ["Staten Island", "Queens", "Bronx", "Brooklyn"] } }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })],
 ["Q17c", 'db.restaurant.countDocuments({ borough: { $in: ["Staten Island", "Queens", "Bronx", "Brooklyn"] } })', () => db.restaurant.countDocuments({ borough: { $in: ["Staten Island", "Queens", "Bronx", "Brooklyn"] } })],
 ["Q18", 'db.restaurant.find({ borough: { $nin: ["Staten Island", "Queens", "Bronx", "Brooklyn"] } }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })', () => db.restaurant.find({ borough: { $nin: ["Staten Island", "Queens", "Bronx", "Brooklyn"] } }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })],
 ["Q18c", 'db.restaurant.countDocuments({ borough: { $nin: ["Staten Island", "Queens", "Bronx", "Brooklyn"] } })', () => db.restaurant.countDocuments({ borough: { $nin: ["Staten Island", "Queens", "Bronx", "Brooklyn"] } })],
 ["Q19", 'db.restaurant.find({ "grades.score": { $not: { $gt: 10 } } }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })', () => db.restaurant.find({ "grades.score": { $not: { $gt: 10 } } }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })],
 ["Q19c", 'db.restaurant.countDocuments({ "grades.score": { $not: { $gt: 10 } } })', () => db.restaurant.countDocuments({ "grades.score": { $not: { $gt: 10 } } })],
 ["Q20", 'db.restaurant.find({ $or: [ { name: /^Wil/ }, { cuisine: { $nin: ["American ", "Chinese"] } } ] }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })', () => db.restaurant.find({ $or: [ { name: /^Wil/ }, { cuisine: { $nin: ["American ", "Chinese"] } } ] }, { restaurant_id: 1, name: 1, borough: 1, cuisine: 1, _id: 0 })],
 ["Q20c", 'db.restaurant.countDocuments({ $or: [ { name: /^Wil/ }, { cuisine: { $nin: ["American ", "Chinese"] } } ] })', () => db.restaurant.countDocuments({ $or: [ { name: /^Wil/ }, { cuisine: { $nin: ["American ", "Chinese"] } } ] })],
 ["Q21", 'db.restaurant.find({ grades: { $elemMatch: { date: ISODate("2014-08-11T00:00:00Z"), grade: "A", score: 11 } } }, { restaurant_id: 1, name: 1, grades: 1, _id: 0 })', () => db.restaurant.find({ grades: { $elemMatch: { date: ISODate("2014-08-11T00:00:00Z"), grade: "A", score: 11 } } }, { restaurant_id: 1, name: 1, grades: 1, _id: 0 })],
 ["Q22", 'db.restaurant.find({ "grades.1.date": ISODate("2014-08-11T00:00:00Z"), "grades.1.grade": "A", "grades.1.score": 9 }, { restaurant_id: 1, name: 1, grades: 1, _id: 0 })', () => db.restaurant.find({ "grades.1.date": ISODate("2014-08-11T00:00:00Z"), "grades.1.grade": "A", "grades.1.score": 9 }, { restaurant_id: 1, name: 1, grades: 1, _id: 0 })],
 ["Q23", 'db.restaurant.find({ "address.coord.1": { $gt: 42, $lt: 52 } }, { restaurant_id: 1, name: 1, address: 1, _id: 0 })', () => db.restaurant.find({ "address.coord.1": { $gt: 42, $lt: 52 } }, { restaurant_id: 1, name: 1, address: 1, _id: 0 })],
 ["Q24", 'db.restaurant.find().sort({ name: 1 })', () => db.restaurant.find().sort({ name: 1 })],
 ["Q25", 'db.restaurant.find({ "address.street": { $exists: false } })', () => db.restaurant.find({ "address.street": { $exists: false } })],
 ["Q25a", 'db.restaurant.countDocuments({ "address.street": { $exists: true } })', () => db.restaurant.countDocuments({ "address.street": { $exists: true } })],
 ["Q25b", 'db.restaurant.countDocuments()', () => db.restaurant.countDocuments()],
 ["Q26", 'db.restaurant.find({ name: /^Mad/ }, { name: 1, borough: 1, "address.coord": 1, cuisine: 1, _id: 0 })', () => db.restaurant.find({ name: /^Mad/ }, { name: 1, borough: 1, "address.coord": 1, cuisine: 1, _id: 0 })],
];
for (const [id, cmd, fn] of Q) {
  print("#### " + id);
  print("Restaurants> " + cmd);
  const r = fn();
  if (r && typeof r.hasNext === "function") {
    const docs = [];
    while (docs.length < 21 && r.hasNext()) docs.push(r.next());
    if (docs.length) print(docs.slice(0, 20));
    if (docs.length > 20) print('Type "it" for more');
  } else {
    print(r);
  }
  print("Restaurants> ");
}
