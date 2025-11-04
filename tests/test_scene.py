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
duration_seconds: 8
frame_rate: 60
arena:
  type: circle
  radius: 6.0
  bumpers:
    - position: [1.0, 0.0]
      radius: 0.5
teams:
  - name: Team A
    color: "#FF0000"
    players:
      - name: Alpha
        spawn: [0.0, 0.0]
        velocity: [1.0, 0.0]
  - name: Team B
    color: "#00FF00"
    players:
      - name: Beta
        spawn: [1.5, 0.0]
"""
    yaml_file = tmp_path / "scene.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    scene = load_scene_config(yaml_file)
    assert scene.name == "Demo"
    assert scene.frame_rate == 60
    assert scene.arena.type == "circle"
    assert len(scene.teams) == 2
    assert scene.teams[0].players[0].velocity == (1.0, 0.0)
    assert scene.arena.bumpers[0].radius == 0.5


def test_load_scene_invalid_arena(tmp_path: Path) -> None:
    yaml_content = """
name: Demo
arena:
  type: hexagon
teams:
  - name: A
    color: "#FFFFFF"
    players:
      - spawn: [0, 0]
  - name: B
    color: "#000000"
    players:
      - spawn: [1, 0]
"""
    yaml_file = tmp_path / "scene.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(SceneConfigError):
        load_scene_config(yaml_file)


def test_load_scene_requires_players(tmp_path: Path) -> None:
    yaml_content = """
name: Demo
arena:
  type: circle
  radius: 5
teams:
  - name: A
    color: "#FF00FF"
  - name: B
    color: "#00FFFF"
    players:
      - spawn: [1, 0]
"""
    yaml_file = tmp_path / "scene.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    with pytest.raises(SceneConfigError):
        load_scene_config(yaml_file)


if __name__ == "__main__":  # pragma: no cover - convenience execution
    raise SystemExit(pytest.main([__file__]))
