#!/usr/bin/env python3
# Combiner : additionne sommes et effectifs (opération associative) -> cuisine<TAB>somme,effectif
import sys

courant, somme, n = None, 0.0, 0
for ligne in sys.stdin:
    cle, valeur = ligne.rstrip("\n").split("\t")
    s, c = valeur.split(",")
    if cle != courant:
        if courant is not None:
            print(f"{courant}\t{somme},{n}")
        courant, somme, n = cle, 0.0, 0
    somme += float(s)
    n += int(c)
if courant is not None:
    print(f"{courant}\t{somme},{n}")
