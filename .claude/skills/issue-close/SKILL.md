---
description: イシュー完了時に使用。PRマージ・worktree削除・ブランチ安全削除を一括実行
name: issue-close
---

# Issue Close

イシュー対応完了後のクリーンアップを実行します。
PR マージ、worktree 削除、ブランチ削除、Issue クローズを一括実行します。

## いつ使うか

| タイミング | このスキルを使用 |
|-----------|-----------------|
| PRがApproveされマージ可能 | ✅ 使用 |
| PRレビュー待ち | ❌ 待機 |
| 作業途中 | ❌ 不要 |

**ワークフロー内の位置**: implement → review-code → i-dev-final-check → i-pr → **close**

## 入力

### ハーネス経由（コンテキスト変数）

**常に注入される変数:**

| 変数 | 型 | 説明 |
|------|-----|------|
| `issue_id` | str | 正規化済み Issue ID（GitHub 数値） |
| `issue_ref` | str | 人間可読の Issue 参照（GitHub では `#<issue_id>`） |
| `step_id` | str | 現在のステップ ID |

**provider 解決時に追加で注入される変数:**

| 変数 | 型 | 説明 |
|------|-----|------|
| `provider_type` | str | `github`（現行唯一の provider） |
| `default_branch` | str | ベースブランチ名（`main` 等）。branch 削除判定と `git pull` の引数に使用 |
| `branch_name` | str | フィーチャーブランチ名（`feat/<id>` 等） |
| `worktree_dir` | str | worktree 絶対パス |

### 手動実行（スラッシュコマンド）

```
$ARGUMENTS = <issue_id>
```

### 解決ルール

コンテキスト変数 `issue_id` が存在すればそちらを使用。
なければ `$ARGUMENTS` の第1引数を `issue_id` として使用。

`issue_ref` はハーネス経由ではプロンプトに自動注入される（`prompt.py` 側で provider 別に整形）。手動実行時は `issue_id` から `#<issue_id>` を導出する。

## 前提条件

- `/i-pr` でPRが作成済みであること
- Merge commit方式を使用（ブランチ履歴を保持）

## 実行手順

Step 1〜6 を順に実行する（`uv run kaji pr merge` / worktree 削除 / branch 削除 /
`git pull` / `uv run kaji issue close` / 報告）。

## 共通: ワークフロー完了後の確認項目の移管

親 Issue を close する直前に、provider に関係なく本手順を実行する。
正本は
[`docs/dev/workflow_completion_criteria.md`](../../../docs/dev/workflow_completion_criteria.md)
§ follow-up Issue への移管、本文 template は
[`templates/follow-up-issue.md`](templates/follow-up-issue.md) とする。

### 1. 未完了項目の抽出

親本文の `## 完了条件` 内にある末尾サブセクション
`### ワークフロー完了後の確認項目` だけを対象にし、次の `## ` 見出しまたは本文末尾までから
`- [ ]` の項目を抽出する。

| 状態 | 処理 |
|------|------|
| セクションなし | follow-up なしで close 手順を続行 |
| `- なし`、または未チェック項目 0 件 | follow-up なしで close 手順を続行 |
| 未チェック項目 1 件以上 | 以降の検索・作成・マーカー追記を実行 |
| 見出し重複、チェックリストとして解釈不能 | 項目喪失を避けるため `ABORT` |

`i-dev-final-check` / `i-doc-final-check` が同サブセクションを更新対象外としているため、
ここに残る `[ ]` は未完了のまま follow-up へ移す。`[x]` は移さない。

### 2. 親マーカーと既存 Issue の確認

follow-up のタイトルは次の完全一致形式に固定する。

```text
[follow-up] [parent_title] ([issue_ref])
```

まず親本文に次のマーカーがあるか確認する。

```text
<!-- kaji-follow-up-issue: [follow_up_issue_id] -->
```

- マーカーが 1 件ある場合: 値を `FOLLOW_UP_ID` に設定して `uv run kaji issue view` で確認し、
  次の 3 点をすべて満たすときだけ再利用する
  1. `state` が `open` である
  2. title が完全一致形式である
  3. 本文に `<!-- kaji-follow-up-parent: [issue_ref] -->` が 1 件ある
- マーカーが複数、値が空、参照先が存在しない場合: `ABORT`
- マーカーの参照先が close 済みの場合: `ABORT`。未チェック項目が親に残っているのに
  追跡先が閉じている状態であり、close 済み follow-up を再利用すると追跡が失われる。
  同名タイトルの open Issue 検索へフォールバックしてもマーカーとの不整合が残るため、
  自動復旧はしない。人間が (a) 完了済みの項目を親本文で `[x]` に更新する、
  (b) follow-up Issue を reopen する、(c) 親のマーカー行を削除して再作成させる、
  のいずれかを選んだうえで再実行する
- マーカーがない場合: open Issue を完全一致タイトルで検索する

