# Adverse Media Screening - Makefile
# Usage: make <command> [SERVICE=ai|web|all] [ENV=prod|dev]

# Configuration
CODE_PATHS := app tests
POETRY := poetry -C services/ai
DC_FILEPATH := docker/docker-compose.yml
DC := docker compose -f $(DC_FILEPATH)

# Variables for flexible targeting
SERVICE ?= all
ENV ?= prod

# Helper variables for service selection
ifeq ($(SERVICE),all)
	DC_SERVICES = ai web
	DC_BUILD_SERVICES = ai web
else
	DC_SERVICES = $(SERVICE)
	DC_BUILD_SERVICES = $(SERVICE)
endif

# Helper variables for environment selection
ifeq ($(ENV),dev)
	WEB_SERVICE = web-dev
else
	WEB_SERVICE = web
endif

# Services to use based on environment
ifeq ($(SERVICE),all)
	DC_ENV_SERVICES = ai $(WEB_SERVICE)
else ifeq ($(SERVICE),web)
	DC_ENV_SERVICES = $(WEB_SERVICE)
else
	DC_ENV_SERVICES = $(SERVICE)
endif

# Log services (for logs command)
ifeq ($(SERVICE),all)
	LOG_SERVICES = ai web
else ifeq ($(SERVICE),web)
	ifeq ($(ENV),dev)
		LOG_SERVICES = web-dev
	else
		LOG_SERVICES = web
	endif
else
	LOG_SERVICES = $(SERVICE)
endif

.PHONY: help setup build rebuild start stop restart ps logs shell clean format lint test

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Adverse Media Screening - Make Commands"
	@echo ""
	@echo "Usage: make <command> [SERVICE=ai|web|all] [ENV=prod|dev]"
	@echo ""
	@echo "Setup:"
	@echo "  make setup                    Run initial setup (check dependencies, create env files)"
	@echo ""
	@echo "Docker Operations:"
	@echo "  make build [SERVICE=all]      Build services"
	@echo "  make rebuild [SERVICE=all]    Rebuild services without cache"
	@echo "  make start [ENV=prod] [...]   Start services (detached mode)"
	@echo "  make stop [SERVICE=all]       Stop services"
	@echo "  make restart [SERVICE=all]    Restart services"
	@echo "  make ps                       Show service status"
	@echo "  make logs [SERVICE=all] [ENV] Show logs (follow mode)"
	@echo "  make shell SERVICE=<svc>      Open shell in service (SERVICE required)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean                    Stop and remove all containers, images, and volumes"
	@echo ""
	@echo "Python (AI service):"
	@echo "  make format                   Format code with black and isort"
	@echo "  make lint                     Lint code with flake8"
	@echo "  make test                     Run tests with pytest"
	@echo ""
	@echo "Examples:"
	@echo "  make build SERVICE=ai         Build AI service only"
	@echo "  make start ENV=dev            Start all services in development mode"
	@echo "  make start ENV=dev SERVICE=web  Start only web in dev mode"
	@echo "  make logs SERVICE=ai          Show AI service logs only"
	@echo "  make shell SERVICE=web        Open shell in web container"

# Setup
setup:
	@bash scripts/setup.sh

# Docker operations
build:
	$(DC) build $(DC_BUILD_SERVICES)

rebuild:
	$(DC) build --no-cache $(DC_BUILD_SERVICES)

start:
	$(DC) up -d $(DC_ENV_SERVICES)

stop:
	$(DC) stop $(DC_SERVICES)

restart:
	$(DC) restart $(DC_SERVICES)

ps:
	$(DC) ps

logs:
	$(DC) logs -f $(LOG_SERVICES)

shell:
ifeq ($(SERVICE),all)
	$(error SERVICE is required. Usage: make shell SERVICE=ai|web)
endif
	$(DC) exec $(SERVICE) sh

clean:
	$(DC) down --rmi local -v
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Python operations (AI service)
format:
	@echo "Formatting code..."
	$(POETRY) run black $(CODE_PATHS)
	$(POETRY) run isort $(CODE_PATHS)

lint:
	@echo "Linting code..."
	$(POETRY) run flake8 $(CODE_PATHS)

test:
	@echo "Running tests..."
	$(POETRY) run pytest
