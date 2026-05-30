# ============================================================
# WAY Backend
# ============================================================

PYTHON=python3.12
PIP=pip
MANAGE=$(PYTHON) manage.py

APP=config

.DEFAULT_GOAL := help

# ============================================================
# HELP
# ============================================================

help:
	@echo ""
	@echo "WAY backend commands"
	@echo ""
	@echo " install          install project"
	@echo " dev              install dev deps"
	@echo " test             run tests"
	@echo " cov              run coverage"
	@echo " lint             lint"
	@echo " format           format code"
	@echo " migrate          migrate database"
	@echo " makemigrations   create migrations"
	@echo " superuser        create admin"
	@echo " run              django dev server"
	@echo " daphne           websocket server"
	@echo " shell            django shell"
	@echo " worker           celery worker"
	@echo " beat             celery beat"
	@echo " flower           flower monitor"
	@echo " redis            start redis"
	@echo " docker-up        start containers"
	@echo " docker-down      stop containers"
	@echo " kafka-topics     list kafka topics"
	@echo " collectstatic    collect static"
	@echo " clean            cleanup"
	@echo ""

# ============================================================
# INSTALL
# ============================================================

install:
	$(PIP) install -e .

dev:
	$(PIP) install -e ".[dev,test]"

prod:
	$(PIP) install ".[prod]"

upgrade-pip:
	$(PYTHON) -m pip install --upgrade pip

# ============================================================
# DJANGO
# ============================================================

run:
	$(MANAGE) runserver

daphne:
	daphne config.asgi:application

shell:
	$(MANAGE) shell

migrate:
	$(MANAGE) migrate

makemigrations:
	$(MANAGE) makemigrations

superuser:
	$(MANAGE) createsuperuser

collectstatic:
	$(MANAGE) collectstatic --noinput

check:
	$(MANAGE) check

# ============================================================
# TESTS
# ============================================================

test:
	pytest

cov:
	pytest --cov

test-wallet:
	pytest tests/wallet

test-skills:
	pytest tests/skills

# ============================================================
# LINT / FORMAT
# ============================================================

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy .

precommit:
	pre-commit run --all-files

# ============================================================
# CELERY
# ============================================================

worker:
	celery -A $(APP) worker -l info

beat:
	celery -A $(APP) beat -l info

flower:
	flower

# ============================================================
# REDIS
# ============================================================

redis:
	redis-server

# ============================================================
# KAFKA
# ============================================================

kafka-topics:
	kafka-topics --bootstrap-server localhost:9092 --list

# ============================================================
# MINIO
# ============================================================

minio:
	docker run \
		-p 9000:9000 \
		-p 9001:9001 \
		-e MINIO_ROOT_USER=minio \
		-e MINIO_ROOT_PASSWORD=minio123 \
		minio/minio server /data --console-address ":9001"

# ============================================================
# DOCKER
# ============================================================

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

restart:
	docker compose down
	docker compose up -d

# ============================================================
# DB
# ============================================================

db-reset:
	dropdb way || true
	createdb way
	$(MANAGE) migrate

flush:
	$(MANAGE) flush

# ============================================================
# OBSERVABILITY
# ============================================================

metrics:
	curl http://localhost:8000/metrics/

# ============================================================
# CLEAN
# ============================================================

clean:
	find . -name "__pycache__" -type d -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	find . -name ".ruff_cache" -type d -exec rm -rf {} +
	rm -rf build
	rm -rf dist

# ============================================================
# FULL DEV START
# ============================================================

start:
	make docker-up
	make migrate
	make run

# ============================================================
# FULL BACKGROUND
# ============================================================

background:
	make worker &
	make beat &
	make run