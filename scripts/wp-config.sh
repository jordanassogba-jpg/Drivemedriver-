#!/usr/bin/env bash
# Configuration de la connexion a l'API REST WordPress de vtc-strasbourg-dmd.fr
#
# Ce fichier ne s'execute pas seul : il se charge dans un autre script.
#   source scripts/wp-config.sh
#
# Il expose ensuite :
#   wp_api <METHODE> <ENDPOINT> [donnees JSON]  -> appel authentifie, renvoie le JSON
#   wp_code <METHODE> <ENDPOINT> [donnees JSON] -> renvoie uniquement le code HTTP
#   WP_SITE_URL, WP_USER, WP_API                -> variables pretes a l'emploi

set -euo pipefail

# --- 1. Chargement des identifiants depuis .env -------------------------------

_wp_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
_wp_env="${WP_ENV_FILE:-$_wp_root/.env}"

if [[ ! -f "$_wp_env" ]]; then
  echo "Erreur : fichier $_wp_env introuvable." >&2
  echo "Copiez .env.example en .env puis renseignez le mot de passe d'application." >&2
  exit 1
fi

# shellcheck disable=SC1090
set -a; source "$_wp_env"; set +a

for _var in WP_SITE_URL WP_USER WP_APP_PASSWORD; do
  if [[ -z "${!_var:-}" ]]; then
    echo "Erreur : $_var n'est pas defini dans $_wp_env" >&2
    exit 1
  fi
done

# --- 2. Normalisation ---------------------------------------------------------

# Pas de slash final, sinon les URLs d'API se retrouvent avec un double slash.
WP_SITE_URL="${WP_SITE_URL%/}"
WP_API="$WP_SITE_URL/wp-json/wp/v2"

# WordPress ignore les espaces du mot de passe d'application, curl non : on les retire.
WP_APP_PASSWORD="${WP_APP_PASSWORD// /}"

# HTTPS obligatoire : en HTTP, WordPress refuse l'authentification par
# mot de passe d'application et l'identifiant circulerait en clair.
if [[ "$WP_SITE_URL" != https://* ]]; then
  echo "Erreur : WP_SITE_URL doit etre en https:// (recu : $WP_SITE_URL)" >&2
  exit 1
fi

# --- 3. Options curl communes ------------------------------------------------

# --netrc-file /dev/null evite qu'un ~/.netrc local vienne ecraser nos identifiants.
_WP_CURL_OPTS=(
  --silent
  --show-error
  --location
  --netrc-file /dev/null
  --connect-timeout 10
  --max-time 60
  --user "$WP_USER:$WP_APP_PASSWORD"
  --header "Content-Type: application/json"
  --header "Accept: application/json"
  --user-agent "SEO Monkey / vtc-strasbourg-dmd"
)

# --- 4. Fonctions d'appel ----------------------------------------------------

# Construit l'URL complete : un endpoint commencant par / est relatif a
# /wp-json/wp/v2, sinon on accepte une URL absolue telle quelle.
_wp_url() {
  case "$1" in
    http://*|https://*) printf '%s' "$1" ;;
    /wp-json/*)         printf '%s%s' "$WP_SITE_URL" "$1" ;;
    /*)                 printf '%s%s' "$WP_API" "$1" ;;
    *)                  printf '%s/%s' "$WP_API" "$1" ;;
  esac
}

# wp_api GET /posts
# wp_api POST /posts '{"title":"Titre","status":"draft"}'
wp_api() {
  local method="$1" endpoint="$2" data="${3:-}"
  local url; url="$(_wp_url "$endpoint")"

  if [[ -n "$data" ]]; then
    curl "${_WP_CURL_OPTS[@]}" --request "$method" --data "$data" "$url"
  else
    curl "${_WP_CURL_OPTS[@]}" --request "$method" "$url"
  fi
}

# Meme signature, mais ne renvoie que le code HTTP. Utile pour les tests.
wp_code() {
  local method="$1" endpoint="$2" data="${3:-}"
  local url; url="$(_wp_url "$endpoint")"

  if [[ -n "$data" ]]; then
    curl "${_WP_CURL_OPTS[@]}" --output /dev/null --write-out '%{http_code}' \
      --request "$method" --data "$data" "$url"
  else
    curl "${_WP_CURL_OPTS[@]}" --output /dev/null --write-out '%{http_code}' \
      --request "$method" "$url"
  fi
}

export WP_SITE_URL WP_USER WP_API
