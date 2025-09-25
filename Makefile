.PHONY: help install install-dev test lint format clean demo

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package and dependencies
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

install-all: ## Install the package with all optional dependencies
	pip install -e ".[all]"

test: ## Run tests
	pytest

lint: ## Run linting checks
	flake8 .
	mypy .

format: ## Format code with black and isort
	black .
	isort .

format-check: ## Check code formatting without making changes
	black --check .
	isort --check-only .

clean: ## Clean up build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

demo-hello: ## Run the hello world demo
	python simple_hello_world.py

demo-inter-agent: ## Run the inter-agent communication demo
	python inter_agent_communication_demo_v2.py

demo-all: ## Run all demos
	@echo "Running hello world demo..."
	python simple_hello_world.py
	@echo "\nRunning inter-agent communication demo..."
	python inter_agent_communication_demo_v2.py

check-env: ## Check if required environment variables are set
	@echo "Checking environment..."
	@if [ -z "$$ANTHROPIC_API_KEY" ]; then \
		echo "❌ ANTHROPIC_API_KEY is not set"; \
		echo "Please set it with: export ANTHROPIC_API_KEY='your-api-key'"; \
		exit 1; \
	else \
		echo "✅ ANTHROPIC_API_KEY is set"; \
	fi

setup: install check-env ## Complete setup: install dependencies and check environment
	@echo "✅ Setup complete! You can now run demos with 'make demo-hello' or 'make demo-inter-agent'"