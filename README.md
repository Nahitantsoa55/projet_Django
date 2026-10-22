# Gestion des rapports de voyage d'étude

Application Django de suivi des voyages d'étude et des rapports remis par les
groupes d'étudiants. Les administrateurs organisent les voyages et les
affectations, les étudiants gèrent leur groupe et déposent un rapport PDF, et
les encadrants consultent puis évaluent les rapports.

## Fonctionnalités

- Inscription et connexion des étudiants et des encadrants.
- Validation des nouveaux comptes encadrants par un administrateur.
- Création de groupes et gestion de leurs membres (quatre étudiants maximum).
- Affectation des groupes à un voyage et à un encadrant.
- Dépôt et consultation des rapports PDF, avec verrouillage après consultation.
- Évaluation des rapports et génération d'un procès-verbal PDF.
- Espaces adaptés aux rôles étudiant, encadrant et administrateur.

## Technologies

- Python et Django
- SQLite pour le développement local
- Bootstrap et CSS
- WeasyPrint pour la génération des PDF

## Installation et lancement en local

Prérequis : Python 3.12 ou une version compatible avec les dépendances de
`requirements.txt`.

```bash
git clone <URL_DU_DEPOT>
cd projet_Django
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

Générez une clé secrète locale sans l'afficher dans le terminal :

```bash
./venv/bin/python -c "from pathlib import Path; from secrets import token_urlsafe; p = Path('.env'); p.write_text(p.read_text().replace('replace-with-a-new-secret-key', token_urlsafe(50)))"
chmod 600 .env
```

Chargez les variables du fichier dans votre terminal, puis initialisez et
lancez l'application :

```bash
set -a
. ./.env
set +a
./venv/bin/python manage.py migrate
./venv/bin/python manage.py runserver
```

L'application est accessible sur <http://127.0.0.1:8000/>. Pour accéder au
serveur depuis d'autres machines du même réseau, ajoutez son adresse IP locale
à `DJANGO_ALLOWED_HOSTS` dans `.env`, puis lancez `runserver 0.0.0.0:8000`.
Le serveur de développement Django n'est pas destiné à la production.

## Configuration

Les réglages sensibles sont lus depuis l'environnement. `.env` est ignoré par
Git; ne le publiez jamais et ne réutilisez pas sa clé en production.

| Variable | Description |
| --- | --- |
| `DJANGO_SECRET_KEY` | Clé secrète Django, obligatoire et privée. |
| `DJANGO_DEBUG` | Active le mode développement (`True` ou `False`); désactivé par défaut. |
| `DJANGO_ALLOWED_HOSTS` | Noms d'hôte autorisés séparés par des virgules. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origines HTTPS de confiance, séparées par des virgules si nécessaire. |
| `DJANGO_SECURE_SSL_REDIRECT` | Redirige vers HTTPS; activé par défaut hors mode debug. |
| `DJANGO_SECURE_HSTS_SECONDS` | Durée HSTS; un an par défaut hors mode debug. |
| `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` | Active HSTS pour les sous-domaines (désactivé par défaut). |
| `DJANGO_SECURE_HSTS_PRELOAD` | Demande l'inclusion dans les listes de préchargement HSTS (désactivé par défaut). |

Avant tout déploiement, configurez une nouvelle clé, les hôtes et origines
réels, HTTPS et les réglages de base de données. Ne désactivez pas les
protections HTTPS en production. N'activez HSTS pour les sous-domaines que
s'ils utilisent tous HTTPS; le préchargement HSTS a des effets durables.

## Tests et contrôles

```bash
set -a
. ./.env
set +a
./venv/bin/python manage.py test
./venv/bin/black --check config gestion
./venv/bin/flake8 config gestion
DJANGO_DEBUG=False DJANGO_SECURE_SSL_REDIRECT=True \
DJANGO_SECURE_HSTS_SECONDS=31536000 \
  ./venv/bin/python manage.py check --deploy
```

`check --deploy` peut signaler des réglages propres à l'hébergeur ou au
proxy HTTPS; corrigez-les avant la mise en production. Il signale aussi
l'absence d'un fournisseur d'e-mail de production : le backend console actuel
est réservé au développement et n'a pas été modifié.

Une ancienne clé secrète était présente dans les réglages du projet. Si elle a
été poussée vers un dépôt distant, révoquez-la et remplacez-la dans les secrets
de l'hébergeur; une nouvelle clé n'efface pas l'ancienne des commits existants.

## Démonstration et conception

Aucun compte de démonstration ni capture d'écran n'est inclus. Créez les
comptes depuis l'application et créez un administrateur avec
`./venv/bin/python manage.py createsuperuser`.

Les auteurs, l'établissement, l'année de réalisation, le MCD et les diagrammes
de conception doivent être ajoutés par l'équipe du projet : ces informations
et documents ne figurent pas dans le dépôt actuel.
