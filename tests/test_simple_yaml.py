from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":  # Direct execution support
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from powerpit.simple_yaml import safe_load


def test_list_of_mappings() -> None:
    content = """
teams:
  - name: Alpha
    color: "#FFFFFF"
  - name: Beta
    color: "#000000"
"""
    data = safe_load(content)
    assert isinstance(data, dict)
    assert len(data["teams"]) == 2
    assert data["teams"][0]["name"] == "Alpha"


if __name__ == "__main__":  # pragma: no cover - convenience execution
    import pytest

    raise SystemExit(pytest.main([__file__]))
