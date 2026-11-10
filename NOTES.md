# Notes de l'enseignant

## Préférences et contexte
- Langue : français. Ton direct, chiffres concrets.
- L'apprenant a demandé : accompagnement payant (spécialisé Google Ads) ou apprendre seul ? Il attend une réponse argumentée, pas un sermon. Lui demander le prix et le contenu exact de l'offre, puis l'analyser avec la grille de `reference/rentabilite-pub.html`.
- Leçons publiées en artifact (site du cours : `index.html` + `lessons/` + `reference/` + `assets/`) car la session tourne dans un conteneur distant.

## Point du 10/11/2026
- L'apprenant a pris l'accompagnement payant. Il en est à la recherche produit : environ 40 idées de niches dans un Google Sheet, à valider avec un second Sheet de critères fourni par la formation.
- Outil de la formation : OneClickBrand (oneclickbrand.ai). Pas d'API publique ; d'après son propre site, ses données de niche (volume, CPC, concurrence) viennent de Semrush.
- Il veut déléguer la vérification et le remplissage du Sheet. Blocages : pas d'outil d'édition Google Sheets dans la session, et les deux fichiers sont introuvables dans le Drive connecté (on y voit seulement « modele-sheet-fiches-produits » et « Sourcing Concurrents V2 »).
- Pistes proposées : export du Planificateur de mots clés (gratuit), ou API DataForSEO (recharge minimum de 50 $) pour automatiser.
- Idée pour la leçon 2 : partir de SES niches et lui apprendre à lire volume, CPC et prix moyen, pour qu'il puisse contrôler le tri (le mien comme celui de l'outil). Il garde la décision finale.
- Test du 10/11/2026 (3 produits) fait sur le compte OneClickBrand de l'apprenant, à sa demande explicite. Leurs CGU interdisent le partage d'identifiants et l'extraction de données : signalé, l'apprenant a choisi de continuer.
  - OneClickBrand donne : volume (moyenne 12 mois), CPC moyen, variantes, top 5 Google, export mensuel sur 10 ans. Il ne donne PAS la concurrence Ads ni le CPC « fourchette haute » demandés par la grille.
  - Incohérence relevée : « chaise ergonomique » 14 800 sur la carte, 22 200 dans le tableau des variantes. Il affiche aussi des volumes identiques pour des variantes proches (ne pas les additionner).
  - Quota de l'essai épuisé (0/5 analyses approfondies). Essai terminé vers le 14/11/2026.
  - Fournisseurs : VidaXL lisible (prix public, délai, stock) ; AliExpress lisible en recherche avec filtre « expédié de France », mais les délais des fiches ne se lisent pas.
  - Résultat : brasero = printemps (bleu), chaise ergonomique = à creuser (CPC limite selon le mot-clé), cave à vin = éliminée (pas de fournisseur de cave électrique trouvé).
- Retours de l'apprenant sur le test (10/11/2026) :
  - « Concurrent » = boutique en dropshipping, en général sous Shopify (il vérifie avec l'extension TrendTrack). Les marques et grandes enseignes ne comptent pas.
  - Un fournisseur peut proposer un produit équivalent (même type, mêmes usages), pas forcément le même modèle.
  - Sources fournisseurs de sa formation : Europages, BigBuy, Google (« produit supplier / wholesale »), Alibaba avec commande minimum à 1.
- Faisabilité testée : détection Shopify fiable (code de la page) ; Google bloque (captcha), Bing brouille ses résultats après 1 ou 2 requêtes, BigBuy (Cloudflare) et Alibaba (curseur anti-robot) bloquent ; Europages = fiches entreprises sans prix. Les concurrents en dropshipping sont à trouver par l'apprenant (TrendTrack) ou par une API de résultats Google.
- Validation chiffrée du 10/11/2026 (DataForSEO, compte de l'apprenant, 0,09 $ dépensé sur 1 $) : 41 produits écrits dans la grille (lignes 8 à 48). Répartition des 38 nouveaux : 11 jaunes, 19 bleus (saison plus tard), 7 rouges (volume), 1 sans données (porte-bébé).
  - Google met la concurrence Ads à « élevée » (100/100) sur 93 mots-clés sur 93 : le seuil de la formation (faible ou moyenne) ne trie plus rien avec ces chiffres. Affichée, pas utilisée pour éliminer. Question posée à l'apprenant pour sa formation.
  - Le CPC fourchette haute Google est plus élevé que le CPC moyen de OneClickBrand (chaise : 1,76 € contre 1,17 €).
  - La grille impose des listes déroulantes (J : FAIBLE, MOYENNE, ÉLEVÉE ; K : EVERGREEN, PRINTEMPS, ÉTÉ, AUTOMNE, HIVER, Q4). L'apprenant a lui-même remis K8:K10 à ces valeurs.
  - Partage du travail validé : moi = tous les chiffres ; lui = concurrents (TrendTrack) et fournisseurs. Objectif : environ 20 produits qui passent les chiffres ; il cherchera d'autres idées si besoin.
- Question ouverte : aligner le plan du cours sur le programme de sa formation ?

## Hypothèses de l'apprenant à travailler
- « Google Ads permet de cibler un public plus aisé » : faux tel quel en France (pas de ciblage par revenu du foyer). Le vrai levier est l'intention de recherche. Abordé en leçon 1 ; vérifier au début de la leçon 2 s'il l'a retenu avant d'écrire un learning record.
- « Si j'interromps les gens, ça ne marchera pas en high ticket » : hypothèse raisonnable mais non testée. Ne pas la contredire maintenant ; la garder comme hypothèse.
- « Google Ads fait moins perdre d'argent aux débutants » : vrai seulement si le produit est déjà recherché et si l'économie unitaire tient. Le petit budget (≈ 1 000 € de pub) ne donne pas assez de conversions pour le ROAS cible (15 en 30 jours).

## Vocabulaire canonique (à promouvoir dans GLOSSARY.md quand maîtrisé)
- **Marge par commande** (pas « bénéfice », pas « profit unitaire ») : prix de vente − coût produit livré − frais variables (paiement, cotisations, provision retours).
- **CPA max** : égal à la marge par commande.
- **ROAS de rentabilité** (pas « break-even ROAS », pas « ROAS minimum ») : prix de vente ÷ marge par commande.
- **Coût produit livré** : produit + livraison + taxes et droits jusqu'au client.
- **Intention de recherche** : ce que la requête tapée révèle du projet d'achat.

## Plan provisoire (8 semaines, ≈ 10 h/sem.)
1. Les 4 calculs avant la pub (fait le 23/10/2026)
2. Vérifier que le produit est déjà recherché (Planificateur de mots clés, Google Trends, CPC réels)
3. Produit et fournisseur high ticket (délais, entrepôt UE, retours, douane > 150 €)
4. Cadre légal FR de la boutique (mentions, CGV, rétractation, garanties)
5. Boutique Shopify qui inspire confiance (fiches produit, Higgsfield)
6. Merchant Center sans suspension, flux produits
7. Campagne test Shopping/Search et suivi des conversions
8. Lire les résultats et décider

## Révision espacée
- Début de leçon 2 : 3 questions de rappel sur la leçon 1 (ROAS de rentabilité, ventes attendues, ciblage par revenu absent en France).
