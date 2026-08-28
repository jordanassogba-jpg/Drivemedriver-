#!/usr/bin/env python3
"""Rend la FAQ de la page 2189 autonome vis-a-vis du CSS genere par Elementor.

Un widget cree hors de l'editeur Elementor n'a pas de regles dans
uploads/elementor/css/post-2189.css, et le fichier n'est pas regenere par une
ecriture via l'API REST. Sur cette page au fond sombre, un titre sans style
serait illisible.

La FAQ est donc regroupee dans un seul widget de texte dont toute la mise en
forme est portee en ligne, comme le fait deja le bloc de liens de bas de page.
Le titre precedemment ajoute est retire.

Usage :
    python3 scripts/wp-faq-inline-francfort.py --dry-run
    python3 scripts/wp-faq-inline-francfort.py
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

ID_TITRE = "fa91d01"   # widget titre a retirer
ID_TEXTE = "fa91d02"   # widget texte a remplir

BASE = "https://vtc-strasbourg-dmd.fr"
POPUP = "#elementor-action%3Aaction%3Dpopup%3Aopen%26settings%3DeyJpZCI6MTc4OSwidG9nZ2xlIjpmYWxzZX0%3D"

OR = "#d0b039"
BLANC = "#ffffff"
S_H2 = f'style="color: {OR}; font-size: 25px; font-weight: 600; margin: 40px 0 10px;"'
S_H3 = f'style="color: {OR}; font-size: 18px; font-weight: 600; margin: 22px 0 6px;"'
S_P = f'style="color: {BLANC}; margin: 0;"'
S_A = f'style="color: {OR}; text-decoration: underline;"'

QUESTIONS = [
    (
        "Comment réserver un VTC entre Strasbourg et Francfort ?",
        f'Vous réservez à l\'avance depuis notre <a {S_A} href="{POPUP}">page de réservation en ligne</a>, '
        f'<a {S_A} href="{BASE}/contactez-nous/">par mail ou par téléphone</a>. Nous confirmons votre trajet, '
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

FAQ_HTML = f'<h2 {S_H2}>Foire aux questions (FAQ)</h2>' + "".join(
    f'<h3 {S_H3}>{q}</h3><p {S_P}>{r}</p>' for q, r in QUESTIONS
)


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

    etat = {"titre_retire": False, "texte_rempli": False}

    def parcours(els):
        for e in list(els):
            if e.get("id") == ID_TITRE:
                els.remove(e)
                etat["titre_retire"] = True
                continue
            if e.get("id") == ID_TEXTE:
                e["settings"]["editor"] = FAQ_HTML
                e["settings"]["text_color"] = BLANC
                etat["texte_rempli"] = True
            parcours(e.get("elements", []))

    parcours(data)

    if not etat["texte_rempli"]:
        sys.exit(f"Erreur : widget {ID_TEXTE} introuvable, rien n'a ete ecrit.")

    print(f"Titre {ID_TITRE} retire   : {etat['titre_retire']}")
    print(f"Texte {ID_TEXTE} rempli   : {len(FAQ_HTML)} caracteres, {len(QUESTIONS)} questions")
    print("Toute la mise en forme est portee en ligne : aucun CSS a regenerer.")

    if args.dry_run:
        print("\nRien n'a ete ecrit (--dry-run).")
        return

    charge = json.dumps(data, ensure_ascii=False)
    reponse = appel(conf, "POST", f"/wp-json/wp/v2/pages/{PAGE_ID}", {"meta": {"_elementor_data": charge}})
    ok = json.loads(reponse["meta"]["_elementor_data"]) == data
    print("\nRelecture apres ecriture :", "conforme" if ok else "DIFFERENTE, a verifier")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
