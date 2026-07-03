#!/usr/bin/env bash
# workflow が依存する GitHub ラベル（type:*）を作成する。
#
# GitHub のラベルは git 管理外のため「Use this template」では複製されない。
# fresh repo で最初に Issue を起票する前に一度だけ実行する。
#
# Usage:
#   scripts/setup_labels.sh                       # origin remote から repo を推定
#   scripts/setup_labels.sh <owner>/<repo>        # repo を明示
#
# 既存ラベルは --force で色・説明を上書きする（冪等）。gh CLI と認証が必要。

set -euo pipefail

repo="${1:-}"
if [[ -z "$repo" ]]; then
  repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
fi

echo "creating type:* labels in $repo"

create() {
  gh label create "$1" --repo "$repo" --color "$2" --description "$3" --force
}

create "type:feature"  "0e8a16" "新機能"
create "type:bug"      "d73a4a" "バグ修正"
create "type:refactor" "fbca04" "リファクタリング"
create "type:docs"     "0075ca" "ドキュメント"
create "type:test"     "c5def5" "テスト追加・改善"
create "type:chore"    "ededed" "雑務・依存の掃除"

echo "done"
