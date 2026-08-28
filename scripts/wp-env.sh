#!/usr/bin/env bash
# Chargement et validation de la configuration de connexion WordPress.
# Ce fichier est destiné à être sourcé, pas exécuté directement.

set -euo pipefail

WP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -f "$WP_ROOT/.env" ]]; then
  echo "Erreur : fichier .env absent." >&2
  echo "  cp .env.example .env   puis renseignez vos identifiants." >&2
  exit 1
fi

# shellcheck disable=SC1091
set -a; source "$WP_ROOT/.env"; set +a

for var in WP_SITE_URL WP_USER WP_APP_PASSWORD; do
  if [[ -z "${!var:-}" ]]; then
    echo "Erreur : $var non défini dans .env" >&2
    exit 1
  fi
done

# Normalisation
WP_SITE_URL="${WP_SITE_URL%/}"
WP_APP_PASSWORD="${WP_APP_PASSWORD// /}"   # WordPress ignore les espaces
WP_TIMEOUT="${WP_TIMEOUT:-30}"
WP_API="$WP_SITE_URL/wp-json"

if [[ "$WP_SITE_URL" != https://* ]]; then
  echo "Attention : $WP_SITE_URL n'est pas en HTTPS." >&2
  echo "Un mot de passe d'application en HTTP circule en clair." >&2
fi

# Appel authentifié. Les identifiants passent par stdin (-K -) et n'apparaissent
# donc jamais dans la liste des processus ni dans l'historique du shell.
#
# Usage : wp_curl <methode> <chemin> [corps_json] [options curl supplementaires...]
# Le corps doit toujours être fourni, même vide, avant les options curl.
wp_curl() {
  local method="$1" path="$2" body="${3-}"
  if (( $# >= 3 )); then shift 3; else shift $#; fi

  local url="$WP_API/${path#/}"
  local args=(
    --silent --show-error --location
    --max-time "$WP_TIMEOUT"
    --request "${method^^}"
    --header "Accept: application/json"
    --header "User-Agent: dmd-wp-client/1.0"
  )
  if [[ -n "$body" ]]; then
    args+=(--header "Content-Type: application/json" --data-binary "$body")
  fi
  args+=("$@" "$url")

  printf 'user = "%s:%s"\n' "$WP_USER" "$WP_APP_PASSWORD" | curl -K - "${args[@]}"
}

# Idem, mais la sortie se termine par une ligne contenant le code HTTP.
wp_curl_status() {
  local method="$1" path="$2" body="${3-}"
  if (( $# >= 3 )); then shift 3; else shift $#; fi
  wp_curl "$method" "$path" "$body" --write-out $'\n%{http_code}' "$@"
}

# Formatage JSON si jq est présent
wp_pretty() {
  if command -v jq >/dev/null 2>&1; then jq .; else cat; fi
}
