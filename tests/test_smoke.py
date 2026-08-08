"""Smoke tests: the package imports and exposes its version.

These cover the package `__init__` so the coverage gate passes during the
bootstrap phase (no application modules yet). They must stay green forever;
application tests live in `tests/` mirroring `src/fortress_tui/`.
"""

from __future__ import annotations

import fortress_tui


def test_package_imports() -> None:
    assert fortress_tui is not None


def test_version_exposed() -> None:
    assert isinstance(fortress_tui.__version__, str)
    assert fortress_tui.__version__ == "0.1.0"
