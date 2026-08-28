#!/usr/bin/env python3
"""Ajoute la FAQ a la page Transfert VTC Aeroport de Francfort (2189).

Les neuf questions sont inserees dans la colonne existante 80cc1b8, juste avant
le bloc de liens de bas de page. Deux widgets sont crees : un titre et un bloc
de texte. Leurs reglages reprennent ceux des widgets voisins pour rester dans
la charte de la page, sans la condition d'affichage "subscriber" portee par le
titre voisin, qui masquerait la FAQ.

Ces widgets ayant des identifiants neufs, le CSS de la page devrait ensuite etre
regenere depuis Elementor, ce qu'une ecriture par l'API REST ne declenche pas.
C'est pourquoi wp-faq-inline-francfort.py est passe juste apres : il retire le
titre cree ici et reporte toute la mise en forme en ligne, dans le seul widget
de texte. Les deux scripts se lisent donc dans cet ordre.

Usage :
    python3 scripts/wp-ajout-faq-francfort.py --dry-run
    python3 scripts/wp-ajout-faq-francfort.py
"""

import argparse
import base64
import datetime
import json
import pathlib
import sys
import urllib.request

PAGE_ID = 2189
RACINE = pathlib.Path(__file__).resolve().parent.parent
DOSSIER_BACKUP = RACINE / "backup"

COLONNE = "80cc1b8"      # colonne d'accueil
AVANT_ID = "4cd5fc4"     # on insere juste avant ce titre
# Identifiants au format Elementor : 7 caracteres hexadecimaux.
ID_TITRE = "fa91d01"
ID_TEXTE = "fa91d02"

BASE = "https://vtc-strasbourg-dmd.fr"
POPUP = "#elementor-action%3Aaction%3Dpopup%3Aopen%26settings%3DeyJpZCI6MTc4OSwidG9nZ2xlIjpmYWxzZX0%3D"
LIEN = 'style="color: #d0b039; text-decoration: underline;"'

QUESTIONS = [
    (
        "Comment réserver un VTC entre Strasbourg et Francfort ?",
        f'Vous réservez à l\'avance depuis notre <a {LIEN} href="{POPUP}">page de réservation en ligne</a>, '
        f'<a {LIEN} href="{BASE}/contactez-nous/">par mail ou par téléphone</a>. Nous confirmons votre trajet, '
        "le véhicule et le tarif avant le départ.",
    ),
    (
        "Combien coûte un transfert Strasbourg Francfort ?",
        "Le tarif est forfaitaire : à partir de 390 € TTC en berline et 460 € TTC en van, en journée. "
        "Le prix est fixé au moment du devis et n'évolue plus, quelle que soit la circulation.",
    ),
    (
        "Où mon chauffeur m'attend-il à l'aéroport de Francfort ?",
        "Votre chauffeur vous attend dans le hall des arrivées, à la sortie de la zone bagages, avec une "
        "pancarte à votre nom. Il vous accompagne ensuite jusqu'au véhicule et se charge de vos bagages.",
    ),
    (
        "Que se passe-t-il si mon vol est en retard ?",
        "Nous suivons votre vol grâce au numéro que vous nous communiquez et adaptons l'heure de prise en "
        "charge. En cas de retard indépendant de votre volonté, aucun supplément n'est appliqué.",
    ),
    (
        "Quelle est la durée du trajet ?",
        "Comptez environ 2h40 pour les 217 km entre Strasbourg et l'aéroport de Francfort, selon les "
        "conditions de circulation.",
    ),
    (
        "Quels véhicules proposez-vous ?",
        "Des berlines Mercedes Classe E et Classe S pour 1 à 3 passagers, et des vans Classe V pour les "
        "groupes et les bagages volumineux. Tous nos véhicules disposent du Wi-Fi, de prises de recharge, "
        "de bouteilles d'eau et de la climatisation.",
    ),
    (
        "Le service est-il disponible la nuit et les jours fériés ?",
        "Oui, nos chauffeurs assurent les transferts 24h/24 et 7j/7, y compris les week-ends et jours fériés.",
    ),
    (
        "Puis-je faire un arrêt en route ou réserver un aller-retour ?",
        "Oui. Arrêts intermédiaires, aller-retour dans la journée ou mise à disposition sur plusieurs "
        "heures : indiquez-le lors de votre demande de devis, nous intégrons ces éléments au forfait.",
    ),
    (
        "Combien de bagages puis-je emporter ?",
        "Cela dépend du véhicule et du nombre de passagers. Précisez le volume de vos bagages à la "
        "réservation pour que nous vous orientions vers la berline ou le van.",
    ),
]

