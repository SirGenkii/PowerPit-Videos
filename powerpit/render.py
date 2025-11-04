"""Rendering utilities for Power Pit (M0)."""
from __future__ import annotations

import logging
from pathlib import Path

try:
    import imageio.v2 as imageio
except ImportError:  # pragma: no cover - fallback for older imageio
    try:
        import imageio  # type: ignore[no-redef]
    except ImportError as exc:  # pragma: no cover - missing runtime dependency
        raise RuntimeError(
            "Le module 'imageio' est requis pour le rendu vidéo. "
            "Installez les dépendances avec 'pip install -e .[dev]' ou 'pip install -r requirements.txt'."
        ) from exc
import numpy as np

from .scene import SceneConfig

LOGGER = logging.getLogger(__name__)

# 1080x1920 (w x h) pour le format vertical 9:16
FRAME_SIZE = (1920, 1080)
COLOR_BLACK = (0, 0, 0)


def render_blank_clip(scene: SceneConfig, output_path: str | Path) -> Path:
    """Render a blank MP4 clip for the given scene.

    M0 génère un MP4 noir tout en respectant la durée et la cadence définies
    dans la configuration. Les jalons suivants remplaceront cette fonction par
    un rendu basé sur la simulation.
    """

    frame_w, frame_h = FRAME_SIZE
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    LOGGER.info(
        "Export video noir — scène=%s, durée=%.2fs, fps=%d, frames=%d, sortie=%s",
        scene.name,
        scene.duration_seconds,
        scene.frame_rate,
        scene.frame_count,
        output,
    )

    frame = np.zeros((frame_h, frame_w, 3), dtype=np.uint8)
    frame[:] = COLOR_BLACK

    writer = imageio.get_writer(output, fps=scene.frame_rate, format="mp4")
    try:
        for _ in range(scene.frame_count):
            writer.append_data(frame)
    finally:
        writer.close()

    LOGGER.info("Export terminé: %s", output)
    return output
