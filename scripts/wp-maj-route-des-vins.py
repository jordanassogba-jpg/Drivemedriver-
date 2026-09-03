#!/usr/bin/env python3
"""Publie le nouveau contenu de la page Chauffeur Prive Route des Vins d'Alsace.

Page 4404 : https://vtc-strasbourg-dmd.fr/chauffeur-prive-vtc-route-des-vins-alsace/

Comme pour la page Francfort, seuls les widgets existants sont remplis : aucun
widget n'est cree ni supprime, aucun reglage de style n'est touche, donc le CSS
deja genere par Elementor reste valide.

Deux blocs de maillage deja en place sont conserves tels quels :
  - le bloc "Nos services sur-mesure" du widget a309dc6, dont la conclusion
    prend la suite dans le meme encadre ;
  - l'accordeon e82e29b, qui liste destinations, aeroports, gares et visites.

Les liens ne portent pas de style en ligne : sur cette page au fond clair, la
couleur de lien du theme (#0170B9) s'applique, comme pour les liens deja
presents dans le bloc "Nos services sur-mesure".

Usage :
    python3 scripts/wp-maj-route-des-vins.py --dry-run
    python3 scripts/wp-maj-route-des-vins.py
    python3 scripts/wp-maj-route-des-vins.py --restore fichier.json
"""

import argparse
import base64
import datetime
import json
import pathlib
import sys
import urllib.request

PAGE_ID = 4404
RACINE = pathlib.Path(__file__).resolve().parent.parent
DOSSIER_BACKUP = RACINE / "backup"

BASE = "https://vtc-strasbourg-dmd.fr"
CONTACT = f"{BASE}/contactez-nous/"

# Le contenu fourni pointait ses six appels a l'action vers /contact/, qui
# renvoie une 301 vers un modele Elementor et non vers une page de contact.
# La page reelle est /contactez-nous/.

DORE = "#C1A566"  # couleur d'accent de la page, reprise de l'accordeon


def lien(url, ancre):
    return f'<a href="{url}">{ancre}</a>'


def cta(texte):
    style = (
        f"display: inline-block; background-color: {DORE}; color: #000000; "
        "padding: 14px 28px; border-radius: 6px; font-weight: 600; "
        "text-decoration: none; margin: 10px 0;"
    )
    return f'<p style="text-align: center;"><a href="{CONTACT}" style="{style}">{texte}</a></p>'


U = {
    "degustation": f"{BASE}/vtc-degustation-vins-alsace-strasbourg/",
    "prestations": f"{BASE}/nos-prestations/",
    "gare": f"{BASE}/vtc-strasbourg-gare/",
    "riquewihr": f"{BASE}/transfert-vtc-chauffeur-prive-riquewihr-strasbourg/",
    "ribeauville": f"{BASE}/transfert-vtc-chauffeur-prive-ribeauville-strasbourg/",
    "obernai": f"{BASE}/transfert-vtc-chauffeur-prive-obernai-strasbourg/",
    "kaysersberg": f"{BASE}/transfert-vtc-chauffeur-prive-kaysersberg-strasbourg/",
    "eguisheim": f"{BASE}/transfert-vtc-chauffeur-prive-eguisheim-strasbourg/",
    "colmar": f"{BASE}/transfert-vtc-chauffeur-prive-colmar-strasbourg/",
    "chateau": f"{BASE}/vtc-chateau-haut-koenigsbourg-strasbourg/",
    "van7": f"{BASE}/van-vtc-7-places-route-des-vins-alsace/",
    "van8": f"{BASE}/service-van-8-places-a-strasbourg-vtc/",
    "surmesure": f"{BASE}/chauffeur-prive-sur-mesure-strasbourg-vtc/",
    "mariage": f"{BASE}/location-voiture-chauffeur-mariage-strasbourg/",
    "entreprise": f"{BASE}/transport-evenements-entreprise-strasbourg-vtc/",
    "noel": f"{BASE}/marche-de-noel-strasbourg-vtc/",
    "entzheim": f"{BASE}/chauffeur-prive-vtc-aeroport-entzheim-strasbourg/",
    "bale": f"{BASE}/chauffeur-prive-vtc-aeroport-bale-mulhouse-fribourg/",
    "francfort": f"{BASE}/transfert-vtc-aeroport-francfort-strasbourg/",
    "zurich": f"{BASE}/transfert-vtc-aeroport-zurich-strasbourg/",
    "badenbaden": f"{BASE}/chauffeur-prive-vtc-aeroport-baden-baden/",
    "services": f"{BASE}/services-transport-taxi-strasbourg/",
    "confidentialite": f"{BASE}/politique-de-confidentialite/",
    "avantages": f"{BASE}/3-avantages-du-vtc-par-rapport-au-taxi/",
    "contact": CONTACT,
}

