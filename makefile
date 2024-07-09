.PHONY: start stop restart shell logs
dc := docker compose

start:
	$(dc) up -d
stop:
	$(dc) down -v
restart: stop
	$(dc) up -d
shell:
	$(dc) run --rm bot bash
logs:
	$(dc) logs --tail=100 -f
