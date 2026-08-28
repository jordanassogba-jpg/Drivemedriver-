#!/usr/bin/env python3
"""Met a jour le contenu Elementor de la page Transfert VTC Aeroport de Francfort.

Page 2189 : https://vtc-strasbourg-dmd.fr/transfert-vtc-aeroport-francfort-strasbourg/

Le contenu de cette page vit dans le meta _elementor_data, expose en lecture et
en ecriture par l'API REST en context=edit. Le script remplace uniquement le
texte des widgets existants : aucun widget n'est ajoute, supprime ou renomme,
et aucun reglage de style n'est touche. Les identifiants d'element restent donc
valides pour le CSS deja genere par Elementor.

Usage :
    python3 scripts/wp-maj-francfort.py --dry-run   # montre le diff, n'ecrit rien
    python3 scripts/wp-maj-francfort.py             # applique
    python3 scripts/wp-maj-francfort.py --restore fichier.json   # rollback
"""

import argparse
import base64
import datetime
import json
import os
import pathlib
import sys
import urllib.request

PAGE_ID = 2189
RACINE = pathlib.Path(__file__).resolve().parent.parent
DOSSIER_BACKUP = RACINE / "backup"

# Couleur d'accent de la charte, utilisee par les titres et le bouton.
# Les sections de la page sont sombres : un lien sans couleur explicite
# passerait en bleu par defaut et deviendrait illisible.
LIEN = 'style="color: #d0b039; text-decoration: underline;"'


def a(url, ancre):
    return f'<a {LIEN} href="{url}">{ancre}</a>'


BASE = "https://vtc-strasbourg-dmd.fr"
POPUP = "#elementor-action%3Aaction%3Dpopup%3Aopen%26settings%3DeyJpZCI6MTc4OSwidG9nZ2xlIjpmYWxzZX0%3D"

# --- Nouveau contenu, par identifiant de widget Elementor ---------------------
# Les cles sont les ids reels lus dans _elementor_data. Un id absent de la page
# fait echouer le script avant tout appel d'ecriture.

TITRES = {
    "74e47e0": "VTC Strasbourg Francfort : notre service de transfert aéroport",
    "d3c0f20": "VTC aéroport Francfort Strasbourg : le confort d'un chauffeur privé",
    "ad5d3d5": "Nos tarifs Strasbourg Francfort",
    "52013d7": "Pourquoi choisir notre service ?",
    "a5c8316": "Des formules adaptées à vos besoins",
    "046990e": "Des chauffeurs professionnels expérimentés",
    "3223f5c": "Une disponibilité 24h/24 et 7j/7",
    "65b499a": "Le confort à bord",
    "14469de": "Une flotte de véhicules haut de gamme",
    "a692534": "Découvrez Strasbourg, l'Alsace et Francfort avec votre chauffeur",
    # 4cd5fc4 conserve son titre : il introduit le bloc de liens de bas de page.
}

# Le H3 "Pourquoi choisir notre service ?" ouvre une serie de H3 : il passe en H2
# pour que la hierarchie reste coherente. Le CSS Elementor cible l'id, pas la
# balise, donc l'apparence ne change pas.
NIVEAUX = {"52013d7": "h2", "14469de": "h3"}

BOUTONS = {"beb37a7": "Réserver un VTC Strasbourg Francfort"}

