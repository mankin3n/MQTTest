# Makefile for SmartHome IoT Test Framework

.PHONY: help setup install certs services start stop status test smoke api mqtt security integration clean lint format

help:
	@echo "SmartHome IoT Test Framework - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make setup       - Full environment setup (install + certs + services)"
	@echo "  make install     - Install Python dependencies"
	@echo "  make certs       - Generate test certificates"
	@echo ""
	@echo "Services:"
	@echo "  make services    - Start Docker services"
	@echo "  make start       - Alias for 'make services'"
	@echo "  make stop        - Stop Docker services"
	@echo "  make status      - Show service status"
	@echo ""
	@echo "Testing:"
	@echo "  make test        - Run all tests"
	@echo "  make smoke       - Run smoke tests"
	@echo "  make api         - Run API tests"
	@echo "  make mqtt        - Run MQTT tests"
	@echo "  make security    - Run security tests"
	@echo "  make integration - Run integration tests"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       - Clean reports and cache"
	@echo "  make lint        - Run code linters"
	@echo "  make format      - Format Python code"

setup: install certs services
	@echo "✓ Setup complete!"

install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

certs:
	@echo "Generating certificates..."
	python3 scripts/generate_certs.py

services:
	@echo "Starting Docker services..."
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "✓ Services started"

start: services

stop:
	@echo "Stopping Docker services..."
	docker-compose down

status:
	docker-compose ps

test:
	python3 cli.py run --suite all

smoke:
	python3 cli.py run --suite smoke

api:
	python3 cli.py run --suite api

mqtt:
	python3 cli.py run --suite mqtt

security:
	python3 cli.py run --suite security

integration:
	python3 cli.py run --suite integration

clean:
	@echo "Cleaning reports and cache..."
	python3 cli.py clean
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

lint:
	@echo "Running linters..."
	flake8 libraries/ config/ --max-line-length=120 --exclude=venv

format:
	@echo "Formatting Python code..."
	black libraries/ config/
