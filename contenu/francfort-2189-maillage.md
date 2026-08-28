# Maillage interne, page Transfert VTC Aéroport de Francfort

Page cible : https://vtc-strasbourg-dmd.fr/transfert-vtc-aeroport-francfort-strasbourg/ (ID 2189, Elementor)
Statut : publié en ligne le 28/08/2026.
URL vérifiées en HTTP 200 le 28/08/2026, 24 liens internes contrôlés sur la page publiée.

Le contenu a été poussé via l'API REST, dans le meta `_elementor_data`, par
`scripts/wp-maj-francfort.py`. La FAQ a été ajoutée ensuite par
`scripts/wp-faq-inline-francfort.py`. Sauvegarde d'origine :
`backup/2189_AVANT_MODIFICATION.json`, restaurable avec
`python3 scripts/wp-maj-francfort.py --restore backup/2189_AVANT_MODIFICATION.json`.

## Principe retenu

La page comportait déjà un bloc de liens en pied de contenu vers Baden-Baden,
Entzheim, Stuttgart, Bâle-Mulhouse, Zurich, Europa-Park, Colmar, Ribeauvillé,
Obernai, Kaysersberg, Riquewihr et Eguisheim.

Le maillage contextuel ajouté ici ne double donc pas ce bloc. Il ouvre en
priorité des chemins vers des pages qui ne recevaient aucun lien depuis
Francfort, et ne renforce dans le corps de texte que quatre destinations à fort
volume déjà présentes dans le bloc (Obernai, Colmar, Baden-Baden, Zurich).

17 URL internes distinctes, sur environ 950 mots. Ancres descriptives, aucune
ancre générique, aucun lien en exact match répété.

## Liens ajoutés

| # | Ancre | Destination | Section | Statut |
|---|---|---|---|---|
| 1 | l'Eurométropole | /vtc-business-espace-europeen-schiltigheim-illkirch/ | Chapeau | Nouveau chemin |
| 2 | la gare centrale de Strasbourg | /vtc-strasbourg-gare/ | Confort chauffeur privé | Nouveau chemin |
| 3 | le Conseil de l'Europe | /vtc-parlement-europeen-strasbourg-transport-vip/ | Confort chauffeur privé | Nouveau chemin |
| 4 | plusieurs correspondances en train | /transfert-vtc-gare-de-kehl-strasbourg-allemagne/ | Confort chauffeur privé | Nouveau chemin |
| 5 | déplacement professionnel | /chauffeur-prive-vtc-pour-les-evenements-dentreprise-strasbourg/ | Confort chauffeur privé | Nouveau chemin |
| 6 | Demandez votre devis gratuit en ligne | /contactez-nous/ | Tarifs | Conversion |
| 7 | Obernai | /transfert-vtc-chauffeur-prive-obernai-strasbourg/ | Pourquoi nous choisir | Renfort contextuel |
| 8 | Colmar | /transfert-vtc-chauffeur-prive-colmar-strasbourg/ | Pourquoi nous choisir | Renfort contextuel |
| 9 | Baden-Baden | /chauffeur-prive-vtc-aeroport-baden-baden/ | Pourquoi nous choisir | Renfort contextuel |
| 10 | Zurich | /transfert-vtc-aeroport-zurich-strasbourg/ | Pourquoi nous choisir | Renfort contextuel |
| 11 | Paris | /vtc-strasbourg-longue-distance-paris-lyon-bruxelles/ | Pourquoi nous choisir | Nouveau chemin |
| 12 | nos autres transferts aéroports | /nos-prestations/ | Pourquoi nous choisir | Vers la page hub |
| 13 | van spacieux | /service-van-8-places-a-strasbourg-vtc/ | Formules adaptées | Nouveau chemin |
| 14 | Europa Park | /chauffeur-prive-vtc-europa-park-strasbourg/ | Flotte | Renfort contextuel |
| 15 | mise à disposition spécifique | /chauffeur-prive-sur-mesure-strasbourg-vtc/ | Flotte | Nouveau chemin |
| 16 | les incontournables du Bas-Rhin | /visiter-strasbourg-en-vtc-les-lieux-et-activites-incontournables/ | Tourisme | Nouveau chemin |
| 17 | circuits touristiques en Alsace | /circuits-touristiques/ | Tourisme | Nouveau chemin |
| 18 | page de réservation en ligne | Popup Elementor 1789 | FAQ | Conversion |
| 19 | par mail ou par téléphone | /contactez-nous/ | FAQ | Conversion |

Deux liens sortants du bloc de bas de page ont par ailleurs été corrigés : il
pointait vers la page courante, et listait Entzheim deux fois.

Le popup de réservation est celui déjà utilisé par le bouton en haut de page.
Href à reprendre tel quel :

```
#elementor-action%3Aaction%3Dpopup%3Aopen%26settings%3DeyJpZCI6MTc4OSwidG9nZ2xlIjpmYWxzZX0%3D
```

## Écarts par rapport au texte fourni

Le texte a été repris mot pour mot. Deux points seulement :

- Ajout de l'article défini sur trois ancres (« la gare centrale de Strasbourg »,
  « le Conseil de l'Europe », « les incontournables du Bas-Rhin ») pour que le
  lien porte sur un groupe nominal complet plutôt qu'un fragment.
- Aucun chiffre, tarif, durée ni distance n'a été modifié.

## Contraintes techniques rencontrées

Les widgets ont été réutilisés un à un, sans en créer ni en supprimer, pour que
le CSS déjà généré par Elementor reste valide. Structure vérifiée après
publication : 40 éléments, 2 sections, aucun identifiant perdu.

La FAQ faisait exception, aucun emplacement n'étant libre. Son widget porte donc
un identifiant neuf, absent de `uploads/elementor/css/post-2189.css`, et une
écriture par l'API REST ne régénère pas ce fichier. Toute sa mise en forme est
pour cette raison portée en ligne, comme le fait déjà le bloc de liens de bas de
page. Si la page est un jour rouverte puis enregistrée dans Elementor, le CSS
sera régénéré et ces styles en ligne resteront sans effet de bord.

Le site tourne sous LiteSpeed Cache, avec un cache page de sept jours. Toute
modification passée par l'API reste invisible aux visiteurs tant que le cache
n'est pas purgé.

## Liens retour à créer ensuite

Vérification faite le 28/08/2026 : quatre pages candidates pointent déjà vers
Francfort, mais uniquement via le menu de navigation et le bloc de pied de page,
présents sur tout le site. Ces liens ne portent aucun contexte sémantique.

Un seul lien contextuel entrant a été trouvé, depuis
/vtc-strasbourg-longue-distance-paris-lyon-bruxelles/.

À créer dans le corps de texte, en réciprocité du maillage posé ici :

- /nos-prestations/ vers Francfort, dans la rubrique transferts aéroports.
- /transfert-vtc-gare-de-kehl-strasbourg-allemagne/ vers Francfort : la page
  traite du train ICE vers l'Allemagne, le transfert direct est l'alternative.
- /vtc-parlement-europeen-strasbourg-transport-vip/ vers Francfort : l'arrivée
  de délégations par Francfort est un cas d'usage direct.
