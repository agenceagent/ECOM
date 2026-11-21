"""Délai de livraison VidaXL de chaque fiche, lu dans les données structurées de la page
(JSON-LD : offers.shippingDetails.deliveryTime, avec transitTime et handlingTime quand il y en a).
Usage : python3 -I delais_vidaxl.py entree.json sortie.json
entree.json : {"produit": ["url VidaXL", ...], ...}"""
import json
import re
import sys
import time
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36", "Accept-Language": "fr-FR,fr;q=0.9"}


def lire(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read().decode("utf-8", "replace")


def offres(h):
    for bloc in re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S):
        try:
            d = json.loads(bloc)
        except ValueError:
            continue
        pile = [d]
        while pile:
            o = pile.pop()
            if isinstance(o, list):
                pile.extend(o)
            elif isinstance(o, dict):
                if o.get("@type") == "Offer":
                    yield o
                pile.extend(o.values())


def delai(url):
    h = lire(url)
    for o in offres(h):
        dt = (o.get("shippingDetails") or {}).get("deliveryTime") or {}
        res = {"dispo": (o.get("availability") or "").rsplit("/", 1)[-1], "prix": o.get("price")}
        for cle in ("handlingTime", "transitTime"):
            v = dt.get(cle)
            if v:
                res[cle] = [v.get("minValue"), v.get("maxValue"), v.get("unitCode")]
        return res
    return {"erreur": "pas d'offre JSON-LD"}


if __name__ == "__main__":
    entree = json.load(open(sys.argv[1], encoding="utf-8"))
    sortie = {}
    for produit, urls in entree.items():
        sortie[produit] = []
        for url in urls:
            try:
                r = delai(url)
            except Exception as e:
                r = {"erreur": f"{e.__class__.__name__}: {e}"[:120]}
            r["url"] = url
            sortie[produit].append(r)
            print(produit, "|", {k: v for k, v in r.items() if k != "url"}, "|", url.rsplit("/", 1)[-1])
            time.sleep(1)
    json.dump(sortie, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
