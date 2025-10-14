CODE_PATHS := app tests
POETRY := poetry -C services/ai

DC_FILEPATH := docker/docker-compose.yml
DC := docker compose -f $(DC_FILEPATH)

.PHONY: help build rebuild start stop restart ps logs shell-web shell-ai clean format lint test

help:
	@echo "Adverse Media Screening App commands"
	@echo ""
	@echo "Docker:"
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
	@echo "Python (services/ai):"
	@echo "  make format     Format code with black and isort"
	@echo "  make lint       Lint code with flake8"
	@echo "  make test       Run tests"

# Docker operations
build:
	$(DC) build

rebuild:
	$(DC) build --no-cache

start:
	$(DC) up -d

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