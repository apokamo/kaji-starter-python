# Configuration

`.kaji/config.toml` と `.env` の責務分担。

## `.kaji/config.toml`（tracked）

kaji の repository 共通設定。設定仕様の正本は kaji 本体の
[configuration.md](https://github.com/apokamo/kaji/blob/main/docs/reference/configuration.md)。

| key | 本 repository の値 | 備考 |
|-----|-------------------|------|
| `paths.artifacts_dir` | `.kaji/artifacts` | 実行ログの保存先（gitignored） |
| `paths.skill_dir` | `.claude/skills` | skill 正本の置き場 |
| `execution.default_timeout` | `2400` | step あたりの timeout 秒 |
| `execution.agent_runner` | `headless` | `interactive_terminal` に変えると tmux pane で agent が動く（tmux 3.1+ 必須） |
| `provider.type` | `github` | repository 既定の provider |
| `provider.github.repo` | `<owner>/<repo>` | **template 利用時に必ず書き換える** |
| `provider.github.default_branch` | `main` | |
| `provider.github.git_remote` | `origin` | skill 内 git push / fetch の対象 remote |

## `.kaji/config.local.toml`（gitignored）

machine-local な overlay。`uv run kaji local init` が生成し、provider 切替
（github ⇄ local）や machine_id を保持する。手書きせず CLI に任せる。commit 禁止。

## `.env` / `.env.example`

- アプリケーションが使う secret・環境変数は `.env`（gitignored）に置く
- 雛形は `.env.example`（tracked）に置き、実際の値は書かない
- secret をコード・設定ファイルにハードコードしない

## `.kaji/` 配下の tracked / ignored

| パス | 扱い | 理由 |
|------|------|------|
| `.kaji/config.toml` / `.kaji/wf/` | tracked | repository 共通設定・workflow 定義 |
| `.kaji/issues/` | tracked | local provider 利用時の Issue 永続化 |
| `.kaji/artifacts/` | ignored | 実行ログ（肥大化する） |
| `.kaji/counters/` | ignored | per-machine 採番 |
| `.kaji/config.local.toml` / `.kaji/cache/` | ignored | machine-local overlay / cache |
