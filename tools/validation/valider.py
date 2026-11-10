#!/usr/bin/env python3
"""Validation chiffrée des idées produits avec DataForSEO (données Google Ads, France).

Usage :
  python3 valider.py fetch              appelle DataForSEO une fois et enregistre la réponse brute
  python3 valider.py analyse FICHIER    calcule les critères et écrit le CSV et les lignes pour la grille
  python3 valider.py test               vérifie les calculs sur des données fictives

La clé DataForSEO n'est jamais dans ce fichier : le proxy de la session l'ajoute
aux requêtes vers api.dataforseo.com. L'en-tête envoyé ici est un leurre qu'il remplace.
"""
import csv
import datetime as dt
import json
import os
import statistics
import sys
import urllib.parse
import urllib.request
from collections import defaultdict

ICI = os.path.dirname(os.path.abspath(__file__))
DONNEES = os.path.join(ICI, "donnees")

# Règles de la grille de la formation (onglet « LA GRILLE »)
VOLUME_MIN = 8000                 # recherches par mois, variantes additionnées
CONCURRENCE_OK = {"LOW", "MEDIUM"}  # faible ou moyenne
CLICS_PAR_VENTE = 100             # CPC × 100 doit rester sous la marge brute (1 % de conversion)
# Règle à nous : un produit est « evergreen » si son meilleur mois ne dépasse pas 1,35 fois la moyenne
PIC_EVERGREEN_MAX = 1.35

MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
CONCURRENCE_FR = {"LOW": "Faible", "MEDIUM": "Moyenne", "HIGH": "Élevée"}


def lire_idees():
    with open(os.path.join(ICI, "idees.json"), encoding="utf-8") as f:
        return json.load(f)["idees"]


def http_json(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers=headers or {})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode("utf-8"))


def taux_usd_eur():
    """Taux de référence BCE (USD pour 1 EUR), avec repli sur frankfurter.app (qui republie la BCE)."""
    try:
        url = "https://data-api.ecb.europa.eu/service/data/EXR/D.USD.EUR.SP00.A?lastNObservations=1&format=csvdata"
        with urllib.request.urlopen(url, timeout=60) as r:
            lignes = list(csv.DictReader(r.read().decode("utf-8").splitlines()))
        return float(lignes[-1]["OBS_VALUE"]), lignes[-1]["TIME_PERIOD"], "BCE"
    except Exception:
        d = http_json("https://api.frankfurter.app/latest?from=EUR&to=USD")
        return float(d["rates"]["USD"]), d["date"], "frankfurter.app (taux BCE)"


