.PHONY: start_with_fixtures only_start stop

start_with_fixtures:
	@echo "Starting DB..."
	docker compose up --build -d db
	@echo "Waiting for DB to initialize..."
	@sleep 5
	@echo "Running load_fixtures (migrations + fixtures)..."
	docker compose run --rm load_fixtures
	@echo "Starting app..."
	docker compose up --build -d app
	@echo "Done."

only_start:
	@echo "Starting DB and app..."
	docker compose up --build -d db app
	@echo "Done."

stop:
	@echo "Stopping and removing containers and volumes..."
	docker compose down -v
	@echo "Stopped."
