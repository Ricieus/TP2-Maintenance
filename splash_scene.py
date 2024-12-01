import pygame

from scene import Scene
from scene_manager import SceneManager
from game_settings import GameSettings, Files


class SplashScene(Scene):
    """ Scène titre (splash). """

    _FADE_OUT_DURATION: int = 1500  # ms
    FADE_IN_DURATION: int = 1500  # ms

    def __init__(self) -> None:
        super().__init__()
        self._surface = pygame.image.load(GameSettings.FILE_NAMES[Files.IMG_SPLASH]).convert_alpha()
        self._music = pygame.mixer.Sound(GameSettings.FILE_NAMES[Files.SND_SPLASH])
        self._music.play(loops=-1, fade_ms=1000)
        self._fade_out_start_time = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._fade_out_start_time = pygame.time.get_ticks()
                SceneManager().change_scene("level1_load", SplashScene._FADE_OUT_DURATION)

    def update(self) -> None:
        if self._fade_out_start_time:
            elapsed_time = pygame.time.get_ticks() - self._fade_out_start_time
            volume = max(0.0, 1.0 - (elapsed_time / SplashScene._FADE_OUT_DURATION))
            self._music.set_volume(volume)
            if volume == 0:
                self._fade_out_start_time = None

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self._surface, (0, 0))

    def surface(self) -> pygame.Surface:
        return self._surface
