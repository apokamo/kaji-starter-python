.PHONY: check lint format fmt typecheck test test-small test-medium test-large \
        verify-docs setup help

SOURCES := src/ tests/ scripts/
TYPED := src/ tests/ scripts/

check: lint format typecheck test

lint:
	ruff check $(SOURCES)

# gate 用: 整形差分の有無だけを検査し、ファイルは書き換えない
# （書き換えは `make fmt` で明示的に行う。gate が worktree を汚さないため）
format:
	ruff format --check $(SOURCES)

# 明示的に整形を適用する
fmt:
	ruff format $(SOURCES)

typecheck:
	mypy $(TYPED)

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
	@echo "  make check        - lint + format(check) + typecheck + test"
	@echo "  make fmt          - apply ruff format (mutating)"
	@echo "  make test         - pytest (all markers)"
	@echo "  make test-small   - pytest -m small"
	@echo "  make test-medium  - pytest -m medium"
	@echo "  make test-large   - pytest -m large"
	@echo "  make verify-docs  - run doc link checker"
	@echo "  make setup        - uv sync"
