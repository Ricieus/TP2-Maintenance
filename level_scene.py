import os.path

import pygame
import time
import configparser

from astronaut import Astronaut
from game_settings import GameSettings, Files
from fatal_error import FatalError
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
        self._surface = None
        self._music = None
        self._music_started = False
        self._fade_out_start_time = None
        self._settings = None
        self._hud = None
        self._taxi = None
        self._gate = None
        self._obstacles = None
        self._pumps = None
        self._pads = None
        self._last_taxied_astronaut_time = time.time()

        try:
            config = configparser.ConfigParser()
            config.read(GameSettings.FILE_NAMES[Files.CFG_LEVEL].replace("#", str(self._level)))

            self._surface = pygame.image.load(config.get("level", "surface")).convert_alpha()
            self._music = pygame.mixer.Sound(config.get("level", "music"))

            self._gate = Gate(GameSettings.FILE_NAMES[Files.IMG_GATE], (582, 3))



            self._settings = GameSettings()
            self._hud = HUD()

            self._taxi = Taxi((self._settings.SCREEN_WIDTH / 2, self._settings.SCREEN_HEIGHT / 2))

            gate_path = config.get("gate", "gate")

            gate_data = gate_path.split(",")

            self._gate = pygame.image.load(gate_data[0].strip()).convert_alpha()

            # Extraction des coordonnées (x, y)
            x, y = map(int, gate_data[1:])
            self._gate_position = (x, y)

            self._gate = Gate(gate_data[0].strip(), (x, y))

            self._obstacles = []
            for key in config["obstacles"]:
                img_path, x, y = config.get("obstacles", key).split(", ")
                self._obstacles.append(Obstacle(img_path, (int(x), int(y))))
            self._obstacle_sprites = pygame.sprite.Group()
            self._obstacle_sprites.add(self._obstacles)

            self._pumps = []
            for key in config["pumps"]:
                img_path, x, y = config.get("pumps", key).split(", ")
                self._pumps.append(Pump(img_path, (int(x), int(y))))
            self._pump_sprites = pygame.sprite.Group()
            self._pump_sprites.add(self._pumps)

            self._pads = []
            for key in config["pads"]:
                img_path, x, y, width, height = config.get("pads", key).split(", ")
                self._pads.append(Pad(int(key[3:]), img_path, (int(x), int(y)), int(width), int(height)))
            self._pad_sprites = pygame.sprite.Group()
            self._pad_sprites.add(self._pads)

            self._reinitialize()
            self._hud.visible = True

        except FileNotFoundError as e:
            directory_plus_filename = str(e).split("'")[1]
            filename = directory_plus_filename.split("/")[-1]
            fatal_error_app = FatalError()
            fatal_error_app.run(filename)

    def handle_event(self, event: pygame.event.Event) -> None:
        """ Gère les événements PyGame. """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self._taxi.is_destroyed():
                self._taxi.reset()
                self._retry_current_astronaut()
                return

        if self._taxi:
            self._taxi.handle_event(event)

    def update(self) -> None:
        """
        Met à jour le niveau de jeu. Cette méthode est appelée à chaque itération de la boucle de jeu.
        :param delta_time: temps écoulé (en secondes) depuis la dernière trame affichée
        """
        # Initialisation de la musique si ce n'est pas déjà fait
        if not self._music_started:
            self._music.play(-1)
            self._music_started = True

        # Gestion du fade-out
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
                        if os.path.exists(GameSettings.FILE_NAMES[Files.CFG_LEVEL].replace("#", str(self._level + 1))):
                            SceneManager().change_scene(f"level{self._level + 1}_load", LevelScene._FADE_OUT_DURATION)
                        else:
                            SceneManager().change_scene("game_over", LevelScene._FADE_OUT_DURATION)
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
            if self._nb_taxied_astronauts < len(
                    self._astronauts) and time.time() - self._last_taxied_astronaut_time >= LevelScene._TIME_BETWEEN_ASTRONAUTS:
                self._astronaut = self._astronauts[self._nb_taxied_astronauts]

        # Mise à jour du taxi et gestion des collisions
        self._taxi.update()

        for pad in self._pads:
            if self._taxi.land_on_pad(pad):
                pass  # Effets secondaires d'un atterrissage ici
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
                pass  # Effets secondaires de remplissage de réservoir ici

        self.game_over_validation()

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
           Remet l'argent à 0 si le taxi crash et un astronaut est à bord"""
        astronaut_inside_taxi = self._astronaut and self._astronaut.is_onboard()
        if astronaut_inside_taxi:
            self._astronaut.set_trip_money(0.0)

    def game_over_validation(self) -> bool:
        if self._hud.get_lives() <= 0: #Condition pour voir si le joueur n'a pas de vie
            SceneManager().change_scene("game_over", LevelScene._FADE_OUT_DURATION) #Si le joueur n'a pas de vie, alors ca change le scène à game_over
