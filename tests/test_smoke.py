"""Smoke tests: fresh repo で `make check` が通ることを保証する最小テスト。"""

import pytest

from starter_app import __version__, hello


@pytest.mark.small
def test_import() -> None:
    assert __version__


@pytest.mark.small
def test_hello() -> None:
    assert hello() == "Hello from starter_app!"