TITRE_H1 = "Chauffeur privé Route des Vins d'Alsace et circuit touristique sur-mesure"

# --- Widget 4b8dca0 : introduction, centree -----------------------------------

INTRO = (
    "<p>L'Alsace est mondialement réputée pour ses paysages de carte postale, son vignoble à perte de "
    "vue et ses villages pittoresques aux maisons à colombages. Mais pour profiter pleinement de la "
    "Route des Vins d'Alsace au départ de Strasbourg, la logistique devient vite complexe. Louer un "
    "véhicule, chercher une place de stationnement dans des villages bondés, et surtout désigner un "
    "capitaine de soirée pour les dégustations en cave : tout cela gâche le plaisir.</p>"
    "<p>Drive Me Driver vous propose une expérience touristique haut de gamme. Un chauffeur privé à "
    "votre disposition, en berline ou en van Mercedes Classe V 7 places, pour une demi-journée ou une "
    "journée complète d'excursion sur-mesure. Prise en charge à l'adresse de votre choix, itinéraire "
    "personnalisé, tarif fixe communiqué avant le départ.</p>"
    "<p>Notre offre complète est détaillée sur notre page dédiée : "
    + lien(U["degustation"], "circuit Route des Vins d'Alsace en VTC avec dégustation")
    + ".</p>"
    + cta("Demander un devis")
)

# --- Widget 1068fab : liberte du chauffeur a disposition ----------------------

RYTHME = (
    "<h2>Visitez l'Alsace à votre rythme avec un chauffeur à disposition</h2>"
    "<p>Dans une excursion en autocar, vous êtes soumis à un chronomètre strict, fondu dans un groupe "
    "de cinquante personnes. Notre "
    + lien(U["prestations"], "service de VTC à Strasbourg")
    + " vous offre l'inverse : le temps et la liberté.</p>"
    "<p>Avec la formule de mise à disposition, votre chauffeur privé vous est exclusivement dédié pour "
    "la durée de votre choix, généralement de 4 h à 10 h. Il vous récupère directement à votre hôtel, "
    "à votre domicile ou à "
    + lien(U["gare"], "la gare de Strasbourg")
    + ", et le circuit commence.</p>"
    "<p>Vous souhaitez flâner une heure de plus dans les ruelles de Colmar et de sa Petite Venise ? "
    "Vous avez repéré une terrasse à Kaysersberg pour déjeuner ? Prenez votre temps, votre chauffeur "
    "vous attend. Oubliez le GPS, les routes sinueuses du vignoble et les parcmètres.</p>"
    "<p>Nous vous déposons au plus près des centres historiques piétons et des domaines viticoles. Une "
    "fois votre visite terminée, un simple message suffit pour que votre véhicule climatisé vienne "
    "vous récupérer.</p>"
    "<p>Cette liberté vaut aussi pour les trajets simples entre deux étapes. Nous assurons par exemple "
    "le " + lien(U["riquewihr"], "transfert VTC entre Strasbourg et Riquewihr") + " ou le "
    + lien(U["ribeauville"], "transfert vers Ribeauvillé")
    + " si vous préférez composer votre journée étape par étape.</p>"
)

# --- Widget eb1c652 : degustation, villages, circuits -------------------------

