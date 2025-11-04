"""Optional real-time preview window using pygame."""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:  # pragma: no cover
    import numpy as np


class PreviewWindow:
    """Display frames in a pygame window during export."""

    def __init__(self, size: Tuple[int, int], fps: int):
        try:
            import pygame
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "Le module 'pygame' est requis pour l'option --show. "
                "Installez-le via 'pip install pygame'."
            ) from exc

        self._pygame = pygame
        pygame.init()
        self._size = size
        self._fps = fps
        self._screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Power Pit Preview")
        self._clock = pygame.time.Clock()
        self._lock = threading.Lock()

    def show(self, frame: "np.ndarray") -> None:
        with self._lock:
            for event in self._pygame.event.get():
                if event.type == self._pygame.QUIT:
                    self.close()
                    raise RuntimeError("Fenêtre de prévisualisation fermée par l'utilisateur")

            surface = self._pygame.image.frombuffer(frame.tobytes(), self._size, "RGB")
            self._screen.blit(surface, (0, 0))
            self._pygame.display.flip()
            self._clock.tick(self._fps)

    def close(self) -> None:
        with self._lock:
            self._pygame.quit()
