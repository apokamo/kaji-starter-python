@AGENTS.md

## Development Skills

スキルは `.claude/skills/` に格納。`/issue-create` から `/issue-close` までのライフサイクルと、
PR 作成後のレビュー収束サイクルを管理する。

| フェーズ | スキル |
|---------|--------|
| 起票 | `/issue-create` |
| 着手前ゲート | `/issue-review-ready` → (`/issue-fix-ready`) |
| 着手 | `/issue-start` |
| 設計 | `/issue-design` → `/issue-review-design` → (`/issue-fix-design` → `/issue-verify-design`) |
| 実装 | `/issue-implement` → `/issue-review-code` → (`/issue-fix-code` → `/issue-verify-code`) |
| docs-only | `/i-doc-update` → `/i-doc-review` → (`/i-doc-fix` → `/i-doc-verify`) |
| 最終チェック | `/i-dev-final-check` / `/i-doc-final-check` |
| PR 作成 | `/i-pr` |
| PR レビュー後 | `/review` / `/pr-fix` / `/pr-verify` |
| 完了 | `/issue-close` |

各スキルの役割詳細: [docs/dev/kaji-workflow.md](docs/dev/kaji-workflow.md)
