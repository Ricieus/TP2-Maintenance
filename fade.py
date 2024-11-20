import pygame

from scene import Scene


class Fade:
    """ Les objets de cette classe gèrent la transition graduelle entre deux surfaces. """

    def __init__(self, source: Scene, target: Scene) -> None:
        self._source = source
        self._target = target

        self._source_alpha = 255  # opaque
        self._target_alpha = 0    # transparent

        self._duration = None
        self._fading = False
        self._start_time = None

    def start(self, duration: int = 0) -> None:
        """
        Débute la transition de la surface source vers la surface cible.
        :param duration: durée en millisecondes (0 = instantané par défaut)
        :return: aucun
        """
        self._duration = duration
        self._start_time = pygame.time.get_ticks()

        if duration > 0:
            self._fading = True
        else:
            source_surface = self._source.surface()
            source_surface.set_alpha(0)
            target_surface = self._target.surface()
            target_surface.set_alpha(255)

    def update(self) -> None:
        if not self._fading:
            return

        elapsed_time = pygame.time.get_ticks() - self._start_time

        # source : d'opaque à transparent
        self._source_alpha = max(0, 255 - (elapsed_time / self._duration) * 255)
        source_surface = self._source.surface()
        source_surface.set_alpha(self._source_alpha)

        # cible : de transparent à opaque
        self._target_alpha = min(255, (elapsed_time / self._duration) * 255)
        target_surface = self._target.surface()
        target_surface.set_alpha(self._target_alpha)

        self._fading = self._source_alpha != 0 and self._target_alpha != 255

    def is_fading(self):
        return self._fading
