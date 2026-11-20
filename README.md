# Reservation Service

Microservice de gestion des réservations du projet **UniBook**, une plateforme
distribuée de réservation de ressources universitaires.

## Fonctionnalités
- Créer, modifier et annuler une réservation
- Consulter l'historique des réservations (par utilisateur ou par ressource)
- Éviter les doubles réservations et les conflits horaires
- Vérifier l'utilisateur et la ressource via le User & Resource Service (REST)

## Technologies
Python, FastAPI, SQLAlchemy, Microsoft SQL Server, httpx, Pytest

## Prérequis
- Python 3.10 ou plus
- SQL Server (ou SQL Server Express) et SSMS
- ODBC Driver 17 ou 18 for SQL Server
- User & Resource Service lancé (port 8001 par défaut)

## Installation
```bash
cd reservation-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration
Copie `env.example` en `.env` et adapte les valeurs :

```
DB_SERVER=localhost\SQLEXPRESS
DB_NAME=reservation_db
DB_DRIVER=ODBC Driver 17 for SQL Server
USER_RESOURCE_SERVICE_URL=http://localhost:8001
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

Crée la base `reservation_db` dans SSMS. Les tables sont créées
automatiquement au démarrage du service.

## Lancer le service
```bash
uvicorn app.main:app --reload --port 8002
```
Documentation Swagger : http://localhost:8002/docs

## Endpoints
| Méthode | Route | Description |
|---|---|---|
| GET | `/health` | État du service |
| POST | `/reservations` | Créer une réservation |
| GET | `/reservations?user_id=&resource_id=` | Historique (filtres optionnels) |
| GET | `/reservations/{id}` | Détail d'une réservation |
| PUT | `/reservations/{id}` | Modifier une réservation |
| PATCH | `/reservations/{id}/cancel` | Annuler une réservation |

### Exemple de création
```json
{
  "user_id": 1,
  "resource_id": 1,
  "date": "2026-12-01",
  "start_time": "09:00:00",
  "end_time": "11:00:00"
}
```

### Codes d'erreur
- `404` : réservation, utilisateur ou ressource introuvable
- `409` : créneau déjà réservé
- `422` : données invalides
- `503` : User & Resource Service indisponible

## Communication avec les autres services
- **REST** : `GET /users/{id}` et `GET /resources/{id}` sur le User & Resource Service.
- **RabbitMQ** (prévu, Epic 4) : publication de `ReservationCreated` et
  `ReservationCancelled` vers le Notification Service.

## Tests
```bash
python -m pytest tests -v
```

## Structure
```
reservation-service/
├── app/            # point d'entrée FastAPI
├── models/         # modèles SQLAlchemy
├── schemas/        # schémas Pydantic
├── routers/        # routes API
├── services/       # logique métier et client REST
├── tests/          # tests Pytest
├── database.py
├── requirements.txt
└── Dockerfile
```
