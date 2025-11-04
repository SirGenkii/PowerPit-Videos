from __future__ import annotations

from pathlib import Path
import sys

import pytest

if __package__ is None or __package__ == "":  # Direct execution support
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from powerpit.scene import SceneConfigError, load_scene_config


def test_load_scene_success(tmp_path: Path) -> None:
    yaml_content = """
name: Demo
arena:
  type: circle
"""
    yaml_file = tmp_path / "scene.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    scene = load_scene_config(yaml_file)
    assert scene.name == "Demo"
    assert scene.frame_rate == 30
    assert scene.arena.type == "circle"


def test_load_scene_invalid_arena(tmp_path: Path) -> None:
    yaml_content = """
name: Demo
arena:
  type: hexagon
"""
    yaml_file = tmp_path / "scene.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(SceneConfigError):
        load_scene_config(yaml_file)


if __name__ == "__main__":  # pragma: no cover - convenience execution
    raise SystemExit(pytest.main([__file__]))