DEGUSTATION = (
    "<h2>Dégustation de vins sans contrainte et achats facilités</h2>"
    "<p>Parcourir la Route des Vins, de Marlenheim à Thann en passant par Obernai, Ribeauvillé ou "
    "Eguisheim, est indissociable du plaisir de pousser la porte d'un caveau indépendant. Déguster un "
    "Riesling grand cru, découvrir la puissance d'un Gewurztraminer ou la finesse d'un Pinot Noir fait "
    "partie intégrante de la culture alsacienne.</p>"
    "<p>La législation sur l'alcool au volant est stricte, et c'est une excellente chose pour la "
    "sécurité de tous. En réservant votre circuit avec un chauffeur privé, chaque personne du groupe "
    "peut participer à la dégustation avec modération. Personne n'est frustré, personne ne conduit.</p>"
    "<p>Votre chauffeur Drive Me Driver s'occupe de la route et garantit le retour à Strasbourg en "
    "toute tranquillité.</p>"
    "<p>Autre avantage concret : si vous avez un coup de cœur lors de la visite d'une cave, achetez "
    "sans compter. Bouteilles ou cartons entiers, vous n'aurez rien à porter sous le soleil. Votre "
    "chauffeur les range dans le coffre de la berline ou du van, à l'abri de la chaleur, avec vos "
    "bagages, jusqu'au retour à votre hôtel.</p>"
    + cta("Réserver votre chauffeur")
    + "<h2>Les plus beaux villages viticoles de notre circuit</h2>"
    "<p>La Route des Vins traverse le Bas-Rhin puis le Haut-Rhin sur environ 170 kilomètres. Voici les "
    "étapes que nos clients demandent le plus souvent. Vous composez votre itinéraire librement, dans "
    "l'ordre qui vous plaît.</p>"
    "<h3>Dans le Bas-Rhin, au nord du vignoble</h3>"
    "<p>Molsheim ouvre la route au départ de Strasbourg. Ville d'art et d'histoire, elle marque "
    "l'entrée dans le vignoble.</p>"
    "<p>" + lien(U["obernai"], "Obernai") + " est l'un des joyaux de la région. Sa place du marché, "
    "son beffroi et ses ruelles alsaciennes en font une étape courte et très photogénique.</p>"
    "<p>Barr est la capitale du Sylvaner et un excellent point d'ancrage pour rayonner dans les "
    "côteaux alentour.</p>"
    "<p>Le Mont Sainte-Odile offre une vue panoramique exceptionnelle sur la plaine d'Alsace. La "
    "montée en van reste confortable, là où le trajet en voiture de location décourage souvent les "
    "visiteurs.</p>"
    "<p>Sélestat et son voisin le "
    + lien(U["chateau"], "château du Haut-Koenigsbourg")
    + " forment le duo incontournable des amateurs de patrimoine médiéval. Nous vous déposons au plus "
    "près de l'entrée du château, sans navette ni parking saturé.</p>"
    "<h3>Dans le Haut-Rhin, au cœur des grands crus</h3>"
    "<p>Ribeauvillé et ses trois châteaux dominent le vignoble. Une adresse idéale pour une "
    "dégustation en domaine familial.</p>"
    "<p>Riquewihr est classée parmi les plus beaux villages de France. Ses façades colorées et ses "
    "caves historiques en font l'étape la plus demandée de nos circuits.</p>"
    "<p>" + lien(U["kaysersberg"], "Kaysersberg") + " séduit par son pont fortifié et son ambiance de "
    "village de conte. Superbe en été comme pendant les marchés de Noël.</p>"
    "<p>" + lien(U["eguisheim"], "Eguisheim") + ", village concentrique unique en Alsace, est le "
    "berceau du vignoble alsacien.</p>"
    "<p>Colmar clôt souvent la journée. La Petite Venise, le quartier des tanneurs et les terrasses "
    "justifient à eux seuls une heure ou deux de visite libre. Nous assurons également le "
    + lien(U["colmar"], "transfert VTC Colmar Strasbourg")
    + " à prix fixe en dehors des circuits touristiques.</p>"
    "<h2>Exemple de circuit au départ de Strasbourg</h2>"
    "<p>Pour vous aider à visualiser votre journée, voici deux itinéraires que nous construisons "
    "régulièrement au départ de Strasbourg. Ils servent de base de discussion, rien n'est imposé.</p>"
    "<h3>Circuit découverte, la journée complète des villages emblématiques</h3>"
    "<p><strong>Strasbourg &rarr; Obernai &rarr; Haut-Koenigsbourg &rarr; Ribeauvillé &rarr; Riquewihr "
    "&rarr; Kaysersberg &rarr; Colmar &rarr; Strasbourg</strong></p>"
    "<p>Ce parcours est le grand classique de la Route des Vins. Vous quittez Strasbourg le matin pour "
    "Obernai et sa place du marché, puis vous prenez de la hauteur au château du Haut-Koenigsbourg. "
    "L'après-midi enchaîne trois villages viticoles parmi les plus beaux d'Alsace, avant une fin de "
    "journée à Colmar et sa Petite Venise. Comptez une journée complète de 10 h pour en profiter sans "
    "courir.</p>"
    "<h3>Circuit dégustation, deux domaines et une pause déjeuner</h3>"
    "<p><strong>Strasbourg &rarr; Obernai &rarr; domaine viticole &rarr; Ribeauvillé &rarr; déjeuner "
    "&rarr; Riquewihr &rarr; seconde dégustation &rarr; Strasbourg</strong></p>"
    "<p>Cette version privilégie le vin et le rythme. Une première dégustation en matinée dans un "
    "domaine familial, un déjeuner dans un village de votre choix, puis un second caveau dans "
    "l'après-midi à Riquewihr. Vos achats voyagent dans le coffre, à l'abri de la chaleur, et personne "
    "ne prend le volant.</p>"
    "<p>Vous pouvez inverser les étapes, en retirer une pour prendre votre temps, ou en ajouter le "
    "jour même. Votre chauffeur adapte l'itinéraire en cours de journée.</p>"
    + cta("Créer mon circuit sur mesure")
)

