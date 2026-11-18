"""Planche de comparaison : photo du concurrent à gauche, puis les résultats AliExpress numérotés."""
import io
import json
import os
import sys
import urllib.request

from PIL import Image, ImageDraw

dossier, nom, sortie = sys.argv[1], sys.argv[2], sys.argv[3]
res = json.load(open(os.path.join(dossier, nom + "-resultats.json"), encoding="utf-8"))
T = 260
vignettes = [("Concurrent", Image.open(os.path.join(dossier, nom + "-q.jpg")).convert("RGB"))]
for i, r in enumerate(res[:6], 1):
    if not r.get("img"):
        continue
    url = r["img"] if r["img"].startswith("http") else "https:" + r["img"]
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read()
        vignettes.append((f"{i}", Image.open(io.BytesIO(data)).convert("RGB")))
    except Exception as e:
        print("image", i, "illisible :", e)
planche = Image.new("RGB", (T * len(vignettes), T + 30), "white")
d = ImageDraw.Draw(planche)
for k, (lab, im) in enumerate(vignettes):
    im.thumbnail((T - 10, T - 10))
    planche.paste(im, (k * T + 5, 30))
    d.text((k * T + 8, 8), lab, fill="black")
planche.save(sortie, "JPEG", quality=85)
print(sortie, len(vignettes) - 1, "résultats")
