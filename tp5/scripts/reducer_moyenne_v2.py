#!/usr/bin/env python3
# Reducer : somme globale / effectif global = vraie moyenne, même avec combiner
import sys

courant, somme, n = None, 0.0, 0
for ligne in sys.stdin:
    cle, valeur = ligne.rstrip("\n").split("\t")
    s, c = valeur.split(",")
    if cle != courant:
        if courant is not None:
            print(f"{courant}\t{round(somme / n, 2)}")
        courant, somme, n = cle, 0.0, 0
    somme += float(s)
    n += int(c)
if courant is not None:
    print(f"{courant}\t{round(somme / n, 2)}")
