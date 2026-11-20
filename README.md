# User & Resource Service

Microservice du projet **UniBook** (plateforme distribuée de réservation des ressources universitaires).
Il gère les **utilisateurs** et les **ressources** (salles, laboratoires, équipements).

- **Backend** : Python + FastAPI
- **Base de données** : Microsoft SQL Server (base `UniBook_UsersResources`)
- **ORM** : SQLAlchemy (pilote `pyodbc`)
- **Tests** : Pytest (SQLite en mémoire, aucun SQL Server nécessaire)
- **Port par défaut** : `8001`

---

## 1. Structure du projet

```
user-resource-service/
├── app/
│   ├── models/        # Tables SQLAlchemy (User, Resource)
│   ├── schemas/       # Validation Pydantic (Create / Update / Out)
│   ├── services/      # Logique métier + accès à la base + bcrypt
│   ├── routers/       # Routes HTTP (/users, /resources)
│   ├── database.py    # Connexion SQL Server, fonction get_db
│   └── main.py        # Application FastAPI
├── tests/
│   ├── conftest.py    # SQLite en mémoire + client de test
│   ├── test_smoke.py
│   ├── test_resources.py
│   └── test_users.py
├── database/init.sql  # Script de création de la base et des tables
├── pytest.ini
├── requirements.txt
├── .env.example
└── Dockerfile
```

**Architecture en couches** : `routers` reçoivent la requête HTTP, `services` appliquent la logique métier, `models` accèdent à SQL Server, `schemas` valident les données échangées.

---

## 2. Prérequis

