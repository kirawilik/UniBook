# Contrat des événements RabbitMQ

Ce document est l'accord entre le **Reservation Service** (producteur, Membre B) et le **Notification Service** (consommateur, Membre A). Toute modification doit être validée par les deux membres.

## 1. Connexion

```
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
```

Dans Docker Compose (Epic 6), `localhost` sera remplacé par le nom du conteneur : `amqp://guest:guest@rabbitmq:5672/`.

## 2. Exchange, queue et routing keys

| Élément | Valeur |
|---|---|
| Exchange | `reservation_events` (type `direct`, durable) |
| Queue | `notification_queue` (durable) |
| Routing key de création | `reservation.created` |
| Routing key d'annulation | `reservation.cancelled` |

La queue est liée à l'exchange avec les deux routing keys.

**Qui déclare quoi ?** Les deux services déclarent l'exchange, la queue et les bindings au démarrage. La déclaration est idempotente : elle ne fait rien si l'élément existe déjà avec les mêmes paramètres. L'ordre de démarrage des services n'a donc pas d'importance.

## 3. Message `ReservationCreated`

Routing key : `reservation.created`

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

## 4. Message `ReservationCancelled`

Routing key : `reservation.cancelled`

```json
{
  "event_type": "ReservationCancelled",
  "reservation_id": 12,
  "user_id": 1,
  "resource_id": 1,
  "date": "2026-12-01",
  "start_time": "09:00:00",
  "end_time": "11:00:00",
  "cancelled_at": "2026-11-24T08:30:00"
}
```

## 5. Description des champs

| Champ | Type | Obligatoire | Description |
|---|---|---|---|
| `event_type` | string | oui | `ReservationCreated` ou `ReservationCancelled` |
| `reservation_id` | integer | oui | Identifiant de la réservation |
| `user_id` | integer | oui | Identifiant de l'utilisateur (User & Resource Service) |
| `resource_id` | integer | oui | Identifiant de la ressource (User & Resource Service) |
| `date` | string | oui | Format ISO `YYYY-MM-DD` |
| `start_time` | string | oui | Format `HH:MM:SS` |
| `end_time` | string | oui | Format `HH:MM:SS` |
| `created_at` | string | oui pour Created | Date ISO 8601 de création |
| `cancelled_at` | string | oui pour Cancelled | Date ISO 8601 d'annulation |

Le message ne contient **ni nom ni email** de l'utilisateur. Si le Notification Service a besoin de ces informations, il appelle `GET /users/{user_id}` sur le User & Resource Service.

## 6. Règles

- Format JSON, encodage UTF-8.
- Exchange et queue **durables**, messages **persistants** (`delivery_mode = 2`).
- Le consommateur envoie un `ack` uniquement **après** avoir enregistré la notification.
- Un message invalide (JSON illisible ou champ obligatoire manquant) est rejeté sans remise dans la queue (`nack`, `requeue=false`) et journalisé.
- Le producteur ne bloque pas la réponse HTTP si RabbitMQ est indisponible : la réservation est créée et l'erreur de publication est journalisée.
- Les champs existants ne sont ni renommés ni supprimés. Un nouveau champ optionnel peut être ajouté sans casser le consommateur.

## 7. Test manuel sans code

Dans l'interface `http://localhost:15672` (login `guest` / `guest`) :

1. **Exchanges > Add a new exchange** : `reservation_events`, type `direct`, durable.
2. **Queues > Add a new queue** : `notification_queue`, durable.
3. Sur l'exchange, **Bindings** : vers `notification_queue` avec la routing key `reservation.created`.
4. **Publish message** sur l'exchange avec la routing key `reservation.created` et le JSON de la section 3.
5. Vérifier dans la queue que **Ready = 1**, puis lire le message avec **Get messages**.

## 8. Répartition (Epic 4)

| Tâche | Responsable |
|---|---|
| Installation de RabbitMQ | Membre A |
| Définition de l'événement `ReservationCreated` (ce document) | Membre A |
| Publication depuis le Reservation Service | Membre B |
| Initialisation du Notification Service | Membre A |
| Consommateur RabbitMQ | Membre B |
| Enregistrement des notifications | Membre A |
| Test de communication asynchrone | Membre B |