# SecureTask

## Description

SecureTask est une application web de gestion de tâches multi-utilisateurs développée avec **Flask**.
Elle sert de **cible applicative** à un projet académique DevSecOps / Shift-Left Security
(pre-commit, Gitleaks, Semgrep, Bandit, Trivy, OWASP ZAP, SonarQube, quality gates GitLab CI/CD).

Fonctionnalités : inscription, connexion, déconnexion, CRUD des tâches, recherche et filtre,
tableau de bord, rôles `USER` / `ADMIN` (l'administrateur consulte la liste des utilisateurs).

> Cette version est l'**étape 1** : application réelle, sans outil de sécurité intégré.

## Architecture

```text
Browser
   ↓
Flask (routes → services)
   ↓
SQLAlchemy
   ↓
SQLite
```

## Installation locale

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python run.py
```

### Windows (PowerShell)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
python run.py
```

### Windows (cmd)

```bat
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements-dev.txt
copy .env.example .env
python run.py
```

L'application est accessible sur http://localhost:5000.
Éditer `.env` pour définir `SECRET_KEY` (générer : `python -c "import secrets; print(secrets.token_hex(32))"`).

### Créer un administrateur

```bash
flask --app run create-admin
```

## Tests

```bash
pytest
```

## Docker

```bash
docker build -t securetask .
docker run -p 5000:5000 securetask
```

Avec une clé fixe et une base persistante :

```bash
docker run -p 5000:5000 -e SECRET_KEY=<valeur-aleatoire> -v securetask-data:/app/instance securetask
```

Avec Docker Compose (nécessite `SECRET_KEY` dans `.env`) :

```bash
docker compose up --build
```

Créer un admin dans le conteneur :

```bash
docker compose exec web flask --app run create-admin
```

## Structure du projet

| Chemin | Rôle |
|---|---|
| `app/__init__.py` | Application factory, extensions, gestionnaires d'erreurs, commandes CLI |
| `app/extensions.py` | Instances `db`, `login_manager`, `csrf` |
| `app/models.py` | Modèles `User` et `Task` (SQLAlchemy), constantes de rôles, statuts, priorités |
| `app/routes/` | Blueprints : `auth.py`, `tasks.py`, `dashboard.py` (dashboard + admin + `/health`) |
| `app/services/` | Logique métier : `user_service.py`, `task_service.py` |
| `app/decorators.py` | Décorateur `admin_required` |
| `app/templates/` | Templates Jinja2 (Bootstrap 5) : base, auth, tasks, admin, erreurs |
| `app/static/` | CSS et JavaScript |
| `tests/` | Tests pytest |
| `config.py` | Configuration via variables d'environnement (`SECRET_KEY`, `DATABASE_URL`) |
| `run.py` | Point d'entrée |
| `Dockerfile`, `docker-compose.yml` | Conteneurisation (gunicorn, utilisateur non-root) |
| `requirements.txt` / `requirements-dev.txt` | Dépendances d'exécution / de test |
| `.env.example` | Exemple de configuration (le vrai `.env` est ignoré par Git) |
| `.gitlab-ci.yml` | Pipeline minimal (tests) |
