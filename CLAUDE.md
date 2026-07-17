@AGENTS.md

## Development Skills

スキルは `.claude/skills/` に格納し、`/issue-create` から `/issue-close` までのライフサイクルと
PR 作成後のレビュー収束サイクルを管理する。

独立 skill `/series-create` は、明示順の GitHub Issue 群から検証済み series YAML と dry-run plan を生成し、実行開始前に停止する。

`/grill-me` は one-way door を含みうる Issue で、workflow 開始前に人間が明示起動する任意 interview。未決判断を Issue 本文へ固定した後、通常の review-ready へ進む。

skill lifecycle の一覧（フェーズ → skill の対応表）の正本は
[docs/dev/kaji-workflow.md](docs/dev/kaji-workflow.md) § skill lifecycle。
CLAUDE.md には重複させず参照に寄せる（表記 drift を避けるため）。
