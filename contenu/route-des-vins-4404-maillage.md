# Maillage interne, page Chauffeur Privé Route des Vins d'Alsace

Page cible : https://vtc-strasbourg-dmd.fr/chauffeur-prive-vtc-route-des-vins-alsace/ (ID 4404, Elementor)
Statut : publié en ligne le 03/09/2026.
28 liens internes contrôlés en HTTP 200 sur la page publiée.

Publié par `scripts/wp-maj-route-des-vins.py`. Sauvegarde d'origine dans
`backup/`, restaurable avec l'option `--restore`.

## Correction apportée au contenu fourni

Les six appels à l'action du texte pointaient vers `/contact/`. Cette URL n'est
pas une page de contact : elle renvoie une 301 vers `/?elementor_library=contact`,
un modèle Elementor. Les six boutons pointent donc vers `/contactez-nous/`, la
page de contact réelle.

## Liens posés sur les ancres du texte

| Ancre | Destination |
|---|---|
| circuit Route des Vins d'Alsace en VTC avec dégustation | /vtc-degustation-vins-alsace-strasbourg/ |
| service de VTC à Strasbourg | /nos-prestations/ |
| la gare de Strasbourg | /vtc-strasbourg-gare/ |
| transfert VTC entre Strasbourg et Riquewihr | /transfert-vtc-chauffeur-prive-riquewihr-strasbourg/ |
| transfert vers Ribeauvillé | /transfert-vtc-chauffeur-prive-ribeauville-strasbourg/ |
| château du Haut-Koenigsbourg | /vtc-chateau-haut-koenigsbourg-strasbourg/ |
| transfert VTC Colmar Strasbourg | /transfert-vtc-chauffeur-prive-colmar-strasbourg/ |
| van VTC 7 places pour la Route des Vins | /van-vtc-7-places-route-des-vins-alsace/ |
| van 8 places avec chauffeur à Strasbourg | /service-van-8-places-a-strasbourg-vtc/ |
| transfert avec chauffeur privé entièrement sur-mesure | /chauffeur-prive-sur-mesure-strasbourg-vtc/ |
| aéroport de Strasbourg-Entzheim | /chauffeur-prive-vtc-aeroport-entzheim-strasbourg/ |
| aéroport de Bâle-Mulhouse-Fribourg | /chauffeur-prive-vtc-aeroport-bale-mulhouse-fribourg/ |
| aéroport de Francfort | /transfert-vtc-aeroport-francfort-strasbourg/ |
| aéroport de Zurich | /transfert-vtc-aeroport-zurich-strasbourg/ |
| aéroport de Baden-Baden | /chauffeur-prive-vtc-aeroport-baden-baden/ |
| services de transport à Strasbourg | /services-transport-taxi-strasbourg/ |
| politique de confidentialité | /politique-de-confidentialite/ |
| avantages du VTC par rapport au taxi | /3-avantages-du-vtc-par-rapport-au-taxi/ |
| formulaire de contact, devis gratuit, 6 boutons | /contactez-nous/ |

## Liens ajoutés sur des entités déjà nommées dans le texte

Ces mentions n'étaient pas présentées comme des ancres, mais elles désignent des
pages existantes et le lien y est naturel.

| Ancre | Destination |
|---|---|
| Obernai | /transfert-vtc-chauffeur-prive-obernai-strasbourg/ |
| Kaysersberg | /transfert-vtc-chauffeur-prive-kaysersberg-strasbourg/ |
| Eguisheim | /transfert-vtc-chauffeur-prive-eguisheim-strasbourg/ |
| séminaire d'entreprise | /transport-evenements-entreprise-strasbourg-vtc/ |
| mariage | /location-voiture-chauffeur-mariage-strasbourg/ |
| marchés de Noël | /marche-de-noel-strasbourg-vtc/ |

Ribeauvillé, Riquewihr et Colmar ne sont pas liés une seconde fois dans la liste
des villages : ils le sont déjà en contexte plus haut dans la page.

## Blocs conservés

Deux blocs de maillage déjà en place ont été conservés à l'identique :

- « Nos services sur-mesure sur la Route des Vins d'Alsace » (widget a309dc6),
  qui pointe vers les pages dégustation, Haut-Koenigsbourg, circuit villages et
  van 7 places. La conclusion de la nouvelle page prend la suite dans le même
  encadré.
- L'accordéon de bas de page (widget e82e29b), qui liste destinations, dessertes
  aéroports, dessertes gares et visites touristiques.

## JSON-LD FAQPage

Ajouté dans le widget HTML qui porte déjà l'iframe de réservation, à la suite de
celle-ci. Les sept questions balisées correspondent mot pour mot à des questions
visibles en H3 dans la section « Questions fréquentes », condition posée par
Google pour l'éligibilité au rich result. Vérifié après publication.

## Points relevés, hors périmètre

L'iframe de réservation de cette page porte `width="LARGEUR"`, un libellé
d'exemple resté en place. La valeur étant invalide, le navigateur l'ignore et
l'iframe s'affiche à sa largeur par défaut. `width="100%"` corrigerait le
cadrage du formulaire. Non modifié, ce bloc touche à la conversion.

## Caches à purger après toute écriture par l'API

Deux couches, et la seconde a été découverte sur cette page :

1. LiteSpeed Cache, cache page de sept jours.
2. Le cache d'éléments d'Elementor, qui stocke le HTML rendu de chaque widget.
   Tant qu'il n'est pas vidé, la page sert l'ancien contenu y compris à un
   administrateur connecté, alors que la base est à jour. Il se vide depuis
   Elementor puis Outils, bouton « Effacer les fichiers et les données ».
