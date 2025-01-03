import pygame
import gate
from game_settings import GameSettings


class Pad(pygame.sprite.Sprite):
    """ Plateforme. """

    # Initialisation de Pad.UP en tant qu'instance de Pad, pas une classe
    UP = None  # Pad.UP sera initialisé plus tard avec une instance de Pad

    _TEXT_COLOR = (255, 255, 255)
    _HEIGHT = 40

    _PAD_SURFACES = {}

    def __init__(self, number: int, filename: str, pos: tuple, astronaut_start_x: int, astronaut_end_x: int) -> None:
        """
        Initialise une instance de plateforme.
        :param number: le numéro de la plateforme
        :param filename: le nom du fichier graphique à utiliser
        :param pos: la position (x, y) de la plateforme à l'écran
        :param astronaut_start_x: la distance horizontale à partir du bord où apparaissent les astronautes
        :param astronaut_end_x: la distance horizontale à partir du bord où disparaissent les astronautes
        """
        super(Pad, self).__init__()

        self.number = number

        if filename in self._PAD_SURFACES:
            self.image, self.mask = self._PAD_SURFACES[filename]
        else:
            self.image = pygame.image.load(filename).convert_alpha()
            self.mask = pygame.mask.from_surface(self.image)
            self._PAD_SURFACES[filename] = (self.image, self.mask)

        font = GameSettings().pad_font
        self._label_text = font.render(f"  PAD {number}  ", True, Pad._TEXT_COLOR)

        text_width, text_height = self._label_text.get_size()

        background_height = text_height + 4
        background_width = text_width + background_height  # + hauteur, pour les coins arrondis
        self._label_background = Pad._build_label(background_width, background_height)

        visible_pixels_pad = 0
        transparent_pixels_pad = 0
        self.image.lock()
        for x in range(self.image.get_width()):
            r, g, b, a = self.image.get_at((x, 0))
            if a != 0:
                visible_pixels_pad += 1
            elif a == 0 and visible_pixels_pad == 0:
                transparent_pixels_pad += 1
        self.image.unlock()
        self._label_text_offset = ((visible_pixels_pad - text_width) / 2 + transparent_pixels_pad + 1, 3)
        self._label_background_offset = ((visible_pixels_pad - background_width) / 2 + transparent_pixels_pad, 2)

        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

        self.astronaut_start = pygame.Vector2(self.rect.x + astronaut_start_x, self.rect.y - 24)
        self.astronaut_end = pygame.Vector2(self.rect.x + astronaut_end_x, self.rect.y - 24)

    def draw(self, surface: pygame.Surface) -> None:
        image_copy = self.image.copy()

        image_copy.blit(self._label_background, self._label_background_offset)
        image_copy.blit(self._label_text, self._label_text_offset)

        surface.blit(image_copy, self.rect)

    def update(self, *args, **kwargs) -> None:
        pass

    @staticmethod
    def _build_label(width: int, height: int) -> pygame.Surface:
        """
        Construit l'étiquette (text holder) semi-tranparente sur laquelle on affiche le nom de la plateforme
        :param width: largeur de l'étiquette
        :param height: hauteur de l'étiquette
        :return: une surface contenant un rectangle arrondi semi-trasparent (l'étiquette)
        """
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        radius = height / 2
        pygame.draw.circle(surface, (0, 0, 0), (radius, radius), radius)
        pygame.draw.circle(surface, (0, 0, 0), (width - radius, radius), radius)
        pygame.draw.rect(surface, (0, 0, 0), (radius, 0, width - 2 * radius, height))

        surface.lock()
        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                r, g, b, a = surface.get_at((x, y))
                if a != 0:
                    surface.set_at((x, y), (r, g, b, 128))
        surface.unlock()

        return surface


