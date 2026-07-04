# Python Standards

> English: [python-standards.en.md](python-standards.en.md)

コーディング規約。正本は本ドキュメント + `pyproject.toml` の ruff / mypy 設定。
`make check` がバックストップとして機械的に強制する。

## Style

- formatter / linter は ruff（`line-length = 100`、`select = ["E", "F", "I", "W", "B", "UP"]`）
- import は標準ライブラリ → サードパーティ → ローカルの順（ruff `I` が強制）
- コメント・docstring は「なぜ」を書く。コードから読み取れる「何を」は書かない

## Naming

- module / function / variable: `snake_case`
- class: `PascalCase`
- 定数: `UPPER_SNAKE_CASE`
- private は `_` prefix。公開 API は package の `__init__.py` で明示する

## Typing

- mypy strict を全 `src/` に適用する。新規コードは型注釈必須
- `Any` の使用は外部境界（未型付けライブラリの戻り値等）に限定し、内部へ伝播させない
- `typing` より組み込み generics（`list[str]` / `dict[str, int]`）と `X | None` を使う（Python 3.11+）

## Error Handling

- 例外は握りつぶさない。捕捉するなら回復・変換・ログのいずれかを行う
- 外部入力（設定・API 応答・ファイル）は境界で検証し、不正値は fail-fast で reject する
- ライブラリ的なコードでは独自例外を定義し、呼び出し側が判別できるようにする

## Logging

- `print` ではなく `logging` を使う（CLI のユーザー向け出力を除く）
- log message には文脈（対象・入力値の要約）を含め、secret は含めない

## Testing

テスト規約は [docs/dev/testing-convention.md](../dev/testing-convention.md) を参照。
