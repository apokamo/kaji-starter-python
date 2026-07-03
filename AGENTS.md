# AGENTS.md

## Project

<project-name> — Python application/library（kaji-starter-python template から作成）。
[kaji](https://github.com/apokamo/kaji) による Issue 起点の開発 workflow / TDD-first / Docs-as-Code。

本ファイルは repo 内で作業する agent 向け instructions の**正本**。
外部読者向けの説明は README.md が担う。

## Always-Apply Rules（skill 外のターンでも常に適用）

- コード変更（`src/` / `tests/` / `Makefile` / `pyproject.toml` 等）は
  feature branch (worktree) → `--no-ff` merge。main 直コミット禁止
  （例外: docs / `.kaji/issues/` / 軽微な設定 → [docs/dev/git-workflow.md](docs/dev/git-workflow.md)）
- コード変更を含む commit の前に `source .venv/bin/activate && make check` を必ず通す
  （docs のみのコミットは省略可）
- Conventional Commits（feat/fix/docs/test/refactor/chore）。merge は `--no-ff` のみ（squash 禁止）
- secrets をハードコードしない。`.env`（gitignored）に置く
- コードを書く前に [docs/reference/python-standards.md](docs/reference/python-standards.md) の規約をロードする
  （規約の正本は docs + ruff/mypy 設定。`make check` がバックストップ）

## Routing（作業種別 → 入口）

- 開発作業: skill lifecycle（/issue-create → … → /issue-close）
  → [docs/dev/kaji-workflow.md](docs/dev/kaji-workflow.md)
- Issue / PR 操作: `uv run kaji issue` / `uv run kaji pr`（内部で `gh` CLI へ委譲）
- ドキュメント索引: [docs/README.md](docs/README.md)

## kaji workflow の最小前提

- kaji は project-local 導入。CLI は `uv run kaji ...` で実行する
- workflow 実行: `uv run kaji run .kaji/wf/dev.yaml <issue-id>`（5 本の使い分けは
  [docs/dev/kaji-workflow.md](docs/dev/kaji-workflow.md)）
- interactive terminal runner を使う場合は tmux 3.1+ のセッション内で実行する