# --- Widget a70a82e : groupes, tarifs, reservation, acces, FAQ ----------------

TARIFS = [
    ("Demi-journée découverte", "5 h", "Berline", "400 €"),
    ("Demi-journée découverte", "5 h", "Van 7 places", "450 €"),
    ("Journée complète", "10 h", "Berline", "750 €"),
    ("Journée complète", "10 h", "Van 7 places", "850 €"),
    ("Heure supplémentaire", "1 h", "Berline", "75 €"),
    ("Heure supplémentaire", "1 h", "Van 7 places", "95 €"),
]

CEL = "padding: 10px 14px; border: 1px solid #d9d9d9; text-align: left;"
ENT = CEL + f" background-color: {DORE}; color: #000000; font-weight: 600;"

TABLEAU = (
    '<div style="overflow-x: auto;">'
    '<table style="width: 100%; border-collapse: collapse; margin: 16px 0;">'
    "<thead><tr>"
    + "".join(f'<th style="{ENT}">{c}</th>' for c in ("Formule", "Durée", "Véhicule", "Tarif"))
    + "</tr></thead><tbody>"
    + "".join(
        "<tr>" + "".join(f'<td style="{CEL}">{c}</td>' for c in ligne) + "</tr>" for ligne in TARIFS
    )
    + "</tbody></table></div>"
)