- Python 3.11 ou plus récent
- Git
- *(Uniquement pour lancer l'API, pas pour les tests)* SQL Server + SSMS + **ODBC Driver 18 for SQL Server**

---

## 3. Installation

```powershell
git clone <url-du-depot>
cd UniBook/user-resource-service

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
```

---

## 4. Tester rapidement (sans SQL Server)

C'est le moyen le plus simple de vérifier que le service est correct sur votre machine.

```powershell
pytest -v
```

Résultat attendu : **34 passed**.

Les tests utilisent une base **SQLite en mémoire** (créée puis supprimée à chaque test). Ils ne touchent **jamais** la vraie base SQL Server et n'ont besoin ni de `.env`, ni de Docker.

---

## 5. Lancer le service (avec SQL Server)

### 5.1 Créer la base et les tables

Ouvrir `database/init.sql` dans SSMS puis cliquer sur **Execute** (F5).
Le script est rejouable sans erreur (il vérifie l'existence avant de créer).

### 5.2 Configurer l'environnement

Copier `.env.example` vers `.env` et le remplir :

```env
DB_SERVER=localhost
DB_PORT=1433
DB_NAME=UniBook_UsersResources
DB_USER=sa
DB_PASSWORD=votre_mot_de_passe
DB_DRIVER=ODBC Driver 18 for SQL Server
```

> Le fichier `.env` contient un mot de passe : il est ignoré par Git et ne doit **jamais** être envoyé sur GitHub.

Si l'authentification `sa` n'est pas activée, utiliser l'authentification Windows (voir la section Dépannage).

### 5.3 Démarrer l'API

```powershell
uvicorn app.main:app --reload --port 8001
```

Si un autre conteneur ou une autre machine doit appeler le service, ajouter `--host 0.0.0.0`.

### 5.4 Vérifier

| URL | Contenu |
|---|---|
| http://localhost:8001/docs | Interface **Swagger** (tester les routes avec le bouton *Try it out*) |
| http://localhost:8001/health/db | Vérifie la connexion à SQL Server |

---

## 6. Endpoints

### Ressources

| Méthode | Route | Description |
|---|---|---|
| POST | `/resources` | Créer une ressource |
| GET | `/resources` | Lister (filtres : `type`, `only_active`, `skip`, `limit`) |
| GET | `/resources/{id}` | Détail d'une ressource |
| PUT | `/resources/{id}` | Modifier (partiellement) |
| DELETE | `/resources/{id}` | Désactiver (suppression logique) |

### Utilisateurs

| Méthode | Route | Description |
|---|---|---|
| POST | `/users` | Créer un utilisateur |
| GET | `/users` | Lister (`skip`, `limit`) |
| GET | `/users/{id}` | Détail d'un utilisateur |
| PUT | `/users/{id}` | Modifier (partiellement) |
| DELETE | `/users/{id}` | Désactiver (suppression logique) |

### Codes de réponse

| Code | Signification |
|---|---|
| 200 / 201 / 204 | Succès / créé / succès sans contenu |
| 404 | Ressource ou utilisateur introuvable |
| 409 | Email déjà utilisé |
| 422 | Données invalides (rôle, type, capacité négative, email mal formé...) |

### Valeurs autorisées

- `role` : `Student`, `Teacher`, `Admin`
- `type` (ressource) : `Classroom`, `Laboratory`, `Equipment`

---

## 7. Exemples de requêtes

**Créer une ressource**

```bash
curl -X POST http://localhost:8001/resources \
  -H "Content-Type: application/json" \
  -d '{"name":"Salle A101","type":"Classroom","description":"Salle avec projecteur","location":"Bâtiment A, 1er étage","capacity":40}'
```

**Créer un utilisateur**

```bash
curl -X POST http://localhost:8001/users \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Ahmed Benali","email":"ahmed@univ.dz","password":"secret123","role":"Student"}'
```

**Réponse (le mot de passe n'apparaît jamais)**

```json
{
  "id": 1,
  "full_name": "Ahmed Benali",
  "email": "ahmed@univ.dz",
  "role": "Student",
  "is_active": true,
  "created_at": "2026-11-16T23:41:24.135175"
}
```

---

## 8. Utilisation par le Reservation Service (Membre B)

Chaque microservice possède **sa propre base de données**. Le Reservation Service **ne lit jamais** les tables `Users` et `Resources` : il interroge ce service par **REST**.

```
Reservation Service  --GET /resources/5-->  User & Resource Service  -->  SQL Server
```

Pour valider une réservation :

| Réponse de `GET /resources/{id}` | Action côté Reservation Service |
|---|---|
| 200 et `is_active = true` | Continuer (vérifier les conflits horaires) |
| 200 et `is_active = false` | Refuser : ressource non disponible |
| 404 | Refuser : ressource introuvable |
| Pas de réponse (service arrêté) | Répondre 503 : service indisponible |

Même principe avec `GET /users/{id}`. La Reservation Service stocke seulement `user_id` et `resource_id` (des nombres), sans clé étrangère vers cette base.

**Adresse du service** (toujours dans une variable d'environnement, jamais en dur) :

| Contexte | Valeur de `USER_RESOURCE_SERVICE_URL` |
|---|---|
| Les deux services en local | `http://localhost:8001` |
| Reservation Service dans Docker, ce service sur l'hôte | `http://host.docker.internal:8001` |
| Docker Compose | `http://user-resource-service:8001` |

**Tester sans lancer ce service** : dans les tests du Reservation Service, remplacer l'appel REST par un mock (réponse simulée) pour couvrir les cas 200, 404 et 503.

---

## 9. Choix techniques à retenir

- **Suppression logique** : `DELETE` met `is_active = false` au lieu d'effacer la ligne, pour conserver l'historique des réservations.
- **Mots de passe** : jamais stockés en clair, hachés avec **bcrypt** (colonne `password_hash`).
- **Schémas distincts** `Create` / `Update` / `Out` : contrôle de ce qui entre et de ce qui sort.
- **Isolation des tests** : `dependency_overrides` de FastAPI remplace la base réelle par SQLite en mémoire.
- **Limite actuelle** : pas d'authentification ni de contrôle d'accès par rôle (par exemple, réserver la gestion des ressources à l'Admin). Évolution prévue via JWT.

---

## 10. Dépannage

| Erreur | Cause probable | Solution |
|---|---|---|
| `No module named 'app'` | Commande lancée depuis le mauvais dossier | Se placer dans `user-resource-service/` |
| `Can't open lib 'ODBC Driver 18...'` | Pilote ODBC absent ou autre version | Installer le pilote, ou adapter `DB_DRIVER` (ex. 17) |
| `Login failed for user 'sa'` | Mauvais mot de passe, compte `sa` désactivé, mode mixte non activé | Vérifier dans SSMS, redémarrer le service SQL Server |
| `Cannot open database` | Base absente ou `DB_NAME` incorrect | Exécuter `database/init.sql` |
| Connexion refusée / timeout | TCP/IP désactivé ou mauvais port | Activer TCP/IP dans SQL Server Configuration Manager |
| `ModuleNotFoundError` au lancement | Environnement virtuel non activé | `venv\Scripts\activate` puis `pip install -r requirements.txt` |

**Authentification Windows** (sans mot de passe) : remplacer la construction de l'URL dans `app/database.py` par

```python
DATABASE_URL = (
    f"mssql+pyodbc://@{DB_SERVER}/{DB_NAME}"
    f"?driver={quote_plus(DB_DRIVER)}"
    f"&trusted_connection=yes&TrustServerCertificate=yes"
)
```

---
