# Notification Service

Ce service reçoit les événements de réservation (via RabbitMQ) et enregistre une **notification** dans sa base de données.

**Port** : 8003 | **Base** : `UniBook_Notifications` | **Langage** : Python + FastAPI

---

## 1. Comment ça marche (en 4 lignes)

```
Reservation Service  --message-->  RabbitMQ  --message-->  consumer.py  -->  base de données
   (producteur)                    (queue)                (À ÉCRIRE)
```

1. Le Reservation Service publie un message JSON quand une réservation est créée ou annulée.
2. RabbitMQ garde le message dans la queue `notification_queue`.
3. **Le consumer lit la queue** (c'est la partie à écrire).
4. Le consumer appelle `process_event(...)` qui enregistre la notification.

---

## 2. Où écrire le code

Tout se passe dans `app/`. Les fichiers marqués **déjà fait** ne sont pas à modifier.

```
notification-service/
├── app/
│   ├── consumer.py                      ← À ÉCRIRE (Membre B)
│   ├── main.py                          ← 1 ligne à ajouter (voir section 5)
│   ├── schemas/event.py                 ← déjà fait : valide le message
│   ├── services/notification_service.py ← déjà fait : contient process_event
│   ├── models/, routers/, database.py   ← déjà fait
│   └── ...
└── tests/
    ├── test_notifications.py            ← déjà fait
    └── test_consumer.py                 ← À ÉCRIRE (Membre B)
```

**À écrire : `app/consumer.py` et `tests/test_consumer.py`.**

---

## 3. Ce que le consumer doit faire

| Étape | Action |
|---|---|
| 1 | Se connecter à RabbitMQ (`RABBITMQ_URL` dans `.env`) |
| 2 | Déclarer l'exchange, la queue et les bindings (voir le contrat) |
| 3 | Lire les messages de `notification_queue` |
| 4 | Transformer le JSON en `ReservationEvent` (ça valide le message) |
| 5 | Ouvrir une session de base, appeler `process_event(db, event)`, fermer la session |
| 6 | Envoyer `ack` **seulement après** l'enregistrement |
| 7 | Si le message est invalide : `nack` avec `requeue=False` et afficher l'erreur |

---

## 4. Point de départ (à copier dans `app/consumer.py`)

Ce code fonctionne déjà. Il sert de base : à toi de l'adapter (par exemple le lancer dans un thread au démarrage du service).

```python
import json
import pika

from app.database import SessionLocal
from app.schemas import ReservationEvent
from app.services.notification_service import process_event

QUEUE = "notification_queue"


def on_message(ch, method, properties, body):
    # 1. Valider le message
    try:
        event = ReservationEvent(**json.loads(body))
    except Exception as e:
        print("Message invalide:", e)
        ch.basic_nack(method.delivery_tag, requeue=False)
        return

    # 2. Enregistrer la notification
    db = SessionLocal()
    try:
        process_event(db, event)
        ch.basic_ack(method.delivery_tag)     # ack APRÈS l'enregistrement
    finally:
        db.close()


def start_consumer(rabbitmq_url: str):
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE, durable=True)
    channel.basic_consume(queue=QUEUE, on_message_callback=on_message)
    channel.start_consuming()
```

Un exemple identique (`scripts/try_consumer.py`) a été utilisé pour tester : il a bien enregistré une notification.

**Ce que tu dois améliorer** : déclarer l'exchange `reservation_events` et les bindings du contrat, lire `RABBITMQ_URL` dans `.env`, et lancer `start_consumer` en arrière-plan.

---

## 5. Lancer le consumer avec le service

Dans `app/main.py`, un emplacement est déjà prévu dans `lifespan` :

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # consumer: Membre B ajoute ici start_consumer()
    yield
```

`start_consumer` bloque (il attend les messages en boucle). Il faut donc le lancer dans un **thread**, sinon l'API ne démarre pas :

```python
import threading
threading.Thread(target=start_consumer, args=(RABBITMQ_URL,), daemon=True).start()
```

---

## 6. Le message à recevoir (résumé du contrat)

Le contrat complet est dans `docs/contrat-evenements.md`. Résumé :

| Élément | Valeur |
|---|---|
| Exchange | `reservation_events` (direct, durable) |
| Queue | `notification_queue` (durable) |
| Routing keys | `reservation.created`, `reservation.cancelled` |

Exemple de message :

```json
{
  "event_type": "ReservationCreated",
  "reservation_id": 12,
  "user_id": 1,
  "resource_id": 1,
  "date": "2026-12-01",
  "start_time": "09:00:00",
  "end_time": "11:00:00",
  "created_at": "2026-11-23T10:00:00"
}
```

`event_type` peut aussi valoir `ReservationCancelled`. La classe `ReservationEvent` vérifie déjà les champs : un message incorrect lève une erreur, c'est ce qui déclenche le `nack`.

---

## 7. Installation et lancement

```powershell
cd notification-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Crée un fichier `.env` à partir de `.env.example` et remplis-le (mot de passe SQL Server). Puis crée la base : ouvre `database/init.sql` dans SSMS et exécute-le.

```powershell
uvicorn app.main:app --reload --port 8003
```

- Documentation Swagger : http://localhost:8003/docs
- Test de la base : http://localhost:8003/health/db

Il faut aussi que **RabbitMQ tourne** (Docker Desktop lancé) :

```powershell
docker start rabbitmq
```

Interface RabbitMQ : http://localhost:15672 (login `guest` / `guest`).

---

## 8. Tester son consumer à la main

1. Lance le service (ou le consumer seul).
2. Dans http://localhost:15672 : **Queues > notification_queue > Publish message**.
3. Colle le JSON de la section 6 et clique sur **Publish message**.
4. Vérifie la notification : http://localhost:8003/docs puis `GET /notifications`.

Cas à essayer :

| Message envoyé | Résultat attendu |
|---|---|
| Le même JSON deux fois | Une seule notification (protection contre les doublons) |
| Avec `"event_type": "ReservationCancelled"` | Une notification « annulée » |
| `{"hello": "world"}` | « Message invalide » affiché, le message est rejeté |

---

## 9. Tests unitaires

```powershell
pytest -v
```

Les tests utilisent SQLite en mémoire : ni SQL Server ni RabbitMQ ne sont nécessaires. Pour `test_consumer.py`, ne teste pas avec un vrai RabbitMQ : appelle directement `on_message` avec un faux canal (par exemple `unittest.mock.MagicMock()`) et vérifie :

- message valide : `basic_ack` est appelé et une notification est enregistrée ;
- message invalide : `basic_nack` est appelé avec `requeue=False`.

---

## 10. Règles du contrat à respecter

- `ack` seulement après l'enregistrement en base.
- Message invalide : `nack` sans remise dans la queue, avec un message d'erreur affiché.
- Ne pas renommer les champs du message.
- Pas besoin d'écrire dans la base à la main : tout passe par `process_event`.

---

## 11. Problèmes courants

| Problème | Solution |
|---|---|
| `No module named 'app'` | Lance les commandes depuis `notification-service/` |
| `No module named 'pika'` | Active le venv et fais `pip install -r requirements.txt` |
| `AMQPConnectionError` | RabbitMQ est arrêté : `docker start rabbitmq` |
| `Invalid object name 'Notifications'` | Exécute `database/init.sql` dans SSMS |
| L'API ne démarre pas après l'ajout du consumer | `start_consumer` doit tourner dans un thread |
| Avertissement `BlockingConnection is deprecated` | Sans gravité. Pour l'éviter, fixer `pika<2` dans `requirements.txt` |