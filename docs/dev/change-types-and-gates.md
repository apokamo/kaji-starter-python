# Change Types and Gates

変更種別ごとに、commit / PR 前に通すべき品質 gate を定義する。

## 変更種別と required gate

| 変更種別 | 対象 | required gate |
|----------|------|---------------|
| 実行時コード変更 | `src/` / `tests/` / `Makefile` / `pyproject.toml` | `make check`（lint + format + typecheck + test） |
| docs-only | `docs/` / `README.md` / `AGENTS.md` / `CLAUDE.md` / `.claude/skills/` | `make verify-docs`（doc link check） |
| 設定変更 | `.kaji/config.toml` / `.kaji/wf/*.yaml` | `uv run kaji validate .kaji/wf/*.yaml`（workflow YAML 変更時）+ 影響 docs の整合確認 |

- 実行時コード変更を含む commit の前に `source .venv/bin/activate && make check` を必ず通す
- docs のみの commit では `make check` を省略してよい（`make verify-docs` は通す）
- 種別が混在する場合は、該当するすべての gate を通す

## gate の内訳

`make check` は以下を順に実行する:

| ターゲット | コマンド | 対象 |
|-----------|---------|------|
| `make lint` | `ruff check` | `src/ tests/ scripts/` |
| `make format` | `ruff format` | `src/ tests/ scripts/` |
| `make typecheck` | `mypy`（strict） | `src/ scripts/` |
| `make test` | `pytest` | `tests/` |

## 変更固有の一時検証

恒久テストに残さない検証（動作確認スクリプト・手動確認手順）は、
その内容と結果を Issue コメントに証跡として残す。
判断基準は [testing-convention.md](testing-convention.md) を参照。
