"""Scene configuration loading and validation for Power Pit."""
from __future__ import annotations
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .simple_yaml import safe_load


class SceneConfigError(RuntimeError):
    """Raised when the scene configuration is invalid."""


@dataclass
class ArenaConfig:
    """Basic arena definition.

    M1 enrichit cette structure pour décrire la géométrie utilisée par la
    simulation.
    """

    type: str
    radius: float | None = None
    width: float | None = None
    height: float | None = None
    corner_radius: float | None = None
    bumpers: list["BumperConfig"] = field(default_factory=list)

    @property
    def horizontal_span(self) -> float:
        """Return the arena width in simulation units."""

        if self.type == "circle":
            if self.radius is None:
                raise SceneConfigError("Champ 'radius' requis pour l'arène 'circle'.")
            return self.radius * 2
        if self.type == "stadium":
            if self.width is None:
                raise SceneConfigError("Champ 'width' requis pour l'arène 'stadium'.")
            return self.width
        if self.type == "donut":
            raise SceneConfigError("L'arène 'donut' n'est pas encore supportée.")
        raise SceneConfigError(f"Type d'arène inconnu: {self.type}")

    @property
    def vertical_span(self) -> float:
        """Return the arena height in simulation units."""

        if self.type == "circle":
            if self.radius is None:
                raise SceneConfigError("Champ 'radius' requis pour l'arène 'circle'.")
            return self.radius * 2
        if self.type == "stadium":
            if self.height is None:
                raise SceneConfigError("Champ 'height' requis pour l'arène 'stadium'.")
            return self.height
        if self.type == "donut":
            raise SceneConfigError("L'arène 'donut' n'est pas encore supportée.")
        raise SceneConfigError(f"Type d'arène inconnu: {self.type}")


@dataclass
class BumperConfig:
    position: tuple[float, float]
    radius: float
    restitution: float


@dataclass
class PlayerConfig:
    """Player/balle initiale."""

    name: str
    spawn: tuple[float, float]
    velocity: tuple[float, float] | None = None


@dataclass
class TeamConfig:
    """Team definition."""

    name: str
    color: tuple[int, int, int]
    players: list[PlayerConfig]


@dataclass
class SceneConfig:
    """Top-level scene configuration."""

    name: str
    duration_seconds: float
    frame_rate: int
    arena: ArenaConfig
    teams: list[TeamConfig]
    ball_radius: float
    ball_mass: float
    friction: float
    restitution: float

    @property
    def frame_count(self) -> int:
        return int(round(self.duration_seconds * self.frame_rate))


SUPPORTED_ARENAS = {"circle", "stadium"}
DEFAULT_FRAME_RATE = 30
DEFAULT_DURATION = 10.0
DEFAULT_BALL_RADIUS = 0.45
DEFAULT_BALL_MASS = 1.0
DEFAULT_FRICTION = 0.995
DEFAULT_RESTITUTION = 0.98
DEFAULT_BUMPER_RESTITUTION = 1.35


def load_scene_config(path: str | Path) -> SceneConfig:
    """Load and validate a scene configuration from YAML."""

    scene_path = Path(path)
    if not scene_path.exists():
        raise SceneConfigError(f"Scene YAML introuvable: {scene_path}")

    with scene_path.open("r", encoding="utf-8") as handle:
        data = safe_load(handle.read())

    if not isinstance(data, Mapping):
        raise SceneConfigError("Le YAML de scène doit contenir un mapping racine.")

    name = _require_str(data, "name")
    duration = _get_float(data, "duration_seconds", DEFAULT_DURATION)
    frame_rate = _get_int(data, "frame_rate", DEFAULT_FRAME_RATE)

    arena_info = data.get("arena")
    arena = _parse_arena(arena_info)

    teams_info = data.get("teams")
    teams = _parse_teams(teams_info)

    ball_radius = _get_float(data, "ball_radius", DEFAULT_BALL_RADIUS)
    ball_mass = _get_float(data, "ball_mass", DEFAULT_BALL_MASS)
    friction = _get_float(data, "friction", DEFAULT_FRICTION)
    restitution = _get_float(data, "restitution", DEFAULT_RESTITUTION)

    return SceneConfig(
        name=name,
        duration_seconds=duration,
        frame_rate=frame_rate,
        arena=arena,
        teams=teams,
        ball_radius=ball_radius,
        ball_mass=ball_mass,
        friction=friction,
        restitution=restitution,
    )


