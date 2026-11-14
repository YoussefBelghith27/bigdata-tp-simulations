#!/usr/bin/env python3
# Reducer : additionne les 1 de chaque ville (entrée triée par clé)
import sys

courant, total = None, 0
for ligne in sys.stdin:
    cle, valeur = ligne.rstrip("\n").split("\t")
    if cle != courant:
        if courant is not None:
            print(f"{courant}\t{total}")
        courant, total = cle, 0
    total += int(valeur)
if courant is not None:
    print(f"{courant}\t{total}")
