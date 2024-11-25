import pygame

from level_scene import LevelScene
from fatal_error import FatalError
from scene import Scene
from scene_manager import SceneManager


class LevelLoadingScene(Scene):
    """ Scène de chargement d'un niveau. """

    _FADE_OUT_DURATION: int = 500  # ms

    def __init__(self, level: int) -> None:
        super().__init__()
        self._level = level
        self._surface = None
        self._music = None
        self._music_started = False
        self._fade_out_start_time = None
        self._scene_in_use = False
        print("Construit level_loading_scene ", level)

        try:
            self._surface = pygame.image.load("img/loading.png").convert_alpha()
            self._music = pygame.mixer.Sound("snd/390539__burghrecords__dystopian-future-fx-sounds-8.wav")
        except FileNotFoundError as e:
            directory_plus_filename = str(e).split("'")[1]
            filename = directory_plus_filename.split("/")[-1]
            fatal_error_app = FatalError()
            fatal_error_app.run(filename)


    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._fade_out_start_time = pygame.time.get_ticks()

                SceneManager().change_scene(f"level{self._level}", LevelLoadingScene._FADE_OUT_DURATION)

    def update(self, delta_time: float) -> None:
        if not self._scene_in_use:
            SceneManager().add_scene(f"level{self._level}", LevelScene(self._level))
            self._scene_in_use = True

        if not self._music_started:
            self._music.play()
            self._music_started = True

        if self._fade_out_start_time:
            elapsed_time = pygame.time.get_ticks() - self._fade_out_start_time
            volume = max(0.0, 1.0 - (elapsed_time / LevelLoadingScene._FADE_OUT_DURATION))
            self._music.set_volume(volume)
            if volume == 0:
                self._fade_out_start_time = None

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self._surface, (0, 0))

    def surface(self) -> pygame.Surface:
        return self._surface
