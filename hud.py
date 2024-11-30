import threading
import time
import pygame

from game_settings import GameSettings, Files


class HUD:
    """ Singleton pour l'affichage tête haute (HUD). """

    _LIVES_ICONS_FILENAME = GameSettings.FILE_NAMES[Files.IMG_ICON_LIVES]
    _LIVES_ICONS_SPACING = 10

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(HUD, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._settings = GameSettings()

            self._text_font = pygame.font.Font("fonts/boombox2.ttf", 24)

            self._bank_money = 0
            self._bank_money_surface = self._render_bank_money_surface()
            self._bank_money_pos = pygame.Vector2(20, self._settings.SCREEN_HEIGHT - (self._bank_money_surface.get_height() + 10))

            self._trip_money = 0
            self._last_saved_money = 0
            self._trip_money_surface = self._render_trip_money_surface()

            self._lives = self._settings.NB_PLAYER_LIVES
            self._lives_icon = pygame.image.load(HUD._LIVES_ICONS_FILENAME).convert_alpha()
            self._lives_pos= pygame.Vector2(20, self._settings.SCREEN_HEIGHT - (self._lives_icon.get_height() + 40))

            self._current_pad = None
            self._current_pad_surface = None
            self._text_thread = None
            self._lock = threading.Lock()
            self._opacity = 0

            self.visible = False

            self._initialized = True

    def render(self, screen: pygame.Surface) -> None:
        spacing = self._lives_icon.get_width() + HUD._LIVES_ICONS_SPACING
        for n in range(self._lives):
            screen.blit(self._lives_icon, (self._lives_pos.x + (n * spacing), self._lives_pos.y))

        screen.blit(self._bank_money_surface, (self._bank_money_pos.x, self._bank_money_pos.y))

        x = self._settings.SCREEN_WIDTH - self._trip_money_surface.get_width() - 20
        y = self._settings.SCREEN_HEIGHT - self._trip_money_surface.get_height() - 10
        screen.blit(self._trip_money_surface, (x, y))

        if self._current_pad_surface:
            self._current_pad_surface.set_alpha(self._opacity)
            x = (self._settings.SCREEN_WIDTH - self._current_pad_surface.get_width()) / 2
            y = self._settings.SCREEN_HEIGHT / 2
            screen.blit(self._current_pad_surface, (x, y))

    def add_bank_money(self, amount: float) -> None:
        self._bank_money += round(amount, 2)
        self._last_saved_money = amount
        self._bank_money_surface = self._render_bank_money_surface()

    def get_lives(self) -> int:
        return self._lives

    def loose_live(self) -> None:
        if self._lives > 0:
            self._lives -= 1

    def reset(self) -> None:
        self._bank_money = 0
        self._bank_money_surface = self._render_bank_money_surface()
        self._lives = self._settings.NB_PLAYER_LIVES

    def set_trip_money(self, trip_money: float) -> None:
        if self._trip_money != trip_money:
            self._trip_money = trip_money
            self._trip_money_surface = self._render_trip_money_surface()

    def set_current_pad(self, pad: str) -> None:
        with self._lock:
            self._current_pad = pad
            self._current_pad_surface = self._render_current_pad_surface()
            self._text_thread = threading.Thread(target=self._animate_text)
            self._text_thread.start()

    def _render_bank_money_surface(self) -> pygame.Surface:
        money_str = f"{self._bank_money:.2f}"
        return self._text_font.render(f"${money_str: >8}", True, (51, 51, 51))

    def _render_trip_money_surface(self) -> pygame.Surface:
        money_str = f"{self._trip_money:.2f}"
        return self._text_font.render(f"${money_str: >5}", True, (51, 51, 51))

    def _render_current_pad_surface(self) -> pygame.Surface:
        message_str = f"PAD {self._current_pad} PLEASE" if self._current_pad != "UP" else f"{self._current_pad} PLEASE"
        return self._text_font.render(f"{message_str}", True, (255, 255, 255))

    def _animate_text(self) -> None:
        for alpha in range(0, 256, 10):
            self._opacity = alpha
            time.sleep(0.01)

        time.sleep(1.75)

        for alpha in range(255, -1, -5):
            self._opacity = alpha
            time.sleep(0.01)

        self._animating = False