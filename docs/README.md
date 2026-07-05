# Documentation Index

この repository の開発規約・運用ドキュメントの索引。
agent 向けの最小ルールは [AGENTS.md](../AGENTS.md) にあり、詳細は本索引から辿る。

## dev — 開発の進め方

| ドキュメント | 内容 |
|-------------|------|
| [change-types-and-gates.md](dev/change-types-and-gates.md) | 変更種別ごとの required gate（`make check` / `make verify-docs` 等） |
| [testing-convention.md](dev/testing-convention.md) | Small / Medium / Large テスト規約と恒久テスト追加の判断基準 |
| [git-workflow.md](dev/git-workflow.md) | branch / commit / merge 運用 |
| [kaji-workflow.md](dev/kaji-workflow.md) | workflow 5 本の使い分け・skill lifecycle・完了確認の分担 |
| [shared_skill_rules.md](dev/shared_skill_rules.md) | skill 間の責務境界と verdict 出力規約 |
| [documentation_update_criteria.md](dev/documentation_update_criteria.md) | docs 更新要否の判断基準 |

## reference — 設定・規約の正本

| ドキュメント | 内容 |
|-------------|------|
| [configuration.md](reference/configuration.md) | `.kaji/config.toml` と `.env` の責務（[English](reference/configuration.en.md)） |
| [python-standards.md](reference/python-standards.md) | Python コーディング規約（style / naming / typing / error handling / logging）（[English](reference/python-standards.en.md)） |

## 外部ドキュメント

- kaji 本体（CLI 仕様・workflow 記法・local mode の正本）: <https://github.com/apokamo/kaji>
- starter の利用ガイド（セットアップ・カスタマイズ）:
  <https://github.com/apokamo/kaji/blob/main/docs/guides/python-starter.md>
  （[日本語](https://github.com/apokamo/kaji/blob/main/docs/guides/python-starter.ja.md)）
