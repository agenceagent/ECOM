"""Prix de vente des concurrents relevés par l'apprenant (colonne G) et moyenne par produit (colonne E).
Boutiques Shopify : fiche <url>.json, prix de la variante pointée par le lien (sinon la variante par défaut),
demandé en euros pour la France. Autres sites : prix lu dans les données de la page (JSON-LD, balises meta).
Usage : python3 -I prix_vente.py concurrents_grille.json sortie.json"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36", "Accept-Language": "fr-FR,fr;q=0.9"}


def lire(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "replace")


def prix_shopify(url):
    u = urllib.parse.urlsplit(url)
    variante = urllib.parse.parse_qs(u.query).get("variant", [None])[0]
    base = f"{u.scheme}://{u.netloc}{u.path.rstrip('/')}"
    p = json.loads(lire(base + ".json?currency=EUR&country=FR"))["product"]
    v = next((x for x in p["variants"] if str(x["id"]) == str(variante)), None) if variante else None
    choisie = "variante du lien" if v else "variante par défaut"
    v = v or p["variants"][0]
    devise = v.get("price_currency") or (v.get("presentment_prices") or [{}])[0].get("price", {}).get("currency_code")
    return {"prix": float(v["price"]), "titre": p["title"], "variante": v.get("title"), "choix": choisie,
            "devise": devise, "methode": "shopify .json"}


def prix_page(url):
    h = lire(url)
    for motif in (r'"price"\s*:\s*"?([0-9]+(?:[.,][0-9]+)?)"?',
                  r'product:price:amount"\s+content="([0-9.,]+)"',
                  r'itemprop="price"\s+content="([0-9.,]+)"'):
        m = re.search(motif, h)
        if m:
            titre = (re.search(r"<title>([^<]+)</title>", h) or [None, ""])[1].strip()
            return {"prix": float(m.group(1).replace(",", ".")), "titre": titre, "methode": "page (" + motif[:20] + ")"}
    return {"erreur": "prix introuvable dans la page"}


def relever(url):
    try:
        if "/products/" in url:
            try:
                return prix_shopify(url)
            except Exception as e:
                r = prix_page(url)
                r["note"] = f"pas de .json Shopify ({e.__class__.__name__})"
                return r
        return prix_page(url)
    except Exception as e:
        return {"erreur": f"{e.__class__.__name__}: {e}"[:160]}


if __name__ == "__main__":
    entree = json.load(open(sys.argv[1], encoding="utf-8"))["lignes"]
    sortie = []
    for ligne in entree:
        res = []
        for url in dict.fromkeys(ligne["urls"]):  # un même lien collé deux fois ne compte qu'une fois
            r = relever(url)
            r["url"] = url
            res.append(r)
            print(ligne["ligne"], ligne["produit"], "|", r.get("prix"), r.get("devise", ""), "|", (r.get("titre") or r.get("erreur", ""))[:60], "|", r.get("choix", r.get("methode", "")))
            time.sleep(1)
        prix = [r["prix"] for r in res if r.get("prix")]
        sortie.append({**ligne, "releves": res, "moyenne": round(sum(prix) / len(prix), 2) if prix else None, "nb": len(prix)})
    json.dump(sortie, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
