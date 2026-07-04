# kaji-starter-python

言語: [English](README.md) | 日本語

[kaji](https://github.com/apokamo/kaji) で Issue 起点の開発 workflow
（設計 → 実装 → レビュー → PR）を回せる状態から始める Python starter repository。

- Python project 骨格（`src/` layout / `uv` / `ruff` / `mypy` / `pytest` / `Makefile`）
- kaji 導入済み（dev dependency。`uv run kaji` で実行）
- workflow YAML 5 本（GitHub provider 3 本 + local provider 2 本、claude 単騎構成）
- 汎用化済み skills 23 本（`.claude/skills/`。Claude 以外の agent は `.agents/skills/` 経由で参照）

対応環境: Linux / macOS / WSL2（native Windows は対象外。WSL2 を利用してください）。

## Quickstart

前提: [uv](https://docs.astral.sh/uv/) / [gh](https://cli.github.com/) /
agent CLI（既定は [Claude Code](https://claude.com/claude-code)。codex / gemini への
寄せ替えは `scripts/set_agent.py`）。tmux 3.1+ は interactive terminal runner
（`execution.agent_runner = "interactive_terminal"`）利用時のみ必要で、既定の headless では不要。

```bash
# 1. GitHub 上で「Use this template」から自分の repository を作成して clone

# 2. セットアップ値を編集
#    - .kaji/config.toml: [provider.github] repo = "<owner>/<repo>" を自分の repo に
#    - AGENTS.md: <project-name> placeholder を埋める
#    - LICENSE: 自分のプロジェクトのものに差し替えてよい（starter は 0BSD で帰属義務なし）
#    - （任意）rename: pyproject.toml の name / src/starter_app/ / tests

# 3. セットアップと品質ゲート確認（rename した場合はここで uv.lock が再生成される）
uv sync
source .venv/bin/activate && make check   # 作成直後にパスする

# 4. 初回セットアップ commit（workflow を回す前に main へ反映する）
git add -A && git commit -m "chore: initial setup"
#    ↑ uv sync の後に commit することで uv.lock 差分も含まれる。未 commit のまま
#      workflow を回すと、これらの設定変更が最初の feature PR に混入する

# 5. GitHub 認証とラベル作成
gh auth status
scripts/setup_labels.sh                    # workflow が使う type:* ラベルを作成（初回のみ）

# 6. 最初の workflow 実行
uv run kaji issue create --title "..." --body-file issue.md --label type:feature
uv run kaji run .kaji/wf/dev.yaml <issue-id>
```

GitHub ラベル（`type:*`）は template では複製されないため、`scripts/setup_labels.sh` で
一度だけ作成する（workflow の起票がこのラベルに依存する）。

GitHub 連携なしで試す場合は local provider を使う。`dev.yaml` と違い `dev-local.yaml` は
`design` step から始まり、issue-create / issue-start を手動実行済みであることが前提
（worktree 作成が必要）。手動 issue-start の手順は
[docs/dev/kaji-workflow.md](docs/dev/kaji-workflow.md)（§ local provider での issue-create / issue-start）を参照:

```bash
uv run kaji local init
# 上記ガイドの手動 issue-create + issue-start 手順を実施してから:
uv run kaji run .kaji/wf/dev-local.yaml <issue-id>
```

## Documentation

- セットアップ詳細・開発の進め方・カスタマイズ: kaji 本体の利用ガイド（準備中。
  進捗は [apokamo/kaji#242](https://github.com/apokamo/kaji/issues/242) を参照）
- この repository の開発規約: [docs/README.md](docs/README.md)
- agent 向け instructions: [AGENTS.md](AGENTS.md)
