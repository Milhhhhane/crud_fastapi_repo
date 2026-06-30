# Lab 2.3 — DevOps Monitoring API (FastAPI CRUD)

Refactor du health checker du Jour 1 en architecture OOP, exposé en REST via FastAPI.

## Structure

```
day2-lab/
├── __init__.py
├── models.py          # Server dataclass + ServerIn/Out Pydantic schemas
├── config.py          # ConfigLoader class (charge servers.json)
├── health.py          # HealthChecker class (async, asyncio.gather)
├── main.py            # FastAPI app + endpoints CRUD
├── servers.json       # Exemple de config initiale
└── requirements.txt
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate         # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

## Lancement

```bash
uvicorn main:app --reload --port 8000
```

Puis ouvre :
- Swagger UI interactif : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

## Endpoints

| Method | Path | Description | Auth |
|---|---|---|---|
| GET    | `/health`                       | API liveness                              | None |
| POST   | `/servers`                      | Enregistrer un serveur                    | API key |
| GET    | `/servers?status=UP`            | Lister (filtre optionnel par status)      | None |
| GET    | `/servers/{id}`                 | Récupérer un serveur                      | None |
| DELETE | `/servers/{id}`                 | Supprimer un serveur                      | API key |
| POST   | `/servers/{id}/check`           | Health check sur un serveur               | None |
| POST   | `/servers/check-all`            | Health check concurrent sur tous          | None |

## Auth (stretch goal)

Les endpoints `POST /servers` et `DELETE /servers/{id}` exigent le header :

```
X-API-Key: ops-secret
```

## Test rapide (curl)

```bash
# 1) Enregistrer un serveur
curl -X POST http://localhost:8000/servers \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ops-secret" \
  -d '{"name": "api-prod-1", "host": "httpbin.org", "port": 443}'

# 2) Lister
curl http://localhost:8000/servers

# 3) Health check
curl -X POST http://localhost:8000/servers/1/check

# 4) Tous d'un coup
curl -X POST http://localhost:8000/servers/check-all

# 5) Filtrer
curl "http://localhost:8000/servers?status=UP"
```

## Logique du statut

| Status   | Condition                                        |
|----------|--------------------------------------------------|
| `UP`       | HTTP 200 et temps de réponse ≤ 500ms             |
| `DEGRADED` | HTTP 200 mais lent, OU réponse non-200           |
| `DOWN`     | Erreur de connexion ou timeout                   |
| `unknown`  | Serveur enregistré mais jamais checké            |
