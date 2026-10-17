# kaji-starter-python

言語: [English](README.md) | 日本語

[kaji](https://github.com/apokamo/kaji) で Issue 起点の開発 workflow
（設計 → 実装 → レビュー → PR）を回せる状態から始める Python starter repository。

- Python project 骨格（`src/` layout / `uv` / `ruff` / `mypy` / `pytest` / `Makefile`）
- kaji 導入済み（dev dependency。`uv run kaji` で実行）
- workflow YAML 3 本（GitHub provider、claude 単騎構成）
- 汎用化済み skills 24 本（`.claude/skills/`。Claude 以外の agent は `.agents/skills/` 経由で参照。検証済み Issue 直列計画を作る `/series-create` を含む）

対応環境: Linux / macOS / WSL2（native Windows は対象外。WSL2 を利用してください）。

## Quickstart

前提: [uv](https://docs.astral.sh/uv/) / [gh](https://cli.github.com/) /
agent CLI（既定は [Claude Code](https://claude.com/claude-code)。codex への
寄せ替えは `scripts/set_agent.py`。kaji 所有の `.kaji/wf/official/**` は書き換えず、
変換結果は `.kaji/wf/custom/**` へ生成する）。既定の headless runner では terminal は不要。
interactive terminal runner（`execution.agent_runner = "interactive_terminal"`）を使う場合は
`interactive_terminal_backend = "herdr"` を設定し、Herdr 0.8.2+ の pane 内で実行する（tmux 不要）。
tmux backend（未指定時の既定、tmux 3.1+ 必須）は kaji v0.23.0 で deprecated となり、後続 release で削除される。

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

# 5. GitHub の Settings > General > Features > Issues で
#    "Auto-close issues with merged linked pull requests" を無効化
#    （workflow は PR と Issue をリンクするが、Issue は最終 step で明示 close する）

# 6. GitHub 認証とラベル作成
gh auth status
scripts/setup_labels.sh                    # type:*、epic、incident ラベルを作成（初回のみ）

# 7. 最初の workflow 実行
uv run kaji issue create --title "..." --body-file issue.md --label type:feature
uv run kaji run .kaji/wf/official/dev.yaml <issue-id>
```

GitHub ラベル（`type:*`、`epic`、`incident:*`）は template では複製されないため、`scripts/setup_labels.sh` で
一度だけ作成する（workflow の起票がこのラベルに依存する）。

## Documentation

- セットアップ詳細・開発の進め方・カスタマイズ:
  [Python Starter ガイド](https://github.com/apokamo/kaji/blob/main/docs/guides/python-starter.ja.md)
- この repository の開発規約: [docs/README.md](docs/README.md)
- agent 向け instructions: [AGENTS.md](AGENTS.md)