FAQ = [
    (
        "Comment réserver un chauffeur privé ?",
        "Par le formulaire de contact du site ou par téléphone. Indiquez la date, l'heure de prise en "
        "charge, l'adresse de départ, le nombre de personnes et le nombre de bagages. Vous recevez un "
        "devis avec un tarif fixe. La réservation devient définitive dès votre validation, et vos "
        "coordonnées restent confidentielles, comme indiqué dans notre "
        + lien(U["confidentialite"], "politique de confidentialité") + ".",
    ),
    (
        "Quels sont les tarifs pour un circuit ?",
        "Le tarif est fixe et forfaitaire, calculé selon la durée de mise à disposition, le véhicule "
        "retenu, berline ou van, et le point de départ. Rien n'est facturé au compteur. Le prix inclut "
        "le carburant, les péages et le stationnement. "
        + lien(U["contact"], "Demandez votre devis gratuit")
        + " pour connaître le prix exact de votre circuit.",
    ),
    (
        "Quelles destinations inclut la route des vins ?",
        "Le vignoble s'étire de Marlenheim à Thann. Nos circuits desservent notamment Molsheim, "
        "Obernai, Barr, Sélestat, le château du Haut-Koenigsbourg, Ribeauvillé, Riquewihr, "
        "Kaysersberg, Eguisheim et Colmar. Vous choisissez vos étapes, et vous pouvez en changer en "
        "cours de journée.",
    ),
    (
        "Quels services sont offerts par les chauffeurs ?",
        "Prise en charge à l'adresse de votre choix, véhicule haut de gamme climatisé, aide au "
        "chargement des bagages et des achats de vin, sièges auto pour les enfants, wifi à bord, eau à "
        "disposition, attente sur place pendant vos visites et conseils sur les domaines viticoles. "
        "Nos chauffeurs connaissent la région et parlent plusieurs langues.",
    ),
    (
        "Comment se déroule une excursion sur la route des vins ?",
        "Votre chauffeur vous récupère à l'heure convenue. Vous rejoignez la première étape, "
        "généralement un village viticole, puis un domaine pour une dégustation. La pause déjeuner se "
        "fait dans le village de votre choix. L'après-midi enchaîne deux ou trois étapes, souvent un "
        "château et une cave. Le retour se fait à votre point de départ. Rien n'est figé : le circuit "
        "s'adapte à votre rythme en cours de journée.",
    ),
    (
        "Quels sont les avantages d'un chauffeur privé ?",
        "La liberté d'abord, puisque l'itinéraire vous appartient. La tranquillité ensuite, car vous "
        "dégustez sans vous soucier de la conduite. Le confort d'un véhicule de classe supérieure, le "
        "temps gagné sur le stationnement, et un service personnalisé pour une expérience unique. Nous "
        "détaillons ce comparatif dans notre article sur les "
        + lien(U["avantages"], "avantages du VTC par rapport au taxi") + ".",
    ),
    (
        "Comment se rendre à la route des vins ?",
        "Le départ le plus courant se fait depuis Strasbourg, à trente minutes des premiers villages. "
        "Depuis Colmar, vous êtes au cœur du vignoble. Les transports en commun ne permettent pas "
        "toujours de relier facilement plusieurs villages au cours d'une même journée. Le VTC avec "
        "chauffeur privé reste la solution la plus souple pour couvrir le Bas-Rhin et le Haut-Rhin "
        "sans contrainte.",
    ),
]

