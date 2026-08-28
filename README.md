# Connexion API - VTC Strasbourg DMD

Configuration d'accès à l'API REST WordPress de `vtc-strasbourg-dmd.fr`, via un
mot de passe d'application. Permet de lire et modifier le contenu du site en
ligne de commande, sans passer par l'admin.

## Mise en route

```bash
cp .env.example .env      # puis renseignez le mot de passe d'application
chmod 600 .env
./scripts/wp-test-connexion.sh
```

Le test vérifie quatre choses dans l'ordre : l'API REST répond, les identifiants
sont acceptés, le contenu est lisible, l'écriture fonctionne. Il crée un
brouillon de test puis le supprime, donc rien ne reste sur le site.

## Fichiers

| Fichier | Rôle |
|---|---|
| `.env` | Identifiants réels. Ignoré par git, ne part jamais sur le dépôt. |
| `.env.example` | Modèle à copier, sans secret. |
| `scripts/wp-config.sh` | Configuration et fonctions d'appel. Se charge avec `source`. |
| `scripts/wp-test-connexion.sh` | Diagnostic de la connexion. |

## Utilisation dans vos propres scripts

```bash
#!/usr/bin/env bash
source scripts/wp-config.sh

# Lecture
wp_api GET '/posts?per_page=5&status=publish'
wp_api GET '/pages?search=tarifs'

# Création d'un brouillon
wp_api POST /posts '{"title":"Nouvel article","content":"<p>Texte</p>","status":"draft"}'

# Mise à jour d'une page (id 42)
wp_api POST /pages/42 '{"title":"Nouveau titre"}'

# Endpoint hors /wp/v2 : donnez le chemin complet
wp_api GET /wp-json/yoast/v1/get_head
```

Conventions des endpoints passés aux fonctions :

- `/posts` → `https://vtc-strasbourg-dmd.fr/wp-json/wp/v2/posts`
- `/wp-json/...` → relatif à la racine du site, hors namespace `wp/v2`
- `https://...` → utilisé tel quel

`wp_code` a la même signature que `wp_api` mais ne renvoie que le code HTTP.

## Renouveler le mot de passe d'application

Dans l'admin WordPress : **Utilisateurs → Profil → Mots de passe d'application**.
Créez une entrée dédiée (par exemple « Automatisation SEO »), copiez la valeur
affichée une seule fois, reportez-la dans `.env`. Révoquer une entrée coupe
l'accès immédiatement, sans toucher au mot de passe du compte.

## En cas d'échec

**401 alors que les identifiants sont bons.** Certains hébergements en PHP-CGI
ou FastCGI ne transmettent pas l'en-tête `Authorization` à WordPress. À ajouter
au `.htaccess`, avant le bloc `# BEGIN WordPress` :

```apache
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteCond %{HTTP:Authorization} ^(.*)
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
</IfModule>
```

**403 sur toutes les requêtes.** Un plugin de sécurité (Wordfence, iThemes,
SecuPress) ou le WAF de l'hébergeur bloque l'API REST. Autorisez l'IP source, ou
désactivez la règle « REST API / XML-RPC » le temps du diagnostic.

**Code 000 ou erreur de tunnel.** Le réseau ne laisse pas sortir vers le
domaine. C'est le cas depuis une session Claude Code sur le web : le domaine
doit être ajouté à la liste d'autorisation de l'environnement. Voir
https://code.claude.com/docs/en/claude-code-on-the-web

## Sécurité

Le mot de passe d'application vit uniquement dans `.env`, en `chmod 600`, ignoré
par git. S'il a été partagé par un canal non chiffré (mail, message), révoquez-le
et régénérez-en un dans l'admin WordPress.
