"""Rendering pipeline for the Power Pit simulation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:  # pragma: no cover - import guard for environments missing imageio
    import imageio.v2 as imageio
except ImportError:  # pragma: no cover
    try:
        import imageio  # type: ignore[no-redef]
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            "Le module 'imageio' est requis pour le rendu vidéo. "
            "Installez les dépendances avec 'pip install -e .[dev]' ou 'pip install -r requirements.txt'."
        ) from exc

import numpy as np
from PIL import Image, ImageDraw

from .preview import PreviewWindow
from .scene import SceneConfig
from .simulation import SimulationSnapshot, simulate_frames

LOGGER = logging.getLogger(__name__)

FRAME_SIZE = (1920, 1080)  # (width, height)
BACKGROUND_COLOR = (8, 12, 24)
ARENA_BORDER_COLOR = (38, 168, 255)
BUMPER_COLOR = (255, 220, 120)


@dataclass
class Projection:
    scale: float
    offset: tuple[float, float]


def render_scene(scene: SceneConfig, output_path: str | Path, show_preview: bool = False) -> Path:
    """Run the simulation and export an MP4 clip."""

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    projection = _build_projection(scene)
    writer = imageio.get_writer(
        output,
        fps=scene.frame_rate,
        format="mp4",
        macro_block_size=None,
    )
    LOGGER.info(
        "Export simulation — scène=%s, durée=%.2fs, fps=%d, frames=%d, preview=%s",
        scene.name,
        scene.duration_seconds,
        scene.frame_rate,
        scene.frame_count,
        show_preview,
    )
    preview: PreviewWindow | None = None

    if show_preview:
        try:
            preview = PreviewWindow(FRAME_SIZE, scene.frame_rate)
        except RuntimeError as exc:  # pragma: no cover - optional dependency
            LOGGER.warning("Prévisualisation indisponible: %s", exc)
            preview = None

    try:
        for snapshot in simulate_frames(scene):
            frame = _render_frame(scene, snapshot, projection)
            writer.append_data(frame)
            if preview is not None:
                try:
                    preview.show(frame)
                except RuntimeError as exc:
                    LOGGER.info("Prévisualisation interrompue: %s", exc)
                    preview.close()
                    preview = None
    finally:
        writer.close()
        if preview is not None:
            preview.close()

    LOGGER.info("Export terminé: %s", output)
    return output


def _render_frame(scene: SceneConfig, snapshot: SimulationSnapshot, projection: Projection) -> np.ndarray:
    image = Image.new("RGB", FRAME_SIZE, BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    _draw_arena(draw, scene, projection)
    _draw_bumpers(draw, scene, projection)
    _draw_balls(draw, snapshot, projection)

    return np.asarray(image)


def _draw_arena(draw: ImageDraw.ImageDraw, scene: SceneConfig, projection: Projection) -> None:
    cx, cy = projection.offset
    scale = projection.scale

    if scene.arena.type == "circle":
        assert scene.arena.radius is not None
        radius_px = scene.arena.radius * scale
        bbox = [
            cx - radius_px,
            cy - radius_px,
            cx + radius_px,
            cy + radius_px,
        ]
        draw.ellipse(bbox, outline=ARENA_BORDER_COLOR, width=6)
    elif scene.arena.type == "stadium":
        assert scene.arena.width is not None
        assert scene.arena.height is not None
        assert scene.arena.corner_radius is not None
        half_w = scene.arena.width / 2.0
        half_h = scene.arena.height / 2.0
        corner_radius = scene.arena.corner_radius
        bbox = [
            cx - half_w * scale,
            cy - half_h * scale,
            cx + half_w * scale,
            cy + half_h * scale,
        ]
        draw.rounded_rectangle(bbox, radius=corner_radius * scale, outline=ARENA_BORDER_COLOR, width=6)
    else:  # pragma: no cover - unsupported yet
        raise RuntimeError(f"Type d'arène non géré pour le rendu: {scene.arena.type}")


def _draw_bumpers(draw: ImageDraw.ImageDraw, scene: SceneConfig, projection: Projection) -> None:
    scale = projection.scale
    cx, cy = projection.offset
    for bumper in scene.arena.bumpers:
        bx = cx + bumper.position[0] * scale
        by = cy - bumper.position[1] * scale
        radius_px = bumper.radius * scale
        bbox = [bx - radius_px, by - radius_px, bx + radius_px, by + radius_px]
        draw.ellipse(bbox, outline=BUMPER_COLOR, width=4)


def _draw_balls(draw: ImageDraw.ImageDraw, snapshot: SimulationSnapshot, projection: Projection) -> None:
    scale = projection.scale
    cx, cy = projection.offset

    for ball in snapshot.balls:
        bx = cx + float(ball.position[0]) * scale
        by = cy - float(ball.position[1]) * scale
        radius_px = ball.radius * scale
        bbox = [bx - radius_px, by - radius_px, bx + radius_px, by + radius_px]
        draw.ellipse(bbox, fill=ball.team.color, outline=(255, 255, 255), width=2)


def _build_projection(scene: SceneConfig) -> Projection:
    frame_w, frame_h = FRAME_SIZE
    span_x = scene.arena.horizontal_span
    span_y = scene.arena.vertical_span
    margin = 1.15
    scale_x = frame_w / (span_x * margin)
    scale_y = frame_h / (span_y * margin)
    scale = min(scale_x, scale_y)
    offset = (frame_w / 2.0, frame_h / 2.0)
    return Projection(scale=scale, offset=offset)


def render_frames(scene: SceneConfig, snapshots: Iterable[SimulationSnapshot], projection: Projection) -> list[np.ndarray]:
    """Utility primarily used by tests to convert snapshots into frames."""

    return [_render_frame(scene, snapshot, projection) for snapshot in snapshots]
