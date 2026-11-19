"""Synthèse fournisseurs : à partir de verdicts.json et des fichiers du lot, prépare pour chaque produit
le texte de la colonne C (liens), le prix d'achat (colonne D), le délai (colonne M)
et une note de cellule (niveau de ressemblance, prix, prix du concurrent, règle achat × 3).
Les numéros de ligne sont ceux de la grille au moment du lot : l'apprenant a pu supprimer des lignes
depuis, donc on écrit dans la grille en retrouvant chaque produit par son nom (colonne A).
Usage : python3 -I synthese.py DOSSIER_LOT DOSSIER_VIDAXL2 [sortie.json]"""
import json
import os
import sys

ICI = os.path.dirname(os.path.abspath(__file__))
RETENUS = ("identique", "quasi identique", "équivalent")
EXCLUS = ("trop cher", "prix d'appel", "plus petite taille")
DELAI_VIDAXL = "1-3 jours ouvrables (VidaXL)"


def euros(x):
    return "prix non affiché" if x is None else f"{x:,.2f} €".replace(",", " ").replace(".", ",")


def candidats(lot, vx2, ligne):
    r = json.load(open(os.path.join(lot, f"ligne{ligne}.json"), encoding="utf-8"))
    c = {}
    for i, a in enumerate((r.get("aliexpress") or {}).get("resultats") or [], 1):
        c[f"A{i}"] = ("AliExpress", a["url"], a.get("prix"))
    for i, v in enumerate(r.get("vidaxl") or [], 1):
        if v.get("url"):
            c[f"V{i}"] = ("VidaXL", v["url"], v.get("prix"))
    f2 = os.path.join(vx2, f"ligne{ligne}.json")
    if os.path.exists(f2):
        for i, v in enumerate(json.load(open(f2, encoding="utf-8")).get("vidaxl") or [], 1):
            if v.get("url"):
                c[f"X{i}"] = ("VidaXL", v["url"], v.get("prix"))
    return r, c


def synthese(lot, vx2):
    verdicts = json.load(open(os.path.join(ICI, "verdicts.json"), encoding="utf-8"))["lignes"]
    sortie = {}
    for ligne, v in verdicts.items():
        r, c = candidats(lot, vx2, ligne)
        prix_conc = r["concurrent"].get("prix")
        choisis = [(code, niveau) + c[code] for code, niveau in v["choix"]]
        sources = {s for _, _, s, _, _ in choisis}
        # Prix d'achat : celui du meilleur fournisseur (le premier de la liste, rangée du plus ressemblant
        # au moins ressemblant) parmi les identiques / équivalents au prix connu. Pas le moins cher :
        # sur AliExpress, le prix le plus bas est souvent celui de la plus petite taille de l'annonce.
        achats = [(p, s) for _, niv, s, _, p in choisis
                  if p is not None and niv.startswith(RETENUS) and not any(m in niv for m in EXCLUS)]
        achat = achats[0] if achats else None
        lignes_note = [f"Fournisseurs (recherche du 19/11/2026, comparaison visuelle avec la photo du concurrent) :"]
        for code, niv, s, url, p in choisis:
            lignes_note.append(f"- {s} {euros(p)} : {niv}")
        lignes_note.append(f"Concurrent comparé : {r['concurrent']['url']} ({euros(prix_conc)})")
        if achat and prix_conc:
            coef = f"{prix_conc / achat[0]:.1f}".replace(".", ",")
            lignes_note.append(f"Règle achat × 3 : {euros(achat[0])} × 3 = {euros(achat[0] * 3)} ; le concurrent vend {euros(prix_conc)} (coefficient {coef}).")
        if v.get("remarque"):
            lignes_note.append(v["remarque"])
        nb = len({(s, url) for _, _, s, url, _ in choisis})
        lignes_note.append(f"Critère 2 fournisseurs : {'OK' if nb >= 2 else 'NON (un seul)'} ; sources : {', '.join(sorted(sources))}.")
        sortie[ligne] = {
            "produit": r["produit"],
            "C": "\n".join(url for _, _, _, url, _ in choisis),
            "D": round(achat[0], 2) if achat else None,
            "D_source": achat[1] if achat else None,
            "M": DELAI_VIDAXL if achat and achat[1] == "VidaXL" else None,
            "note": "\n".join(lignes_note),
            "prix_concurrent": prix_conc,
            "coefficient": round(prix_conc / achat[0], 2) if achat and prix_conc else None,
        }
    return sortie


if __name__ == "__main__":
    res = synthese(sys.argv[1], sys.argv[2])
    if len(sys.argv) > 3:
        json.dump(res, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for ligne, s in res.items():
        print(f"ligne {ligne} | achat {s['D']} ({s['D_source']}) | concurrent {s['prix_concurrent']} | coef {s['coefficient']}")
