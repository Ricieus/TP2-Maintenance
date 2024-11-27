import pygame

from scene import Scene


class GameOver(Scene):

    def __init__(self) -> None:
        super().__init__()
        self._surface = pygame.image.load("img/game_over.jpg").convert_alpha()

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, delta_time: float) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self._surface, (0, 0))

    def surface(self) -> pygame.Surface:
        return self._surface
