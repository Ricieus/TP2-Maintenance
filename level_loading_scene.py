import random

import pygame
from pygame import Vector2

from level_scene import LevelScene
from fatal_error import FatalError
from scene import Scene
from scene_manager import SceneManager
from game_settings import GameSettings, Files
from star import Star
from taxi import Taxi


class LevelLoadingScene(Scene):
    """ Scène de chargement d'un niveau. """

    _FADE_OUT_DURATION: int = 500  # ms

    def __init__(self, level: int) -> None:
        super().__init__()
        self._settings = GameSettings()
        self._text_font = pygame.font.Font(GameSettings.FILE_NAMES[Files.FONT], 24)

        self._level = level
        self._music_started = False
        self._fade_out_start_time = None
        self._scene_in_use = False

        try:
            self._surface = pygame.image.load(GameSettings.FILE_NAMES[Files.IMG_LOADING]).convert_alpha()
            self._taxi_surface = pygame.image.load(GameSettings.FILE_NAMES[Files.IMG_TAXIS]).convert_alpha()
            self._level_name_pos = Vector2(
                (self._settings.SCREEN_WIDTH - self._render_level_message_surface().get_width()) / 2,
                (self._settings.SCREEN_HEIGHT - self._render_level_message_surface().get_height()) / 2,
            )
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
        self._stars = [
            Star(angle, Vector2(self._settings.SCREEN_WIDTH / 2, self._settings.SCREEN_HEIGHT / 2))
            for angle in [0, 90, 180, 270, 45, 135, 225, 315]
        ]
        self._taxi_width = self._taxi_surface.get_width()
        self._taxi_height = self._taxi_surface.get_height()
        self._taxi_sprite = self._taxi_surface.subsurface((0, 0, self._taxi_width / Taxi._NB_TAXI_IMAGES, self._taxi_height))
        self._taxi_position = Vector2((self._settings.SCREEN_WIDTH - (self._taxi_width / Taxi._NB_TAXI_IMAGES) - 25) / 2,
                                      self._settings.SCREEN_HEIGHT)
        self._vertical_speed = 1
        self._horizontal_speed = 2
        self._direction_taxi = 1
        self._horizontal_travel = 100
        self._distance_traveled = 0
        self._first_segment = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type in (pygame.KEYDOWN, pygame.JOYBUTTONDOWN):
            is_key_event = (event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE))
            is_joy_event = (event.type == pygame.JOYBUTTONDOWN and pygame.joystick.Joystick(0).get_button(9))

            if is_key_event or is_joy_event:
                self._fade_out_start_time = pygame.time.get_ticks()
                SceneManager().change_scene(f"level{self._level}", LevelLoadingScene._FADE_OUT_DURATION)

    def update(self) -> None:
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

        for star in self._stars:
            star.move_direction()

        if self._taxi_position.y > (self._settings.SCREEN_HEIGHT - self._taxi_height) / 2:
            self._taxi_position.y -= self._vertical_speed
            self._taxi_position.x += self._direction_taxi * self._horizontal_speed
            self._distance_traveled += self._horizontal_speed
            if self._distance_traveled > self._horizontal_travel:
                if self._first_segment:
                    self._horizontal_travel *= 2
                self._direction_taxi *= -1
                self._horizontal_travel -= 10
                self._distance_traveled = 0
                self._first_segment = False

                self._taxi_sprite = pygame.transform.flip(
                    self._taxi_surface.subsurface((0, 0, self._taxi_width / Taxi._NB_TAXI_IMAGES, self._taxi_height)),
                    self._direction_taxi == -1, False)
        else:
            SceneManager().change_scene(f"level{self._level}", LevelLoadingScene._FADE_OUT_DURATION)

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self._surface, (0, 0))
        screen.blit(self._render_level_message_surface(), self._level_name_pos)

        screen.blit(self._taxi_sprite, self._taxi_position)

        for star in self._stars:
            star.draw(screen)

    def surface(self) -> pygame.Surface:
        return self._surface

    def _render_level_message_surface(self) -> pygame.Surface:
        message_str = f"Level 1"
        return self._text_font.render(f"{message_str}", True, (255, 255, 255))