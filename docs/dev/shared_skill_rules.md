# Shared Skill Rules

workflow 横断で使う skill の責務境界と共通規約を定義する。

## `/i-pr` の責務

- worktree / branch 解決
- 未コミット変更の確認
- push
- `uv run kaji pr create`（`gh pr create` 直接呼び出しではなく `kaji` ラッパーを経由する）

## `/i-pr` が持たない責務

- workflow 固有の完了条件判定
- dev / docs-only の個別ルール判定
- docs 昇格や docs 同梱の妥当性判定
- final-check 実行済みかの代行判断

workflow 固有の最終判定は `i-dev-final-check` または `i-doc-final-check` が持つ。

## 後方互換（共通）

kaji の [ADR 008](https://github.com/apokamo/kaji/blob/main/docs/adr/008-no-backward-compat-layer.md) に従い、skill / harness に旧形式の読み取り fallback や version 分岐を追加しない。破壊的変更は CHANGELOG / Release notes の BREAKING セクションにある「壊れる契約・影響判定・適用指針」で移行する。検出不能時に破壊操作を避けて ABORT する fail-safe は後方互換層ではない。

## verdict マーカー契約（producer / consumer）

cross-skill 契約は skill の自由記述ではなく kaji CLI が付与する判定コメント先頭の marker を使う。

- producer は `uv run kaji issue comment` に `--verdict-step <step> --verdict-status <STATUS>` を無条件付与する。CLI が body 1 行目へ `<!-- kaji-verdict: step=<step> status=<STATUS> -->` を埋め込む。
- 現行 producer は `issue-review-code` / `i-dev-final-check` / `issue-implement` / `issue-review-design` / `issue-design`。
- consumer の `issue-design` は body 1 行目の marker だけを参照し、`BACK` / `BACK_DESIGN` を design 再入として扱う。旧見出しや checkbox regex の fallback は残さない。
- step は `^[a-z][a-z0-9_-]*$`、status は `PASS` / `RETRY` / `ABORT` / `BACK` / `BACK_<UPPER>`。不正語彙や片方だけの指定は CLI が fail-loud に拒否する。

## レビューサイクルの責務境界

| 責務 | 担当 skill |
|------|-----------|
| 新規指摘 | `issue-review-design`, `issue-review-code`, `i-doc-review`, `review` |
| 修正確認のみ（新規指摘不可） | `issue-verify-design`, `issue-verify-code`, `i-doc-verify`, `pr-verify` |

`fix/verify` 系（`issue-fix-*` / `issue-verify-*` / `pr-fix` / `pr-verify` / `i-doc-fix` /
`i-doc-verify`）はレビューサイクルの収束保証のため、新規指摘を行わない原則を共有する。

## 共通参照ドキュメント

| 共通ルール | パス | 用途 |
|-----------|------|------|
| worktree パス解決 | `.claude/skills/_shared/worktree-resolve.md` | Issue 本文 NOTE ブロックから worktree パスを取得 |
| 無関係な問題の報告 | `.claude/skills/_shared/report-unrelated-issues.md` | 作業中に発見した無関係な問題の報告手順 |
| 設計書の昇格 | `.claude/skills/_shared/promote-design.md` | draft 設計書から恒久ドキュメントへの昇格手順 |
| 重要判断と provenance | `.claude/skills/_shared/critical-decision-checklist.md` | 人間決定・AI 仮定・one-way door の分類と停止条件 |

## 重要判断の伝播（共通）

`grill-me` / `issue-review-ready` / `issue-design` / `issue-review-design` は
[`critical-decision-checklist.md`](../../.claude/skills/_shared/critical-decision-checklist.md)
を単一情報源として使う。人間が指定した source of truth と重要方針を後段へ伝播し、
AI の仮定は provenance で区別する。記述を補えば直る不備は `RETRY`、人間の決定が
存在しない one-way door は `ABORT` とし、AI の fix step へ判断を委ねない。

`grill-me` は workflow 外の有人 front-load であり、未決を質問して Issue 本文へ固定する。
後続3 skill は無人 workflow 内でその決定を検査・伝播し、新たな人間判断を代行しない。

## スキル実体

- 実体: `.claude/skills/`
- 互換導線: `.agents/skills/` の symlink（Claude 以外の agent 向け）

新規スキル追加や改名時は `.claude/skills/` を先に更新し、必要なら `.agents/skills/` に
symlink を追加する。

## auto close keyword 回避規約

### 前提: linked PR の auto-close を無効化

GitHub では PR と Issue の正式リンクと、default branch への merge 時の linked Issue auto-close は不可分である。`/i-pr` は PR description に `Closes [issue_ref]` を1行入れて正式リンクを作るため、生成先 repository では Settings → General → Features → Issues の **Auto-close issues with merged linked pull requests** を無効化する。この設定は REST / GraphQL から検証できないため、template 利用時に人間が確認する。

この設定が抑止するのは linked PR 経由だけであり、commit message 経由を抑止する保証はない。したがって commit body / merge commit message の closing keyword 回避は維持する。

### GitHub 仕様（公式）

`provider.type='github'` 配下では、**PR description**（および default branch に
merge された commit message）内の以下パターン（大小区別なし、word boundary 単位で検出）が
auto-close keyword として解釈され、PR merge 時点で issue が自動 close される
（仕様: [Linking a pull request to an issue using a keyword](https://docs.github.com/en/issues/tracking-your-work-with-issues/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword)）。

- `Closes #N` / `Closing #N` / `Close #N` / `Closed #N`
- `Fixes #N` / `Fix #N` / `Fixed #N`
- `Resolves #N` / `Resolve #N` / `Resolved #N`

GitHub の closing pattern に `Implements` 系は**含まれない**が、本 workflow では
起点で抑止する追加ルールとして本規約に含める（保守的防御）。

### 共通規約（必須）

skill が生成する **commit body**、および **PR description**（`/i-pr` の `Closes [issue_ref]` 1行を除く）に対して必須:

- close keyword（`Clos(e[sd]?|ing)` / `Fix(e[sd]|ing)?` / `Resolv(e[sd]?|ing)` /
  `Implement(s|ing|ed)?`）の直後に `#` + 数字が連続するテキストを書かない。
  例文を書く必要があるときは数字部分を `<N>` placeholder にする（例: `Fix #<N>`）
- review item index の参照は `Must Fix item N` / `指摘 N` / `point N` 形式を使い、
  `Must Fix #N` や `Fix [N]` のような close keyword と隣接する表記を避ける
- Issue comment 本文でも `#N` 単独表記を避ける（comment 内容が後で commit /
  PR description へ転記される際の hazard 持ち込みを起点で防ぐ）
- `/i-pr` の PR description にある `Closes [issue_ref]` 1行だけ live closing keyword を許可・必須とし、正式リンクに使う。Issue の close 自体は `/issue-close` が明示的に行う

### push / push 後の検証

- **push 前**: 該当範囲の commit body を grep し hazard pattern が無いことを確認する:

  ```bash
  git log <range> --format='%B' | \
    grep -iE '\b(clos(e[sd]?|ing)|fix(e[sd]|ing)?|resolv(e[sd]?|ing)|implement(s|ing|ed)?)\s*:?\s*#[0-9]'
  ```

  match したら commit を amend して placeholder 化してから push する。
  PR description は match が `/i-pr` の `Closes <issue_ref>` 1件だけであることを確認する。

- **push 後**: 意図しない close が発生していないか確認し、発生していたら
  `gh issue reopen <N>` で戻した上で、原因の hazard 表記を placeholder 化する。

## verdict 出力規約

すべての workflow skill は作業完了時に、verdict を **3 経路**で残す。
harness は **artifact → comment → stdout** の順で解決する。

1. **作業報告 Issue comment 末尾（fallback）**: 作業報告コメントの末尾に
   `---VERDICT---` block を追記する（verdict 専用コメントは新設しない）
2. **stdout（互換 fallback）**: 同じ block を stdout にも出力する
3. **artifact `verdict.yaml`（primary / 書き込みは最後）**: コンテキスト変数
   `verdict_path` が指す絶対パスへ、`status` / `reason` / `evidence` / `suggestion` の
   pure YAML（delimiter なし）を保存する。interactive terminal runner では
   `verdict.yaml` の出現が次 step への完了トリガになるため、外部副作用
   （Issue comment 投稿等）を完了してから最後に保存する

```
---VERDICT---
status: <PASS | RETRY | BACK | ABORT>
reason: |
  (1-2文で判断理由を要約)
evidence: |
  (判断の根拠。テスト結果、レビュー指摘、差分など)
suggestion: |
  (ABORT/BACK 時は必須: 次のアクションの提案)
---END_VERDICT---
```

`verdict.yaml` の例（pure YAML）:

```yaml
status: PASS
reason: 設計書と整合し品質基準を満たす
evidence: ruff / mypy / pytest すべて pass
suggestion: ""
```

### verdict の選択基準

| verdict | 使用条件 |
|---------|---------|
| `PASS` | 目標を達成し、次ステップへ進んでよい |
| `RETRY` | 同一ステップの再実行で解決できる問題がある |
| `BACK` | 前段のステップを修正しなければ解決できない問題がある |
| `ABORT` | workflow 全体を停止すべき重大な問題がある |

制約: `reason` / `evidence` は必須。`ABORT` / `BACK` では `suggestion` も必須。
複数行は YAML block scalar (`|`) を使う。

**verdict 不在は fail-loud**: 3 経路のいずれにも verdict が無いままセッションが終了すると、
harness は補完せずエラーで停止する。セッション終了時点で verdict を残す責務は skill 側にある。
