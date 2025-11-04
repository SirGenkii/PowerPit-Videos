"""Power Pit package initializer."""

from .rng import build_rng
from .scene import SceneConfig, load_scene_config

__all__ = ["SceneConfig", "load_scene_config", "render_scene", "build_rng"]


def render_scene(*args, **kwargs):  # type: ignore[override]
    """Lazy import helper to avoid hard dependency during tests."""

    from .render import render_scene as _render_scene

    return _render_scene(*args, **kwargs)