```bash
FOLLOW_UP_STATE=$(uv run kaji issue view "$FOLLOW_UP_ID" --json state -q '.state')
# 大文字小文字の揺れに依存しないよう小文字化して比較する
case "$(printf '%s' "$FOLLOW_UP_STATE" | tr '[:upper:]' '[:lower:]')" in
  open) : ;;
  *)
    echo "ABORT: marked follow-up Issue $FOLLOW_UP_ID is not open (state=$FOLLOW_UP_STATE)"
    exit 1
    ;;
esac
```

```bash
PARENT_TITLE=$(uv run kaji issue view [issue_id] --json title -q '.title')
FOLLOW_UP_TITLE="[follow-up] $PARENT_TITLE ([issue_ref])"
uv run kaji issue list --state open --limit 1000 --json number,title > /tmp/kaji-open-issues.json
jq -r --arg title "$FOLLOW_UP_TITLE" \
  '.[] | select(.title == $title) | .number' \
  /tmp/kaji-open-issues.json > /tmp/kaji-follow-up-candidates.txt
```

| 完全一致件数 | 処理 |
|-------------|------|
| 0 | 新規作成 |
| 1 | 候補の `.number` を `FOLLOW_UP_ID` に設定し、既存 open Issue を再利用 |
| 2 以上 | 対象を一意に決められないため `ABORT` |

作成後にマーカー追記だけが失敗した場合も、再実行時は完全一致検索で作成済み Issue を
再利用する。これにより重複起票を防ぐ。

### 3. follow-up Issue の作成

完全一致候補がない場合だけ、`templates/follow-up-issue.md` を読み、以下を実値へ置換して
`/tmp/kaji-follow-up-body.md` を作る。

- `[parent_issue_ref]` / `[parent_issue_title]`
- `[unchecked_items]`: 抽出した未チェック項目だけ
- `[reference_docs]`: 親本文の `docs/...` 参照。なければ正本
  `docs/dev/workflow_completion_criteria.md`

```bash
CREATE_OUTPUT=$(uv run kaji issue create \
  --title "$FOLLOW_UP_TITLE" \
  --body-file /tmp/kaji-follow-up-body.md) || {
    echo "ABORT: follow-up Issue creation failed"
    exit 1
  }
FOLLOW_UP_ID=${CREATE_OUTPUT##*/}

# github provider では --commit は無視される（CLI 互換のため付与を維持）。
uv run kaji issue edit "$FOLLOW_UP_ID" --commit \
  --body-file /tmp/kaji-follow-up-body.md || {
    echo "ABORT: follow-up Issue persistence failed"
    exit 1
  }
```

### 4. 親本文へのマーカー追記

親本文に有効なマーカーがなかった場合だけ、新規作成・既存検索で得た Issue ID の
マーカーを親本文末尾へ 1 件追記する。Step 2 で有効なマーカーを確認済みの場合は追記を
スキップし、既存の 1 件を維持する。

```bash
CURRENT_BODY=$(uv run kaji issue view [issue_id] --json body -q '.body')
{
  printf '%s\n\n' "$CURRENT_BODY"
  printf '<!-- kaji-follow-up-issue: %s -->\n' "$FOLLOW_UP_ID"
} > /tmp/kaji-parent-body-with-follow-up.md

uv run kaji issue edit [issue_id] --commit \
  --body-file /tmp/kaji-parent-body-with-follow-up.md || {
    echo "ABORT: parent follow-up marker update failed; parent Issue remains open"
    exit 1
  }
```

追記後、`uv run kaji issue view` で同じマーカーが 1 件だけ存在することを確認する。作成・再利用、
マーカー追記、追記後確認のいずれかが失敗した場合は `ABORT` とし、親 Issue の close を
実行しない。

> **結果を記録**: `follow_up_result` = 「対象なし」/「作成: [follow_up_issue_id]」/
> 「既存再利用: [follow_up_issue_id]」。完了報告に含める。

### provider=github の場合

### Step 1: Worktree情報の取得

Issue本文からWorktree情報を取得します:

```bash
uv run kaji issue view [issue_id] --json body -q '.body'
```

以下の情報を抽出:
- `> **Worktree**: \`../kaji-[prefix]-[issue_id]\`` → worktree パス
- `> **Branch**: \`[prefix]/[issue_id]\`` → ブランチ名

### Step 2: メインリポジトリのパスを特定

`git worktree list` の最初の行が常に main worktree（bare repository のルート）を示す:

```bash
MAIN_REPO=$(git worktree list | head -1 | awk '{print $1}')
```

> **注意**: `git rev-parse --show-toplevel` は現在の worktree のルートを返すため、
> worktree 内から実行すると main repo を取得できない。必ず `git worktree list` を使うこと。

worktree 内にいる場合は main repo に移動:

```bash
cd "$MAIN_REPO"
```

### Step 3: PRのマージ

```bash
uv run kaji pr merge [branch_name]
```

マージコミットを作成してブランチ履歴を保持する。ブランチ削除は worktree 削除後に Step 4.5 で行う。

> **結果を記録**: `pr_merge_result` = 「マージ済み」。この値は Step 6 で使用する。

### Step 4: worktree削除

```bash
git worktree remove "$MAIN_REPO/../kaji-[prefix]-[issue_id]"
```

