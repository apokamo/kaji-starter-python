# Git Workflow

branch / commit / merge の運用規約。

## branch 運用

- コード変更は feature branch（worktree）で行う。main への直コミット禁止
  - 例外: docs のみ・`.kaji/issues/` のみ・軽微な設定変更は main 直コミット可
- branch 名は `<type>/<issue-id>`（例: `feat/12` / `fix/34` / `docs/56`）
- worktree は `kaji run` の issue-start step が `../<prefix>-<branch_type>-<issue_id>` 形式で作成する

## commit 規約

- Conventional Commits（`feat:` / `fix:` / `docs:` / `test:` / `refactor:` / `chore:`）
- コード変更を含む commit の前に `source .venv/bin/activate && make check` を通す
  （docs のみの commit は省略可。[change-types-and-gates.md](change-types-and-gates.md) 参照）
- commit message には何を・なぜ変えたかを書く。Issue 番号を末尾に含める（例: `feat: add X (#12)`）

## merge 運用

- PR merge は `--no-ff` のみ（squash / rebase merge 禁止）。履歴に merge commit を残す
- merge 後は worktree / branch を削除する（issue-close skill が行う）

## push / PR

- push と PR 作成は i-pr skill 経由（`uv run kaji pr create`）を正とする
- PR body には Issue への参照（`Closes #<id>` 等の auto-close キーワード）を含める
