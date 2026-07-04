.PHONY: check lint format typecheck test test-small test-medium test-large \
        verify-docs setup help

SOURCES := src/ tests/ scripts/

check: lint format typecheck test

lint:
	ruff check $(SOURCES)

format:
	ruff format $(SOURCES)

typecheck:
	mypy src/ scripts/

test:
	pytest

test-small:
	pytest -m small

test-medium:
	pytest -m medium

test-large:
	pytest -m large

verify-docs:
	python3 scripts/check_doc_links.py docs/ README.md README.ja.md AGENTS.md CLAUDE.md .claude/skills/

setup:
	uv sync

help:
	@echo "Common targets:"
	@echo "  make check        - lint + format + typecheck + test"
	@echo "  make test         - pytest (all markers)"
	@echo "  make test-small   - pytest -m small"
	@echo "  make test-medium  - pytest -m medium"
	@echo "  make test-large   - pytest -m large"
	@echo "  make verify-docs  - run doc link checker"
	@echo "  make setup        - uv sync"
