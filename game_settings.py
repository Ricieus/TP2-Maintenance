import pygame


class GameSettings:
    """ Singleton pour les paramètres de jeu. """

    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 90

    NB_PLAYER_LIVES = 5

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GameSettings, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self.screen = None
            self.pad_font = pygame.font.Font("fonts/boombox2.ttf", 11)

            self._initialized = True
