.DEFAULT_GOAL := help

.PHONY: help validate-contracts lint up down

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

validate-contracts: ## Parse all JSON contracts (use check-jsonschema for full validation when installed)
	@python -c "import json,pathlib; files=list(pathlib.Path('contracts').rglob('*.json')); [json.loads(p.read_text(encoding='utf-8')) for p in files]; print(f'Parsed {len(files)} JSON contracts')"
	@python -c "import importlib.util,subprocess,sys; raise SystemExit(subprocess.call(['check-jsonschema','--check-metaschema',*map(str,__import__('pathlib').Path('contracts').rglob('*.json'))]) if importlib.util.find_spec('check_jsonschema') else 0)"

lint: validate-contracts ## Run repository validation

up: ## Start future local dependencies
	docker compose up -d

down: ## Stop local dependencies
	docker compose down

