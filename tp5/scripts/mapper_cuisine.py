#!/usr/bin/env python3
# Mapper : émet  cuisine<TAB>rating
import sys, csv

for ligne in csv.reader(sys.stdin):
    if len(ligne) < 6 or ligne[0] == "restaurant_id":
        continue
    print(f"{ligne[3]}\t{ligne[4]}")
