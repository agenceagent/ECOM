"""Mise à jour de la grille du 19/11/2026, demandée par l'apprenant :
1. prix de vente (E) = moyenne des concurrents SANS ceux qui sont hors du lot
   (3 concurrents ou plus : on retire un prix plus de 2 fois au-dessus ou en dessous de la médiane ;
   2 concurrents : on ne retire rien, sauf décision de l'apprenant dans prix_vente_corrections.json) ;
2. notes de cellule courtes (fournisseurs en C, prix de vente en E), suppression des notes périmées ;
3. commentaires de la colonne N raccourcis et remis à jour (seulement les miens, jamais ceux de l'apprenant) ;
4. liens cliquables dans les cases à plusieurs liens (C et G), sans changer le texte des cases.
Usage : python3 -I grille_menage.py prix_vente.json synthese.json textes_liens.json etat_grille.json > requetes.json"""
import json
import re
import statistics
import sys
from urllib.parse import parse_qs, parse_qsl, urlencode, urlsplit

SHEET = 1589929953
ICI = __file__.rsplit("/", 1)[0]


def euros(x):
    return f"{x:,.2f} €".replace(",", " ").replace(".", ",")


def entier(x):
    return f"{x:,.0f} €".replace(",", " ")


TRACAGE = re.compile(r"^(utm_|gad_|gclid|gbraid|gclsrc|tw_|hsa_|ve_|sv1|sv_|awc|stkn|campaignid|adgroupid|keyword|matchtype|"
                     r"network|device|spm|algo_|pdp_|utparam|curPageLogUid|scm|gps-id|pvid|_t$|af$|selling_plan|country|currency)")


def lien_propre(url):
    """Adresse sans les paramètres de pub ni de suivi (le texte affiché dans la case ne change pas)."""
    u = urlsplit(url)
    if "/products/" in u.path:
        v = parse_qs(u.query).get("variant", [None])[0]
        return f"{u.scheme}://{u.netloc}{u.path}" + (f"?variant={v}" if v else "")
    gardes = [(k, v) for k, v in parse_qsl(u.query, keep_blank_values=True) if not TRACAGE.match(k) and "://" not in k]
    return f"{u.scheme}://{u.netloc}{u.path}" + (("?" + urlencode(gardes)) if gardes else "")


def runs_liens(texte):
    """Morceaux de texte avec un lien pour chaque adresse (indices en UTF-16, comme l'API)."""
    def u16(i):
        return len(texte[:i].encode("utf-16-le")) // 2
    runs = []
    for m in re.finditer(r"https?://\S+", texte):
        runs.append({"startIndex": u16(m.start()), "format": {"link": {"uri": lien_propre(m.group(0))}}})
        if m.end() < len(texte):
            runs.append({"startIndex": u16(m.end()), "format": {}})
    return runs


def cellule(ligne, colonne, valeur, champs):
    return {"updateCells": {"start": {"sheetId": SHEET, "rowIndex": ligne - 1, "columnIndex": colonne},
                            "rows": [{"values": [valeur]}], "fields": champs}}


def moyennes(releves, corrections):
    res = {}
    for l in releves:
        gardes, notes_retrait = [], []
        for r in l["releves"]:
            url, dom = r["url"], urlsplit(r["url"]).netloc.replace("www.", "")
            cle = f"{url}|{l['ligne']}"
            if cle in corrections["exclus"]:
                notes_retrait.append(f"Retiré : {dom} ({corrections['exclus'][cle]})")
                continue
            if url in corrections["manuel"]:
                r = {**r, **corrections["manuel"][url]}
            if r.get("prix"):
                gardes.append((dom, r["prix"]))
            else:
                notes_retrait.append(f"Non lu : {dom} (site inaccessible)")
        if len(gardes) >= 3:
            med = statistics.median(p for _, p in gardes)
            hors = [(d, p) for d, p in gardes if p > 2 * med or p < med / 2]
            for d, p in hors:
                notes_retrait.append(f"Retiré, hors du lot : {d} {euros(p)}")
            gardes = [g for g in gardes if g not in hors]
        moy = round(sum(p for _, p in gardes) / len(gardes), 2) if gardes else None
        prix_txt = " · ".join(euros(p) for _, p in gardes)
        note = (f"Moyenne de : {prix_txt}" if len(gardes) > 1 else f"Prix du concurrent : {prix_txt}")
        res[l["ligne"]] = {"moyenne": moy, "note": "\n".join([note] + notes_retrait)}
    return res


AVERTISSEMENTS_C = {  # une ligne, seulement quand c'est important
    "13": "Prix de la plus petite taille : relever celui de la bonne taille.",
    "44": "Prix des petites tailles (4,5 à 6,5 L) : relever celui du 15 L.",
    "42": "Prix non affichés : à relever sur les fiches.",
    "51": "Prix AliExpress = prix d'appel : à relever sur la fiche.",
    "28": "Copie de la marque Ergobaby : risque de contrefaçon.",
    "38": "Aucun brûleur à l'éthanol trouvé : ce sont des cheminées à vapeur d'eau.",
    "59": "L'annonce AliExpress la plus ressemblante est en 70x140.",
}


