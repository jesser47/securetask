# État des lieux AS-IS (avant DevSecOps)

## Application
SecureTask : application Flask (Python 3.12), SQLAlchemy/SQLite, Docker.

## Pipeline initial (GitHub Actions)

```text
Developer → git push → GitHub → test (pytest) → build-image (docker build + smoke test)
```

## Contrôles de sécurité présents

| Contrôle | Avant DevSecOps |
|---|---|
| Scan de secrets (pre-commit et CI) | Absent |
| SAST (analyse statique du code) | Absent |
| SCA (dépendances vulnérables) | Absent |
| Scan de l'image Docker | Absent |
| DAST (test dynamique) | Absent |
| Scan IaC (Dockerfile, CI) | Absent |
| Quality gates bloquantes | Absentes |
| Reporting centralisé | Absent |
| Politique d'exemption des faux positifs | Absente |

## Risques identifiés
- Un secret commité dans l'historique Git n'est détecté par personne.
- Une dépendance vulnérable (requirements.txt) passe en production sans alerte.
- Une faille de code (injection SQL, XSS) n'est détectée qu'après déploiement.
- Une image de base obsolète est livrée telle quelle.
- Aucune preuve (rapport) pour auditer la sécurité d'une livraison.

## Constat
Le pipeline vérifie que l'application fonctionne (tests, build), mais pas qu'elle est sûre.