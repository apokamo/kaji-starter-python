"""`scripts/set_agent.py` の所有権契約テスト。

kaji v0.17.0 以降、`.kaji/wf/official/**` は kaji 所有で下流リポジトリは直接編集しない。
agent 寄せ替えがこの契約を破らないこと（official を書き換えず custom へ派生を作ること）を
回帰テストとして固定する。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"


def _load_set_agent() -> ModuleType:
    """`scripts/` は package ではないため file path から読み込む。"""
    spec = importlib.util.spec_from_file_location("set_agent", _SCRIPTS / "set_agent.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["set_agent"] = module
    spec.loader.exec_module(module)
    return module


set_agent = _load_set_agent()

OFFICIAL_DEV = """name: dev
description: "dev workflow"
execution_policy: auto

steps:
  - id: design
    skill: issue-design
    agent: claude
    model: opus
    effort: high
  - id: pr
    skill: i-pr
    agent: claude
    model: sonnet
"""

# official 由来の派生先（custom/dev/dev-codex.yaml）と同名の手動管理ファイル。
# codex 変換で agent / model / effort がすべて書き換わる値を持たせ、「変換対象を含むのに
# 触られない」ことを検査できるようにする（byte 一致が偶然にならないようにする）。
MANUAL_DEV_CODEX = """name: dev-codex
description: "手動管理の codex 版 dev workflow"
execution_policy: auto

steps:
  - id: design
    skill: issue-design
    agent: claude
    model: opus
    effort: max
"""

CUSTOM_THOROUGH = """name: dev-thorough
description: "dev workflow (thorough)"
execution_policy: auto

steps:
  - id: design
    skill: issue-design
    agent: claude
    model: opus
    effort: max
"""


@pytest.fixture
def wf_dir(tmp_path: Path) -> Path:
    """starter と同じ official / custom レイアウトの workflow tree を作る。"""
    root = tmp_path / ".kaji" / "wf"
    (root / "official").mkdir(parents=True)
    (root / "custom" / "dev").mkdir(parents=True)
    (root / "official" / "dev.yaml").write_text(OFFICIAL_DEV, encoding="utf-8")
    (root / "custom" / "dev" / "dev-thorough.yaml").write_text(CUSTOM_THOROUGH, encoding="utf-8")
    return root


def _apply(writes: list[Any]) -> None:
    """`plan_conversions` の計画を実際に書き込む（script の Phase 2 相当）。"""
    for item in writes:
        item.path.parent.mkdir(parents=True, exist_ok=True)
        item.path.write_text(item.content, encoding="utf-8")


@pytest.mark.medium
def test_official_is_never_written(wf_dir: Path) -> None:
    before = (wf_dir / "official" / "dev.yaml").read_text(encoding="utf-8")

    writes, errors, _ = set_agent.plan_conversions(wf_dir, "codex")
    _apply(writes)

    assert errors == []
    assert all(wf_dir / "official" not in item.path.parents for item in writes)
    assert (wf_dir / "official" / "dev.yaml").read_text(encoding="utf-8") == before


@pytest.mark.medium
def test_official_conversion_becomes_custom_derivative(wf_dir: Path) -> None:
    writes, errors, _ = set_agent.plan_conversions(wf_dir, "codex")
    _apply(writes)

    derived = wf_dir / "custom" / "dev" / "dev-codex.yaml"
    assert errors == []
    assert derived.exists()
    text = derived.read_text(encoding="utf-8")
    assert text.startswith(set_agent.GENERATED_MARK)
    # name は filename stem と一致させる（kaji の不変条件）
    assert "\nname: dev-codex\n" in text
    assert "    agent: codex\n" in text
    assert "    agent: claude\n" not in text
    assert "    model: gpt-5.5\n" in text


@pytest.mark.medium
def test_custom_is_converted_in_place(wf_dir: Path) -> None:
    writes, errors, _ = set_agent.plan_conversions(wf_dir, "codex")
    _apply(writes)

    thorough = (wf_dir / "custom" / "dev" / "dev-thorough.yaml").read_text(encoding="utf-8")
    assert errors == []
    assert "    agent: codex\n" in thorough
    assert "name: dev-thorough\n" in thorough
    # codex に max は無いため対応表で xhigh へ落ちる
    assert "    effort: xhigh\n" in thorough


@pytest.mark.medium
def test_no_derivative_when_official_already_matches(wf_dir: Path) -> None:
    writes, errors, notices = set_agent.plan_conversions(wf_dir, "claude")

    assert errors == []
    assert [item.path for item in writes] == [wf_dir / "custom" / "dev" / "dev-thorough.yaml"]
    assert not (wf_dir / "custom" / "dev" / "dev-claude.yaml").exists()
    assert any("派生を作らない" in notice for notice in notices)


@pytest.mark.medium
def test_manually_managed_custom_file_is_not_overwritten(wf_dir: Path) -> None:
    manual = wf_dir / "custom" / "dev" / "dev-codex.yaml"
    manual.write_text(MANUAL_DEV_CODEX, encoding="utf-8")
    # fixture が変換対象 field を持つこと自体を担保する（no-op fixture だと
    # 「触られない」を byte 一致だけで確認しても意味が無くなる）
    converted, _, _ = set_agent.convert_text(MANUAL_DEV_CODEX, "codex", str(manual))
    assert converted != MANUAL_DEV_CODEX

    writes, errors, notices = set_agent.plan_conversions(wf_dir, "codex")
    _apply(writes)

    assert errors == []
    # write plan 自体に含まれない（official 由来の派生生成も custom の in-place 変換も無い）
    assert manual not in [item.path for item in writes]
    assert manual.read_text(encoding="utf-8") == MANUAL_DEV_CODEX
    assert any("手動管理" in notice for notice in notices)


@pytest.mark.medium
def test_conversion_is_idempotent(wf_dir: Path) -> None:
    _apply(set_agent.plan_conversions(wf_dir, "codex")[0])
    snapshot = {p: p.read_text(encoding="utf-8") for p in sorted(wf_dir.rglob("*.yaml"))}

    _apply(set_agent.plan_conversions(wf_dir, "codex")[0])

    assert {p: p.read_text(encoding="utf-8") for p in sorted(wf_dir.rglob("*.yaml"))} == snapshot


@pytest.mark.medium
def test_other_cli_variant_is_left_alone(wf_dir: Path) -> None:
    variant = wf_dir / "custom" / "dev" / "dev-claude.yaml"
    variant.write_text(CUSTOM_THOROUGH.replace("dev-thorough", "dev-claude"), encoding="utf-8")

    writes, errors, notices = set_agent.plan_conversions(wf_dir, "codex")

    assert errors == []
    assert variant not in [item.path for item in writes]
    assert any("別 CLI 向けの変種" in notice for notice in notices)