def _require_str(data: Mapping[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise SceneConfigError(f"Champ '{field}' manquant ou vide.")
    return value


def _get_float(data: Mapping[str, Any], field: str, default: float) -> float:
    value = data.get(field, default)
    try:
        value = float(value)
    except (TypeError, ValueError) as exc:
        raise SceneConfigError(f"Champ '{field}' doit être un nombre réel.") from exc
    if value <= 0:
        raise SceneConfigError(f"Champ '{field}' doit être strictement positif.")
    return value


def _get_int(data: Mapping[str, Any], field: str, default: int) -> int:
    value = data.get(field, default)
    try:
        value = int(value)
    except (TypeError, ValueError) as exc:
        raise SceneConfigError(f"Champ '{field}' doit être un entier.") from exc
    if value <= 0:
        raise SceneConfigError(f"Champ '{field}' doit être strictement positif.")
    return value


def _parse_arena(info: Any) -> ArenaConfig:
    if not isinstance(info, Mapping):
        raise SceneConfigError("Champ 'arena' manquant ou invalide (doit être un mapping).")

    arena_type = _require_str(info, "type")
    if arena_type not in SUPPORTED_ARENAS:
        raise SceneConfigError(
            f"Type d'arène '{arena_type}' non supporté (options: {sorted(SUPPORTED_ARENAS)})."
        )

    bumpers_data = info.get("bumpers", [])
    bumpers: list[BumperConfig] = []
    if bumpers_data:
        if not isinstance(bumpers_data, Iterable):
            raise SceneConfigError("Le champ 'bumpers' doit être une liste de définitions.")
        for idx, raw in enumerate(bumpers_data):
            if not isinstance(raw, Mapping):
                raise SceneConfigError(f"Bumper #{idx} invalide: doit être un mapping.")
            position = _parse_vec2(raw, "position")
            radius = _get_float(raw, "radius", 0.6)
            restitution = _get_float(raw, "restitution", DEFAULT_BUMPER_RESTITUTION)
            bumpers.append(BumperConfig(position=position, radius=radius, restitution=restitution))

    if arena_type == "circle":
        radius = _get_float(info, "radius", 0.0)
        if radius <= 0:
            raise SceneConfigError("Le rayon de l'arène circulaire doit être > 0.")
        return ArenaConfig(type=arena_type, radius=radius, bumpers=bumpers)

    if arena_type == "stadium":
        width = _get_float(info, "width", 0.0)
        height = _get_float(info, "height", 0.0)
        if width <= 0 or height <= 0:
            raise SceneConfigError("Les dimensions de l'arène stadium doivent être > 0.")
        corner_radius = _get_float(info, "corner_radius", min(width, height) / 6)
        if corner_radius <= 0:
            raise SceneConfigError("'corner_radius' doit être > 0.")
        if corner_radius * 2 > min(width, height):
            raise SceneConfigError(
                "'corner_radius' doit être <= min(width, height) / 2 pour un stadium valide."
            )
        return ArenaConfig(
            type=arena_type,
            width=width,
            height=height,
            corner_radius=corner_radius,
            bumpers=bumpers,
        )

    raise SceneConfigError(f"Type d'arène '{arena_type}' non géré.")


def _parse_teams(info: Any) -> list[TeamConfig]:
    if not isinstance(info, Sequence) or not info:
        raise SceneConfigError("La scène doit définir au moins une équipe.")

    teams: list[TeamConfig] = []
    for team_idx, team_data in enumerate(info):
        if not isinstance(team_data, Mapping):
            raise SceneConfigError(f"Équipe #{team_idx} invalide: doit être un mapping.")
        name = _require_str(team_data, "name")
        color_value = _require_str(team_data, "color")
        color = _parse_color(color_value)
        players_field = team_data.get("players")
        if not isinstance(players_field, Sequence) or not players_field:
            raise SceneConfigError(f"L'équipe '{name}' doit contenir au moins un joueur.")
        players: list[PlayerConfig] = []
        for player_idx, player_data in enumerate(players_field):
            if not isinstance(player_data, Mapping):
                raise SceneConfigError(
                    f"Joueur #{player_idx} de l'équipe '{name}' invalide: doit être un mapping."
                )
            pname = player_data.get("name")
            if not isinstance(pname, str) or not pname.strip():
                pname = f"{name}#{player_idx + 1}"
            spawn = _parse_vec2(player_data, "spawn")
            velocity = _parse_optional_vec2(player_data, "velocity")
            players.append(PlayerConfig(name=pname, spawn=spawn, velocity=velocity))
        teams.append(TeamConfig(name=name, color=color, players=players))

    return teams


def _parse_vec2(data: Mapping[str, Any], field: str) -> tuple[float, float]:
    raw = data.get(field)
    if not isinstance(raw, Sequence) or len(raw) != 2:
        raise SceneConfigError(f"Champ '{field}' doit être une séquence de 2 valeurs.")
    try:
        x = float(raw[0])
        y = float(raw[1])
    except (TypeError, ValueError) as exc:
        raise SceneConfigError(f"Champ '{field}' doit contenir des nombres.") from exc
    return (x, y)


def _parse_optional_vec2(data: Mapping[str, Any], field: str) -> tuple[float, float] | None:
    if field not in data:
        return None
    value = data.get(field)
    if value is None:
        return None
    if not isinstance(value, Sequence) or len(value) != 2:
        raise SceneConfigError(f"Champ '{field}' doit être une séquence de 2 valeurs.")
    try:
        return (float(value[0]), float(value[1]))
    except (TypeError, ValueError) as exc:
        raise SceneConfigError(f"Champ '{field}' doit contenir des nombres.") from exc


def _parse_color(value: str) -> tuple[int, int, int]:
    if not value.startswith("#"):
        raise SceneConfigError("Les couleurs doivent être exprimées en hex (#RRGGBB).")
    hex_value = value[1:]
    if len(hex_value) not in (6, 8):
        raise SceneConfigError("Les couleurs hex doivent contenir 6 (ou 8) caractères.")
    try:
        r = int(hex_value[0:2], 16)
        g = int(hex_value[2:4], 16)
        b = int(hex_value[4:6], 16)
    except ValueError as exc:
        raise SceneConfigError(f"Couleur hex invalide: {value}") from exc
    return (r, g, b)
