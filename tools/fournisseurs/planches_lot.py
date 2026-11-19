"""Planches de comparaison pour un lot : pour chaque ligneXX.json, une image avec
la photo du concurrent, puis les résultats AliExpress (A1 à A6) et VidaXL (V1 à V4), avec leur prix.
Usage : python3 -I planches_lot.py DOSSIER_DU_LOT [ligne ...]"""
import io
import json
import os
import re
import sys
import urllib.request

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prix import premier_prix  # noqa: E402


def page_vidaxl(url):
    """Photo et prix d'une fiche VidaXL (le prix est dans les données structurées de la page)."""
    try:
        h = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Chrome/124"}), timeout=40).read().decode("utf-8", "replace")
    except Exception:
        return None, None
    img = (re.search(r'og:image" content="([^"]+)"', h) or [None, None])[1]
    p = re.search(r'"price":\s*"?([0-9.]+)', h)
    return img, (float(p.group(1)) if p else None)


dossier = sys.argv[1]
lignes = sys.argv[2:]
T = 230


def charge(url):
    if not url:
        return None
    url = url if url.startswith("http") else "https:" + url
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read()
        return Image.open(io.BytesIO(data)).convert("RGB")
    except Exception:
        return None


for f in sorted(os.listdir(dossier)):
    if not (f.startswith("ligne") and f.endswith(".json")):
        continue
    if lignes and f[5:-5] not in lignes:
        continue
    r = json.load(open(os.path.join(dossier, f), encoding="utf-8"))
    # Prix AliExpress relus avec la lecture corrigée ; fiches VidaXL complétées (photo, prix)
    for a in (r.get("aliexpress") or {}).get("resultats") or []:
        a["prix"] = premier_prix(a.get("texte"))
    for v in r.get("vidaxl") or []:
        if v.get("url") and (not v.get("img") or v.get("prix") is None):
            img, px = page_vidaxl(v["url"])
            v["img"] = v.get("img") or img
            v["prix"] = v.get("prix") if v.get("prix") is not None else px
    json.dump(r, open(os.path.join(dossier, f), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cases = []
    c = r.get("concurrent", {})
    if c.get("fichier") and os.path.exists(c["fichier"]):
        try:
            cases.append((f"Concurrent {c.get('prix', '?')} €", Image.open(c["fichier"]).convert("RGB")))
        except Exception:
            pass
    for i, a in enumerate((r.get("aliexpress") or {}).get("resultats") or [], 1):
        cases.append((f"A{i} {a.get('prix', '?')} €", charge(a.get("img"))))
    for i, v in enumerate(r.get("vidaxl") or [], 1):
        if v.get("url"):
            cases.append((f"V{i} {v.get('prix', '?')} €", charge(v.get("img"))))
    if not cases:
        continue
    par_ligne = 6
    nb_l = (len(cases) + par_ligne - 1) // par_ligne
    planche = Image.new("RGB", (T * min(par_ligne, len(cases)), (T + 28) * nb_l), "white")
    d = ImageDraw.Draw(planche)
    for k, (lab, im) in enumerate(cases):
        x, y = (k % par_ligne) * T, (k // par_ligne) * (T + 28)
        d.text((x + 6, y + 6), lab, fill="black")
        if im:
            im.thumbnail((T - 10, T - 10))
            planche.paste(im, (x + 5, y + 26))
    sortie = os.path.join(dossier, f"planche-{f[:-5]}.jpg")
    planche.save(sortie, "JPEG", quality=80)
    print(sortie, len(cases), "cases")