> `$MAIN_REPO` は Step 2 で取得済み。

> **結果を記録**: `worktree_result` = 「削除済み」。この値は Step 6 で使用する。

### Step 4.5: ブランチ削除

worktree 削除後にローカル・リモートブランチを削除する。
`git fetch [git_remote]` で `[git_remote]/[default_branch]` を最新化してから、`merge-base --is-ancestor` でマージ済み判定を行い、安全に削除する。
ローカル削除とリモート削除は独立して実行し、片方の失敗がもう片方をブロックしない。
ブランチが既に存在しない場合はスキップする。

```bash
# 1. fetch して [git_remote]/[default_branch] を更新
git fetch [git_remote]

# 2. ローカルブランチ削除: 存在確認 → マージ済み判定 → 安全な -D
if git show-ref --verify --quiet refs/heads/[branch_name]; then
    if git merge-base --is-ancestor [branch_name] [git_remote]/[default_branch]; then
        git branch -D [branch_name]
    else
        echo "WARNING: branch not merged into [git_remote]/[default_branch], skipping local delete"
    fi
fi

# 3. リモートブランチ削除（ローカル削除の成否に依存しない）
git ls-remote --exit-code --heads [git_remote] [branch_name] >/dev/null 2>&1
LS_EXIT=$?
if [ "$LS_EXIT" -eq 0 ]; then
    if ! git push [git_remote] --delete [branch_name]; then
        echo "ERROR: git push [git_remote] --delete failed"
        exit 1
    fi
elif [ "$LS_EXIT" -eq 2 ]; then
    echo "INFO: remote branch already deleted"
else
    echo "ERROR: git ls-remote failed (exit $LS_EXIT)"
    exit 1
fi

# 4. stale remote-tracking ref を掃除
git fetch --prune [git_remote]
```

> **結果を記録**:
> - `local_branch_result` = 「削除済み」/「未存在を確認」/「未マージのためスキップ」
> - `remote_branch_result` = 「削除済み」/「未存在を確認」/「削除失敗（要手動対応）」
>
> これらの値は Step 6 で使用する。

### Step 5: mainを最新化

```bash
git pull [git_remote] [default_branch]
```

> **結果を記録**: `pull_result` = 「最新化済み」。この値は Step 6 で使用する。

### Step 5.4: ワークフロー完了後の確認項目を移管

「共通: ワークフロー完了後の確認項目の移管」を実行する。失敗時は `ABORT` とし、
Step 5.5 へ進まない。

### Step 5.5: Issue クローズ

```bash
uv run kaji issue close [issue_id] --reason completed
```

> **結果を記録**: `close_result` = 「クローズ済み」/「クローズ失敗（要手動対応）」。この値は Step 6 で使用する。
>
> **重要**: `uv run kaji issue close` が失敗した場合は verdict を **ABORT** にすること。Issue が未クローズのまま残ることは許容しない。

### Step 6: 完了報告

Step 3〜5.5 の結果を使って、**stdout への報告**と **Issue タイムラインへのコメント投稿**の両方を行う。

#### 6a. Issue コメント投稿

各ステップで記録した結果変数を使い、コメント内容を動的に組み立てて投稿する:

```bash
uv run kaji issue comment [issue_id] --commit --body-file - <<'COMMENT_EOF'
## Issue クローズ完了

| 項目 | 状態 |
|------|------|
| PR | [pr_merge_result] |
| worktree | [worktree_result] |
| ローカルブランチ | [local_branch_result] |
| リモートブランチ | [remote_branch_result] |
| main | [pull_result] |
| follow-up Issue | [follow_up_result] |
| Issue | [close_result] |
COMMENT_EOF

```

> `[pr_merge_result]` 等のプレースホルダーは、実際の実行結果に置き換えること。ハードコードしない。

#### 6b. stdout 報告

以下の形式で報告してください:

```
## Issue クローズ完了

| 項目 | 状態 |
|------|------|
| Issue | [issue_ref] |
| PR | [pr_merge_result] |
| worktree | [worktree_result] |
| ローカルブランチ | [local_branch_result] |
| リモートブランチ | [remote_branch_result] |
| main | [pull_result] |
| follow-up Issue | [follow_up_result] |
| Issue 状態 | [close_result] |
```

## Verdict 出力

実行完了後、以下の形式で verdict を出力すること:

```
---VERDICT---
status: PASS
reason: |
  クローズ完了
evidence: |
  事後確認の移管要否を確認し、必要な follow-up Issue の作成または再利用と親マーカー追記を完了した。PR マージ・worktree 削除・main 最新化・Issue クローズ済み
suggestion: |
---END_VERDICT---
```

**重要**: verdict は **stdout にそのまま出力** すること。Issue コメントや Issue 本文更新とは別に、最終的な verdict ブロックは stdout に残す。

### status の選択基準

| status | 条件 |
|--------|------|
| PASS | クローズ完了 |
| ABORT | follow-up 作成・再利用・親マーカー追記の失敗（マーカー参照先が close 済みの場合を含む）、またはクローズ失敗（`uv run kaji issue close` 失敗を含む） |
