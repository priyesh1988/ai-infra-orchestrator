.PHONY: up down logs test fmt

up:
	docker compose up --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

test:
	python -m compileall app

fmt:
	@echo "Add ruff/black if you want formatting. (kept minimal)"
