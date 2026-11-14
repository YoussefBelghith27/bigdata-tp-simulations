#!/usr/bin/env python3
# Mapper : émet  ville<TAB>1  pour chaque restaurant
import sys, csv

for ligne in csv.reader(sys.stdin):
    if len(ligne) < 6 or ligne[0] == "restaurant_id":            # en-tête ou ligne invalide
        continue
    print(f"{ligne[2]}\t1")
