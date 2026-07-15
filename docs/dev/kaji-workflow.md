# kaji Workflow

workflow 5 本の使い分け・skill lifecycle・完了確認の分担。

複数 Issue の直列実行計画は `/series-create` で `.kaji/series/<id>.yaml` を生成し、`uv run kaji run-series` で実行する。skill は validate と dry-run まで行い、実行自体は開始しない。

kaji v0.15.0 では workflow failure triage が既定で有効で、失敗分類・証跡コメント・incident 集約を package 側で行う。自動再開は `execution.auto_recover = true` の明示 opt-in。第2層の incident 調査 workflow は高度な任意運用資産であり、この最小 starter には同梱しない。

## 初回セットアップ（template から作った直後に一度だけ）

1. `.kaji/config.toml` の `provider.github.repo` を自分の repo に書き換える。`AGENTS.md` の `<project-name>` を埋める。LICENSE は自分のプロジェクトのものに差し替えてよい（starter は 0BSD で帰属義務なし）。package を rename する場合はここで行う
2. `uv sync` → `make check` を実行（rename すると `uv.lock` が再生成される）
3. 上記をまとめて `git commit` して main へ反映する（`uv sync` の後に commit することで `uv.lock` 差分も含まれる。未 commit のまま workflow を回すと最初の feature PR に混入する）
4. `scripts/setup_labels.sh` で workflow が使う `type:*`、`epic`、`incident:*` ラベルを作成する（GitHub ラベルは template 複製されないため）。local provider のみで使う場合は不要

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

### local provider での issue-create / issue-start（dev-local / docs-local の前提）

github 系（`dev.yaml` / `docs.yaml`）は `review-ready` → `start` を workflow 内で実行するが、
**local 系（`dev-local.yaml` / `docs-local.yaml`）は `design`（または `doc-update`）から始まり、
`issue-create` / `issue-start` は手動実行済みが前提**。local で回す前に次を実施する。

```bash
# 1. issue を local provider 配下で作成
uv run kaji issue create --title "..." --body-file issue.md --label type:feature
# → local-<machine>-<n> の issue id が返る

# 2. issue-start 相当（worktree 作成 + venv / overlay symlink + NOTE 追記）
MAIN=$(git rev-parse --show-toplevel)
BRANCH=$(uv run kaji issue context <issue-id> -q '.branch_name')
WT=$(uv run kaji issue context <issue-id> -q '.worktree_dir')
git worktree add -b "$BRANCH" "$WT" main
ln -s "$MAIN/.venv" "$WT/.venv"
# config.local.toml は gitignored で worktree に転写されないため symlink 必須
# （無いと worktree 内 kaji が github 既定で動き local-* id を拒否する）
[ -f "$MAIN/.kaji/config.local.toml" ] && ln -sf "$MAIN/.kaji/config.local.toml" "$WT/.kaji/config.local.toml"
uv run kaji issue prepend-note <issue-id> --worktree "$(basename "$WT")" --branch "$BRANCH" --commit

# 3. workflow 実行
uv run kaji run .kaji/wf/dev-local.yaml <issue-id>
```

各手順の詳細は `.claude/skills/issue-start/SKILL.md` を参照。

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
