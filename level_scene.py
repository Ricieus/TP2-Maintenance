import pygame
import time

from astronaut import Astronaut
from game_settings import GameSettings, Files
from gate import Gate
from hud import HUD
from obstacle import Obstacle
from pad import Pad
from pump import Pump
from scene import Scene
from scene_manager import SceneManager
from taxi import Taxi


class LevelScene(Scene):
    """ Un niveau de jeu. """

    _FADE_OUT_DURATION: int = 500  # ms

    _TIME_BETWEEN_ASTRONAUTS: int = 5  # s

    def __init__(self, level: int) -> None:
        """
        Initialise une instance de niveau de jeu.
        :param level: le numéro de niveau
        """
        super().__init__()
        self._level = level
        self._surface = pygame.image.load(GameSettings.FILE_NAMES[Files.IMG_LEVEL]).convert_alpha()
        self._music = pygame.mixer.Sound(GameSettings.FILE_NAMES[Files.SND_MUSIC_LEVEL])
        self._music_started = False
        self._fade_out_start_time = None

        self._settings = GameSettings()
        self._hud = HUD()

        self._taxi = Taxi((self._settings.SCREEN_WIDTH / 2, self._settings.SCREEN_HEIGHT / 2))

        self._gate = Gate(GameSettings.FILE_NAMES[Files.IMG_GATE], (582, 3))

        self._obstacles = [Obstacle(GameSettings.FILE_NAMES[Files.IMG_OBSTACLES][0], (0, self._settings.SCREEN_HEIGHT - 141)),
                           Obstacle(GameSettings.FILE_NAMES[Files.IMG_OBSTACLES][1], (0, 0)),
                           Obstacle(GameSettings.FILE_NAMES[Files.IMG_OBSTACLES][2], (self._settings.SCREEN_WIDTH - 99, 0)),
                           Obstacle(GameSettings.FILE_NAMES[Files.IMG_OBSTACLES][3], (0, 0)),
                           Obstacle(GameSettings.FILE_NAMES[Files.IMG_OBSTACLES][4], (840, 150)),
                           Obstacle(GameSettings.FILE_NAMES[Files.IMG_OBSTACLES][5], (250, 200))]
        self._obstacle_sprites = pygame.sprite.Group()
        self._obstacle_sprites.add(self._obstacles)

        self._pumps = [Pump(GameSettings.FILE_NAMES[Files.IMG_PUMP], (305, 335))]
        self._pump_sprites = pygame.sprite.Group()
        self._pump_sprites.add(self._pumps)

        self._pads = [Pad(1, GameSettings.FILE_NAMES[Files.IMG_PADS][0], (650, self._settings.SCREEN_HEIGHT - 68), 5, 5),
                      Pad(2, GameSettings.FILE_NAMES[Files.IMG_PADS][1], (510, 205), 90, 15),
                      Pad(3, GameSettings.FILE_NAMES[Files.IMG_PADS][2], (150, 360), 10, 10),
                      Pad(4, GameSettings.FILE_NAMES[Files.IMG_PADS][3], (670, 480), 30, 280),
                      Pad(5, GameSettings.FILE_NAMES[Files.IMG_PADS][4], (1040, 380), 30, 120)]
        self._pad_sprites = pygame.sprite.Group()
        self._pad_sprites.add(self._pads)

        self._reinitialize()
        self._hud.visible = True

    def handle_event(self, event: pygame.event.Event) -> None:
        """ Gère les événements PyGame. """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self._taxi.is_destroyed():
                self._taxi.reset()
                self._retry_current_astronaut()
                return

        if self._taxi:
            self._taxi.handle_event(event)

    def update(self, delta_time: float) -> None:
        """
        Met à jour le niveau de jeu. Cette méthode est appelée à chaque itération de la boucle de jeu.
        :param delta_time: temps écoulé (en secondes) depuis la dernière trame affichée
        """
        if not self._music_started:
            self._music.play(-1)
            self._music_started = True

        if self._fade_out_start_time:
            elapsed_time = pygame.time.get_ticks() - self._fade_out_start_time
            volume = max(0.0, 1.0 - (elapsed_time / LevelScene._FADE_OUT_DURATION))
            self._music.set_volume(volume)
            if volume == 0:
                self._fade_out_start_time = None

        if self._taxi is None:
            return

        if self._astronaut:
            self._astronaut.update()
            self._hud.set_trip_money(self._astronaut.get_trip_money())

            if self._astronaut.is_onboard():
                self._taxi.board_astronaut(self._astronaut)
                if self._astronaut.target_pad is Pad.UP:
                    if self._gate.is_closed():
                        self._gate.open()
                    elif self._taxi.has_exited():
                        self._taxi.unboard_astronaut()
                        self._taxi = None
                        self._fade_out_start_time = pygame.time.get_ticks()
                        SceneManager().change_scene(f"level{self._level + 1}_load", LevelScene._FADE_OUT_DURATION)
                        return
            elif self._astronaut.has_reached_destination():
                if self._nb_taxied_astronauts < len(self._astronauts) - 1:
                    self._nb_taxied_astronauts += 1
                    self._astronaut = None
                    self._last_taxied_astronaut_time = time.time()
            elif self._taxi.hit_astronaut(self._astronaut):
                self._retry_current_astronaut()
            elif self._taxi.pad_landed_on:
                if self._taxi.pad_landed_on.number == self._astronaut.source_pad.number:
                    if self._astronaut.is_waiting_for_taxi():
                        self._astronaut.jump(self._taxi.rect.x + 20)
            elif self._astronaut.is_jumping_on_starting_pad():
                self._astronaut.wait()
        else:
            if time.time() - self._last_taxied_astronaut_time >= LevelScene._TIME_BETWEEN_ASTRONAUTS:
                self._astronaut = self._astronauts[self._nb_taxied_astronauts]

        self._taxi.update()

        for pad in self._pads:
            if self._taxi.land_on_pad(pad):
                pass  # introduire les effets secondaires d'un atterrissage ici
            elif self._taxi.crash_on_obstacle(pad):
                self.reset_money_after_crash()
                self._hud.loose_live()

        for obstacle in self._obstacles:
            if self._taxi.crash_on_obstacle(obstacle):
                self.reset_money_after_crash()
                self._hud.loose_live()

        if self._gate.is_closed() and self._taxi.crash_on_obstacle(self._gate):
            self.reset_money_after_crash()
            self._hud.loose_live()

        for pump in self._pumps:
            if self._taxi.crash_on_obstacle(pump):
                self.reset_money_after_crash()
                self._hud.loose_live()
            elif self._taxi.refuel_from(pump):
                pass  # introduire les effets secondaires de remplissage de réservoir ici

    def render(self, screen: pygame.Surface) -> None:
        """
        Effectue le rendu du niveau pour l'afficher à l'écran.
        :param screen: écran (surface sur laquelle effectuer le rendu)
        """
        screen.blit(self._surface, (0, 0))
        self._obstacle_sprites.draw(screen)
        self._gate.draw(screen)
        self._pump_sprites.draw(screen)
        self._pad_sprites.draw(screen)
        if self._taxi:
            self._taxi.draw(screen)
        if self._astronaut:
            self._astronaut.draw(screen)
        self._hud.render(screen)

    def surface(self) -> pygame.Surface:
        return self._surface

    def _reinitialize(self) -> None:
        """ Initialise (ou réinitialise) le niveau. """
        self._nb_taxied_astronauts = 0
        self._retry_current_astronaut()
        self._hud.reset()

    def _retry_current_astronaut(self) -> None:
        """ Replace le niveau dans l'état où il était avant la course actuelle. """
        self._gate.close()
        self._astronauts = [Astronaut(self._pads[3], self._pads[0], 20.00),
                            Astronaut(self._pads[2], self._pads[4], 20.00),
                            Astronaut(self._pads[0], self._pads[1], 20.00),
                            Astronaut(self._pads[4], self._pads[2], 20.00),
                            Astronaut(self._pads[1], self._pads[3], 20.00),
                            Astronaut(self._pads[0], Pad.UP, 20.00)]
        self._last_taxied_astronaut_time = time.time()
        self._astronaut = None

    def reset_money_after_crash(self):
        """Cette methode est appeler a chaque crash.
           Remet l'argent à 0 si le taxi crash et un astronaut est a bord"""
        astronaut_inside_taxi = self._astronaut and self._astronaut.is_onboard()
        if astronaut_inside_taxi:
            self._astronaut.set_trip_money(0.0)
