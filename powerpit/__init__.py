"""Power Pit package initializer."""

from .scene import SceneConfig, load_scene_config
from .rng import build_rng

__all__ = ["SceneConfig", "load_scene_config", "render_blank_clip", "build_rng"]


def render_blank_clip(*args, **kwargs):  # type: ignore[override]
    """Lazy import helper to avoid hard dependency during tests."""

    from .render import render_blank_clip as _render_blank_clip

    return _render_blank_clip(*args, **kwargs)
