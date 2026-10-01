# Configuration

> English: [configuration.en.md](configuration.en.md)

`.kaji/config.toml` と `.env` の責務分担。

## `.kaji/config.toml`（tracked）

kaji の repository 共通設定。設定仕様の正本は kaji 本体の
[configuration.md](https://github.com/apokamo/kaji/blob/main/docs/reference/configuration.md)。

| key | 本 repository の値 | 備考 |
|-----|-------------------|------|
| `paths.artifacts_dir` | `.kaji/artifacts` | 実行ログ・run 記録の出力先（gitignored。§ 実行ログの出力先） |
| `paths.skill_dir` | `.claude/skills` | skill 正本の置き場 |
| `execution.default_timeout` | `2400` | step あたりの timeout 秒 |
| `execution.agent_runner` | `headless` | `interactive_terminal` に変えると terminal pane で agent が動く（既定 backend の tmux は tmux 3.1+ のセッション内、`herdr` は Herdr 0.8.2+ の pane 内で実行。`headless` は terminal 不要） |
| `execution.interactive_terminal_backend` | 未指定（`tmux`） | `agent_runner = "interactive_terminal"` のときの backend。`tmux`（既定、tmux 3.1+ 必須）または `herdr`（Herdr 0.8.2+ の pane 内でのみ起動可。tmux は不要） |
| `execution.failure_triage` | `true`（既定） | ERROR / 対象 ABORT を分類し、証跡コメント・artifact・incident 集約を行う |
| `execution.auto_recover` | `false`（既定） | recovery chain ごと1回の自動再開を許可する opt-in |
| `incident.kind_label` / `initial_status_label` / `transient_label` | `incident` / `incident:investigating` / `incident:cause:transient` | triage が起票する incident Issue のラベル名。kaji v0.21.0 の既定名は `kaji:incident` 系に変わったため、`scripts/setup_labels.sh` が作る旧名を明示している |
| `provider.type` | `github` | repository 既定の provider（`local` は kaji v0.21.0 で deprecated。警告のみで当面利用可） |
| `provider.github.repo` | `<owner>/<repo>` | **template 利用時に必ず書き換え、workflow を回す前に commit する**（未 commit のまま実行すると設定変更が最初の feature PR に混入する） |
| `provider.github.default_branch` | `main` | |
| `provider.github.git_remote` | `origin` | skill 内 git push / fetch の対象 remote |

## 実行ログの出力先

`kaji run` の実行記録は **`.kaji/artifacts/<issue>/`（gitignored）** に構造化して出力される。
出力先は `paths.artifacts_dir` で定義する（既定 `.kaji/artifacts`）。

| パス | 内容 |
|------|------|
| `runs/<timestamp>/run.log` | その run の完全なログ |
| `runs/<timestamp>/steps/<step>/attempt-NNN/console.log` / `stdout.log` | step ごとの agent 出力 |
| `runs/<timestamp>/steps/<step>/attempt-NNN/verdict.yaml` | step の verdict |
| `progress.md` / `session-state.json` | 進捗・再開用 state |

- `kaji run` は進捗を **stdout にも** 流す。`.kaji/artifacts/` に完全なログが残るため、
  通常はリダイレクト不要
- stdout を別途ファイルに残したい場合は、**repository 直下に置かない**。repo 直下の未追跡
  ファイルは `issue-close` の安全ガードが検知して merge を中断する。scratch 用の `tmp/`
  （gitignored）か repository 外に出力する。念のため `.gitignore` は `*.log` も無視する

failure triage は既定で有効だが、自動再開は無効。`scripts/setup_labels.sh` は triage が GitHub Issue を集約できるよう `incident` ラベル群も作成する。詳細は kaji 本体の [Failure Triage / Recovery guide](https://github.com/apokamo/kaji/blob/main/docs/cli-guides/failure-recovery.md) を参照。

## `.kaji/config.local.toml`（gitignored）

machine-local な overlay。`uv run kaji local init` が生成し、provider 切替
（github ⇄ local）や machine_id を保持する。手書きせず CLI に任せる。commit 禁止。
`[incident]` は overlay の対象外（tracked の `.kaji/config.toml` のみ読む）。local provider と
`kaji local init` / `kaji sync` は kaji v0.21.0 で deprecated（stderr に警告。当面は利用可能）。

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
