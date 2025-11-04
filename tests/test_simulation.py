from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pytest

if __package__ is None or __package__ == "":  # Direct execution support
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from powerpit.scene import (
    ArenaConfig,
    PlayerConfig,
    SceneConfig,
    TeamConfig,
)
from powerpit.simulation import Simulation


def _make_scene(arena: ArenaConfig, teams: list[TeamConfig]) -> SceneConfig:
    return SceneConfig(
        name="Test",
        duration_seconds=2.0,
        frame_rate=30,
        arena=arena,
        teams=teams,
        ball_radius=0.4,
        ball_mass=1.0,
        friction=0.999,
        restitution=0.98,
    )


def test_circle_wall_bounce() -> None:
    arena = ArenaConfig(type="circle", radius=5.0)
    teams = [
        TeamConfig(
            name="A",
            color=(255, 0, 0),
            players=[PlayerConfig(name="A1", spawn=(4.4, 0.0), velocity=(2.5, 0.0))],
        ),
        TeamConfig(
            name="B",
            color=(0, 255, 0),
            players=[PlayerConfig(name="B1", spawn=(-4.4, 0.0), velocity=(-2.5, 0.0))],
        ),
    ]
    scene = _make_scene(arena, teams)
    sim = Simulation(scene)

    for _ in range(30):  # advance ~0.25 s
        sim.step()

    left = sim.balls[1]
    right = sim.balls[0]
    assert np.linalg.norm(left.position) < arena.radius
    assert np.linalg.norm(right.position) < arena.radius
    assert right.velocity[0] < 0  # bounced inward
    assert left.velocity[0] > 0


def test_ball_ball_collision_exchanges_velocity() -> None:
    arena = ArenaConfig(type="circle", radius=6.0)
    teams = [
        TeamConfig(
            name="A",
            color=(255, 0, 0),
            players=[PlayerConfig(name="A1", spawn=(-1.0, 0.0), velocity=(3.0, 0.0))],
        ),
        TeamConfig(
            name="B",
            color=(0, 255, 0),
            players=[PlayerConfig(name="B1", spawn=(1.0, 0.0), velocity=(-3.0, 0.0))],
        ),
    ]
    scene = _make_scene(arena, teams)
    sim = Simulation(scene)

    for _ in range(40):
        sim.step()

    vel_a = sim.balls[0].velocity[0]
    vel_b = sim.balls[1].velocity[0]
    assert vel_a < 0  # A should head left after collision
    assert vel_b > 0  # B should head right


def test_stadium_corner_collision() -> None:
    arena = ArenaConfig(type="stadium", width=12.0, height=8.0, corner_radius=2.0)
    teams = [
        TeamConfig(
            name="A",
            color=(255, 0, 0),
            players=[PlayerConfig(name="A1", spawn=(4.5, 3.0), velocity=(2.5, 1.5))],
        ),
        TeamConfig(
            name="B",
            color=(0, 255, 0),
            players=[PlayerConfig(name="B1", spawn=(-4.5, -3.0), velocity=(-2.5, -1.5))],
        ),
    ]
    scene = _make_scene(arena, teams)
    sim = Simulation(scene)

    for _ in range(80):
        sim.step()

    ball = sim.balls[0]
    assert abs(ball.position[0]) < arena.width / 2 + 1e-6
    assert abs(ball.position[1]) < arena.height / 2 + 1e-6
    assert ball.velocity[0] < 0
    assert ball.velocity[1] < 0


if __name__ == "__main__":  # pragma: no cover - convenience execution
    raise SystemExit(pytest.main([__file__]))
