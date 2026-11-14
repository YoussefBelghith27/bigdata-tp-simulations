#!/usr/bin/env python3
# Reducer : note moyenne par cuisine (version complétée du TP)
import sys

courant, somme, n = None, 0.0, 0
for ligne in sys.stdin:
    cle, valeur = ligne.rstrip("\n").split("\t")
    if cle != courant:
        if courant is not None:
            print(f"{courant}\t{round(somme / n, 2)}")              # diviser par l'effectif
        courant, somme, n = cle, 0.0, 0
    somme += float(valeur)
    n += 1                                                        # incrémenter l'effectif
if courant is not None:
    print(f"{courant}\t{round(somme / n, 2)}")
