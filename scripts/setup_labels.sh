#!/usr/bin/env bash
# workflow と failure triage が依存する GitHub ラベルを作成する。
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

if ! gh auth status >/dev/null 2>&1; then
  echo "error: gh not authenticated. Run 'gh auth login' first." >&2
  exit 1
fi

repo="${1:-}"
if [[ -z "$repo" ]]; then
  repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
fi

echo "creating workflow labels in $repo"

create() {
  gh label create "$1" --repo "$repo" --color "$2" --description "$3" --force
}

create "type:feature"  "0e8a16" "新機能"
create "type:bug"      "d73a4a" "バグ修正"
create "type:refactor" "fbca04" "リファクタリング"
create "type:docs"     "0075ca" "ドキュメント"
create "type:test"     "c5def5" "テスト追加・改善"
create "type:chore"    "ededed" "雑務・依存の掃除"
create "type:perf"     "a2eeef" "パフォーマンス改善"
create "type:security" "b60205" "セキュリティ対応"

create "epic"                        "cba6f7" "複数 Issue を束ねる親 Issue"
create "incident"                   "eba0ac" "failure triage が起票したインシデント"
create "incident:investigating"     "f9e2af" "status: 調査中"
create "incident:mitigated"         "fab387" "status: 暫定緩和済み"
create "incident:resolved"          "a6e3a1" "status: 恒久解決済み"
create "incident:cause:internal"    "89b4fa" "cause: kaji / workflow 内部起因"
create "incident:cause:upstream"    "cba6f7" "cause: 外部 CLI / API 起因"
create "incident:cause:environment" "94e2d5" "cause: 実行環境起因"
create "incident:cause:transient"   "9399b2" "cause: 一過性・自己回復"

echo "done"