FAQ_HTML = "".join(
    f'<p><strong style="color: #d0b039;">{q}</strong><br />{r}</p>' for q, r in QUESTIONS
)

WIDGET_TITRE = {
    "id": ID_TITRE,
    "elType": "widget",
    "widgetType": "heading",
    "elements": [],
    "settings": {
        "title": "Foire aux questions (FAQ)",
        "header_size": "h2",
        "align": "left",
        "title_color": "#d0b039",
        "typography_typography": "custom",
        "typography_font_size": {"unit": "px", "size": 25},
        "typography_font_weight": "600",
        "_margin": {"unit": "px", "top": "40", "right": "0", "bottom": "0", "left": "0", "isLinked": False},
    },
}

WIDGET_TEXTE = {
    "id": ID_TEXTE,
    "elType": "widget",
    "widgetType": "text-editor",
    "elements": [],
    "settings": {
        "editor": FAQ_HTML,
        "text_color": "#FFFFFF",
        "_margin": {"unit": "px", "top": "10", "right": "0", "bottom": "0", "left": "0", "isLinked": False},
    },
}


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


def ids_existants(els, acc):
    for e in els:
        acc.add(e.get("id"))
        ids_existants(e.get("elements", []), acc)
    return acc


def trouve_colonne(els):
    for e in els:
        if e.get("id") == COLONNE:
            return e
        r = trouve_colonne(e.get("elements", []))
        if r:
            return r
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    conf = charge_env()
    DOSSIER_BACKUP.mkdir(exist_ok=True)

    page = appel(conf, "GET", f"/wp-json/wp/v2/pages/{PAGE_ID}?context=edit")
    brut = page["meta"]["_elementor_data"]
    data = json.loads(brut)

    horodatage = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    sauvegarde = DOSSIER_BACKUP / f"2189_elementor_data_{horodatage}.json"
    sauvegarde.write_text(brut, encoding="utf-8")
    print(f"Sauvegarde : {sauvegarde}")

    if ID_TITRE == ID_TEXTE:
        sys.exit("Erreur : les deux widgets auraient le meme identifiant.")

    presents = ids_existants(data, set())
    for nouvel_id in (ID_TITRE, ID_TEXTE):
        if nouvel_id in presents:
            sys.exit(f"Erreur : l'identifiant {nouvel_id} existe deja, rien n'a ete ecrit.")

    colonne = trouve_colonne(data)
    if colonne is None:
        sys.exit(f"Erreur : colonne {COLONNE} introuvable, rien n'a ete ecrit.")

    enfants = colonne["elements"]
    if any(e.get("id") in (ID_TITRE, ID_TEXTE) for e in enfants):
        sys.exit("La FAQ est deja presente, rien a faire.")

    position = next((i for i, e in enumerate(enfants) if e.get("id") == AVANT_ID), None)
    if position is None:
        sys.exit(f"Erreur : widget {AVANT_ID} introuvable dans la colonne, rien n'a ete ecrit.")

    enfants.insert(position, WIDGET_TEXTE)
    enfants.insert(position, WIDGET_TITRE)

    print(f"Insertion a la position {position} de la colonne {COLONNE}")
    print(f"  {ID_TITRE} heading      : {WIDGET_TITRE['settings']['title']}")
    print(f"  {ID_TEXTE} text-editor  : {len(QUESTIONS)} questions, {len(FAQ_HTML)} caracteres")
    print("  ordre final :", [e.get("widgetType") or e.get("elType") for e in enfants])

    if args.dry_run:
        print("\nRien n'a ete ecrit (--dry-run).")
        return

    charge = json.dumps(data, ensure_ascii=False)
    reponse = appel(conf, "POST", f"/wp-json/wp/v2/pages/{PAGE_ID}", {"meta": {"_elementor_data": charge}})
    relu = json.loads(reponse["meta"]["_elementor_data"])
    ok = relu == data
    print("\nRelecture apres ecriture :", "conforme" if ok else "DIFFERENTE, a verifier")
    print("Pensez a regenerer le CSS Elementor puis a purger LiteSpeed.")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
