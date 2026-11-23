"""Lignes de la grille pour les produits retenus du lot DataForSEO du 23/11/2026 (copie de la mise en page d'une ligne modèle,
formule de marge, chiffres A B H I J K L N).
Usage : python3 -I grille_2026_11_23.py > requetes.json
        python3 -I grille_2026_11_23.py retenus.json LIGNE_DEBUT LIGNE_MODELE [SUFFIXE] > requetes.json
        (SUFFIXE « b » : 2e envoi du jour, fichiers ...-2026-11-23b.json)
        (retenus.json : liste de [produit de la liste, nom en colonne A, niche, remarque])"""
import json, os, sys
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import valider
SUFFIXE = sys.argv[4] if len(sys.argv) == 5 else ""
valider.IDEES = os.path.join(ICI, f"idees-2026-11-23{SUFFIXE}.json")
SHEET, MODELE, DEBUT = 1589929953, 60, 61
nb = lambda n: f"{n:,}".replace(",", " ")

RETENUS = [  # (produit de la liste, nom en colonne A, niche, remarque)
 ("canapé convertible", "canapé convertible", "Maison, salon", "Gros meuble : vérifier qu'il n'y a pas que des enseignes sur Google Shopping."),
 ("dressing", "dressing", "Maison, rangement", "Choisir un modèle en kit, sans pose."),
 ("commode", "commode", "Maison, chambre", ""),
 ("lit coffre", "lit coffre", "Maison, chambre", ""),
 ("fauteuil à bascule", "fauteuil à bascule", "Maison, salon", ""),
 ("lit gigogne", "lit gigogne", "Maison, chambre", ""),
 ("lit escamotable", "lit escamotable", "Maison, chambre", ""),
 ("rameur", "rameur", "Sport à la maison", "Limite liste noire : écran à piles."),
 ("îlot central", "îlot central", "Maison, cuisine", "Choisir un îlot indépendant, sans pose."),
 ("reformer pilates", "reformer pilates", "Sport à la maison", "Une partie des recherches vise des cours de pilates."),
 ("banc de musculation", "banc de musculation", "Sport à la maison", ""),
 ("bain nordique", "bain nordique", "Jardin, bien-être", "Très lourd : livraison sur palette."),
 ("handpan", "handpan", "Musique", ""),
 ("lit futon", "futon", "Maison, chambre", ""),
 ("abri bûches", "abri à bûches", "Jardin, extérieur", ""),
 ("établi", "établi", "Atelier, bricolage", ""),
 ("vélo pliant", "vélo pliant", "Mobilité", "Vérifier la place des marques (Brompton, Decathlon)."),
 ("abri vélo", "abri vélo", "Jardin, extérieur", ""),
 ("table de massage", "table de massage", "Professionnels, bien-être", ""),
 ("babyfoot", "babyfoot", "Jeux, loisirs", ""),
 ("tonnelle", "tonnelle", "Jardin, extérieur", ""),
 ("table de jardin", "table de jardin", "Jardin, extérieur", ""),
 ("cuisine d'extérieur", "cuisine d'extérieur", "Jardin, extérieur", ""),
 ("panneau brise-vue", "claustra", "Jardin, extérieur", ""),
 ("fauteuil suspendu", "fauteuil suspendu", "Jardin, extérieur", ""),
 ("portillon", "portillon", "Jardin, extérieur", ""),
 ("gloriette", "gloriette", "Jardin, extérieur", ""),
 ("chalet de jardin", "chalet de jardin", "Jardin, extérieur", ""),
 ("parasol déporté", "parasol déporté", "Jardin, extérieur", ""),
 ("tente de réception", "barnum", "Jardin, réception", ""),
 ("coffre de jardin", "coffre de jardin", "Jardin, extérieur", ""),
 ("float tube", "float tube", "Pêche", ""),
 ("tente gonflable", "tente gonflable", "Camping", ""),
]
if len(sys.argv) in (4, 5):
    RETENUS = [tuple(r) for r in json.load(open(sys.argv[1], encoding="utf-8"))]
    DEBUT, MODELE = int(sys.argv[2]), int(sys.argv[3])
brut = json.load(open(os.path.join(ICI, "donnees", f"dataforseo-2026-11-23{SUFFIXE}.json"), encoding="utf-8"))
items = {it["keyword"].lower(): it for it in brut["tasks"][0]["result"]}
res = {l["produit"]: l for l in json.load(open(os.path.join(ICI, "donnees", f"resultats-2026-11-23{SUFFIXE}.json"), encoding="utf-8"))}
idees = {i["produit"]: i for i in valider.lire_idees()}