TEXTES = {
    # Chapeau
    "33da009": (
        "<p>Après un vol éprouvant, plus besoin de chercher un taxi ou une navette. "
        "Notre service de VTC assure votre transfert entre Strasbourg et l'aéroport "
        "international de Francfort (FRA) sans attente. Départ de Strasbourg, retour "
        "en Alsace ou prise en charge dans "
        + a(f"{BASE}/vtc-business-espace-europeen-schiltigheim-illkirch/", "l'Eurométropole")
        + " (Bas-Rhin) : votre chauffeur vous attend à l'heure convenue. À l'arrivée "
        "à Francfort, il vous accueille dans le hall des arrivées, à la sortie de la "
        "zone bagages, avec une pancarte nominative.</p>"
    ),
    # Confort d'un chauffeur prive
    "47d7ce0": (
        "<p>Rejoindre "
        + a(f"{BASE}/vtc-strasbourg-gare/", "la gare centrale de Strasbourg")
        + ", la Place Kléber, "
        + a(f"{BASE}/vtc-parlement-europeen-strasbourg-transport-vip/", "le Conseil de l'Europe")
        + " ou un hôtel du centre historique depuis Francfort-sur-le-Main demande souvent "
        + a(f"{BASE}/transfert-vtc-gare-de-kehl-strasbourg-allemagne/", "plusieurs correspondances en train")
        + " ou en bus. Notre service vous propose une alternative simple : un chauffeur "
        "privé dédié, sur un trajet direct.</p>"
        "<p>Berlines haut de gamme, minibus et vans VIP : nos chauffeurs professionnels "
        "vous conduisent dans des véhicules récents, propres et climatisés. De quoi vous "
        "détendre après un vol long-courrier, ou travailler en toute confidentialité "
        "pendant un "
        + a(f"{BASE}/chauffeur-prive-vtc-pour-les-evenements-dentreprise-strasbourg/", "déplacement professionnel")
        + ".</p>"
    ),
    # Tarifs
    "a619134": (
        "<p>Nous appliquons la politique du prix fixe et garanti. Le tarif est verrouillé "
        "dès le devis, sans frais cachés liés aux embouteillages ou au temps de trajet.</p>"
        "<ul><li>Berline, en journée : à partir de 390 € TTC</li>"
        "<li>Van, en journée : à partir de 460 € TTC</li></ul>"
        "<p>Le prix final dépend du véhicule choisi, du nombre de passagers et des "
        "éventuels arrêts sur l'itinéraire. "
        + a(f"{BASE}/contactez-nous/", "Demandez votre devis gratuit en ligne")
        + ".</p>"
    ),
    # Pourquoi choisir notre service
    "8c62a4c": (
        "<p>Transfert rapide, aller-retour dans la journée, course vers "
        + a(f"{BASE}/transfert-vtc-chauffeur-prive-obernai-strasbourg/", "Obernai")
        + ", "
        + a(f"{BASE}/transfert-vtc-chauffeur-prive-colmar-strasbourg/", "Colmar")
        + " ou Mulhouse, connexions vers "
        + a(f"{BASE}/chauffeur-prive-vtc-aeroport-baden-baden/", "Baden-Baden")
        + ", Stuttgart, Munich, Bâle, "
        + a(f"{BASE}/transfert-vtc-aeroport-zurich-strasbourg/", "Zurich")
        + ", Genève ou "
        + a(f"{BASE}/vtc-strasbourg-longue-distance-paris-lyon-bruxelles/", "Paris")
        + " : nos chauffeurs privés s'adaptent à votre programme. Découvrez également "
        + a(f"{BASE}/nos-prestations/", "nos autres transferts aéroports")
        + ".</p>"
    ),
    # Formules
    "7847b27": (
        "<p>Chaque voyageur ou groupe a ses contraintes. Choix du véhicule (berline ou "
        + a(f"{BASE}/service-van-8-places-a-strasbourg-vtc/", "van spacieux")
        + "), nombre de passagers, volume de bagages, arrêts intermédiaires : nous "
        "construisons le trajet avec vous.</p>"
    ),
    # Chauffeurs
    "cc971c9": (
        "<p>Nos chauffeurs sont certifiés, ponctuels, courtois et multilingues. Ils "
        "connaissent la région du Rhin et les autoroutes allemandes, gèrent votre prise "
        "en charge, portent vos bagages et vous conseillent volontiers sur l'Alsace.</p>"
    ),
    # Disponibilite
    "74758a1": (
        "<p>Votre vol atterrit en pleine nuit ou un jour férié ? Notre service fonctionne "
        "24h/24 et 7j/7. En renseignant votre numéro de vol lors de la réservation (site "
        "internet, mail ou téléphone), nous suivons votre arrivée en temps réel et "
        "adaptons l'heure de prise en charge. En cas de retard indépendant de votre "
        "volonté, aucun frais supplémentaire ne vous sera demandé.</p>"
    ),
    # Confort a bord
    "df13434": (
        "<p>Van VIP ou berline business : véhicules récents, régulièrement entretenus, "
        "avec Wi-Fi gratuit, prises de recharge, bouteilles d'eau et climatisation "
        "réglable.</p>"
    ),
    # Flotte
    "e293b00": (
        "<p>Notre parc automobile (Mercedes Classe E, Classe S, Classe V) convient aux "
        "trajets en solo, en couple, en famille comme aux déplacements d'affaires. Il "
        "s'adapte aussi aux destinations loisirs de la région, comme "
        + a(f"{BASE}/chauffeur-prive-vtc-europa-park-strasbourg/", "Europa Park")
        + ". Contactez-nous pour toute "
        + a(f"{BASE}/chauffeur-prive-sur-mesure-strasbourg-vtc/", "mise à disposition spécifique")
        + ".</p>"
    ),
    # Tourisme
    "c0134cc": (
        "<p>Le trajet est aussi l'occasion de découvrir la région. Nos chauffeurs locaux "
        "vous conseillent sur "
        + a(f"{BASE}/visiter-strasbourg-en-vtc-les-lieux-et-activites-incontournables/", "les incontournables du Bas-Rhin")
        + " et de la Hesse, et peuvent assurer vos "
        + a(f"{BASE}/circuits-touristiques/", "circuits touristiques en Alsace")
        + ". Réservez à l'avance pour garantir votre véhicule.</p>"
    ),
}

# Corrections ponctuelles du bloc de liens de bas de page, conserve par ailleurs :
# il pointait vers la page courante et listait Entzheim deux fois.
CORRECTIONS_BLOC = [
    (
        f'<a style="color: #ffffff; text-decoration: underline;" href="{BASE}/transfert-vtc-aeroport-francfort-strasbourg/">Transfert vers l&rsquo;aéroport de Francfort</a>',
        "<strong>Transfert vers l&rsquo;aéroport de Francfort</strong>",
    ),
    (
        f'<a style="color: #ffffff; text-decoration: underline;" href="{BASE}/transfert-vtc-aeroport-francfort-strasbourg/">Transfert vers l\'aéroport de Francfort</a>',
        "<strong>Transfert vers l'aéroport de Francfort</strong>",
    ),
    (
        f'<br /><span style="text-decoration: underline;"><span style="color: #ffffff; text-decoration: underline;">-<a style="color: #ffffff; text-decoration: underline;" href="{BASE}/chauffeur-prive-vtc-aeroport-entzheim-strasbourg/"> Transfert vers l\'aéroport de Strasbourg Entzheim</a></span></span>',
        "",
    ),
]


