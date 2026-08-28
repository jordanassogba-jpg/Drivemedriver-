#!/usr/bin/env bash
# Vérifie la connexion à l'API REST WordPress et les droits du compte.
# Usage : ./scripts/wp-check.sh

# shellcheck source=./wp-env.sh
source "$(dirname "${BASH_SOURCE[0]}")/wp-env.sh"

ok()   { printf '  \033[32mOK\033[0m    %s\n' "$1"; }
fail() { printf '  \033[31mECHEC\033[0m %s\n' "$1"; }
warn() { printf '  \033[33mALERTE\033[0m %s\n' "$1"; }

echo
echo "Cible : $WP_SITE_URL"
echo "Compte : $WP_USER"
echo

# 1. Le site répond
echo "1. Joignabilité du site"
code="$(curl -sS -o /dev/null -L --max-time "$WP_TIMEOUT" -w '%{http_code}' "$WP_SITE_URL/" || echo 000)"
if [[ "$code" == "000" ]]; then
  fail "aucune réponse de $WP_SITE_URL (DNS, pare-feu ou proxy)"
  exit 1
elif [[ "$code" =~ ^(2|3) ]]; then
  ok "HTTP $code"
else
  warn "HTTP $code : le site répond mais renvoie une erreur"
fi

# 2. API REST exposée
echo
echo "2. Découverte de l'API REST"
root="$(curl -sS -L --max-time "$WP_TIMEOUT" "$WP_API/" || true)"
if ! echo "$root" | grep -q '"namespaces"'; then
  fail "$WP_API/ ne renvoie pas l'index de l'API REST"
  echo "     Causes fréquentes : permaliens en mode simple, API REST"
  echo "     désactivée par un plugin de sécurité, ou pare-feu applicatif."
  exit 1
fi
ok "index de l'API REST accessible"
if command -v jq >/dev/null 2>&1; then
  echo "     Site       : $(echo "$root" | jq -r '.name // "?"')"
  echo "     Namespaces : $(echo "$root" | jq -r '.namespaces | join(", ")')"
  if echo "$root" | jq -e '.namespaces | index("wp/v2")' >/dev/null; then
    ok "namespace wp/v2 présent"
  else
    fail "namespace wp/v2 absent"
  fi
fi

# 3. Authentification par mot de passe d'application
echo
echo "3. Authentification"
resp="$(wp_curl_status GET "/wp/v2/users/me?context=edit" || true)"
http="$(echo "$resp" | tail -n1)"
body="$(echo "$resp" | sed '$d')"

case "$http" in
  200)
    ok "authentification acceptée (HTTP 200)"
    if command -v jq >/dev/null 2>&1; then
      echo "     ID    : $(echo "$body" | jq -r '.id')"
      echo "     Nom   : $(echo "$body" | jq -r '.name')"
      echo "     Rôles : $(echo "$body" | jq -r '.roles | join(", ")')"
    fi
    ;;
  401)
    fail "identifiants refusés (HTTP 401)"
    echo "$body" | wp_pretty | sed 's/^/     /'
    echo
    echo "     Pistes :"
    echo "     - le mot de passe d'application a été révoqué ou mal recopié ;"
    echo "     - l'identifiant attendu est le login WordPress, pas toujours l'email ;"
    echo "     - l'en-tête Authorization est supprimé par le serveur (CGI/FastCGI)."
    echo "       Correctif dans le .htaccess, avant les règles WordPress :"
    echo '         SetEnvIf Authorization "(.*)" HTTP_AUTHORIZATION=$1'
    exit 1
    ;;
  403)
    fail "accès refusé (HTTP 403)"
    echo "$body" | wp_pretty | sed 's/^/     /'
    echo "     Un pare-feu applicatif ou un plugin de sécurité bloque l'appel."
    exit 1
    ;;
  *)
    fail "réponse inattendue (HTTP $http)"
    echo "$body" | head -c 500 | sed 's/^/     /'
    exit 1
    ;;
esac

# 4. Mots de passe d'application actifs côté serveur
echo
echo "4. Fonctionnalité mots de passe d'application"
if echo "$root" | grep -q 'application-passwords'; then
  ok "route application-passwords exposée"
else
  warn "route application-passwords absente de l'index"
  echo "     WordPress la masque hors HTTPS ou si un filtre la désactive."
fi

# 5. Droits de lecture et d'écriture
echo
echo "5. Droits sur les contenus"
posts="$(wp_curl_status GET "/wp/v2/posts?per_page=1&context=edit&status=any" || true)"
if [[ "$(echo "$posts" | tail -n1)" == "200" ]]; then
  ok "lecture des articles en contexte edit"
else
  warn "lecture en contexte edit refusée (HTTP $(echo "$posts" | tail -n1))"
fi

opts="$(wp_curl_status OPTIONS "/wp/v2/posts" || true)"
if [[ "$(echo "$opts" | tail -n1)" == "200" ]] && command -v jq >/dev/null 2>&1; then
  methods="$(echo "$opts" | sed '$d' | jq -r '[.endpoints[].methods[]] | unique | join(", ")')"
  echo "     Méthodes autorisées sur /wp/v2/posts : $methods"
  if [[ "$methods" == *POST* ]]; then
    ok "création d'articles autorisée"
  else
    warn "création d'articles non autorisée pour ce compte"
  fi
fi

# 6. Inventaire rapide
echo
echo "6. Inventaire"
if command -v jq >/dev/null 2>&1; then
  types="$(wp_curl GET "/wp/v2/types" | jq -r 'keys | join(", ")')"
  echo "     Types de contenu : $types"
  for t in posts pages; do
    total="$(wp_curl GET "/wp/v2/$t?per_page=1" "" -D - -o /dev/null \
      | awk 'tolower($1) == "x-wp-total:" { gsub(/\r/, "", $2); print $2 }')"
    echo "     ${t} : ${total:-?}"
  done
fi

echo
echo "Connexion opérationnelle."
