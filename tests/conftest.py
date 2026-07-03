"""worktree 自身の ``src/`` を import path 先頭に置く。

kaji の worktree 分離開発では、worktree の ``.venv`` は親 repo の ``.venv`` への
symlink であり、editable install（``starter-app``）は親 repo の ``src/`` を指す。
そのままでは worktree 内テストが親 repo のコードを import してしまい、worktree の
変更を検証できない。ローカル ``src/`` を ``sys.path`` 先頭に挿入してこれを防ぐ。

package を rename した場合もこの仕組みはそのまま機能する（``src/`` 直下を優先する
だけで、package 名に依存しない）。
"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
