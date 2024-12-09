import pygame

from fatal_error import FatalError
from game_settings import Files, GameSettings
from scene import Scene


class GameOver(Scene):

    def __init__(self) -> None:
        super().__init__()
        try:
         self._surface = pygame.image.load(GameSettings.FILE_NAMES[Files.GAME_OVER_IMG]).convert_alpha()
        except FileNotFoundError as e:
            directory_plus_filename = str(e).split("'")[1]
            filename = directory_plus_filename.split("/")[-1]
            fatal_error_app = FatalError()
            fatal_error_app.run(filename)

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self) -> None:
        pass

    def render(self, screen: pygame.Surface) -> None:
        screen_size_surface = pygame.transform.scale(self._surface, screen.get_size()) #Pour que la taille de image soit égale à taille de l'écran
        screen.blit(screen_size_surface, (0, 0))

    def surface(self) -> pygame.Surface:
        return self._surface
