# Connexion API REST WordPress

Outils de connexion à l'API REST du site VTC Strasbourg DMD
(`https://vtc-strasbourg-dmd.fr`) par mot de passe d'application WordPress.

## Prérequis

- `bash` 4+, `curl`
- `jq` recommandé (formatage JSON et lecture des compteurs)
- Sur le site : HTTPS actif, permaliens autres que « simple », API REST non bloquée
- Un mot de passe d'application généré depuis WordPress :
  Utilisateurs > Profil > Mots de passe d'application

## Installation

```bash
cp .env.example .env
$EDITOR .env          # renseigner WP_SITE_URL, WP_USER, WP_APP_PASSWORD
./scripts/wp-check.sh
```

`.env` est ignoré par git. Aucun identifiant ne doit être commité.

## Vérification de la connexion

```bash
./scripts/wp-check.sh
```

Le script contrôle six points, dans l'ordre :

1. le site répond
2. `/wp-json/` expose bien l'index de l'API et le namespace `wp/v2`
3. l'authentification par mot de passe d'application est acceptée
4. la route `application-passwords` est exposée
5. le compte a les droits de lecture en contexte `edit` et de création
6. inventaire des types de contenu, nombre d'articles et de pages

Sortie 0 si tout est bon, 1 au premier blocage, avec les pistes de correction.

## Appels à l'API

```bash
# Lecture
./scripts/wp.sh GET "/wp/v2/posts?per_page=5&status=any&context=edit"
./scripts/wp.sh GET "/wp/v2/pages/12?context=edit"

# Écriture, charge utile en ligne
./scripts/wp.sh POST /wp/v2/posts '{"title":"Titre","status":"draft"}'

# Écriture, charge utile dans un fichier
./scripts/wp.sh POST /wp/v2/posts @charge.json
./scripts/wp.sh PUT  /wp/v2/posts/42 @maj.json
```

Le chemin est relatif à `/wp-json`. La réponse est renvoyée telle quelle,
formatée si `jq` est disponible.

## Réutilisation dans un script

```bash
source ./scripts/wp-env.sh

wp_curl GET "/wp/v2/categories?per_page=100" | jq -r '.[].name'

# Corps toujours en troisième position, même vide, avant les options curl
wp_curl GET "/wp/v2/posts" "" -D - -o /dev/null
```

`wp_curl_status` ajoute une dernière ligne contenant le code HTTP, utile pour
distinguer un 200 d'un 401.

## Sécurité

- Les identifiants passent à `curl` via `stdin` (`-K -`). Ils n'apparaissent
  ni dans la liste des processus ni dans l'historique du shell.
- Un mot de passe d'application donne les droits complets du compte associé.
  Créez un compte dédié au rôle strictement nécessaire plutôt que d'utiliser
  un compte administrateur.
- Révoquez le mot de passe depuis WordPress dès qu'il n'est plus utilisé, ou
  s'il a circulé par un canal non chiffré.
- Les espaces du mot de passe sont retirés automatiquement, comme le fait
  WordPress. Vous pouvez le coller tel qu'affiché.

## Dépannage

| Symptôme | Cause probable | Correction |
| --- | --- | --- |
| Étape 2 en échec | permaliens en mode simple | Réglages > Permaliens, choisir un autre format |
| Étape 2 en échec | API REST bloquée par un plugin de sécurité | autoriser `/wp-json/` ou les routes `wp/v2` |
| 401 alors que le mot de passe est bon | en-tête `Authorization` supprimé par le serveur (CGI, FastCGI) | ajouter dans `.htaccess`, avant les règles WordPress : `SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1` |
| 401 persistant | mauvais identifiant | utiliser le login WordPress, qui n'est pas toujours l'email |
| 403 | pare-feu applicatif côté hébergeur | mettre l'IP appelante en liste d'autorisation |
| Route `application-passwords` absente | site en HTTP, ou fonctionnalité désactivée par un filtre | passer en HTTPS, vérifier `wp_is_application_passwords_available` |
