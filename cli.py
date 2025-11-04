"""Power Pit CLI entrypoint (M1)."""
from __future__ import annotations

import argparse
import logging

from powerpit import build_rng, load_scene_config, render_scene
from powerpit.logging_utils import configure_logging

LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Power Pit video generator (M1)")
    parser.add_argument("--scene", required=True, help="Chemin du fichier YAML de scène")
    parser.add_argument("--seed", type=int, default=None, help="Seed RNG (optionnel)")
    parser.add_argument("--out", required=True, help="Chemin de sortie MP4")
    parser.add_argument("--verbose", action="store_true", help="Active le logging debug")
    parser.add_argument(
        "--show",
        action="store_true",
        help="Affiche la fenêtre de prévisualisation pendant l'export si pygame est disponible",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(verbose=args.verbose)

    rng = build_rng(args.seed)
    LOGGER.debug("RNG initialisé avec seed=%s", rng.seed())

    scene = load_scene_config(args.scene)
    LOGGER.info(
        "Scène chargée — name=%s, arena=%s, duration=%.2fs, fps=%d",
        scene.name,
        scene.arena.type,
        scene.duration_seconds,
        scene.frame_rate,
    )

    output = render_scene(scene, args.out, show_preview=args.show)
    LOGGER.info("Clip exporté: %s", output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
