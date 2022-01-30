.PHONY: help
.DEFAULT_GOAL := help

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

fmt format: ## Run code formatters
	isort app
	black app

lint: ## Run code linters
	isort --check app
	black --check app
	flake8 app
	mypy app
