import pygame

from scene import Scene


class GameOver(Scene):

    def __init__(self) -> None:
        super().__init__()
        self._surface = pygame.image.load("img/game_over.jpg").convert_alpha()

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen_size_surface = pygame.transform.scale(self._surface, screen.get_size()) #Pour que la taille de image soit égale à taille de l'écran
        screen.blit(screen_size_surface, (0, 0))

    def surface(self) -> pygame.Surface:
        return self._surface
