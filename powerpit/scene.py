"""Scene configuration loading and validation for Power Pit."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .simple_yaml import safe_load


@dataclass
class ArenaConfig:
    """Basic arena definition.

    M0 utilise seulement le type d'arène pour vérifier la configuration,
    mais le champ sera exploité aux jalons suivants.
    """

    type: str


@dataclass
class SceneConfig:
    """Top-level scene configuration."""

    name: str
    duration_seconds: float
    frame_rate: int
    arena: ArenaConfig

    @property
    def frame_count(self) -> int:
        return int(round(self.duration_seconds * self.frame_rate))


class SceneConfigError(RuntimeError):
    """Raised when the scene configuration is invalid."""


SUPPORTED_ARENAS = {"circle", "stadium", "donut"}
DEFAULT_FRAME_RATE = 30
DEFAULT_DURATION = 10.0


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
    if not isinstance(arena_info, Mapping):
        raise SceneConfigError("Champ 'arena' manquant ou invalide (doit être un mapping).")

    arena_type = _require_str(arena_info, "type")
    if arena_type not in SUPPORTED_ARENAS:
        raise SceneConfigError(
            f"Type d'arène '{arena_type}' non supporté (options: {sorted(SUPPORTED_ARENAS)})."
        )

    return SceneConfig(
        name=name,
        duration_seconds=duration,
        frame_rate=frame_rate,
        arena=ArenaConfig(type=arena_type),
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
