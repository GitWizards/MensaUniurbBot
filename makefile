.PHONY: start stop restart build shell logs

start:
	docker compose up -d

stop:
	docker compose down -v

restart: stop start

build: stop
	docker compose build

shell:
	docker compose run --rm bot bash

logs:
	docker compose logs --tail=100 -f
