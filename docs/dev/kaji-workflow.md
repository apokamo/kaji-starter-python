# kaji Workflow

workflow 5 本の使い分け・skill lifecycle・完了確認の分担。

## workflow 5 本の使い分け

| workflow | provider | 用途 |
|----------|----------|------|
| `.kaji/wf/dev.yaml` | github | 開発作業の標準。Issue → 設計 → 実装 → レビュー → PR → close |
| `.kaji/wf/dev-thorough.yaml` | github | dev と同じ遷移グラフで設計・実装の effort を上げた丁寧版 |
| `.kaji/wf/docs.yaml` | github | docs-only 変更。doc-update → doc-review → PR → close |
| `.kaji/wf/dev-local.yaml` | local | GitHub 連携なしの開発 workflow（PR concept なし） |
| `.kaji/wf/docs-local.yaml` | local | GitHub 連携なしの docs workflow（PR concept なし） |

```bash
uv run kaji run .kaji/wf/dev.yaml <issue-id>
uv run kaji run .kaji/wf/dev.yaml <issue-id> --from <step>   # 途中 step から再開
```

- 全 workflow は claude 単騎構成が既定。codex / gemini への寄せ替えは
  `uv run python scripts/set_agent.py <cli>`
- provider と workflow は一致させる（github provider で `dev-local.yaml` を実行しない。
  不一致は kaji が fail-fast で reject する）
- local provider の初期化は `uv run kaji local init`

## skill lifecycle

| フェーズ | skill |
|---------|--------|
| 起票 | `/issue-create` |
| 着手前ゲート | `/issue-review-ready` → (`/issue-fix-ready`) |
| 着手 | `/issue-start` |
| 設計 | `/issue-design` → `/issue-review-design` → (`/issue-fix-design` → `/issue-verify-design`) |
| 実装 | `/issue-implement` → `/issue-review-code` → (`/issue-fix-code` → `/issue-verify-code`) |
| docs-only | `/i-doc-update` → `/i-doc-review` → (`/i-doc-fix` → `/i-doc-verify`) |
| 最終チェック | `/i-dev-final-check` / `/i-doc-final-check` |
| PR 作成 | `/i-pr` |
| PR レビュー | `/review` → (`/pr-fix` → `/pr-verify`) |
| 完了 | `/issue-close` |

各 skill の責務境界は [shared_skill_rules.md](shared_skill_rules.md) を参照。

## 完了確認の分担

各フェーズで確認できる項目を final-check に先送りしない。final-check は前段の証跡を
集約し、未充足なら `RETRY` または `BACK` を返す。

| 項目 | review-ready | design / review-design | implement / review-code | final-check |
|------|--------------|------------------------|-------------------------|-------------|
| Issue 本文の記述品質 | ✅ | - | - | - |
| テスト戦略の妥当性 | - | ✅ | - | ✅（確認） |
| docs 影響評価 | - | ✅ | ✅ | ✅（確定） |
| 実装・差分の整合 | - | - | ✅ | ✅（集約） |
| 品質 gate（`make check`） | - | - | 実施 | ✅（最終確認） |
| Issue 本文更新・PR 可否判定 | - | - | - | ✅ |

## AI 単独で達成不能な検証の扱い

admin 権限・外部 secret・専用環境が必要な検証は Issue の完了条件（merge 阻害条件）に
含めない。AI フェーズでは静的検証（schema validation / lint / diff レビュー）で代替し、
手順を docs に残して user 側の運用タスクとして位置付ける。

## workflow YAML のカスタマイズ

workflow 記法（step / cycles / verdict 遷移 / `requires_provider`）の正本は kaji 本体の
docs を参照: <https://github.com/apokamo/kaji/blob/main/docs/dev/workflow-authoring.md>
