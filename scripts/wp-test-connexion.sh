#!/usr/bin/env bash
# Verifie que la connexion a l'API REST WordPress fonctionne.
# Usage : ./scripts/wp-test-connexion.sh

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/wp-config.sh"

_ok=0
_ko=0

titre() { printf '\n\033[1m%s\033[0m\n' "$1"; }
vert()  { printf '  \033[32mOK\033[0m   %s\n' "$1"; _ok=$((_ok+1)); }
rouge() { printf '  \033[31mECHEC\033[0m %s\n' "$1"; _ko=$((_ko+1)); }

# jq facilite la lecture mais n'est pas indispensable.
if command -v jq >/dev/null 2>&1; then _jq=1; else _jq=0; fi
champ() { # champ <json> <cle>
  if [[ $_jq -eq 1 ]]; then
    printf '%s' "$1" | jq -r ".$2 // empty"
  else
    printf '%s' "$1" | grep -o "\"$2\":\"[^\"]*\"" | head -1 | cut -d'"' -f4
  fi
}

echo "Site      : $WP_SITE_URL"
echo "Compte    : $WP_USER"
echo "Mot de passe d'application : charge depuis .env ($(printf '%s' "${WP_APP_PASSWORD}" | wc -c | tr -d ' ') caracteres)"

titre "1. L'API REST repond"
code="$(wp_code GET /wp-json/ || true)"
if [[ "$code" == "200" ]]; then
  vert "GET /wp-json/ renvoie 200"
else
  rouge "GET /wp-json/ renvoie $code (API REST desactivee, pare-feu, ou site injoignable)"
fi

titre "2. Les identifiants sont acceptes"
me="$(wp_api GET /users/me || true)"
code="$(wp_code GET /users/me || true)"
if [[ "$code" == "200" ]]; then
  vert "Authentifie comme \"$(champ "$me" name)\" (id $(champ "$me" id))"
  if [[ $_jq -eq 1 ]]; then
    echo "       roles : $(printf '%s' "$me" | jq -r '.roles // [] | join(", ")')"
  fi
elif [[ "$code" == "401" ]]; then
  rouge "401 : identifiant ou mot de passe d'application refuse"
  echo "       Verifiez WP_USER et regenerez le mot de passe d'application."
  echo "       Si le compte est correct, l'en-tete Authorization est peut-etre"
  echo "       filtre par le serveur : voir la section .htaccess du README."
elif [[ "$code" == "403" ]]; then
  rouge "403 : requete bloquee (plugin de securite, WAF, ou IP non autorisee)"
else
  rouge "code inattendu : $code"
  echo "       reponse : $(printf '%s' "$me" | head -c 300)"
fi

titre "3. Droits en lecture sur le contenu"
for endpoint in posts pages media categories tags; do
  code="$(wp_code GET "/$endpoint?per_page=1" || true)"
  if [[ "$code" == "200" ]]; then vert "/$endpoint lisible"; else rouge "/$endpoint renvoie $code"; fi
done

titre "4. Droits d'ecriture (creation puis suppression d'un brouillon de test)"
created="$(wp_api POST /posts '{"title":"Test connexion API - a supprimer","status":"draft"}' || true)"
post_id="$(champ "$created" id)"
if [[ -n "$post_id" && "$post_id" =~ ^[0-9]+$ ]]; then
  vert "brouillon cree (id $post_id)"
  code="$(wp_code DELETE "/posts/$post_id?force=true" || true)"
  if [[ "$code" == "200" ]]; then
    vert "brouillon de test supprime, rien ne reste sur le site"
  else
    rouge "suppression du brouillon $post_id impossible (code $code) : a retirer a la main"
  fi
else
  rouge "creation de brouillon refusee"
  echo "       reponse : $(printf '%s' "$created" | head -c 300)"
fi

titre "Resultat"
printf '  %s reussis, %s en echec\n' "$_ok" "$_ko"
[[ $_ko -eq 0 ]] || exit 1
