from operator import truediv

import pygame

from level_scene import LevelScene
from fatal_error import FatalError
from scene import Scene
from scene_manager import SceneManager
from game_settings import GameSettings, Files


class LevelLoadingScene(Scene):
    """ Scène de chargement d'un niveau. """

    _FADE_OUT_DURATION: int = 500  # ms

    def __init__(self, level: int) -> None:
        super().__init__()
        self._level = level
        self._surface = pygame.image.load(GameSettings.FILE_NAMES[Files.IMG_LOADING]).convert_alpha()
        self._music = pygame.mixer.Sound(GameSettings.FILE_NAMES[Files.SND_MUSIC_LOADING])
        self._music_started = False
        self._fade_out_start_time = None
        self._scene_in_use = False

        try:
            self._surface = pygame.image.load(GameSettings.FILE_NAMES[Files.IMG_LOADING]).convert_alpha()
            self._music = pygame.mixer.Sound(GameSettings.FILE_NAMES[Files.SND_MUSIC_LOADING])
        except FileNotFoundError as e:
            directory_plus_filename = str(e).split("'")[1]
            filename = directory_plus_filename.split("/")[-1]
            fatal_error_app = FatalError()
            fatal_error_app.run(filename)

        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            self.joystick = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.KEYDOWN, pygame.JOYBUTTONDOWN):
            is_key_event = (event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE))
            is_joy_event = (event.type == pygame.JOYBUTTONDOWN and pygame.joystick.Joystick(0).get_button(9))

            if is_key_event or is_joy_event:
                self._fade_out_start_time = pygame.time.get_ticks()
                SceneManager().change_scene(f"level{self._level}", LevelLoadingScene._FADE_OUT_DURATION)

    def update(self) -> None:
        if not self._scene_in_use: # Pour exécuter une seule fois.
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
