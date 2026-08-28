#!/usr/bin/env bash
# Client générique pour l'API REST WordPress du site configuré dans .env
#
# Usage :
#   ./scripts/wp.sh GET  /wp/v2/posts?per_page=5
#   ./scripts/wp.sh GET  /wp/v2/pages/12?context=edit
#   ./scripts/wp.sh POST /wp/v2/posts '{"title":"Test","status":"draft"}'
#   ./scripts/wp.sh POST /wp/v2/posts @charge.json
#   ./scripts/wp.sh PUT  /wp/v2/posts/42 '{"meta":{"_yoast_wpseo_title":"..."}}'

# shellcheck source=./wp-env.sh
source "$(dirname "${BASH_SOURCE[0]}")/wp-env.sh"

if [[ $# -lt 2 ]]; then
  awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "${BASH_SOURCE[0]}"
  exit 1
fi

method="$1"
path="$2"
body="${3:-}"

# Corps lu depuis un fichier si préfixé par @
if [[ "$body" == @* ]]; then
  file="${body#@}"
  [[ -f "$file" ]] || { echo "Fichier introuvable : $file" >&2; exit 1; }
  body="$(cat "$file")"
fi

wp_curl "${method^^}" "$path" "$body" | wp_pretty
