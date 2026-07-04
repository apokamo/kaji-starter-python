# Python Standards

> 日本語版: [python-standards.md](python-standards.md)

Coding conventions. The source of truth is this document plus the ruff / mypy settings in
`pyproject.toml`. `make check` mechanically enforces them as a backstop.

## Style

- The formatter / linter is ruff (`line-length = 100`, `select = ["E", "F", "I", "W", "B", "UP"]`, `ignore = ["E501"]`)
- Line length is delegated to `ruff format`; `E501` (line-too-long) is disabled (long lines that remain after formatting are tolerated)
- Order imports as standard library → third party → local (enforced by ruff `I`)
- Comments and docstrings should explain "why", not the "what" that the code already shows

## Naming

- module / function / variable: `snake_case`
- class: `PascalCase`
- constants: `UPPER_SNAKE_CASE`
- Prefix private names with `_`. Expose the public API explicitly in the package's `__init__.py`

## Typing

- Apply mypy strict to `src/` / `tests/` / `scripts/` (`make typecheck`). Type annotations are required for new code
- Limit `Any` to external boundaries (e.g. return values of untyped libraries); do not let it propagate inward
- Prefer built-in generics (`list[str]` / `dict[str, int]`) and `X | None` over `typing` (Python 3.11+)

## Error Handling

- Do not swallow exceptions. If you catch one, recover, translate, or log it
- Validate external input (config, API responses, files) at the boundary and reject invalid values fail-fast
- In library-like code, define custom exceptions so callers can distinguish them

## Logging

- Use `logging`, not `print` (except for user-facing CLI output)
- Include context (target, a summary of input values) in log messages; never include secrets

## Testing

See [docs/dev/testing-convention.md](../dev/testing-convention.md) for the testing conventions.
