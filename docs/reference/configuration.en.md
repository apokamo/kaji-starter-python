# Configuration

> 日本語版: [configuration.md](configuration.md)

Responsibility split between `.kaji/config.toml` and `.env`.

## `.kaji/config.toml` (tracked)

Repository-wide settings for kaji. The authoritative spec for every key lives in kaji itself:
[configuration.md](https://github.com/apokamo/kaji/blob/main/docs/reference/configuration.md).

| key | Value in this repository | Notes |
|-----|--------------------------|-------|
| `paths.artifacts_dir` | `.kaji/artifacts` | Output location for run logs / records (gitignored; see § Run log output location) |
| `paths.skill_dir` | `.claude/skills` | Location of the canonical skills |
| `paths.design_dir` | unset (`draft/design`) | Location of design documents (repository-relative path). To change it, enable the commented example in `.kaji/config.toml` |
| `execution.default_timeout` | `2400` | Per-step timeout in seconds |
| `execution.agent_runner` | `headless` | Set to `interactive_terminal` to run the agent in a terminal pane (the `herdr` backend must run inside a Herdr 0.8.2+ pane; the deprecated tmux backend must run inside a tmux 3.1+ session; `headless` needs no terminal) |
| `execution.interactive_terminal_backend` | unset (`tmux`) | Backend used when `agent_runner = "interactive_terminal"`: `herdr` (recommended; only starts inside a Herdr 0.8.2+ pane; tmux is not needed) or `tmux` (the default when unset, requires tmux 3.1+). **The tmux backend is deprecated since kaji v0.23.0** (`kaji run` warns on stderr; it will be removed in a subsequent release). To use the interactive terminal, set `herdr` explicitly or move to `headless`. See [tmux backend deprecation](https://github.com/apokamo/kaji/blob/main/docs/cli-guides/interactive-terminal-runner.md#tmux-backend-deprecation) in kaji |
| `execution.failure_triage` | `true` (default) | Classifies ERROR and eligible ABORT results, then records evidence comments, artifacts, and incident aggregation |
| `execution.auto_recover` | `false` (default) | Opt-in to allow one automatic resume per recovery chain |
| `incident.kind_label` / `initial_status_label` / `transient_label` | `incident` / `incident:investigating` / `incident:cause:transient` | Label names triage uses for incident Issues. kaji v0.21.0 changed the defaults to the `kaji:incident` family, so the old names created by `scripts/setup_labels.sh` are set explicitly |
| `provider.type` | `github` | Repository's default provider. kaji supports only `github` (`local` was removed in kaji v0.23.0 and is now a configuration error) |
| `provider.github.repo` | `<owner>/<repo>` | **Must be replaced when using the template, and committed before running any workflow** (if left uncommitted, the setting change leaks into your first feature PR) |
| `provider.github.default_branch` | `main` | |
| `provider.github.git_remote` | `origin` | Remote used for git push / fetch inside skills |

## Run log output location

`kaji run` writes its execution records in a structured form under
**`.kaji/artifacts/<issue>/` (gitignored)**. The location is defined by `paths.artifacts_dir`
(default `.kaji/artifacts`).

| Path | Contents |
|------|----------|
| `runs/<timestamp>/run.log` | The complete log for that run |
| `runs/<timestamp>/steps/<step>/attempt-NNN/console.log` / `stdout.log` | Per-step agent output |
| `runs/<timestamp>/steps/<step>/attempt-NNN/verdict.yaml` | The step's verdict |
| `progress.md` / `session-state.json` | Progress / resume state |

- `kaji run` also streams progress to **stdout**. Since the complete log is kept under
  `.kaji/artifacts/`, redirecting it is normally unnecessary.
- If you want to keep stdout in a separate file, **do not place it at the repository root**.
  An untracked file at the repo root is detected by the `issue-close` safety guard and aborts
  the merge. Write it to the scratch `tmp/` directory (gitignored) or outside the repository.
  As a safety net, `.gitignore` also ignores `*.log`.

Failure triage is enabled by default, while automatic recovery is disabled.
`scripts/setup_labels.sh` also creates the `incident` label family so triage can aggregate
GitHub Issues. See kaji's
[Failure Triage / Recovery guide](https://github.com/apokamo/kaji/blob/main/docs/cli-guides/failure-recovery.md)
for details.

## `.kaji/config.local.toml` (gitignored)

A per-user overlay. Create it by hand when you need machine-specific values; it overrides only
`[execution]` / `[provider]` values, per key. `[paths]` / `[incident]` are not overlaid (only the
tracked `.kaji/config.toml` is read). Never commit it. `git worktree add` does not carry it over, so
`issue-start` symlinks the main overlay into the worktree.

## `.env` / `.env.example`

- Put secrets / environment variables used by the application in `.env` (gitignored)
- Keep the template in `.env.example` (tracked), without real values
- Never hardcode secrets in code or config files

## Tracked / ignored under `.kaji/`

| Path | Handling | Reason |
|------|----------|--------|
| `.kaji/config.toml` / `.kaji/wf/` | tracked | Repository-wide settings / workflow definitions |
| `.kaji/artifacts/` | ignored | Run logs (they grow large) |
| `.kaji/config.local.toml` | ignored | Per-user overlay |