def fetch():
    idees = lire_idees()
    mots = []
    for i in idees:
        for k in i["mots_cles"]:
            if k.lower() not in (m.lower() for m in mots):
                mots.append(k)
    aujourd_hui = dt.date.today()
    debut = dt.date(aujourd_hui.year - 4, aujourd_hui.month, 1) + dt.timedelta(days=32)
    debut = debut.replace(day=1)
    corps = [{"keywords": mots, "location_name": "France", "language_code": "fr", "date_from": debut.isoformat()}]
    rep = http_json(
        "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live",
        data=json.dumps(corps).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": "Basic ZHVtbXk6ZHVtbXk="},
    )
    taux, date_taux, source_taux = taux_usd_eur()
    rep["_contexte"] = {"lance_le": dt.datetime.now().isoformat(timespec="minutes"), "mots_cles": len(mots),
                        "usd_pour_1_eur": taux, "date_taux": date_taux, "source_taux": source_taux}
    os.makedirs(DONNEES, exist_ok=True)
    chemin = os.path.join(DONNEES, f"dataforseo-{aujourd_hui.isoformat()}.json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    tache = rep["tasks"][0]
    print(f"statut {rep.get('status_code')} / tâche {tache.get('status_code')} {tache.get('status_message')} ; "
          f"coût {rep.get('cost')} $ ; {len(tache.get('result') or [])} mots-clés ; fichier {chemin}")
    return chemin


def saisonnalite(series):
    """series : liste de (année, mois, volume). Renvoie le libellé, le statut de lancement et le détail."""
    par_mois = defaultdict(list)
    for a, m, v in series:
        if v is not None:
            par_mois[m].append(v)
    if len(par_mois) < 12:
        return {"libelle": "Données insuffisantes", "ok": None, "indices": None}
    moy = [statistics.mean(par_mois[m]) for m in range(1, 13)]
    mu = statistics.mean(moy)
    if mu == 0:
        return {"libelle": "Données insuffisantes", "ok": None, "indices": None}
    idx = [x / mu for x in moy]
    debut = max(range(12), key=lambda s: idx[s] + idx[(s + 1) % 12] + idx[(s + 2) % 12])
    pic = [debut, (debut + 1) % 12, (debut + 2) % 12]
    fenetre = f"{MOIS[pic[0]]}-{MOIS[pic[2]]}"
    centre = pic[1] + 1
    if max(idx) <= PIC_EVERGREEN_MAX:
        leger = f" (léger pic {fenetre})" if max(idx) > 1.15 else ""
        return {"libelle": "EVERGREEN" + leger, "ok": True, "indices": idx, "lancement": None}
    saison = ("HIVER" if centre in (1, 2) else "PRINTEMPS" if centre in (3, 4, 5) else
              "ÉTÉ" if centre in (6, 7, 8) else "AUTOMNE" if centre == 9 else "Q4")
    lancement = MOIS[(pic[0] - 2) % 12]  # 4 à 6 semaines avant le début du pic
    return {"libelle": f"{saison} (pic {fenetre})", "ok": saison == "PRINTEMPS", "indices": idx,
            "lancement": lancement, "saison": saison}


def analyser(chemin):
    with open(chemin, encoding="utf-8") as f:
        rep = json.load(f)
    ctx = rep.get("_contexte", {})
    taux = ctx.get("usd_pour_1_eur")
    date_releve = (ctx.get("lance_le") or "")[:10]
    items = {}
    for it in rep["tasks"][0].get("result") or []:
        items[it["keyword"].lower()] = it
    lignes = []
    for idee in lire_idees():
        variantes = []
        for k in idee["mots_cles"]:
            it = items.get(k.lower())
            if it and it.get("search_volume") is not None:
                variantes.append(it)
        if not variantes:
            lignes.append({"produit": idee["produit"], "niche": idee["niche"], "statut": "ROUGE",
                           "commentaire": "Éliminé : aucune donnée Google pour ces mots-clés.", "ligne_existante": idee.get("ligne_existante")})
            continue
        # Dédoublonnage : mêmes chiffres mois par mois = variantes que Google regroupe déjà
        groupes, signatures, regroupees = [], {}, []
        for it in variantes:
            sig = (it["search_volume"], tuple((x["year"], x["month"], x["search_volume"]) for x in (it.get("monthly_searches") or [])))
            if sig in signatures:
                regroupees.append((it["keyword"], signatures[sig]))
            else:
                signatures[sig] = it["keyword"]
                groupes.append(it)
        total = sum(it["search_volume"] for it in groupes)
        principal = max(groupes, key=lambda it: it["search_volume"])
        detail = " + ".join(f"{it['keyword']} {it['search_volume']:,}".replace(",", " ") for it in groupes)
        if len(groupes) > 1:
            detail += f" = {total:,}".replace(",", " ")
        if regroupees:
            detail += " (non additionné, Google les compte déjà ensemble : " + ", ".join(f"{a} = {b}" for a, b in regroupees) + ")"
        serie = defaultdict(int)
        for it in groupes:
            for x in it.get("monthly_searches") or []:
                serie[(x["year"], x["month"])] += x["search_volume"] or 0
        s = saisonnalite([(a, m, v) for (a, m), v in sorted(serie.items())])
        haut = principal.get("high_top_of_page_bid")
        cpc_usd = haut if haut is not None else principal.get("cpc")
        cpc_eur = round(cpc_usd / taux, 2) if (cpc_usd is not None and taux) else None
        conc = principal.get("competition")
        raisons = []
        if total < VOLUME_MIN:
            raisons.append(f"volume {total:,} sous les 8 000".replace(",", " "))
        if conc == "HIGH":
            raisons.append("concurrence Google Ads élevée")
        if raisons:
            statut = "ROUGE"
            commentaire = "Éliminé : " + " et ".join(raisons) + "."
        elif s["ok"] is False:
            statut = "BLEU"
            nom_saison = s["saison"] if s["saison"] == "Q4" else s["saison"].lower()
            commentaire = f"Pas pour tout de suite : saison {nom_saison}, à lancer vers {s['lancement']}."
        else:
            statut = "JAUNE"
            commentaire = "À évaluer : chiffres OK, reste fournisseurs et concurrents."
        if cpc_eur is not None and statut != "ROUGE":
            commentaire += f" Critère CPC : il faudra au moins {cpc_eur * CLICS_PAR_VENTE:.0f} € de marge brute."
        if conc is None and statut != "ROUGE":
            commentaire += " Concurrence Ads non fournie par Google."
        q = urllib.parse.quote(principal["keyword"])
        lignes.append({
            "produit": idee["produit"], "niche": idee["niche"], "ligne_existante": idee.get("ligne_existante"),
            "mot_cle_principal": principal["keyword"], "volume_total": total, "volume_detail": detail,
            "cpc_eur": cpc_eur, "cpc_source": "fourchette haute (enchère haut de page)" if haut is not None else "CPC moyen (fourchette haute absente)",
            "concurrence": CONCURRENCE_FR.get(conc, "Non fournie"), "saisonnalite": s["libelle"],
            "indices_mensuels": [round(x, 2) for x in s["indices"]] if s["indices"] else None,
            "trends": f"https://trends.google.fr/trends/explore?date=today%205-y&geo=FR&q={q}",
            "statut": statut, "commentaire": commentaire,
            "source": f"Source : DataForSEO, données Google Ads, France, langue française, relevé le {date_releve}. "
                      f"Montants convertis de USD en EUR au taux {ctx.get('source_taux')} du {ctx.get('date_taux')} "
                      f"({taux} USD pour 1 EUR).",
        })
    base = os.path.splitext(chemin)[0].replace("dataforseo-", "resultats-")
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(lignes, f, ensure_ascii=False, indent=1)
    with open(base + ".csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["produit", "statut", "volume_total", "cpc_eur", "concurrence", "saisonnalite", "volume_detail", "commentaire"])
        for l in lignes:
            w.writerow([l["produit"], l["statut"], l.get("volume_total"), l.get("cpc_eur"), l.get("concurrence"),
                        l.get("saisonnalite"), l.get("volume_detail"), l["commentaire"]])
    for l in lignes:
        print(f"{l['statut']:6} | {l['produit']:28} | {str(l.get('volume_total')):>7} | {str(l.get('cpc_eur')):>5} € | "
              f"{str(l.get('concurrence')):8} | {l.get('saisonnalite')} | {l['commentaire']}")
    print("fichiers :", base + ".json", base + ".csv")
    return lignes


def test():
    """Données fictives : vérifie l'addition, le dédoublonnage, la saisonnalité et les statuts."""
    def serie(base, profil):
        return [{"year": 2023 + (i // 12), "month": i % 12 + 1, "search_volume": int(base * profil[i % 12])} for i in range(36)]
    plat = [1] * 12
    printemps = [0.6, 0.9, 1.6, 1.8, 1.5, 1.1, 0.9, 0.7, 0.6, 0.7, 0.8, 0.8]
    q4 = [0.7, 0.7, 0.8, 0.8, 0.8, 0.9, 1.0, 1.0, 1.0, 1.4, 1.7, 1.2]
    def item(k, vol, comp, bid, prof):
        return {"keyword": k, "search_volume": vol, "competition": comp, "high_top_of_page_bid": bid, "cpc": bid / 2,
                "monthly_searches": serie(vol, prof)}
    fake = {"_contexte": {"usd_pour_1_eur": 1.10, "date_taux": "2026-11-09", "source_taux": "test", "lance_le": "2026-11-10T20:00"},
            "tasks": [{"result": [
                item("chaise ergonomique", 6000, "MEDIUM", 1.32, plat), item("chaise de bureau ergonomique", 4000, "MEDIUM", 1.5, plat),
                item("fauteuil de bureau ergonomique", 4000, "MEDIUM", 1.5, plat),   # mêmes chiffres : regroupée
                item("brasero", 90000, "LOW", 0.55, printemps),
                item("cave à vin", 60000, "HIGH", 0.3, q4),
                item("barbecue", 50000, "MEDIUM", 0.5, q4)]}]}
    os.makedirs(DONNEES, exist_ok=True)
    chemin = os.path.join(DONNEES, "dataforseo-TEST.json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(fake, f)
    lignes = {l["produit"]: l for l in analyser(chemin)}
    c = lignes["chaise ergonomique"]
    assert c["volume_total"] == 10000, c["volume_total"]           # 6000 + 4000, la 3e variante n'est pas recomptée
    assert "non additionné" in c["volume_detail"]
    assert c["statut"] == "JAUNE" and c["saisonnalite"] == "EVERGREEN"
    assert c["cpc_eur"] == 1.2                                       # 1,32 $ / 1,10
    assert lignes["brasero"]["statut"] == "JAUNE" and lignes["brasero"]["saisonnalite"].startswith("PRINTEMPS")
    assert lignes["cave à vin"]["statut"] == "ROUGE"                 # concurrence élevée
    assert lignes["barbecue"]["statut"] == "BLEU" and lignes["barbecue"]["saisonnalite"].startswith("Q4")
    for f in (chemin, chemin.replace("dataforseo-", "resultats-").replace(".json", ".csv"),
              chemin.replace("dataforseo-", "resultats-")):
        os.remove(f)
    print("tests OK")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "fetch":
        analyser(fetch())
    elif cmd == "analyse":
        analyser(sys.argv[2])
    elif cmd == "test":
        test()
    else:
        print(__doc__)