GROUPES = (
    "<h2>Groupes, EVJF et familles : le confort de notre van 7 places</h2>"
    "<p>Une escapade œnotouristique se partage souvent à plusieurs. Enterrement de vie de jeune fille, "
    "week-end entre amis, "
    + lien(U["entreprise"], "séminaire d'entreprise")
    + ", " + lien(U["mariage"], "mariage")
    + " ou sortie familiale : la question du transport de groupe est centrale. Prendre deux ou trois "
    "véhicules séparés casse l'ambiance et complique tout.</p>"
    "<p>Le van Mercedes Classe V de Drive Me Driver accueille jusqu'à 7 passagers. Sièges cuir, "
    "climatisation multizone, wifi, larges vitres teintées et vue dégagée sur le vignoble et le "
    "château du Haut-Koenigsbourg. Pour les enfants, les sièges auto sont fournis gratuitement.</p>"
    "<p>Le tarif de mise à disposition étant fixe pour le véhicule, le prix divisé par le nombre de "
    "personnes rend cette prestation premium étonnamment accessible en petit groupe.</p>"
    "<p>Tous les détails de cette formule sont sur notre page "
    + lien(U["van7"], "van VTC 7 places pour la Route des Vins")
    + ". Pour les groupes plus nombreux, nous disposons aussi d'un service de "
    + lien(U["van8"], "van 8 places avec chauffeur à Strasbourg") + ".</p>"
    "<h2>Nos tarifs pour un circuit sur la Route des Vins</h2>"
    "<p>Chez Drive Me Driver, nous travaillons au forfait, jamais au compteur. Le prix est fixe, connu "
    "et validé avant le départ. Aucune surprise à l'arrivée, y compris en cas de trafic ou de détour "
    "improvisé.</p>"
    + TABLEAU
    + "<p>Ces tarifs comprennent la prise en charge à l'adresse de votre choix, le carburant, les "
    "péages, le stationnement et la mise à disposition du chauffeur sur toute la durée. Les entrées de "
    "sites, les dégustations payantes et les repas restent à votre charge.</p>"
    "<p>Pour une prestation particulière, "
    + lien(U["contact"], "demandez votre devis gratuit")
    + ". Nous pouvons également construire un "
    + lien(U["surmesure"], "transfert avec chauffeur privé entièrement sur-mesure")
    + " autour de votre programme.</p>"
    + cta("Demander un devis")
    + "<h2>Comment réserver votre chauffeur privé pour la Route des Vins</h2>"
    "<p>La réservation se fait en trois étapes simples.</p>"
    "<ol>"
    "<li><strong>Votre demande.</strong> Remplissez le "
    + lien(U["contact"], "formulaire de contact du site")
    + " en précisant la date de la visite, le nombre de personnes, le type de voyage souhaité et "
    "l'heure de prise en charge. Vous pouvez aussi nous joindre directement par téléphone.</li>"
    "<li><strong>Votre devis.</strong> Nous vous adressons une offre détaillée avec l'itinéraire "
    "proposé, le véhicule retenu et le tarif fixe. Nous ajustons autant de fois que nécessaire.</li>"
    "<li><strong>Votre confirmation.</strong> Une fois le devis validé, votre chauffeur et votre "
    "véhicule sont bloqués pour la date convenue. Vous recevez le nom de votre chauffeur et son numéro "
    "avant le jour J.</li>"
    "</ol>"
    "<p>Nous recommandons de réserver au moins une semaine à l'avance en haute saison, d'avril à "
    "octobre, pendant les vendanges de septembre et durant la période des "
    + lien(U["noel"], "marchés de Noël") + ".</p>"
    + cta("Réserver votre chauffeur")
    + "<h2>Se rendre en Alsace puis rejoindre la Route des Vins</h2>"
    "<p>Vous arrivez de loin ? Nous prenons le relais dès votre point d'entrée dans la région, avec "
    "vos bagages.</p>"
    "<ul>"
    "<li>Depuis l'" + lien(U["entzheim"], "aéroport de Strasbourg-Entzheim") + ", la gare de "
    "Strasbourg ou votre hôtel dans le centre.</li>"
    "<li>Depuis l'" + lien(U["bale"], "aéroport de Bâle-Mulhouse-Fribourg") + ", au sud du "
    "vignoble.</li>"
    "<li>Depuis l'" + lien(U["francfort"], "aéroport de Francfort") + " et l'"
    + lien(U["zurich"], "aéroport de Zurich") + " pour les vols long-courriers.</li>"
    "<li>Depuis l'" + lien(U["badenbaden"], "aéroport de Baden-Baden") + ", à quarante minutes de "
    "Strasbourg.</li>"
    "</ul>"
    "<p>Nos chauffeurs suivent les horaires de vol en temps réel. Un retard n'entraîne aucun frais "
    "supplémentaire.</p>"
    "<p>Nous couvrons par ailleurs l'ensemble des "
    + lien(U["services"], "services de transport à Strasbourg")
    + ", du trajet ponctuel à la journée complète.</p>"
    "<h2>Questions fréquentes</h2>"
    + "".join(f"<h3>{q}</h3><p>{r}</p>" for q, r in FAQ)
)

# --- Widget a309dc6 : bloc de services conserve, puis conclusion --------------

