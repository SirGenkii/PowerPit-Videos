"""Core physics simulation for Power Pit (M1)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from .scene import ArenaConfig, SceneConfig, TeamConfig

Vec2 = np.ndarray

DT = 1.0 / 120.0  # simulation tick (120 Hz)


@dataclass
class Bumper:
    position: Vec2
    radius: float
    restitution: float


@dataclass
class BallState:
    """Current state of a simulated ball."""

    team_index: int
    team: TeamConfig
    name: str
    position: Vec2
    velocity: Vec2
    radius: float
    mass: float

    def copy(self) -> "BallState":
        return BallState(
            team_index=self.team_index,
            team=self.team,
            name=self.name,
            position=self.position.copy(),
            velocity=self.velocity.copy(),
            radius=self.radius,
            mass=self.mass,
        )


@dataclass
class SimulationSnapshot:
    """State of the simulation for a given frame."""

    frame_index: int
    time: float
    balls: list[BallState]


class Simulation:
    """Handle the physics integration for a scene."""

    def __init__(self, scene: SceneConfig):
        self.scene = scene
        self.time = 0.0
        self.arena = scene.arena
        self.friction = scene.friction
        self.restitution = scene.restitution

        self.balls: list[BallState] = []
        self.bumpers: list[Bumper] = []
        self._build_balls(scene.teams, scene.ball_radius, scene.ball_mass)
        self._build_bumpers(scene.arena)

    # ------------------------------------------------------------------ utils
    def _build_balls(self, teams: Sequence[TeamConfig], radius: float, mass: float) -> None:
        for team_index, team in enumerate(teams):
            for player in team.players:
                spawn = np.array(player.spawn, dtype=float)
                velocity = (
                    np.array(player.velocity, dtype=float)
                    if player.velocity is not None
                    else np.zeros(2, dtype=float)
                )
                self.balls.append(
                    BallState(
                        team_index=team_index,
                        team=team,
                        name=player.name,
                        position=spawn,
                        velocity=velocity,
                        radius=radius,
                        mass=mass,
                    )
                )

    def _build_bumpers(self, arena: ArenaConfig) -> None:
        for bumper in arena.bumpers:
            self.bumpers.append(
                Bumper(
                    position=np.array(bumper.position, dtype=float),
                    radius=float(bumper.radius),
                    restitution=float(bumper.restitution),
                )
            )

    # ----------------------------------------------------------------- stepping
    def step(self) -> None:
        """Advance the simulation by a fixed tick."""

        for ball in self.balls:
            ball.velocity *= self.friction
            ball.position += ball.velocity * DT

        self._solve_ball_ball()
        self._solve_arena_walls()
        self._solve_bumpers()

        self.time += DT

    def capture(self, frame_index: int) -> SimulationSnapshot:
        return SimulationSnapshot(
            frame_index=frame_index,
            time=self.time,
            balls=[ball.copy() for ball in self.balls],
        )

    # ------------------------------------------------------------ collision
    def _solve_ball_ball(self) -> None:
        restitution = self.restitution
        count = len(self.balls)
        for i in range(count):
            a = self.balls[i]
            for j in range(i + 1, count):
                b = self.balls[j]
                delta = b.position - a.position
                dist_sq = float(np.dot(delta, delta))
                min_dist = a.radius + b.radius
                if dist_sq >= min_dist * min_dist:
                    continue

                dist = float(np.sqrt(dist_sq))
                if dist <= 1e-9:
                    normal = np.array([1.0, 0.0], dtype=float)
                else:
                    normal = delta / dist

                penetration = min_dist - dist
                total_inv_mass = 1.0 / a.mass + 1.0 / b.mass
                correction = normal * (penetration / total_inv_mass)
                a.position -= correction * (1.0 / a.mass)
                b.position += correction * (1.0 / b.mass)

                rel_vel = float(np.dot(b.velocity - a.velocity, normal))
                if rel_vel > 0:
                    continue

                impulse_mag = -(1.0 + restitution) * rel_vel
                impulse_mag /= total_inv_mass
                impulse = normal * impulse_mag
                a.velocity -= impulse * (1.0 / a.mass)
                b.velocity += impulse * (1.0 / b.mass)

    def _solve_arena_walls(self) -> None:
        if self.arena.type == "circle":
            self._solve_circle_walls()
        elif self.arena.type == "stadium":
            self._solve_stadium_walls()
        else:  # pragma: no cover - guarded earlier
            raise RuntimeError(f"Type d'arène non géré: {self.arena.type}")

    def _solve_circle_walls(self) -> None:
        assert self.arena.radius is not None
        arena_radius = float(self.arena.radius)
        for ball in self.balls:
            center_dist = float(np.linalg.norm(ball.position))
            limit = arena_radius - ball.radius
            if center_dist <= limit:
                continue

            if center_dist <= 1e-9:
                normal = np.array([1.0, 0.0], dtype=float)
            else:
                normal = ball.position / center_dist
            penetration = center_dist - limit
            ball.position -= normal * penetration

            vel_along_normal = float(np.dot(ball.velocity, normal))
            if vel_along_normal > 0:
                ball.velocity -= normal * vel_along_normal * (1.0 + self.restitution)

    def _solve_stadium_walls(self) -> None:
        assert self.arena.width is not None
        assert self.arena.height is not None
        assert self.arena.corner_radius is not None

        half_width = float(self.arena.width) / 2.0
        half_height = float(self.arena.height) / 2.0
        corner_radius = float(self.arena.corner_radius)

        flat_width = half_width - corner_radius
        flat_height = half_height - corner_radius
        if flat_width < 0 or flat_height < 0:
            raise RuntimeError("Paramètres 'stadium' invalides: corner_radius trop grand.")

        for ball in self.balls:
            px, py = float(ball.position[0]), float(ball.position[1])

            # Top/bottom flat sections
            if abs(px) <= flat_width:
                limit = half_height - ball.radius
                if py > limit:
                    penetration = py - limit
                    normal = np.array([0.0, 1.0])
                    ball.position[1] -= penetration
                    self._reflect_velocity(ball, normal)
                    continue
                if py < -limit:
                    penetration = -limit - py
                    normal = np.array([0.0, -1.0])
                    ball.position[1] += penetration
                    self._reflect_velocity(ball, normal)
                    continue

            # Left/right flat sections
            if abs(py) <= flat_height:
                limit = half_width - ball.radius
                if px > limit:
                    penetration = px - limit
                    normal = np.array([1.0, 0.0])
                    ball.position[0] -= penetration
                    self._reflect_velocity(ball, normal)
                    continue
                if px < -limit:
                    penetration = -limit - px
                    normal = np.array([-1.0, 0.0])
                    ball.position[0] += penetration
                    self._reflect_velocity(ball, normal)
                    continue

            # Corner sections
            corner_x = np.clip(px, -flat_width, flat_width)
            corner_y = np.clip(py, -flat_height, flat_height)
            corner_center = np.array([corner_x, corner_y], dtype=float)
            if abs(px) > flat_width:
                corner_center[0] = np.sign(px) * flat_width
            if abs(py) > flat_height:
                corner_center[1] = np.sign(py) * flat_height

            direction = ball.position - corner_center
            dist = float(np.linalg.norm(direction))
            limit = corner_radius - ball.radius
            if dist <= limit:
                continue

            if dist <= 1e-9:
                normal = np.array([1.0, 0.0])
            else:
                normal = direction / dist
            penetration = dist - limit
            ball.position -= normal * penetration
            self._reflect_velocity(ball, normal)

    def _solve_bumpers(self) -> None:
        for bumper in self.bumpers:
            for ball in self.balls:
                delta = ball.position - bumper.position
                dist = float(np.linalg.norm(delta))
                limit = bumper.radius + ball.radius
                if dist >= limit:
                    continue

                if dist <= 1e-9:
                    normal = np.array([1.0, 0.0])
                else:
                    normal = delta / dist
                penetration = limit - dist
                ball.position += normal * penetration

                vel_along_normal = float(np.dot(ball.velocity, normal))
                if vel_along_normal < 0:
                    ball.velocity -= normal * vel_along_normal * (1.0 + bumper.restitution)

    def _reflect_velocity(self, ball: BallState, normal: Vec2) -> None:
        vel_along_normal = float(np.dot(ball.velocity, normal))
        if vel_along_normal > 0:
            ball.velocity -= normal * vel_along_normal * (1.0 + self.restitution)


def simulate_frames(scene: SceneConfig) -> Iterable[SimulationSnapshot]:
    """Iterate over snapshots matching the scene frame rate."""

    simulation = Simulation(scene)
    steps_per_frame = max(1, int(round((1.0 / scene.frame_rate) / DT)))
    frame_time = 1.0 / scene.frame_rate

    for frame_index in range(scene.frame_count):
        for _ in range(steps_per_frame):
            simulation.step()
        # Align simulation time with captured frame
        simulation.time = (frame_index + 1) * frame_time
        yield simulation.capture(frame_index)
