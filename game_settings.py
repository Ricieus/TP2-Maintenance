import pygame


class GameSettings:
    """ Singleton pour les paramètres de jeu. """

    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 90

    NB_PLAYER_LIVES = 5

    FILE_NAMES = {
        "font_boombox2": "fonts/boombox2.ttf",
        "img_astronaut": "img/astronaut.png",
        "voices_astronaut_hey_taxi": [
            "voices/gary_hey_taxi_01.mp3",
            "voices/gary_hey_taxi_02.mp3",
            "voices/gary_hey_taxi_03.mp3"
        ],
        "voices_astronaut_pad": [
            "voices/gary_up_please_01.mp3",
            "voices/gary_pad_1_please_01.mp3",
            "voices/gary_pad_2_please_01.mp3",
            "voices/gary_pad_3_please_01.mp3",
            "voices/gary_pad_4_please_01.mp3",
            "voices/gary_pad_5_please_01.mp3"
        ],
        "voices_astronaut_hey": "voices/gary_hey_01.mp3",
        "img_icon_lives": "img/hud_lives.png",
        "img_loading": "img/loading.png",
        "snd_music_loading": "snd/390539__burghrecords__dystopian-future-fx-sounds-8.wav",
        "img_level": "img/space01.png",
        "snd_music_level": "snd/476556__magmisoundtracks__sci-fi-music-loop-01.wav",
        "img_gate": "img/gate.png",
        "img_obstacles": [
            "img/south01.png",
            "img/west01.png",
            "img/east01.png",
            "img/north01.png",
            "img/obstacle01.png",
            "img/obstacle02.png",
        ],
        "img_pump": "img/pump.png",
        "img_pads": [
            "img/pad01.png",
            "img/pad02.png",
            "img/pad03.png",
            "img/pad04.png",
            "img/pad05.png",
        ],
        "img_splash": "img/splash.png",
        "snd_splash": "snd/371516__mrthenoronha__space-game-theme-loop.wav",
        "img_taxis": "img/taxis.png",
        "snd_reactor": "snd/170278__knova__jetpack-low.wav",
        "snd_crash": "snd/237375__squareal__car-crash.wav"

    }

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GameSettings, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self.screen = None
            self.pad_font = pygame.font.Font(GameSettings.FILE_NAMES["font_boombox2"], 11)

            self._initialized = True