def note_c(ligne_lot, s):
    lignes = [l[2:] for l in s["note"].split("\n") if l.startswith("- ")]
    if ligne_lot in AVERTISSEMENTS_C:
        lignes.append(AVERTISSEMENTS_C[ligne_lot])
    return "\n".join(lignes)


def nouveau_n(ligne, ancien, g, cpc, marge):
    """Commentaire court et à jour, ou None pour ne pas toucher (commentaire de l'apprenant)."""
    if not ancien or not ancien.startswith(("À évaluer", "Pas pour tout de suite", "Éliminé")):
        return None
    if ancien.startswith("Éliminé : volume"):
        return ancien.split(" sous les 8 000")[0] + " sous les 8 000."
    if ancien.startswith("À évaluer") and g and not g.startswith("http"):
        return ""  # écarté par l'apprenant (colonne G) : sa remarque suffit
    if ancien.startswith("Pas pour tout de suite"):
        texte = ancien.split(". Critère")[0] + "."
    elif ligne == 8:
        texte = "À évaluer : saison de printemps, à lancer vers février."
    elif ligne == 10:
        texte = "Pas pour tout de suite : saison Q4, à lancer vers septembre."
    else:
        texte = "À évaluer."
        if "Volume proche du seuil" in ancien or "volume proche du seuil" in ancien:
            texte += " Volume proche du seuil."
        if "lourd et encombrant" in ancien:
            texte += " Produit lourd et encombrant : livraison et retours coûteux."
    if ancien.startswith("Éliminé : aucun fournisseur"):
        texte = "Pas pour tout de suite : saison Q4, à lancer vers septembre."
    if marge is not None and marge < 0:
        texte += " Prix de vente moyen sous le prix d'achat."
    elif marge is not None and cpc and marge < cpc * 100:
        texte += f" Marge trop faible pour le CPC : {euros(marge)} pour {entier(cpc * 100)} minimum."
    if "Idée ajoutée par Claude" in ancien:
        texte += " Idée de Claude."
    return texte


if __name__ == "__main__":
    releves = json.load(open(sys.argv[1], encoding="utf-8"))
    synth = json.load(open(sys.argv[2], encoding="utf-8"))
    textes = json.load(open(sys.argv[3], encoding="utf-8"))
    etat = json.load(open(sys.argv[4], encoding="utf-8"))  # colonnes A, D, E, G, H, N actuelles par ligne
    corrections = json.load(open(f"{ICI}/prix_vente_corrections.json", encoding="utf-8"))
    req, journal = [], []

    # 1. Prix de vente
    moy = moyennes(releves, corrections)
    for ligne, m in moy.items():
        if str(ligne) in etat["E_apprenant"] or m["moyenne"] is None:
            continue
        req.append(cellule(ligne, 4, {"userEnteredValue": {"numberValue": m["moyenne"]}, "note": m["note"]}, "userEnteredValue,note"))
        journal.append(f"E{ligne} {m['moyenne']}")

    # 2. Fournisseurs (mes cases C) : texte inchangé, liens cliquables, note courte
    rang = {n.lower(): etat["premiere_ligne"] + i for i, n in enumerate(etat["A"])}
    for ligne_lot, s in synth.items():
        ligne = rang[s["produit"].lower()]
        req.append(cellule(ligne, 2, {"textFormatRuns": runs_liens(s["C"]), "note": note_c(ligne_lot, s)}, "textFormatRuns,note"))
    # Cases de l'apprenant (C8 à C10 et G) : on ajoute seulement les liens, le texte ne bouge pas
    for col, cases in (("C", textes["C_apprenant"]), ("G", textes["G"])):
        for ligne, t in cases.items():
            champs = "textFormatRuns"
            valeur = {"textFormatRuns": runs_liens(t)}
            if col == "G" and int(ligne) in (8, 9, 10):
                champs += ",note"  # notes périmées du 10/11 (anciens concurrents) supprimées
            req.append(cellule(int(ligne), 2 if col == "C" else 6, valeur, champs))

    # 3. Notes périmées supprimées
    for ref in etat["notes_a_supprimer"]:
        col, ligne = ord(ref[0]) - 65, int(ref[1:])
        req.append(cellule(ligne, col, {}, "note"))

    # 4. Commentaires N
    for ligne_s, ancien in etat["N"].items():
        ligne = int(ligne_s)
        e = moy.get(ligne, {}).get("moyenne") if ligne_s not in etat["E_apprenant"] else etat["E_apprenant"][ligne_s]
        d = etat["D"].get(ligne_s)
        marge = round(e - d, 2) if (e is not None and d is not None) else None
        cpc = etat["H"].get(ligne_s)
        nouveau = nouveau_n(ligne, ancien, etat["G"].get(ligne_s, ""), cpc, marge)
        if nouveau is not None and nouveau != ancien:
            req.append(cellule(ligne, 13, {"userEnteredValue": {"stringValue": nouveau}}, "userEnteredValue"))
            journal.append(f"N{ligne}: {nouveau}")

    json.dump(req, sys.stdout, ensure_ascii=False)
    print("\n".join(journal), file=sys.stderr)