# --- Acces API ----------------------------------------------------------------

def charge_env():
    env = RACINE / ".env"
    if not env.exists():
        sys.exit("Erreur : .env introuvable. Copiez .env.example et renseignez-le.")
    conf = {}
    for ligne in env.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or "=" not in ligne:
            continue
        cle, val = ligne.split("=", 1)
        conf[cle.strip()] = val.strip().strip('"').strip("'")
    manquant = [c for c in ("WP_SITE_URL", "WP_USER", "WP_APP_PASSWORD") if not conf.get(c)]
    if manquant:
        sys.exit(f"Erreur : {', '.join(manquant)} absent(s) de .env")
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
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "SEO Monkey / vtc-strasbourg-dmd")
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


# --- Transformation -----------------------------------------------------------

def parcours(elements, action):
    for e in elements:
        action(e)
        parcours(e.get("elements", []), action)


def applique(data):
    """Remplace le texte des widgets vises. Renvoie la liste des changements."""
    vus = set()
    changements = []

    def traite(e):
        eid = e.get("id")
        st = e.setdefault("settings", {})
        if eid in TITRES:
            vus.add(eid)
            changements.append((eid, "titre", st.get("title", ""), TITRES[eid]))
            st["title"] = TITRES[eid]
        if eid in NIVEAUX:
            st["header_size"] = NIVEAUX[eid]
        if eid in BOUTONS:
            vus.add(eid)
            changements.append((eid, "bouton", st.get("text", ""), BOUTONS[eid]))
            st["text"] = BOUTONS[eid]
        if eid in TEXTES:
            vus.add(eid)
            changements.append((eid, "texte", st.get("editor", ""), TEXTES[eid]))
            st["editor"] = TEXTES[eid]
        if eid == "c3bcc33":
            vus.add(eid)
            avant = st.get("editor", "")
            apres = avant
            for cible, remplacement in CORRECTIONS_BLOC:
                apres = apres.replace(cible, remplacement)
            if apres != avant:
                changements.append((eid, "bloc liens", avant, apres))
                st["editor"] = apres

    parcours(data, traite)

    attendus = set(TITRES) | set(BOUTONS) | set(TEXTES)
    absents = attendus - vus
    if absents:
        sys.exit(
            "Erreur : widgets introuvables dans la page : "
            + ", ".join(sorted(absents))
            + "\nLa structure Elementor a change, rien n'a ete ecrit."
        )
    return changements


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="affiche les changements sans ecrire")
    ap.add_argument("--restore", metavar="FICHIER", help="restaure un _elementor_data sauvegarde")
    args = ap.parse_args()

    conf = charge_env()
    DOSSIER_BACKUP.mkdir(exist_ok=True)

    if args.restore:
        brut = pathlib.Path(args.restore).read_text(encoding="utf-8")
        json.loads(brut)  # refuse un fichier qui n'est pas du JSON valide
        appel(conf, "POST", f"/wp-json/wp/v2/pages/{PAGE_ID}", {"meta": {"_elementor_data": brut}})
        print(f"Restaure depuis {args.restore}")
        return

    page = appel(conf, "GET", f"/wp-json/wp/v2/pages/{PAGE_ID}?context=edit")
    brut = page["meta"]["_elementor_data"]
    data = json.loads(brut) if isinstance(brut, str) else brut

    horodatage = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    sauvegarde = DOSSIER_BACKUP / f"2189_elementor_data_{horodatage}.json"
    sauvegarde.write_text(brut if isinstance(brut, str) else json.dumps(brut, ensure_ascii=False), encoding="utf-8")
    print(f"Sauvegarde : {sauvegarde}")

    changements = applique(data)
    for eid, genre, avant, apres in changements:
        print(f"\n[{eid}] {genre}")
        print("  avant : " + (avant[:120].replace("\n", " ") or "(vide)"))
        print("  apres : " + apres[:120].replace("\n", " "))

    if args.dry_run:
        print(f"\n{len(changements)} changements. Rien n'a ete ecrit (--dry-run).")
        return

    charge = json.dumps(data, ensure_ascii=False)
    reponse = appel(conf, "POST", f"/wp-json/wp/v2/pages/{PAGE_ID}", {"meta": {"_elementor_data": charge}})
    ecrit = reponse.get("meta", {}).get("_elementor_data", "")
    ok = json.loads(ecrit) == data if ecrit else False
    print(f"\n{len(changements)} changements envoyes.")
    print("Relecture du meta apres ecriture : " + ("identique, mise a jour confirmee" if ok else "DIFFERENT, a verifier"))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
