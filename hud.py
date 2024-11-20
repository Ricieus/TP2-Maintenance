import pygame

from game_settings import GameSettings


class HUD:
    """ Singleton pour l'affichage tête haute (HUD). """

    _LIVES_ICONS_FILENAME = "img/hud_lives.png"
    _LIVES_ICONS_SPACING = 10

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(HUD, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._settings = GameSettings()

            self._money_font = pygame.font.Font(None, 36)

            self._bank_money = 0
            self._bank_money_surface = self._render_bank_money_surface()
            self._bank_money_pos = pygame.Vector2(20, self._settings.SCREEN_HEIGHT - (self._bank_money_surface.get_height() + 10))

            self._trip_money = 0
            self._trip_money_surface = self._render_trip_money_surface()

            self._lives = self._settings.NB_PLAYER_LIVES
            self._lives_icon = pygame.image.load(HUD._LIVES_ICONS_FILENAME).convert_alpha()
            self._lives_pos= pygame.Vector2(20, self._settings.SCREEN_HEIGHT - (self._lives_icon.get_height() + 40))

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

    def add_bank_money(self, amount: float) -> None:
        self._bank_money += round(amount, 2)
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

    def _render_bank_money_surface(self) -> pygame.Surface:
        money_str = f"{self._bank_money:.2f}"
        return self._money_font.render(f"${money_str: >8}", True, (51, 51, 51))

    def _render_trip_money_surface(self) -> pygame.Surface:
        money_str = f"{self._trip_money:.2f}"
        return self._money_font.render(f"${money_str: >5}", True, (51, 51, 51))
