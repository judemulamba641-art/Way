# WAY Backend

Backend principal de la plateforme **WAY**.

WAY est une infrastructure distribuée permettant :

- gestion d’identités et authentification
- wallet / crédits
- installation et exécution de skills
- marketplace
- événements temps réel
- orchestration asynchrone
- observabilité
- stockage distribué

Architecture basée sur :

- Django
- Django REST Framework
- Django Channels
- Celery
- PostgreSQL
- Redis
- Kafka
- MinIO
- Prometheus
- OpenTelemetry
- Sentry

---

# Table des matières

- Présentation
- Stack technique
- Architecture
- Installation locale
- Variables d’environnement
- Base de données
- Redis
- Kafka
- MinIO
- Lancement
- Workers Celery
- WebSockets
- Structure du projet
- Tests
- Observabilité
- Déploiement Docker
- Sécurité
- API principales
- Event Bus
- Roadmap

---

# Présentation

WAY fournit :

## Authentification

- JWT
- refresh token
- permissions
- rôles
- révocation

## Wallet

- crédits
- transferts
- historique
- transactions

## Skills

- installation
- désinstallation
- manifests
- providers
- exécution

## Marketplace

- catalogue
- recherche
- pricing

## Temps réel

- websocket notifications
- wallet updates
- état skills

## Infrastructure

- object storage
- event streaming
- monitoring
- tracing

---

# Stack technique

## Backend

- Python 3.12+
- Django 5
- Django REST Framework

## Realtime

- Django Channels
- Daphne
- Redis

## Async

- Celery
- Redis broker

## DB

- PostgreSQL

## Event streaming

- Kafka

## Storage

- MinIO
- boto3

## Monitoring

- Prometheus
- OpenTelemetry
- Sentry

---

# Architecture

```txt
Client
│
├── REST API (Django DRF)
│
├── WebSocket (Channels)
│
├── PostgreSQL
│
├── Redis
│
├── Celery Workers
│
├── Kafka Event Bus
│
└── MinIO Object Storage
```

---

# Installation locale

## 1. Clone

```bash
git clone https://github.com/your-org/way-backend.git
cd way-backend
```

---

## 2. Environnement virtuel

Linux / macOS

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

## 3. Installer dépendances

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

# Variables d’environnement

Créer :

```bash
.env
```

Exemple :

```env
DEBUG=True

SECRET_KEY=change-me

ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgresql://postgres:postgres@localhost:5432/way

REDIS_URL=redis://localhost:6379/0

CELERY_BROKER_URL=redis://localhost:6379/1

CELERY_RESULT_BACKEND=redis://localhost:6379/2

KAFKA_BOOTSTRAP_SERVERS=localhost:9092

MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio123
MINIO_BUCKET=way

JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=7

SENTRY_DSN=

PROMETHEUS_ENABLED=True
```

---

# Base de données

Créer :

```bash
createdb way
```

Puis :

```bash
python manage.py migrate
```

Créer admin :

```bash
python manage.py createsuperuser
```

---

# Redis

Lancer :

```bash
redis-server
```

---

# Kafka

Exemple docker :

```bash
docker compose up kafka
```

Topic principaux :

- user_created
- credits_sent
- credits_received
- skill_installed
- skill_removed
- payment_success
- notification_created

---

# MinIO

Docker :

```bash
docker run \
  -p 9000:9000 \
  -p 9001:9001 \
  minio/minio server /data --console-address ":9001"
```

Créer bucket :

```txt
way
```

---

# Lancement

Serveur principal :

```bash
python manage.py runserver
```

ou :

```bash
daphne config.asgi:application
```

---

# Celery

Worker :

```bash
celery -A config worker -l info
```

Beat :

```bash
celery -A config beat -l info
```

Flower :

```bash
flower
```

---

# WebSockets

Endpoint :

```txt
/ws/
```

Exemples :

## wallet

```txt
/ws/wallet/
```

## notifications

```txt
/ws/notifications/
```

## skills

```txt
/ws/skills/
```

---

# Structure projet

```txt
way-backend/

config/
├── settings/
├── urls.py
├── asgi.py
├── wsgi.py

apps/

├── accounts/
├── auth/
├── wallet/
├── skills/
├── marketplace/
├── notifications/
├── analytics/
├── billing/
├── infrastructure/

services/

├── kafka/
├── storage/
├── observability/
├── security/

tests/

requirements.txt

docker-compose.yml

README.md
```

---

# Tests

Tout :

```bash
pytest
```

Module :

```bash
pytest tests/wallet
```

Coverage :

```bash
pytest --cov
```

---

# Observabilité

## Prometheus

Endpoint :

```txt
/metrics/
```

---

## OpenTelemetry

Trace :

- API
- Celery
- Kafka

---

## Sentry

Configurer :

```env
SENTRY_DSN=...
```

---

# Déploiement Docker

Build :

```bash
docker compose build
```

Run :

```bash
docker compose up
```

Services :

- backend
- postgres
- redis
- kafka
- minio
- celery
- flower

---

# Sécurité

Implémenté :

- JWT
- refresh token
- token revoke
- password hashing Argon2
- CORS
- CSRF
- permissions
- audit logs
- signature validation

---

# API principales

## Auth

```txt
/api/auth/login/
/api/auth/refresh/
/api/auth/logout/
```

---

## Wallet

```txt
/api/wallet/
```

Actions :

- balance
- transfer
- history

---

## Skills

```txt
/api/skills/
```

Actions :

- install
- remove
- list
- execute

---

## Marketplace

```txt
/api/marketplace/
```

Actions :

- catalogue
- pricing
- search

---

## Notifications

```txt
/api/notifications/
```

---

# Event Bus

Kafka events :

```json
{
  "event": "skill_installed",
  "user_id": "...",
  "skill_id": "...",
  "timestamp": "..."
}
```

---

# Roadmap

## Phase 1

- auth
- wallet
- notifications

## Phase 2

- marketplace
- skills runtime

## Phase 3

- federation
- analytics

## Phase 4

- autoscaling
- distributed workers

---

# Maintainers

WAY backend team

---

# Licence

Private / Proprietary