def cellule_volume(idee, total_attendu):
    vus, par_mot = set(), []
    for k in idee["mots_cles"]:
        somme = 0
        for v in valider.variantes({"mots_cles": [k]}):
            it = items.get(v.lower())
            if not it or it.get("search_volume") is None:
                continue
            sig = (it["search_volume"], tuple((x["year"], x["month"], x["search_volume"]) for x in (it.get("monthly_searches") or [])))
            if sig in vus:
                continue
            vus.add(sig)
            somme += it["search_volume"]
        par_mot.append((k, somme))
    total = sum(s for _, s in par_mot)
    assert total == total_attendu, (idee["produit"], total, total_attendu)
    gros = [f"{k} {nb(s)}" for k, s in par_mot if s >= 1000]
    autres = sum(s for _, s in par_mot if s < 1000)
    if autres:
        gros.append(f"autres {nb(autres)}")
    return f"TOTAL {nb(total)} (avec et sans accent, singulier et pluriel)\n" + " + ".join(gros)

def concurrence(cpc):
    return "FAIBLE" if cpc < 0.30 else "MOYENNE" if cpc <= 0.80 else "ÉLEVÉE"

def commentaire(r, saison, remarque):
    if saison == "EVERGREEN":
        t = "Chiffres OK, se vend toute l'année."
    elif saison == "Q4":
        t = "Chiffres OK, pic à Noël."
    else:
        idx = r["indices_mensuels"]  # même calcul que valider.saisonnalite : 2 mois avant le début du pic de 3 mois
        debut = max(range(12), key=lambda m: idx[m] + idx[(m + 1) % 12] + idx[(m + 2) % 12])
        mois = valider.MOIS_LONG[(debut - 2) % 12]
        t = f"Chiffres OK, saison {saison.lower()} : lancer en {mois}."
    if r["cpc_eur"] > 0.80:
        t += " Attention CPC élevé."
    return (t + " " + remarque).strip()

str_ = lambda s: {"userEnteredValue": {"stringValue": s}}
lignes, journal = [], []
for produit, nom, niche, remarque in RETENUS:
    r = res[produit]
    saison = r["saison_liste"]
    idx = r["indices_mensuels"]
    if saison != "EVERGREEN" and max(idx) <= 1.36 and min(idx) >= 0.75:
        saison = "EVERGREEN"  # pic de 1,36 : à l'arrondi près de la règle des 1,35
    lignes.append({"values": [str_(nom), str_(niche), {}, {}, {}, {}, {},
                              {"userEnteredValue": {"numberValue": r["cpc_eur"]}},
                              str_(cellule_volume(idees[produit], r["volume_total"])),
                              str_(concurrence(r["cpc_eur"])), str_(saison), str_(r["trends"]), {},
                              str_(commentaire(r, saison, remarque))]})
    journal.append(f"{nom} | {r['volume_total']} | {r['cpc_eur']} | {saison} | {commentaire(r, saison, remarque)}")
n = len(lignes)
fin = DEBUT + n - 1
req = [
 {"copyPaste": {"source": {"sheetId": SHEET, "startRowIndex": MODELE - 1, "endRowIndex": MODELE, "startColumnIndex": 0, "endColumnIndex": 14},
                "destination": {"sheetId": SHEET, "startRowIndex": DEBUT - 1, "endRowIndex": fin, "startColumnIndex": 0, "endColumnIndex": 14},
                "pasteType": "PASTE_FORMAT"}},
 {"copyPaste": {"source": {"sheetId": SHEET, "startRowIndex": MODELE - 1, "endRowIndex": MODELE, "startColumnIndex": 5, "endColumnIndex": 6},
                "destination": {"sheetId": SHEET, "startRowIndex": DEBUT - 1, "endRowIndex": fin, "startColumnIndex": 5, "endColumnIndex": 6},
                "pasteType": "PASTE_FORMULA"}},
 {"updateCells": {"start": {"sheetId": SHEET, "rowIndex": DEBUT - 1, "columnIndex": 0},
                  "rows": [{"values": [v for i, v in enumerate(l["values"]) if i < 5]} for l in lignes], "fields": "userEnteredValue"}},
 {"updateCells": {"start": {"sheetId": SHEET, "rowIndex": DEBUT - 1, "columnIndex": 7},
                  "rows": [{"values": l["values"][7:14]} for l in lignes], "fields": "userEnteredValue"}},
]
json.dump(req, sys.stdout, ensure_ascii=False)
print("\n".join(journal), file=sys.stderr)
print(f"{n} lignes : {DEBUT} à {fin}", file=sys.stderr)
