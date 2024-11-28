import pygame
from scene import Scene

class BlackScene(Scene):
    """ Scene pour effet de fondu noir vers l'écran titre splash """

    def __init__(self):
        super().__init__()
        self._surface = pygame.Surface(pygame.display.get_surface().get_size())
        self._surface.fill((0, 0, 0))

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, delta_time: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        """Pour dessiner le surface noir"""
        screen.blit(self._surface, (0, 0))

    def surface(self) -> pygame.Surface:
        return self._surface
