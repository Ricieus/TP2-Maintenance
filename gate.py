import pygame
from obstacle import Obstacle


class Gate(Obstacle):
    """ Barrière à la sortie d'un niveau. """

    def __init__(self, filename: str, pos: tuple) -> None:
        super(Gate, self).__init__(filename, pos)

        self._closed = True

    def close(self) -> None:
        self._closed = True

    def draw(self, surface: pygame.Surface) -> None:
        if self._closed:
            surface.blit(self.image, self.rect)

    def is_closed(self) -> bool:
        return self._closed

    def open(self) -> True:
        self._closed = False
