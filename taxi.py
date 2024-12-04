import time
from enum import Enum, auto

import pygame
from pygame import Vector2

from game_settings import GameSettings, Files
from astronaut import Astronaut, AstronautState
from hud import HUD
from obstacle import Obstacle
from pad import Pad
from pump import Pump


class ImgSelector(Enum):
    """ Sélecteur d'image de taxi. """
    IDLE = auto()
    BOTTOM_REACTOR = auto()
    TOP_REACTOR = auto()
    REAR_REACTOR = auto()
    BOTTOM_AND_REAR_REACTORS = auto()
    TOP_AND_REAR_REACTORS = auto()
    GEAR_OUT = auto()
    GEAR_SHOCKS = auto()
    GEAR_OUT_AND_BOTTOM_REACTOR = auto()
    DESTROYED = auto()


class Taxi(pygame.sprite.Sprite):
    """ Un taxi spatial. """

    _TAXIS_FILENAME = GameSettings.FILE_NAMES[Files.IMG_TAXIS]
    _NB_TAXI_IMAGES = 6

    _NB_SLIDE_FRAMES = 3
    _SLIDE_FRAME_TIME = 0.5

    _FLAG_LEFT = 1 << 0  # indique si le taxi va vers la gauche
    _FLAG_TOP_REACTOR = 1 << 1  # indique si le réacteur du dessus est allumé
    _FLAG_BOTTOM_REACTOR = 1 << 2  # indique si le réacteur du dessous est allumé
    _FLAG_REAR_REACTOR = 1 << 3  # indique si le réacteur arrière est allumé
    _FLAG_GEAR_OUT = 1 << 4  # indique si le train d'atterrissage est sorti
    _FLAG_DESTROYED = 1 << 5  # indique si le taxi est détruit

    _REACTOR_SOUND_VOLUME = 0.25

    _REAR_REACTOR_POWER = 0.001
    _BOTTOM_REACTOR_POWER = 0.0005
    _TOP_REACTOR_POWER = 0.00025

    _MAX_ACCELERATION_X = 0.075
    _MAX_ACCELERATION_Y_UP = 0.08
    _MAX_ACCELERATION_Y_DOWN = 0.05

    _MAX_VELOCITY_SMOOTH_LANDING = 0.50  # vitesse maximale permise pour un atterrissage en douceur
    _MIN_VELOCITY_SLIDE = 1  # vitesse minimale pour permettre le glissage du taxi
    _SLIDE_POWER = 4
    _CRASH_ACCELERATION = 0.10

    _FRICTION_MUL = 0.9995  # la vitesse horizontale est multipliée par la friction
    _GRAVITY_ADD = 0.005  # la gravité est ajoutée à la vitesse verticale

    def __init__(self, pos: tuple) -> None:
        """
        Initialise une instance de taxi.
        :param pos:
        """
        super(Taxi, self).__init__()

        self._initial_pos = pos

        self._hud = HUD()

        self._reactor_sound = pygame.mixer.Sound(GameSettings.FILE_NAMES[Files.SND_REACTOR])
        self._reactor_sound.set_volume(0)
        self._reactor_sound.play(-1)

        self._crash_sound = pygame.mixer.Sound(GameSettings.FILE_NAMES[Files.SND_CRASH])

        self._smooth_landing = pygame.mixer.Sound(GameSettings.FILE_NAMES[Files.SMOOTH_LANDING])
        self._rough_landing_sound = pygame.mixer.Sound(GameSettings.FILE_NAMES[Files.ROUGH_LANDING])
        self._has_unboarded = False
        self._surfaces, self._masks = Taxi._load_and_build_surfaces()

        self._fuel_status = 100
        self._fuel_consumption = 0.0

        self._reinitialize()

    @property
    def pad_landed_on(self) -> Pad or None:
        return self._pad_landed_on

    def board_astronaut(self, astronaut: Astronaut) -> None:
        self._astronaut = astronaut

    def crash_on_obstacle(self, obstacle: pygame.sprite.Sprite):
        """
        Vérifie si le taxi est en situation de crash contre un obstacle.
        :param obstacle: obstacle avec lequel vérifier
        :return: True si le taxi est en contact avec l'obstacle, False sinon
        """

        if self._flags & Taxi._FLAG_DESTROYED == Taxi._FLAG_DESTROYED:
            return False

        if self.rect.colliderect(obstacle.rect):
            if pygame.sprite.collide_mask(self, obstacle):
                self._flags = self._FLAG_DESTROYED
                self._crash_sound.play()
                self._velocity = pygame.Vector2(0.0, 0.0)
                self._acceleration = pygame.Vector2(0.0, Taxi._CRASH_ACCELERATION)
                self._fuel_status = 100
                self._hud.set_current_fuel(self._fuel_status)

                return True

    def draw(self, surface: pygame.Surface) -> None:
        """ Dessine le taxi sur la surface fournie comme argument. """
        surface.blit(self.image, self.rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        """ Gère les événements du taxi. """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self._pad_landed_on is None:
                    if self._flags & Taxi._FLAG_GEAR_OUT != Taxi._FLAG_GEAR_OUT:
                        # pas de réacteurs du dessus et arrière lorsque le train d'atterrissage est sorti
                        self._flags &= ~(Taxi._FLAG_TOP_REACTOR | Taxi._FLAG_REAR_REACTOR)

                    self._flags ^= Taxi._FLAG_GEAR_OUT  # flip le bit pour refléter le nouvel état

                    self._select_image()

    def has_exited(self) -> bool:
        """
        Vérifie si le taxi a quitté le niveau (par la sortie).
        :return: True si le taxi est sorti du niveau, False sinon
        """
        return self.rect.y <= -self.rect.height

    def hit_astronaut(self, astronaut: Astronaut) -> bool:
        """
        Vérifie si le taxi frappe un astronaute.
        :param astronaut: astronaute pour lequel vérifier
        :return: True si le taxi frappe l'astronaute, False sinon
        """
        if self._pad_landed_on or astronaut.is_onboard():
            return False

        if self.rect.colliderect(astronaut.rect):
            if pygame.sprite.collide_mask(self, astronaut):
                astronaut.play_destination_clip()
                if self._has_unboarded:
                    astronaut._state = AstronautState.REACHED_DESTINATION
                    hitting_fines = self._hud._last_saved_money / 2
                    self._hud._bank_money -= hitting_fines
                    self._hud._bank_money_surface = self._hud._render_bank_money_surface()
                    self._hud._last_saved_money = 0.0
                    self._has_unboarded = False
                    return False
                return True
        return False

    def is_destroyed(self) -> bool:
        """
        Vérifie si le taxi est détruit.
        :return: True si le taxi est détruit, False sinon
        """

        return self._flags & Taxi._FLAG_DESTROYED == Taxi._FLAG_DESTROYED

    def land_on_pad(self, pad: Pad) -> bool:
        """
        Vérifie si le taxi est en situation d'atterrissage sur une plateforme.
        :param pad: plateforme pour laquelle vérifier
        :return: True si le taxi est atterri, False sinon
        """
        gear_out = self._flags & Taxi._FLAG_GEAR_OUT == Taxi._FLAG_GEAR_OUT
        if not gear_out:
            return False

        if self._velocity.y > Taxi._MAX_VELOCITY_SMOOTH_LANDING or self._velocity.y < 0.0:
            return False

        if not self.rect.colliderect(pad.rect):
            return False

        taxi_edges_position = (self.rect.left, self.rect.right)

        visible_platform = 0
        invisible_left_image = 0
        invisible_right_image = 0

        pad.image.lock()
        for x in range(pad.image.get_width()):  # TODO: à refactoriser
            r, g, b, a = pad.image.get_at((x, 0))
            if a != 0:
                visible_platform += 1
            elif a == 0 and visible_platform == 0:
                invisible_left_image += 1
            elif a == 0:
                invisible_right_image += 1
        pad.image.unlock()

        platform_edges_position = (pad.rect.left + invisible_left_image, pad.rect.right - invisible_right_image)

        if taxi_edges_position[0] < platform_edges_position[0] or taxi_edges_position[1] > platform_edges_position[1]:
            return False

        if pygame.sprite.collide_mask(self, pad):
            self.rect.bottom = pad.rect.top + 4
            self._position.y = float(self.rect.y)
            self._flags &= Taxi._FLAG_LEFT | Taxi._FLAG_GEAR_OUT
            if self._velocity.x > self._MIN_VELOCITY_SLIDE or self._velocity.x < -self._MIN_VELOCITY_SLIDE:
                self._sliding = True
                self._last_frame_time = time.time()
                self._top_slide_length = self._velocity.x * self._SLIDE_POWER
                if self._top_slide_length > self._max_slide_length:
                    self._top_slide_length = self._max_slide_length
                elif self._top_slide_length < -self._max_slide_length:
                    self._top_slide_length = -self._max_slide_length
            self._velocity = pygame.Vector2(0.0, 0.0)
            self._acceleration = pygame.Vector2(0.0, 0.0)
            self._pad_landed_on = pad

            if Taxi._MAX_VELOCITY_SMOOTH_LANDING >= self._velocity.y >= 0.0:
                self._smooth_landing.play()

            elif self._velocity.y > Taxi._MAX_VELOCITY_SMOOTH_LANDING:
                self._rough_landing_sound.play()

            if self._astronaut:
                if self._astronaut.target_pad and self._astronaut.target_pad.number == pad.number:
                    self.unboard_astronaut()
            return True

        return False

    def refuel_from(self, pump: Pump) -> bool:
        """
        Vérifie si le taxi est en position de faire le plein d'essence.
        :param pump: pompe pour laquelle vérifier
        :return: True si le taxi est en bonne position, False sinon
        """
        if self._pad_landed_on is None:
            return False

        if not self.rect.colliderect(pump.rect):
            return False

        return True

    def reset(self) -> None:
        """ Réinitialise le taxi. """
        self._reinitialize()

    def unboard_astronaut(self) -> None:
        """ Fait descendre l'astronaute qui se trouve à bord. """
        if self._astronaut.target_pad is not Pad.UP:
            self._astronaut.unboard(self.rect.x + 20, self._pad_landed_on.rect.y - self._astronaut.rect.height)

        self._hud.add_bank_money(self._astronaut.get_trip_money())
        self._astronaut.set_trip_money(0.0)
        self._hud.set_trip_money(0.0)
        self._has_unboarded = True
        self._astronaut = None


    def update(self, *args, **kwargs) -> None:
        """
        Met à jour le taxi. Cette méthode est appelée à chaque itération de la boucle de jeu.
        :param args: inutilisé
        :param kwargs: inutilisé
        """

        # ÉTAPE 1 - gérer les touches présentement enfoncées
        self._handle_keys()

        # ÉTAPE 2 - gérer le taxi qui glisse
        current_time = time.time()
        self._accumulated_frame_time += current_time - self._last_frame_time
        if self._sliding and self._accumulated_frame_time > self._SLIDE_FRAME_TIME:
            self._accumulated_frame_time = 0
            if self._current_slide_frame < self._NB_SLIDE_FRAMES:
                self._slide_length_per_images = self._top_slide_length // (
                        self._NB_SLIDE_FRAMES - self._current_slide_frame)
                self._position.x += self._slide_length_per_images
                self._top_slide_length -= self._slide_length_per_images
                self._current_slide_frame += 1
            else:
                self._sliding = False
                self._current_slide_frame = 0
                self._top_slide_length = 0

        # ÉTAPE 3 - calculer la nouvelle position du taxi
        self._velocity += self._acceleration
        self._velocity.x *= Taxi._FRICTION_MUL
        if self._pad_landed_on is None:
            self._velocity.y += Taxi._GRAVITY_ADD

        self._position += self._velocity

        self.rect.x = round(self._position.x)
        self.rect.y = round(self._position.y)

        if self.has_exited():
            self._reactor_sound.set_volume(0)
            return

        # ÉTAPE 4 - fait entendre les réacteurs ou pas
        reactor_flags = Taxi._FLAG_TOP_REACTOR | Taxi._FLAG_REAR_REACTOR | Taxi._FLAG_BOTTOM_REACTOR
        if self._flags & reactor_flags:
            self._reactor_sound.set_volume(Taxi._REACTOR_SOUND_VOLUME)
        else:
            self._reactor_sound.set_volume(0)

        # ÉTAPE 5 - sélectionner la bonne image en fonction de l'état du taxi
        self._select_image()

    def _handle_keys(self) -> None:
        """ Change ou non l'état du taxi en fonction des touches présentement enfoncées. """
        if self._flags & Taxi._FLAG_DESTROYED == Taxi._FLAG_DESTROYED:
            return

        keys = pygame.key.get_pressed()

        gear_out = self._flags & Taxi._FLAG_GEAR_OUT == Taxi._FLAG_GEAR_OUT

        self._fuel_consumption = 0.0

        if keys[pygame.K_RIGHT] and keys[pygame.K_LEFT] or keys[pygame.K_UP] and keys[pygame.K_DOWN]:
            return

        if keys[pygame.K_LEFT] and not gear_out:
            self._flags |= Taxi._FLAG_LEFT | Taxi._FLAG_REAR_REACTOR
            self._acceleration.x = max(self._acceleration.x - Taxi._REAR_REACTOR_POWER, -Taxi._MAX_ACCELERATION_X)
            self._fuel_consumption += self._acceleration.x

        if keys[pygame.K_RIGHT] and not gear_out:
            self._flags &= ~Taxi._FLAG_LEFT
            self._flags |= self._FLAG_REAR_REACTOR
            self._acceleration.x = min(self._acceleration.x + Taxi._REAR_REACTOR_POWER, Taxi._MAX_ACCELERATION_X)
            self._fuel_consumption += self._acceleration.x

        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            self._flags &= ~Taxi._FLAG_REAR_REACTOR
            self._acceleration.x = 0.0

        if keys[pygame.K_DOWN] and not gear_out:
            self._flags &= ~Taxi._FLAG_BOTTOM_REACTOR
            self._flags |= Taxi._FLAG_TOP_REACTOR
            self._acceleration.y = min(self._acceleration.y + Taxi._TOP_REACTOR_POWER, Taxi._MAX_ACCELERATION_Y_DOWN)
            self._fuel_consumption += self._acceleration.y

        if keys[pygame.K_UP]:
            self._flags &= ~Taxi._FLAG_TOP_REACTOR
            self._flags |= Taxi._FLAG_BOTTOM_REACTOR
            self._acceleration.y = max(self._acceleration.y - Taxi._BOTTOM_REACTOR_POWER, -Taxi._MAX_ACCELERATION_Y_UP)
            self._fuel_consumption += self._acceleration.y
            if self._pad_landed_on:
                self._pad_landed_on = None
                self.hide_gear()

        if not (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
            self._flags &= ~(Taxi._FLAG_TOP_REACTOR | Taxi._FLAG_BOTTOM_REACTOR)
            self._acceleration.y = 0.0

        if any(keys) and self._flags != self._FLAG_DESTROYED:
            self._fuel_status -= abs(self._fuel_consumption)
        else:
            self._fuel_consumption = 0.0

        if self._fuel_status < 0:
            self._flags = self._FLAG_DESTROYED
            self._crash_sound.play()
            self._velocity = pygame.Vector2(0.0, 0.0)
            self._acceleration = pygame.Vector2(0.0, Taxi._CRASH_ACCELERATION)
        self._hud.set_current_fuel(self._fuel_status)

    def is_refueling(self):
        if self._fuel_status < 100:
            self._fuel_status += 0.05
        else:
            self._fuel_status = 100
        self._hud.set_current_fuel(self._fuel_status)

    def hide_gear(self) -> None:
        """ Pour faire  rentrer le train d’atterrissage au décollage d’une plateforme. """
        if not (self._flags & Taxi._FLAG_GEAR_OUT): #Condition pour verifier si le train d'atterrissage sont fermer
            return #Si ils sont deja fermé, alors la fonction fais rien
        else: #Sinon, le train d'atterrissage sont sorti
            self._flags &= ~Taxi._FLAG_GEAR_OUT
            self._select_image()

    def _reinitialize(self) -> None:
        """ Initialise (ou réinitialise) les attributs de l'instance. """
        self._flags = 0
        self._select_image()

        self.rect = self.image.get_rect()
        self.rect.x = self._initial_pos[0] - self.rect.width / 2
        self.rect.y = self._initial_pos[1] - self.rect.height / 2

        self._position = pygame.Vector2(self.rect.x, self.rect.y)
        self._velocity = pygame.Vector2(0.0, 0.0)
        self._acceleration = pygame.Vector2(0.0, 0.0)

        self._current_slide_frame = 0
        self._last_frame_time = 0
        self._accumulated_frame_time = 0
        self._max_slide_length = self.rect.width / 2
        self._slide_length_per_images = 0
        self._top_slide_length = 0
        self._sliding = False

        self._pad_landed_on = None
        self._taking_off = False

        self._astronaut = None
        self._hud.set_trip_money(0.0)

    def _select_image(self) -> None:
        """ Sélectionne l'image et le masque à utiliser pour l'affichage du taxi en fonction de son état. """
        facing = self._flags & Taxi._FLAG_LEFT

        if self._flags & Taxi._FLAG_DESTROYED:
            self.image = self._surfaces[ImgSelector.DESTROYED][facing]
            self.mask = self._masks[ImgSelector.DESTROYED][facing]
            self._fuel_status = 100
            return

        condition_flags = Taxi._FLAG_TOP_REACTOR | Taxi._FLAG_REAR_REACTOR
        if self._flags & condition_flags == condition_flags:
            self.image = self._surfaces[ImgSelector.TOP_AND_REAR_REACTORS][facing]
            self.mask = self._masks[ImgSelector.TOP_AND_REAR_REACTORS][facing]
            return

        condition_flags = Taxi._FLAG_BOTTOM_REACTOR | Taxi._FLAG_REAR_REACTOR
        if self._flags & condition_flags == condition_flags:
            self.image = self._surfaces[ImgSelector.BOTTOM_AND_REAR_REACTORS][facing]
            self.mask = self._masks[ImgSelector.BOTTOM_AND_REAR_REACTORS][facing]
            return

        if self._flags & Taxi._FLAG_REAR_REACTOR:
            self.image = self._surfaces[ImgSelector.REAR_REACTOR][facing]
            self.mask = self._masks[ImgSelector.REAR_REACTOR][facing]
            return

        condition_flags = Taxi._FLAG_GEAR_OUT | Taxi._FLAG_BOTTOM_REACTOR
        if self._flags & condition_flags == condition_flags:
            self.image = self._surfaces[ImgSelector.GEAR_OUT_AND_BOTTOM_REACTOR][facing]
            self.mask = self._masks[ImgSelector.GEAR_OUT_AND_BOTTOM_REACTOR][facing]
            return

        if self._flags & Taxi._FLAG_BOTTOM_REACTOR:
            self.image = self._surfaces[ImgSelector.BOTTOM_REACTOR][facing]
            self.mask = self._masks[ImgSelector.BOTTOM_REACTOR][facing]
            return

        if self._flags & Taxi._FLAG_TOP_REACTOR:
            self.image = self._surfaces[ImgSelector.TOP_REACTOR][facing]
            self.mask = self._masks[ImgSelector.TOP_REACTOR][facing]
            return

        if self._flags & Taxi._FLAG_GEAR_OUT:
            self.image = self._surfaces[ImgSelector.GEAR_OUT][facing]
            self.mask = self._masks[ImgSelector.GEAR_OUT][facing]
            return

        self.image = self._surfaces[ImgSelector.IDLE][facing]
        self.mask = self._masks[ImgSelector.IDLE][facing]

    @staticmethod
    def _load_and_build_surfaces() -> tuple:
        """
        Charge et découpe la feuille de sprites (sprite sheet) pour le taxi.
        Construit les images et les masques pour chaque état.
        :return: un tuple contenant deux dictionnaires (avec les états comme clés):
                     - un dictionnaire d'images (pygame.Surface)
                     - un dictionnaire de masques (pygame.Mask)
        """
        surfaces = {}
        masks = {}
        sprite_sheet = pygame.image.load(Taxi._TAXIS_FILENAME).convert_alpha()
        sheet_width = sprite_sheet.get_width()
        sheet_height = sprite_sheet.get_height()

        # taxi normal - aucun réacteur - aucun train d'atterrissage
        surface = pygame.Surface((sheet_width / Taxi._NB_TAXI_IMAGES, sheet_height), flags=pygame.SRCALPHA)
        source_rect = surface.get_rect()
        surface.blit(sprite_sheet, (0, 0), source_rect)
        flipped = pygame.transform.flip(surface, True, False)
        surfaces[ImgSelector.IDLE] = surface, flipped
        masks[ImgSelector.IDLE] = pygame.mask.from_surface(surface), pygame.mask.from_surface(flipped)

        # taxi avec réacteur du dessous
        surface = pygame.Surface((sheet_width / Taxi._NB_TAXI_IMAGES, sheet_height), flags=pygame.SRCALPHA)
        source_rect = surface.get_rect()
        surface.blit(sprite_sheet, (0, 0), source_rect)
        source_rect.x = source_rect.width
        surface.blit(sprite_sheet, (0, 0), source_rect)
        flipped = pygame.transform.flip(surface, True, False)
        surfaces[ImgSelector.BOTTOM_REACTOR] = surface, flipped
        masks[ImgSelector.BOTTOM_REACTOR] = masks[ImgSelector.IDLE]

        # taxi avec réacteur du dessus
        surface = pygame.Surface((sheet_width / Taxi._NB_TAXI_IMAGES, sheet_height), flags=pygame.SRCALPHA)
        source_rect = surface.get_rect()
        surface.blit(sprite_sheet, (0, 0), source_rect)
        source_rect.x = 2 * source_rect.width
        surface.blit(sprite_sheet, (0, 0), source_rect)
        flipped = pygame.transform.flip(surface, True, False)
        surfaces[ImgSelector.TOP_REACTOR] = surface, flipped
        masks[ImgSelector.TOP_REACTOR] = masks[ImgSelector.IDLE]

        # taxi avec réacteur arrière
        surface = pygame.Surface((sheet_width / Taxi._NB_TAXI_IMAGES, sheet_height), flags=pygame.SRCALPHA)
        source_rect = surface.get_rect()
        surface.blit(sprite_sheet, (0, 0), source_rect)
        source_rect.x = 3 * source_rect.width
        surface.blit(sprite_sheet, (0, 0), source_rect)
        flipped = pygame.transform.flip(surface, True, False)
        surfaces[ImgSelector.REAR_REACTOR] = surface, flipped
        masks[ImgSelector.REAR_REACTOR] = masks[ImgSelector.IDLE]

        # taxi avec réacteurs du dessous et arrière
        surface = pygame.Surface((sheet_width / Taxi._NB_TAXI_IMAGES, sheet_height), flags=pygame.SRCALPHA)
        source_rect = surface.get_rect()
        surface.blit(sprite_sheet, (0, 0), source_rect)
        source_rect.x = source_rect.width
        surface.blit(sprite_sheet, (0, 0), source_rect)
        source_rect.x = 3 * source_rect.width
        surface.blit(sprite_sheet, (0, 0), source_rect)
        flipped = pygame.transform.flip(surface, True, False)
        surfaces[ImgSelector.BOTTOM_AND_REAR_REACTORS] = surface, flipped
        masks[ImgSelector.BOTTOM_AND_REAR_REACTORS] = masks[ImgSelector.IDLE]

        # taxi avec réacteurs du dessus et arrière
        surface = pygame.Surface((sheet_width / Taxi._NB_TAXI_IMAGES, sheet_height), flags=pygame.SRCALPHA)
        source_rect = surface.get_rect()
        surface.blit(sprite_sheet, (0, 0), source_rect)
        source_rect.x = 2 * source_rect.width
        surface.blit(sprite_sheet, (0, 0), source_rect)
        source_rect.x = 3 * source_rect.width
        surface.blit(sprite_sheet, (0, 0), source_rect)
        flipped = pygame.transform.flip(surface, True, False)
        surfaces[ImgSelector.TOP_AND_REAR_REACTORS] = surface, flipped
        masks[ImgSelector.TOP_AND_REAR_REACTORS] = masks[ImgSelector.IDLE]

        # taxi avec train d'atterrissage
        surface = pygame.Surface((sheet_width / Taxi._NB_TAXI_IMAGES, sheet_height), flags=pygame.SRCALPHA)
        source_rect = surface.get_rect()
        surface.blit(sprite_sheet, (0, 0), source_rect)
        source_rect.x = 4 * source_rect.width
        surface.blit(sprite_sheet, (0, 0), source_rect)
        flipped = pygame.transform.flip(surface, True, False)
        surfaces[ImgSelector.GEAR_OUT] = surface, flipped
        masks[ImgSelector.GEAR_OUT] = pygame.mask.from_surface(surface), pygame.mask.from_surface(flipped)

        # taxi avec train d'atterrissage comprimé
        surface = pygame.Surface((sheet_width / Taxi._NB_TAXI_IMAGES, sheet_height), flags=pygame.SRCALPHA)
        source_rect = surface.get_rect()
        source_rect.x = 5 * source_rect.width
        surface.blit(sprite_sheet, (0, 0), source_rect)
        flipped = pygame.transform.flip(surface, True, False)
        surfaces[ImgSelector.GEAR_SHOCKS] = surface, flipped
        masks[ImgSelector.GEAR_SHOCKS] = pygame.mask.from_surface(surface), pygame.mask.from_surface(flipped)

        # taxi avec réacteur du dessous et train d'atterrissage
        surface = pygame.Surface((sheet_width / Taxi._NB_TAXI_IMAGES, sheet_height), flags=pygame.SRCALPHA)
        source_rect = surface.get_rect()
        surface.blit(sprite_sheet, (0, 0), source_rect)
        source_rect.x = source_rect.width
        surface.blit(sprite_sheet, (0, 0), source_rect)
        source_rect.x = 4 * source_rect.width
        surface.blit(sprite_sheet, (0, 0), source_rect)
        flipped = pygame.transform.flip(surface, True, False)
        surfaces[ImgSelector.GEAR_OUT_AND_BOTTOM_REACTOR] = surface, flipped
        masks[ImgSelector.GEAR_OUT_AND_BOTTOM_REACTOR] = masks[ImgSelector.GEAR_OUT]

        # taxi détruit
        surface = pygame.Surface((sheet_width / Taxi._NB_TAXI_IMAGES, sheet_height), flags=pygame.SRCALPHA)
        source_rect = surface.get_rect()
        surface.blit(sprite_sheet, (0, 0), source_rect)
        surface = pygame.transform.flip(surface, False, True)
        flipped = pygame.transform.flip(surface, True, False)
        surfaces[ImgSelector.DESTROYED] = surface, flipped
        masks[ImgSelector.DESTROYED] = pygame.mask.from_surface(surface), pygame.mask.from_surface(flipped)

        return surfaces, masks
