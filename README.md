# kaji-starter-python

[kaji](https://github.com/apokamo/kaji) で Issue 起点の開発 workflow
（設計 → 実装 → レビュー → PR）を回せる状態から始める Python starter repository。

- Python project 骨格（`src/` layout / `uv` / `ruff` / `mypy` / `pytest` / `Makefile`）
- kaji 導入済み（dev dependency。`uv run kaji` で実行）
- workflow YAML 5 本（GitHub provider 3 本 + local provider 2 本、claude 単騎構成）
- 汎用化済み skills 23 本（`.claude/skills/`。Claude 以外の agent は `.agents/skills/` 経由で参照）

対応環境: Linux / macOS / WSL2（native Windows は対象外。WSL2 を利用してください）。

## Quickstart

前提: [uv](https://docs.astral.sh/uv/) / [gh](https://cli.github.com/) / tmux 3.1+ /
agent CLI（既定は [Claude Code](https://claude.com/claude-code)。codex / gemini への
寄せ替えは `scripts/set_agent.py`）。

```bash
# 1. GitHub 上で「Use this template」から自分の repository を作成して clone

# 2. 最小の書き換え
#    - .kaji/config.toml: [provider.github] repo = "<owner>/<repo>" を自分の repo に
#    - （任意）pyproject.toml の project name と src/starter_app/ の rename

# 3. セットアップと品質ゲート確認
uv sync
source .venv/bin/activate && make check   # 作成直後にパスする

# 4. GitHub 認証と最初の workflow 実行
gh auth status
uv run kaji issue create --title "..." --body-file issue.md --label type:feature
uv run kaji run .kaji/wf/dev.yaml <issue-id>
```

GitHub 連携なしで試す場合は local provider を使う（issue は local provider 配下で作成する）:

```bash
uv run kaji local init
uv run kaji issue create --title "..." --body-file issue.md --label type:feature
uv run kaji run .kaji/wf/dev-local.yaml <issue-id>
```

## Documentation

- セットアップ詳細・開発の進め方・カスタマイズ: kaji 本体の利用ガイド（準備中。
  進捗は [apokamo/kaji#242](https://github.com/apokamo/kaji/issues/242) を参照）
- この repository の開発規約: [docs/README.md](docs/README.md)
- agent 向け instructions: [AGENTS.md](AGENTS.md)
