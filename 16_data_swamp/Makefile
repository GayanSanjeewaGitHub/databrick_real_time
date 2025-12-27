# Makefile for common tasks

.PHONY: help setup start stop restart clean data run-swamp run-governed run-propensity

help:
	@echo "Available commands:"
	@echo "  make setup          - Set up Python environment and dependencies"
	@echo "  make start          - Start all Docker services"
	@echo "  make stop           - Stop all Docker services"
	@echo "  make restart        - Restart all Docker services"
	@echo "  make clean          - Remove all data and containers"
	@echo "  make data           - Generate synthetic data"
	@echo "  make run-swamp      - Run Data Swamp demo (No HMS)"
	@echo "  make run-governed   - Run Governed pipeline (With HMS)"
	@echo "  make run-propensity - Run full propensity model"

setup:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	cp .env.example .env
	mkdir -p data/raw/transactions data/raw/weblogs data/processed data/swamp

start:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 30

stop:
	docker-compose down

restart:
	docker-compose restart

clean:
	docker-compose down -v
	rm -rf data/raw/* data/processed/* data/swamp/*
	rm -rf venv __pycache__ src/__pycache__

data:
	. venv/bin/activate && python src/data_generator.py

run-swamp:
	. venv/bin/activate && python src/pipeline_no_hms.py

run-governed:
	. venv/bin/activate && python src/pipeline_with_hms.py

run-propensity:
	. venv/bin/activate && python src/propensity_model.py
