import pygame
from enum import Enum, auto


class Files(Enum):
    FONT = auto()
    IMG_ASTRONAUT = auto()
    VOICES_ASTRONAUT_HEY_TAXI = auto()
    VOICES_ASTRONAUT_PAD = auto()
    VOICES_ASTRONAUT_HEY = auto()
    IMG_FUEL_GAUGE_FULL = auto()
    IMG_FUEL_GAUGE_EMPTY = auto()
    IMG_ICON_LIVES = auto()
    IMG_LOADING = auto()
    SND_MUSIC_LOADING = auto()
    IMG_LEVEL = auto()
    SND_MUSIC_LEVEL = auto()
    IMG_GATE = auto()
    IMG_OBSTACLES = auto()
    IMG_PUMP = auto()
    IMG_PADS = auto()
    IMG_SPLASH = auto()
    SND_SPLASH = auto()
    IMG_TAXIS = auto()
    SND_REACTOR = auto()
    SND_CRASH = auto()
    CFG_LEVEL = auto()
    SND_JINGLE = auto()
    ROUGH_LANDING = auto()
    SMOOTH_LANDING = auto()
    IMG_SPACE_TAXI_ICON = auto()


class GameSettings:
    """ Singleton pour les paramÃ¨tres de jeu. """

    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    FPS = 90

    NB_PLAYER_LIVES = 5

    FILE_NAMES = {
        Files.CFG_LEVEL: "levels/level#.cfg",
        Files.FONT: "fonts/boombox2.ttf",
        Files.IMG_ASTRONAUT: "img/astronaut.png",
        Files.VOICES_ASTRONAUT_HEY_TAXI: [
            "voices/gary_hey_taxi_01.mp3",
            "voices/gary_hey_taxi_02.mp3",
            "voices/gary_hey_taxi_03.mp3"
        ],
        Files.VOICES_ASTRONAUT_PAD: [
            "voices/gary_up_please_01.mp3",
            "voices/gary_pad_1_please_01.mp3",
            "voices/gary_pad_2_please_01.mp3",
            "voices/gary_pad_3_please_01.mp3",
            "voices/gary_pad_4_please_01.mp3",
            "voices/gary_pad_5_please_01.mp3"
        ],
        Files.VOICES_ASTRONAUT_HEY: "voices/gary_hey_01.mp3",
        Files.IMG_ICON_LIVES: "img/hud_lives.png",
        Files.IMG_LOADING: "img/loading.png",
        Files.SND_MUSIC_LOADING: "snd/390539__burghrecords__dystopian-future-fx-sounds-8.wav",
        Files.IMG_LEVEL: "img/space01.png",
        Files.SND_MUSIC_LEVEL: "snd/476556__magmisoundtracks__sci-fi-music-loop-01.wav",
        Files.IMG_GATE: "img/gate.png",
        Files.IMG_OBSTACLES: [
            "img/south01.png",
            "img/west01.png",
            "img/east01.png",
            "img/north01.png",
            "img/obstacle01.png",
            "img/obstacle02.png",
        ],
        Files.IMG_FUEL_GAUGE_FULL: "img/fuel_gauge_full.png",
        Files.IMG_FUEL_GAUGE_EMPTY: "img/fuel_gauge_empty.png",
        Files.IMG_PUMP: "img/pump.png",
        Files.IMG_PADS: [
            "img/pad01.png",
            "img/pad02.png",
            "img/pad03.png",
            "img/pad04.png",
            "img/pad05.png",
        ],
        Files.IMG_SPLASH: "img/splash.png",
        Files.SND_SPLASH: "snd/371516__mrthenoronha__space-game-theme-loop.wav",
        Files.IMG_TAXIS: "img/taxis.png",
        Files.SND_REACTOR: "snd/170278__knova__jetpack-low.wav",
        Files.SND_CRASH: "snd/237375__squareal__car-crash.wav",
        Files.SND_JINGLE: "snd/jingle.mp3",
        Files.ROUGH_LANDING: "snd/land2-43790.mp3",
        Files.SMOOTH_LANDING: "snd/rocket-landing-38715.mp3",
        Files.IMG_SPACE_TAXI_ICON: 'img/space_taxi_icon.ico'
    }

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(GameSettings, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self.screen = None
            self.pad_font = pygame.font.Font(GameSettings.FILE_NAMES[Files.FONT], 11)

            self._initialized = True