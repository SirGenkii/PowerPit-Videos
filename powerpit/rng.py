"""Random utilities."""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class RNGConfig:
    seed: int


def build_rng(seed: int | None) -> random.Random:
    """Return a seeded RNG instance.

    Si `seed` est None, on utilise un seed par défaut mais on retourne quand même
    l'objet RNG pour conserver la reproductibilité au sein du process.
    """

    if seed is None:
        seed = 0
    rng = random.Random(seed)
    return rng
