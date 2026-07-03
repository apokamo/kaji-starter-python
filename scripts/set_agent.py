#!/usr/bin/env python3
"""workflow YAML の agent / model / effort を指定 CLI へ一括変換する。

Usage:
    uv run python scripts/set_agent.py <cli>    # cli: claude | codex | gemini

.kaji/wf/*.yaml の各 step の `agent:` / `model:` 行を、下記対応表に従い
指定 CLI の値へ決定的に書き換える。行単位置換でコメント・構造を保持する。
同じ CLI 指定で再実行しても差分ゼロ（冪等）。

- model は step の役割 tier（heavy / light）で決まる。effort は workflow ごとの
  チューニング値（dev-thorough の xhigh 等）なので、対象 CLI で無効な値でない限り
  変更しない
- CLI 間の model / effort 対応表は本 script 内が正本。ガイドの表はここから転記する
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WF_DIR = Path(".kaji/wf")

# CLI → tier → model の対応表（正本）
MODEL_MAP: dict[str, dict[str, str]] = {
    "claude": {"heavy": "opus", "light": "sonnet"},
    "codex": {"heavy": "gpt-5.5", "light": "gpt-5.5"},
    "gemini": {"heavy": "gemini-3-pro", "light": "gemini-3-flash"},
}

# CLI ごとの effort 許容値。無効値を検出したら対応表で置換する
EFFORT_ALLOWED: dict[str, set[str]] = {
    "claude": {"low", "medium", "high", "xhigh", "max"},
    "codex": {"none", "minimal", "low", "medium", "high", "xhigh"},
    "gemini": {"low", "medium", "high", "xhigh"},
}
EFFORT_FALLBACK: dict[str, dict[str, str]] = {
    "codex": {"max": "xhigh"},
    "gemini": {"max": "xhigh", "none": "low", "minimal": "low"},
}

# 軽量級 step（それ以外は heavy 扱い。未知の step id も heavy に倒す）
LIGHT_STEPS: set[str] = {"start", "pr", "close"}

STEP_ID_RE = re.compile(r"^  - id: (\S+)\s*$")
AGENT_RE = re.compile(r"^    agent: (\S+)\s*$")
MODEL_RE = re.compile(r"^    model: (\S+)\s*$")
EFFORT_RE = re.compile(r"^    effort: (\S+)\s*$")


def tier_of(step_id: str) -> str:
    return "light" if step_id in LIGHT_STEPS else "heavy"


def convert_file(path: Path, cli: str) -> tuple[int, list[str]]:
    """1 ファイルを変換し、(書き換えた step 数, エラーリスト) を返す。"""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    errors: list[str] = []
    changed_steps: set[str] = set()
    current_step = ""

    for lineno, line in enumerate(lines, start=1):
        stripped = line.rstrip("\n")
        if m := STEP_ID_RE.match(stripped):
            current_step = m.group(1)
        elif m := AGENT_RE.match(stripped):
            value = m.group(1)
            if value not in MODEL_MAP:
                errors.append(f"{path}:{lineno}: 想定外の agent 値 '{value}'")
            elif value != cli:
                line = f"    agent: {cli}\n"
                changed_steps.add(current_step)
        elif m := MODEL_RE.match(stripped):
            target = MODEL_MAP[cli][tier_of(current_step)]
            if m.group(1) != target:
                line = f"    model: {target}\n"
                changed_steps.add(current_step)
        elif m := EFFORT_RE.match(stripped):
            value = m.group(1)
            if value not in EFFORT_ALLOWED[cli]:
                replacement = EFFORT_FALLBACK.get(cli, {}).get(value)
                if replacement is None:
                    errors.append(f"{path}:{lineno}: effort '{value}' は {cli} で無効")
                else:
                    line = f"    effort: {replacement}\n"
                    changed_steps.add(current_step)
        out.append(line)

    if not errors:
        path.write_text("".join(out), encoding="utf-8")
    return len(changed_steps), errors


def main() -> int:
    args = sys.argv[1:]
    if len(args) != 1 or args[0] not in MODEL_MAP:
        known = " | ".join(MODEL_MAP)
        print(f"usage: python scripts/set_agent.py <{known}>", file=sys.stderr)
        return 2

    cli = args[0]
    yaml_files = sorted(WF_DIR.glob("*.yaml"))
    if not yaml_files:
        print(f"error: {WF_DIR}/*.yaml が見つからない", file=sys.stderr)
        return 1

    all_errors: list[str] = []
    total_steps = 0
    for path in yaml_files:
        n_steps, errors = convert_file(path, cli)
        all_errors.extend(errors)
        total_steps += n_steps
        status = f"{n_steps} steps updated" if n_steps else "no change"
        print(f"{path}: {status}")

    if all_errors:
        print("\n変換エラー（ファイルは書き換え済みのものを除き未変更）:", file=sys.stderr)
        for err in all_errors:
            print(f"  {err}", file=sys.stderr)
        return 1

    print(f"\n{len(yaml_files)} files processed, {total_steps} steps updated (agent={cli})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
