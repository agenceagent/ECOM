"""Prépare les requêtes Google Sheets (batchUpdate) qui écrivent les fournisseurs dans la grille.
Entrées : la synthèse (synthese.py) et la colonne A de la grille telle qu'elle est maintenant
(fichier JSON : {"premiere_ligne": 11, "noms": [...]}) pour retrouver chaque produit par son nom.
Écrit : C = liens fournisseurs + note de cellule, D = prix d'achat (si connu), M = délai VidaXL.
Ne touche jamais une cellule C, D ou M déjà remplie (liste « deja_rempli » du fichier colonne A).
Usage : python3 -I requetes_grille.py synthese.json colonne_a.json [lignes_du_lot ...] > requetes.json"""
import json
import sys

SHEET_ID = 1589929953
C, D, M = 2, 3, 12

synth = json.load(open(sys.argv[1], encoding="utf-8"))
col = json.load(open(sys.argv[2], encoding="utf-8"))
filtre = set(sys.argv[3:])
rang = {nom.strip().lower(): col["premiere_ligne"] + i for i, nom in enumerate(col["noms"])}
deja = set(col.get("deja_rempli", []))  # ex. "C12"

requetes, journal = [], []
for ligne_lot, s in synth.items():
    if filtre and ligne_lot not in filtre:
        continue
    ligne = rang.get(s["produit"].strip().lower())
    if not ligne:
        journal.append(f"{s['produit']} : introuvable dans la colonne A, rien écrit")
        continue
    cellules = []
    if f"C{ligne}" not in deja:
        cellules.append((C, {"userEnteredValue": {"stringValue": s["C"]}, "note": s["note"]}, "userEnteredValue,note"))
    if s["D"] is not None and f"D{ligne}" not in deja:
        cellules.append((D, {"userEnteredValue": {"numberValue": s["D"]}}, "userEnteredValue"))
    if s["M"] and f"M{ligne}" not in deja:
        cellules.append((M, {"userEnteredValue": {"stringValue": s["M"]}}, "userEnteredValue"))
    for colonne, valeur, champs in cellules:
        requetes.append({"updateCells": {"start": {"sheetId": SHEET_ID, "rowIndex": ligne - 1, "columnIndex": colonne},
                                         "rows": [{"values": [valeur]}], "fields": champs}})
    journal.append(f"{s['produit']} : ligne {ligne} (ligne {ligne_lot} au moment du lot), {len(cellules)} cellule(s)")

json.dump(requetes, sys.stdout, ensure_ascii=False)
print("\n".join(journal), file=sys.stderr)