CONCLUSION = (
    "<h2>Réservez votre journée sur la Route des Vins d'Alsace</h2>"
    "<p>Un circuit sur-mesure, un chauffeur dédié, un tarif fixe et une région à découvrir sans aucune "
    "contrainte. Contactez Drive Me Driver par le "
    + lien(U["contact"], "formulaire du site")
    + " ou par téléphone pour recevoir votre devis gratuit. Nous vous répondons rapidement, et votre "
    "expérience alsacienne devient inoubliable.</p>"
    + cta("Créer mon circuit sur mesure")
)

# --- JSON-LD FAQPage ----------------------------------------------------------

JSONLD = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "Comment réserver un chauffeur privé ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Par le formulaire de contact du site ou par téléphone. Indiquez la date, l'heure de prise en charge, l'adresse de départ, le nombre de personnes et le nombre de bagages. Vous recevez un devis avec un tarif fixe. La réservation devient définitive dès votre validation.",
            },
        },
        {
            "@type": "Question",
            "name": "Quels sont les tarifs pour un circuit ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Le tarif est fixe et forfaitaire, calculé selon la durée de mise à disposition, le véhicule retenu, berline ou van, et le point de départ. Rien n'est facturé au compteur. Le prix inclut le carburant, les péages et le stationnement. Demandez votre devis gratuit pour connaître le prix exact de votre circuit.",
            },
        },
        {
            "@type": "Question",
            "name": "Quelles destinations inclut la route des vins ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Le vignoble s'étire de Marlenheim à Thann. Nos circuits desservent notamment Molsheim, Obernai, Barr, Sélestat, le château du Haut-Koenigsbourg, Ribeauvillé, Riquewihr, Kaysersberg, Eguisheim et Colmar. Vous choisissez vos étapes, et vous pouvez en changer en cours de journée.",
            },
        },
        {
            "@type": "Question",
            "name": "Quels services sont offerts par les chauffeurs ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Prise en charge à l'adresse de votre choix, véhicule haut de gamme climatisé, aide au chargement des bagages et des achats de vin, sièges auto pour les enfants, wifi à bord, eau à disposition, attente sur place pendant vos visites et conseils sur les domaines viticoles. Nos chauffeurs connaissent la région et parlent plusieurs langues.",
            },
        },
        {
            "@type": "Question",
            "name": "Comment se déroule une excursion sur la route des vins ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Votre chauffeur vous récupère à l'heure convenue. Vous rejoignez la première étape, généralement un village viticole, puis un domaine pour une dégustation. La pause déjeuner se fait dans le village de votre choix. L'après-midi enchaîne deux ou trois étapes, souvent un château et une cave. Le retour se fait à votre point de départ. Le circuit s'adapte à votre rythme en cours de journée.",
            },
        },
        {
            "@type": "Question",
            "name": "Quels sont les avantages d'un chauffeur privé ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "La liberté d'abord, puisque l'itinéraire vous appartient. La tranquillité ensuite, car vous dégustez sans vous soucier de la conduite. Le confort d'un véhicule de classe supérieure, le temps gagné sur le stationnement, et un service personnalisé pour une expérience unique.",
            },
        },
        {
            "@type": "Question",
            "name": "Comment se rendre à la route des vins ?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Le départ le plus courant se fait depuis Strasbourg, à trente minutes des premiers villages. Depuis Colmar, vous êtes au cœur du vignoble. Les transports en commun ne permettent pas toujours de relier facilement plusieurs villages au cours d'une même journée. Le VTC avec chauffeur privé reste la solution la plus souple pour couvrir le Bas-Rhin et le Haut-Rhin sans contrainte.",
            },
        },
    ],
}

TITRES = {"cec1592": TITRE_H1}
TEXTES = {"4b8dca0": INTRO, "1068fab": RYTHME, "eb1c652": DEGUSTATION, "a70a82e": GROUPES}
ID_HTML = "b6c9a46"
ID_SERVICES = "a309dc6"

MARQUEUR = "<!-- faq-jsonld -->"


def charge_env():
    env = RACINE / ".env"
    if not env.exists():
        sys.exit("Erreur : .env introuvable.")
    conf = {}
    for ligne in env.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if ligne and not ligne.startswith("#") and "=" in ligne:
            c, v = ligne.split("=", 1)
            conf[c.strip()] = v.strip().strip('"').strip("'")
    return conf


