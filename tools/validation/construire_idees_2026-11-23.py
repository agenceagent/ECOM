"""Idées high ticket du 23/11/2026 (hors liste noire) -> idees-2026-11-23.json"""
import json, sys
sys.path.insert(0, "/home/user/ECOM/tools/validation")
J, M, S, C, B, A, P, L, V = ("Jardin, extérieur", "Maison, mobilier", "Sport, musculation", "Camping, plein air",
                             "Bureau", "Atelier, garage", "Professionnels", "Loisirs, jeux", "Mode, bagagerie")
I = [
 # Jardin et extérieur
 ("tonnelle", J, ["tonnelle", "tonnelle de jardin", "tonnelle autoportante"]), ("voile d'ombrage", J, ["voile d'ombrage"]),
 ("parasol déporté", J, ["parasol déporté"]), ("hamac sur pied", J, ["hamac sur pied"]),
 ("fauteuil suspendu", J, ["fauteuil suspendu", "fauteuil oeuf", "chaise suspendue"]), ("lit de jardin", J, ["lit de jardin", "daybed"]),
 ("canapé de jardin", J, ["canapé de jardin", "canapé d'extérieur"]), ("salon bas de jardin", J, ["salon bas de jardin"]),
 ("table de jardin", J, ["table de jardin", "table de jardin extensible", "table de terrasse"]), ("banc de jardin", J, ["banc de jardin"]),
 ("fauteuil de jardin", J, ["fauteuil de jardin", "fauteuil de terrasse"]), ("bar de jardin", J, ["bar de jardin", "bar extérieur"]),
 ("cuisine d'extérieur", J, ["cuisine extérieure", "cuisine d'été"]), ("coffre de jardin", J, ["coffre de jardin", "coffre de rangement extérieur"]),
 ("abri bûches", J, ["abri bûches", "abri à bois", "range bûches"]), ("potager surélevé", J, ["potager surélevé", "carré potager"]),
 ("jardinière sur pied", J, ["jardinière sur pied"]), ("panneau brise-vue", J, ["panneau brise vue", "claustra"]),
 ("portillon", J, ["portillon"]), ("gloriette", J, ["gloriette", "kiosque de jardin", "pavillon de jardin"]), ("tente de réception", J, ["tente de réception", "barnum", "tente pliante"]),
 ("store banne", J, ["store banne"]), ("douche de jardin", J, ["douche de jardin", "douche solaire", "douche extérieure"]),
 ("bain nordique", J, ["bain nordique", "bain norvégien"]), ("sauna extérieur", J, ["sauna extérieur", "sauna tonneau", "sauna finlandais"]),
 ("abri vélo", J, ["abri vélo", "abri à vélo"]), ("serre tunnel", J, ["serre tunnel"]), ("serre adossée", J, ["serre adossée"]),
 ("table de pique-nique", J, ["table de pique nique"]), ("fauteuil adirondack", J, ["fauteuil adirondack"]),
 ("cheminée d'extérieur", J, ["cheminée d'extérieur", "cheminée de jardin"]), ("boîte aux lettres", J, ["boîte aux lettres"]),
 ("abri poubelle", J, ["abri poubelle", "cache poubelle"]), ("gazon synthétique", J, ["gazon synthétique"]),
 ("chalet de jardin", J, ["chalet de jardin"]), ("mur végétal", J, ["mur végétal"]), ("olivier artificiel", M, ["olivier artificiel", "arbre artificiel"]),
 ("bain de soleil double", J, ["bain de soleil double"]), ("pool house", J, ["pool house"]), ("abri de terrasse", J, ["abri de terrasse"]),
 ("table de jardin en bois", J, ["table de jardin en bois"]), ("salon de jardin en teck", J, ["salon de jardin teck"]),
 ("transat de piscine", J, ["transat piscine"]), ("douche de piscine", J, ["douche de piscine"]),
 # Jeux et loisirs
 ("babyfoot", L, ["baby foot", "babyfoot"]), ("billard", L, ["billard", "table de billard", "billard convertible"]), ("table multi-jeux", L, ["table multi jeux"]),
 ("table de poker", L, ["table de poker"]), ("panier de basket", L, ["panier de basket", "panier de basket sur pied"]), ("chevalet de peinture", L, ["chevalet de peinture", "chevalet"]),
 ("table à dessin", L, ["table à dessin"]), ("métier à tisser", L, ["métier à tisser"]), ("cave à cigares", L, ["cave à cigare", "humidor"]),
 ("jeu de fléchettes", L, ["cible fléchette"]), ("table de jeu", L, ["table de jeu"]),
 # Sport et musculation
 ("banc de musculation", S, ["banc de musculation", "banc développé couché"]), ("rack à squat", S, ["rack à squat", "cage à squat", "cage de musculation"]),
 ("station de musculation", S, ["station de musculation", "appareil de musculation", "machine de musculation"]), ("presse à cuisses", S, ["presse à cuisse"]),
 ("haltères réglables", S, ["haltères réglables"]), ("barre olympique", S, ["barre olympique"]), ("disques de musculation", S, ["disque de musculation"]),
 ("rameur", S, ["rameur", "rameur à eau"]), ("vélo elliptique", S, ["vélo elliptique"]), ("espalier", S, ["espalier"]),
 ("barre de traction", S, ["barre de traction", "station de traction"]), ("chaise romaine", S, ["chaise romaine"]),
 ("reformer pilates", S, ["reformer pilates", "machine pilates"]), ("tatami", M, ["tatami"]), ("mannequin de boxe", S, ["mannequin de boxe"]),
 ("poulie de musculation", S, ["poulie musculation", "poulie haute"]), ("banc abdominaux", S, ["banc abdominaux"]), ("barres parallèles", S, ["barres parallèles", "station dips"]),
 ("smith machine", S, ["smith machine", "cage guidée"]), ("air bike", S, ["air bike"]), ("planche de surf", S, ["planche de surf"]),
 ("longboard", S, ["longboard"]), ("wingfoil", S, ["wingfoil", "wing foil"]), ("float tube", S, ["float tube"]),
 ("bateau gonflable", S, ["bateau gonflable", "annexe bateau"]), ("canoë", S, ["canoë"]), ("ring de boxe", S, ["ring de boxe"]),
 ("vélo de ville", S, ["vélo de ville", "vélo hollandais"]), ("vélo pliant", S, ["vélo pliant"]), ("fixie", S, ["fixie"]), ("tandem", S, ["vélo tandem"]),
 ("gilet lesté", S, ["gilet lesté"]), ("kettlebell réglable", S, ["kettlebell réglable"]), ("plateau de musculation", S, ["home gym"]),
 # Camping et plein air
 ("tente gonflable", C, ["tente gonflable"]), ("tente familiale", C, ["tente familiale", "tente 6 places"]), ("tente tipi", C, ["tente tipi"]),
 ("auvent voiture", C, ["auvent voiture", "auvent van"]), ("glacière rigide", C, ["glacière rigide", "glacière à roulettes"]), ("cuisine de camping", C, ["cuisine de camping"]),
 ("poêle à bois de camping", C, ["poêle à bois camping"]), ("galerie de toit", C, ["galerie de toit"]), ("garage pliable", C, ["garage pliable"]),
 ("tente de camping", C, ["tente de camping"]), ("hamac de camping", C, ["hamac camping"]), ("lit de camp", C, ["lit de camp"]),
 # Maison : salon
 ("canapé convertible", M, ["canapé convertible", "canapé lit"]), ("canapé d'angle", M, ["canapé d'angle", "canapé d'angle convertible"]), ("canapé 3 places", M, ["canapé 3 places"]),
 ("canapé velours", M, ["canapé velours"]), ("canapé modulable", M, ["canapé modulable"]), ("canapé chesterfield", M, ["canapé chesterfield"]),
 ("canapé cuir", M, ["canapé cuir"]), ("fauteuil de lecture", M, ["fauteuil de lecture"]), ("fauteuil scandinave", M, ["fauteuil scandinave"]),
 ("fauteuil club", M, ["fauteuil club"]), ("fauteuil à bascule", M, ["fauteuil à bascule", "rocking chair"]), ("fauteuil relax", M, ["fauteuil relax"]),
 ("fauteuil crapaud", M, ["fauteuil crapaud"]), ("fauteuil bouclette", M, ["fauteuil bouclette"]), ("fauteuil chesterfield", M, ["fauteuil chesterfield"]),
 ("fauteuil en rotin", M, ["fauteuil rotin"]), ("méridienne", M, ["méridienne"]), ("banquette", M, ["banquette"]),
 ("table basse", M, ["table basse"]), ("table basse relevable", M, ["table basse relevable"]), ("table basse ronde", M, ["table basse ronde"]),
 ("meuble TV", M, ["meuble tv"]), ("bibliothèque", M, ["bibliothèque murale", "étagère bibliothèque"]), ("enfilade", M, ["buffet bas", "enfilade"]),
 ("commode", M, ["commode"]), ("console d'entrée", M, ["console d'entrée", "meuble console"]), ("meuble d'entrée", M, ["meuble d'entrée"]),
 ("meuble à chaussures", M, ["meuble à chaussures"]), ("banc d'entrée", M, ["banc d'entrée"]), ("paravent", M, ["paravent"]),
 ("tapis de salon", M, ["tapis de salon", "grand tapis"]), ("tapis berbère", M, ["tapis berbère"]), ("tapis en jute", M, ["tapis jute"]),
 ("tapis persan", M, ["tapis persan"]), ("lampadaire", M, ["lampadaire", "lampe sur pied", "lampadaire arc"]), ("suspension luminaire", M, ["suspension luminaire", "suspension rotin"]),
 ("meuble bar", M, ["meuble bar"]), ("chariot de bar", M, ["chariot de bar"]), ("casier à vin", M, ["casier à vin", "range bouteille"]),
 ("desserte", M, ["desserte"]), ("meuble vinyle", M, ["meuble vinyle"]), ("secrétaire", M, ["secrétaire meuble"]),
 ("meuble de rangement", M, ["meuble de rangement"]), ("vitrine de collection", M, ["vitrine"]),
 # Maison : chambre
 ("tête de lit", M, ["tête de lit"]), ("lit coffre", M, ["lit coffre"]), ("lit double", M, ["lit double", "lit 160x200", "lit 2 places"]), ("lit en bois", M, ["lit en bois"]),
 ("lit baldaquin", M, ["lit baldaquin"]), ("lit escamotable", M, ["lit escamotable"]), ("lit mezzanine", M, ["lit mezzanine"]), ("cadre de lit", M, ["cadre de lit"]),
 ("sommier", M, ["sommier"]), ("dressing", M, ["dressing"]), ("penderie", M, ["penderie"]), ("coiffeuse", M, ["coiffeuse meuble", "table de maquillage"]),
 ("chiffonnier", M, ["chiffonnier"]), ("malle en bois", M, ["malle en bois"]), ("coffre de rangement", M, ["coffre de rangement"]),
 ("lit futon", M, ["futon"]), ("lit rotin", M, ["lit rotin"]), ("lit capitonné", M, ["lit capitonné"]),
 # Maison : salle à manger et cuisine
 ("table à manger", M, ["table à manger", "table de salle à manger"]), ("table extensible", M, ["table extensible"]), ("table ronde", M, ["table ronde"]),
 ("table en bois massif", M, ["table bois massif"]), ("chaises de salle à manger", M, ["chaise salle à manger"]), ("tabouret de bar", M, ["tabouret de bar"]),
 ("table haute", M, ["table haute"]), ("îlot central", M, ["îlot central", "îlot de cuisine"]), ("desserte de cuisine", M, ["desserte de cuisine"]),
 ("couteau japonais", M, ["couteau japonais"]), ("batterie de cuisine", M, ["batterie de cuisine"]), ("meuble sous vasque", M, ["meuble sous vasque"]),
 ("banc de salle à manger", M, ["banc salle à manger"]), ("buffet de cuisine", M, ["buffet de cuisine", "buffet haut"]),
 # Bureau
 ("bureau en bois", B, ["bureau en bois", "bureau bois"]), ("bureau d'angle", B, ["bureau d'angle"]), ("bureau gamer", B, ["bureau gamer"]),
 ("chaise gamer", B, ["chaise gamer", "fauteuil gamer"]), ("bureau mural", B, ["bureau mural"]), ("chaise de bureau", B, ["chaise de bureau", "fauteuil de bureau"]),
 ("bureau scandinave", B, ["bureau scandinave"]), ("bureau secrétaire", B, ["bureau secrétaire"]),
 # Atelier et garage
 ("établi", A, ["établi", "établi de menuisier"]), ("servante d'atelier", A, ["servante d'atelier", "chariot à outils"]), ("armoire métallique", A, ["armoire métallique"]),
 ("étagère métallique", A, ["étagère métallique", "rayonnage"]), ("étagère de garage", A, ["étagère garage"]), ("armoire de garage", A, ["armoire de garage"]),
 # Professionnels
 ("fauteuil de barbier", P, ["fauteuil de barbier", "fauteuil barbier"]), ("fauteuil de coiffure", P, ["fauteuil de coiffure"]),
 ("table de massage", P, ["table de massage", "lit de massage"]), ("table de manucure", P, ["table de manucure"]),
 # Mode et bagagerie
 ("valise rigide", V, ["valise rigide", "valise", "valise soute"]), ("sac de voyage en cuir", V, ["sac de voyage cuir"]), ("sac à dos en cuir", V, ["sac à dos cuir"]),
 ("cartable en cuir", V, ["cartable cuir"]), ("porte-documents en cuir", V, ["porte document cuir"]), ("veste en cuir", V, ["veste en cuir", "blouson cuir"]),
 ("manteau en laine", V, ["manteau en laine"]),
 # Compléments
 ("table basse de jardin", J, ["table basse de jardin"]), ("grand parasol", J, ["grand parasol"]), ("auvent de porte", J, ["auvent de porte", "marquise"]),
 ("armoire de jardin", J, ["armoire de jardin"]), ("grand pot de fleur", J, ["grand pot de fleur"]), ("mobilier de jardin", J, ["mobilier de jardin"]),
 ("canapé", M, ["canapé"]), ("fauteuil", M, ["fauteuil"]), ("fauteuil inclinable", M, ["fauteuil inclinable"]), ("fauteuil de salon", M, ["fauteuil de salon"]),
 ("fauteuil cuir", M, ["fauteuil cuir"]), ("fauteuil velours", M, ["fauteuil velours"]), ("canapé bouclette", M, ["canapé bouclette"]),
 ("canapé scandinave", M, ["canapé scandinave"]), ("clic-clac", M, ["clic clac"]), ("canapé BZ", M, ["canapé bz"]), ("lit gigogne", M, ["lit gigogne"]),
 ("lit 140x190", M, ["lit 140x190"]), ("lit king size", M, ["lit king size"]), ("lit japonais", M, ["lit japonais"]), ("lit banquette", M, ["lit banquette"]),
 ("table ronde extensible", M, ["table ronde extensible"]), ("table scandinave", M, ["table scandinave"]), ("table industrielle", M, ["table industrielle"]),
 ("bureau industriel", B, ["bureau industriel"]), ("étagère industrielle", M, ["étagère industrielle"]), ("chaise scandinave", M, ["chaise scandinave"]),
 ("chaise en velours", M, ["chaise velours"]), ("tapis rond", M, ["tapis rond"]), ("tapis scandinave", M, ["tapis scandinave"]), ("tapis en laine", M, ["tapis laine"]),
 ("tapis vintage", M, ["tapis vintage"]), ("tapis kilim", M, ["tapis kilim"]), ("lustre", M, ["lustre"]),
 ("vélo de route", S, ["vélo de route"]), ("VTT", S, ["vtt"]), ("vélo gravel", S, ["vélo gravel"]), ("BMX", S, ["bmx"]), ("surfskate", S, ["surfskate"]),
 ("wakeboard", S, ["wakeboard"]), ("sac de golf", S, ["sac de golf"]),
 ("tente 4 places", C, ["tente 4 places"]), ("tente cloche", C, ["tente cloche"]), ("toilettes sèches", C, ["toilette sèche"]), ("yourte", C, ["yourte"]),
 ("bureau avec rangement", B, ["bureau avec rangement"]), ("bureau blanc", B, ["bureau blanc"]), ("fauteuil de direction", B, ["fauteuil de direction"]),
 ("fauteuil d'esthétique", P, ["fauteuil esthétique"]), ("fauteuil de tatouage", P, ["fauteuil tatouage"]), ("comptoir d'accueil", P, ["comptoir d'accueil", "banque d'accueil"]),
 ("table de réunion", P, ["table de réunion"]), ("malle de voyage", V, ["malle de voyage"]), ("veste en daim", V, ["veste daim"]),
 ("meuble hi-fi", M, ["meuble hifi"]), ("aménagement de van", C, ["aménagement van", "meuble van"]), ("rampe de chargement", A, ["rampe de chargement"]),
 ("jardinière en bois", J, ["jardinière bois"]), ("salon de balcon", J, ["salon de balcon"]), ("banc coffre", J, ["banc coffre"]),
 ("chariot de plancha", J, ["table plancha", "chariot plancha"]), ("desserte de barbecue", J, ["desserte barbecue"]), ("évier extérieur", J, ["évier extérieur"]),
 ("banc de rangement", M, ["banc de rangement"]), ("vestiaire d'entrée", M, ["vestiaire entrée"]), ("colonne de rangement", M, ["colonne de rangement"]),
 ("meuble de cuisine", M, ["meuble de cuisine"]), ("table console extensible", M, ["table console extensible"]), ("fauteuil papasan", M, ["fauteuil papasan"]),
 ("fauteuil design", M, ["fauteuil design"]), ("fauteuil vintage", M, ["fauteuil vintage"]), ("canapé 2 places", M, ["canapé 2 places"]),
 ("canapé arrondi", M, ["canapé arrondi"]), ("canapé panoramique", M, ["canapé panoramique"]), ("lit 90x190", M, ["lit 90x190", "lit 1 place"]),
 ("lit en métal", M, ["lit en fer forgé", "lit métal"]), ("lit en velours", M, ["lit velours"]), ("cache-radiateur", M, ["cache radiateur"]),
 ("bureau en L", B, ["bureau en l"]), ("tente tunnel", C, ["tente tunnel"]), ("tente 8 places", C, ["tente 8 places"]), ("tente glamping", C, ["tente glamping", "tente safari"]),
 ("abri de camping", C, ["abri de camping"]), ("store de camping-car", C, ["store camping car"]), ("couvre-benne", C, ["couvre benne"]),
 ("comptoir de bar", P, ["comptoir bar"]), ("table de couture", L, ["table de couture"]), ("harpe", L, ["harpe"]), ("violon", L, ["violon"]),
 ("guitare acoustique", L, ["guitare acoustique"]), ("batterie acoustique", L, ["batterie acoustique"]), ("handpan", L, ["handpan"]), ("globe bar", M, ["globe bar"]),
 ("lit de repos", M, ["lit de repos"]), ("table gigogne", M, ["table gigogne"]), ("table de jardin ronde", J, ["table de jardin ronde"]),
 ("salon de terrasse", J, ["salon de terrasse"]), ("porte de grange coulissante", M, ["porte coulissante", "porte grange"]),
 ("tapis d'extérieur", J, ["tapis d'extérieur"]), ("chariot de plage", C, ["chariot de plage"]), ("chariot de jardin", J, ["chariot de jardin"]),
 ("cabanon", J, ["cabanon"]),
]
from valider import variantes
deja = set()
for f in ("/home/user/ECOM/tools/validation/idees.json",):
    for i in json.load(open(f, encoding="utf-8"))["idees"]:
        for k in i["mots_cles"]:
            deja.add(k.lower())
idees, mots = [], []
for produit, niche, mc in I:
    mc = [k for k in mc if k.lower() not in deja]
    if not mc:
        continue
    idees.append({"produit": produit, "niche": niche, "mots_cles": mc})
    for k in variantes(idees[-1]):
        if k.lower() not in (m.lower() for m in mots):
            mots.append(k)
print(len(idees), "idées,", len(mots), "mots-clés")
json.dump({"_lisez_moi": "Idées high ticket du 23/11/2026, hors liste noire, hors produits déjà testés.", "idees": idees},
          open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
