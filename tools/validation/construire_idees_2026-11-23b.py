"""Idées du 23/11/2026 (2e envoi), avec les règles du coach : niches autres que maison et jardin, prix de revente
habituel entre 150 et 500 € chez les boutiques en dropshipping, liste noire, rien de déjà testé.
Usage : python3 -I construire_idees_2026-11-23b.py idees-2026-11-23b.json"""
import json
import os
import sys
ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
from valider import variantes  # noqa: E402

EQ, API, PE, GO, GA, MU, EV, BE, MA, MO, VA, CY, NA, JE, DA, PRO, HO, AN = (
    "Équitation", "Apiculture", "Pêche", "Golf", "Simulation, gaming", "Musique", "Mariage, événementiel",
    "Beauté, cheveux", "Maroquinerie, mode", "Moto, auto", "Van, camping-car", "Cyclisme", "Sports nautiques",
    "Jeux", "Danse, fitness", "Professionnels", "Loisirs créatifs", "Petits animaux de ferme")
I = [
 ("selle de cheval", EQ, ["selle de cheval", "selle cheval"]), ("selle western", EQ, ["selle western"]),
 ("obstacle d'équitation", EQ, ["obstacle équitation", "obstacle cheval"]), ("couverture pour cheval", EQ, ["couverture cheval"]),
 ("ruche", API, ["ruche", "ruche dadant", "ruche warré"]), ("extracteur de miel", API, ["extracteur de miel"]),
 ("maturateur à miel", API, ["maturateur miel"]), ("kit apiculture", API, ["kit apiculture", "kit apiculteur"]),
 ("biwy", PE, ["biwy", "biwy carpe"]), ("bedchair", PE, ["bedchair", "bed chair carpe"]), ("kayak de pêche", PE, ["kayak de pêche"]),
 ("barque de pêche", PE, ["barque de pêche"]),
 ("filet de golf", GO, ["filet de golf", "filet d'entraînement golf"]), ("tapis de golf", GO, ["tapis de golf", "tapis de practice golf"]),
 ("putting green", GO, ["putting green"]), ("chariot de golf", GO, ["chariot de golf"]),
 ("cockpit simracing", GA, ["cockpit simracing", "cockpit sim racing", "siège simracing"]),
 ("cajon", MU, ["cajon"]), ("tongue drum", MU, ["tongue drum", "steel tongue drum"]), ("djembé", MU, ["djembé"]),
 ("harpe lyre", MU, ["harpe lyre"]), ("banjo", MU, ["banjo"]), ("violoncelle", MU, ["violoncelle"]), ("trompette", MU, ["trompette"]),
 ("flûte traversière", MU, ["flûte traversière"]), ("guitare classique", MU, ["guitare classique"]), ("guitare électrique", MU, ["guitare électrique"]),
 ("arche de mariage", EV, ["arche de mariage", "arche mariage"]), ("mur de fleurs", EV, ["mur de fleurs", "mur de fleurs artificielles"]),
 ("robe de mariée", EV, ["robe de mariée"]), ("costume de mariage", EV, ["costume de mariage homme", "costume mariage"]),
 ("perruque cheveux naturels", BE, ["perruque cheveux naturels", "perruque naturelle"]), ("perruque lace", BE, ["perruque lace front", "lace wig"]),
 ("extensions cheveux naturels", BE, ["extension cheveux naturels", "extensions cheveux"]),
 ("sac à main en cuir", MA, ["sac à main cuir", "sac en cuir femme"]), ("sac cabas en cuir", MA, ["sac cabas cuir"]),
 ("sacoche homme en cuir", MA, ["sacoche homme cuir"]), ("montre automatique", MA, ["montre automatique", "montre automatique homme"]),
 ("lève-moto", MO, ["lève moto", "élévateur moto"]), ("porte-moto", MO, ["porte moto"]), ("abri moto", MO, ["abri moto", "garage moto"]),
 ("toilette chimique", VA, ["toilette chimique", "wc chimique", "toilette portable"]), ("marchepied camping-car", VA, ["marchepied camping car"]),
 ("tricycle adulte", CY, ["tricycle adulte"]), ("home trainer", CY, ["home trainer"]), ("remorque vélo", CY, ["remorque vélo"]),
 ("bouée tractée", NA, ["bouée tractée"]), ("kitesurf", NA, ["kitesurf"]), ("bodyboard", NA, ["bodyboard"]),
 ("cornhole", JE, ["cornhole", "jeu de cornhole"]), ("jeu de palet", JE, ["jeu de palet"]),
 ("barre de danse", DA, ["barre de danse", "barre de ballet"]), ("hamac de yoga", DA, ["hamac de yoga", "hamac aérien"]),
 ("tapis de course manuel", DA, ["tapis de course manuel"]),
 ("mannequin de vitrine", PRO, ["mannequin vitrine", "mannequin de magasin"]), ("chaise de massage", PRO, ["chaise de massage"]),
 ("maquette de bateau", HO, ["maquette bateau", "maquette bateau bois"]), ("rouet", HO, ["rouet"]), ("mannequin de couture", HO, ["mannequin couture"]),
 ("fût de chêne", HO, ["fût de chêne", "tonneau en chêne"]),
 ("clapier", AN, ["clapier", "clapier lapin"]), ("volière", AN, ["volière"]), ("cage à lapin", AN, ["cage lapin"]),
 ("sac de frappe sur pied", DA, ["sac de frappe sur pied"]), ("station de street workout", DA, ["station street workout", "barre de traction extérieure"]),
 ("trottinette adulte", CY, ["trottinette adulte"]), ("tambour chamanique", MU, ["tambour chamanique"]), ("gong", MU, ["gong"]),
 ("blouson aviateur", MA, ["blouson aviateur"]), ("tabouret selle", PRO, ["tabouret selle", "tabouret ergonomique selle"]),
 ("cage à oiseaux", AN, ["cage à oiseaux"]), ("cage à perroquet", AN, ["cage perroquet"]), ("pressoir à fruits", HO, ["pressoir", "pressoir à pommes"]),
 ("coffre de sellerie", EQ, ["coffre de sellerie"]), ("mirador de chasse", PE, ["mirador chasse"]),
]

# Déjà testés : les deux listes d'idées précédentes, plus ce que l'associé a dans sa liste
deja = set()
for f in ("idees.json", "idees-2026-11-23.json"):
    for i in json.load(open(os.path.join(ICI, f), encoding="utf-8"))["idees"]:
        deja.update(k.lower() for k in i["mots_cles"])
deja.update(["cave à vin électrique", "extracteur de jus", "rameur d'appartement", "sac à langer", "tableau magnétique",
             "panier pour chien", "chauffage extérieur"])
idees, mots, ecartes = [], [], []
for produit, niche, mc in I:
    garde = [k for k in mc if k.lower() not in deja]
    ecartes += [k for k in mc if k.lower() in deja]
    if not garde:
        continue
    idees.append({"produit": produit, "niche": niche, "mots_cles": garde})
    for k in variantes(idees[-1]):
        if k.lower() not in (m.lower() for m in mots):
            mots.append(k)
print(len(idees), "idées,", len(mots), "mots-clés ; déjà testés, retirés :", ecartes)
json.dump({"_lisez_moi": "2e liste du 23/11/2026 : règles du coach (revente 500 € max, CPC 0,80 € max), niches hors maison et jardin, liste noire.",
           "idees": idees}, open(os.path.join(ICI, sys.argv[1]), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