def appel(conf, methode, chemin, corps=None):
    url = conf["WP_SITE_URL"].rstrip("/") + chemin
    jeton = base64.b64encode(
        f"{conf['WP_USER']}:{conf['WP_APP_PASSWORD'].replace(' ', '')}".encode()
    ).decode()
    donnees = json.dumps(corps).encode("utf-8") if corps is not None else None
    req = urllib.request.Request(url, data=donnees, method=methode)
    req.add_header("Authorization", "Basic " + jeton)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "SEO Monkey / vtc-strasbourg-dmd")
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--restore", metavar="FICHIER")
    args = ap.parse_args()

    conf = charge_env()
    DOSSIER_BACKUP.mkdir(exist_ok=True)

    if args.restore:
        brut = pathlib.Path(args.restore).read_text(encoding="utf-8")
        json.loads(brut)
        appel(conf, "POST", f"/wp-json/wp/v2/pages/{PAGE_ID}", {"meta": {"_elementor_data": brut}})
        print(f"Restaure depuis {args.restore}")
        return

    page = appel(conf, "GET", f"/wp-json/wp/v2/pages/{PAGE_ID}?context=edit")
    brut = page["meta"]["_elementor_data"]
    data = json.loads(brut)

    horodatage = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    sauvegarde = DOSSIER_BACKUP / f"4404_elementor_data_{horodatage}.json"
    sauvegarde.write_text(brut, encoding="utf-8")
    print(f"Sauvegarde : {sauvegarde}")

    vus = set()
    changements = []

    def parcours(els):
        for e in els:
            eid = e.get("id")
            st = e.get("settings")
            if isinstance(st, dict):
                if eid in TITRES:
                    vus.add(eid)
                    changements.append((eid, "titre", st.get("title", ""), TITRES[eid]))
                    st["title"] = TITRES[eid]
                elif eid in TEXTES:
                    vus.add(eid)
                    changements.append((eid, "texte", st.get("editor", ""), TEXTES[eid]))
                    st["editor"] = TEXTES[eid]
                elif eid == ID_HTML:
                    vus.add(eid)
                    avant = st.get("html", "")
                    # l'iframe de reservation est conservee telle quelle
                    base_html = avant.split(MARQUEUR)[0].rstrip()
                    apres = (
                        base_html
                        + "\n"
                        + MARQUEUR
                        + '\n<script type="application/ld+json">'
                        + json.dumps(JSONLD, ensure_ascii=False, indent=2)
                        + "</script>"
                    )
                    changements.append((eid, "html + JSON-LD", avant, apres))
                    st["html"] = apres
                elif eid == ID_SERVICES:
                    vus.add(eid)
                    avant = st.get("editor", "")
                    socle = avant.split("<h2>Réservez votre journée")[0].rstrip()
                    apres = socle + "\n" + CONCLUSION
                    changements.append((eid, "services conserves + conclusion", avant, apres))
                    st["editor"] = apres
            parcours(e.get("elements", []))

    parcours(data)

    attendus = set(TITRES) | set(TEXTES) | {ID_HTML, ID_SERVICES}
    absents = attendus - vus
    if absents:
        sys.exit("Erreur : widgets introuvables : " + ", ".join(sorted(absents)) + ". Rien ecrit.")

    for eid, genre, avant, apres in changements:
        print(f"\n[{eid}] {genre}")
        print("  avant :", (avant[:110].replace("\n", " ") or "(vide)"))
        print("  apres :", apres[:110].replace("\n", " "))

    if args.dry_run:
        print(f"\n{len(changements)} changements. Rien n'a ete ecrit (--dry-run).")
        return

    charge = json.dumps(data, ensure_ascii=False)
    reponse = appel(conf, "POST", f"/wp-json/wp/v2/pages/{PAGE_ID}", {"meta": {"_elementor_data": charge}})
    ok = json.loads(reponse["meta"]["_elementor_data"]) == data
    print(f"\n{len(changements)} changements envoyes.")
    print("Relecture apres ecriture :", "conforme" if ok else "DIFFERENTE, a verifier")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
