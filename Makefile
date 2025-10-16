CODE_PATHS := app tests
POETRY := poetry -C services/ai

DC_FILEPATH := docker/docker-compose.yml
DC := docker compose -f $(DC_FILEPATH)

.PHONY: help build rebuild start stop restart ps logs shell-web shell-ai clean format lint test dev-start dev-stop dev-logs

help:
	@echo "Adverse Media Screening App commands"
	@echo ""
	@echo "Docker (Production):"
	@echo "  make build      Build all services"
	@echo "  make rebuild    Rebuild without cache"
	@echo "  make start      Start all services (detached)"
	@echo "  make stop       Stop all services"
	@echo "  make restart    Restart all services"
	@echo "  make ps         Show service status"
	@echo "  make logs       Show logs for all services"
	@echo "  make shell-web  Open shell in web service"
	@echo "  make shell-ai   Open shell in ai service"
	@echo ""
	@echo "Docker (Development with hot reload):"
	@echo "  make dev-start  Start services in dev mode"
	@echo "  make dev-stop   Stop dev services"
	@echo "  make dev-logs   Show dev logs"
	@echo ""
	@echo "Python (services/ai):"
	@echo "  make format     Format code with black and isort"
	@echo "  make lint       Lint code with flake8"
	@echo "  make test       Run tests"

# Docker operations
build:
	$(DC) build

build-ai:
	$(DC) build ai

build-web:
	$(DC) build web

rebuild:
	$(DC) build --no-cache

rebuild-ai:
	$(DC) build --no-cache ai

rebuild-web:
	$(DC) build --no-cache web

start:
	$(DC) up -d ai web

start-ai:
	$(DC) up -d ai

stop:
	$(DC) down

restart:
	$(DC) restart

ps:
	$(DC) ps

logs:
	$(DC) logs -f ai web

shell-web:
	$(DC) exec web sh

shell-ai:
	$(DC) exec ai sh

clean:       
	$(DC) down --rmi local -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Development mode with hot reload
dev-start:
	$(DC) up -d ai web-dev

dev-stop:
	$(DC) stop web-dev
	$(DC) rm -f web-dev

dev-logs:
	$(DC) logs -f ai web-dev

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